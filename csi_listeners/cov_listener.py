#!/usr/bin/env python2.7

#
# Listener for rdsock messages from coverage.
#
# There are two ways to use this receiver.
#    1. Start it on an attached network host before booting FunOS. Shut it
#       down with a SIGTERM or SIGHUP after FunOS exits. Data files will be
#       left next to the listener.
#    2. Start it on an attached network host and leave it running "forever".
#       Send POST requests to the HTTP server to signal the start of a new
#       run (and where to write data to), and to signal the end of the
#       current run.
#
# The first method supports manual use of this listener, perhaps on custom
# setups. The second method is for fun-on-demand where we want to avoid the
# problem of having the listener be ready before FunOS starts sending data.
#
# There are three threads of note in the listener:
#
# The rdsock server thread listens for and accepts incoming connections.
# It starts an rdsock handler on a new thread for an accepted connection.
# The handler reads rdsock messages from the socket and writes these messages
# to a buffer that is shared with the writer thread.
#
# The writer thread checks the buffer and takes ownership of the messages at
# regular intervals. Messages are written out to files.
#
# The HTTP server thread listens on a specified port on the machine's
# IP address for POST requests. A "start" POST request tells the listener to
# accept data from a new run of FunOS, and where to write the data to.
# An "end" POST request tells the listener to stop writing data.
#
# Usage: cov_listener.py -h for help on usage
#
# Copyright (c) 2019 Fungible Inc. All rights reserved.
#

import argparse
import BaseHTTPServer
import glob
import json
import logging
import os
import re
import select
import signal
import socket
import SocketServer
import struct
import sys
import threading
import time
import urlparse

from functools import partial

import listener_lib

from listener_lib import Buffer
from listener_lib import RdsockServer

# Time in seconds for select and polling intervals
TIMEOUT_INTERVAL = 5.0

# Time in seconds for a connected client to remain quiet before we assume it has
# failed.
# TODO (jimmy): consider passing as arbitrary key-value arguments to the server,
#               which will then pass those arguments to the handler
catastrophic_timeout = 100

# Shutdown event, used to end threads gracefully
shutdown_threads = threading.Event()


class ThreadedHTTPServer(SocketServer.ThreadingMixIn,
                         BaseHTTPServer.HTTPServer):
    """
    Handles requests in a separate thread.
    """
    def __init__(self, server_address, RequestHandlerClass, cov_writer):
        """
        Allows the writer to be passed as an argument, so that
        handlers can get at it.

        One would think that the handler will accept parameters, but we
        pass the handler class to the server and not an object. So it
        is impossible to determine how the server will instantiate the
        handler.
        """
        BaseHTTPServer.HTTPServer.__init__(self,
                                           server_address,
                                           RequestHandlerClass)
        self.cov_writer = cov_writer


class HTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """
    Handles requests that delineate the start and end of a
    run.
    """
    def do_POST(self):
        """
        Respond to a POST request.

        Valid URLS are:
        /start?dir=<directory-for-data-dumps>
        /end
        """
        url = urlparse.urlparse(self.path)
        query_components = urlparse.parse_qs(url.query)

        match = re.match('/start$', url.path)
        if match:
            self.handle_start_post(query_components)

        match = re.match('/end$', url.path)
        if match:
            self.handle_end_post()

    def handle_start_post(self, query_components):
        """
        For a start POST request tell the writer to start a new run
        in the specified directory.
        """
        output_dirs = query_components.get('dir', None)
        if not output_dirs:
            self.send_response(404)
            self.send_json_message('dir not specified')
            return

        output_dir = output_dirs[0]
        if not os.path.isdir(output_dir):
            self.send_response(404)
            self.send_json_message('dir does not exist')
            return

        log('POST start request with dir=%s' % output_dir)
        self.send_success_response_json()
        self.server.cov_writer.start_new_run(output_dir)

    def handle_end_post(self):
        """
        For an end POST request tell the writer to end the current
        run.
        """
        log('POST end request')
        self.send_success_response_json()
        self.server.cov_writer.end_run()

    def send_success_response_json(self):
        self.send_response(200)
        self.send_json_message('success')

    def send_json_message(self, msg):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'text/json')
        self.wfile.write(json.dumps({'msg': msg}))

    def do_GET(self):
        """
        Respond to a GET request.

        Valid URLs are:
        /funhealth
        """
        url = urlparse.urlparse(self.path)
        if url.path == '/funhealth':
            self.handle_funhealth()

    def handle_funhealth(self):
        """ Standard, basic funhealth response """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write('OK')


class Message:
    def __init__(self):
        self.data = ''


class RdsockHandler:
    """
    Handler for a connected rdsock client.

    The handler should be run in a new thread, and will exit once the
    client breaks the connection. It will also exit if the client times
    out by not sending any packets.
    """

    # Header length for messages that we receive. This is
    # sizeof(rdsock_msghdr) in FunOS
    HDR_LEN = 12

    # Possible state values for message processing.
    STATE_HEADER = 0
    STATE_DATA = 1

    def __init__(self, buf):
        self.buf = buf

        # Message processing state
        self.state = self.STATE_HEADER
        self.partial_header = ''
        self.data_remaining = 0
        self.current_message = None

    def recv(self, sock):
        """
        Reads from a socket, writes to a shared buffer.
        """
        global catastrophic_timeout
        total_timeout = 0
        try:
            while not shutdown_threads.is_set():
                ready_for_read, _, _ = select.select([sock], [], [], TIMEOUT_INTERVAL)
                if ready_for_read:
                    alive = self.process_one_recv(sock)
                    if not alive:
                        log('Client disconnection')
                        sock.close()
                        return
                    total_timeout = 0
                else:
                    # Handle catastrophic failure of the client where the FIN
                    # packet does not arrive. This might occur fairly often
                    # given job timeouts or FunOS app failures.
                    #
                    # There appear to be two main ways to deal with catastrophic
                    # failure: keepalive packets, or a scheme where failure is
                    # assumed if the client is silent for too long. We choose
                    # the latter here because it is easier.
                    total_timeout += TIMEOUT_INTERVAL
                    if total_timeout > catastrophic_timeout:
                        log('Failed to recv for %f seconds. '
                            'Assuming catastrophic '
                            'failure of client' % total_timeout)
                        sock.close()
                        return
        except Exception as e:
            log(str(e))
            sock.close()
            return

    def process_one_recv(self, sock):
        """
        Attempts to process one recv() from a socket.

        This should only do one recv() as doing more may block. Think of this
        as attempting to make one transition in the state machine.
        """
        if self.state == self.STATE_HEADER:
            header_remaining = self.HDR_LEN - len(self.partial_header)
            fragment = sock.recv(header_remaining)
            if not fragment:
                return False
            self.partial_header += fragment
            if len(self.partial_header) == self.HDR_LEN:
                self.process_header()
                self.partial_header = ''
                self.state = self.STATE_DATA

        elif self.state == self.STATE_DATA:
            fragment = sock.recv(self.data_remaining)
            if not fragment:
                return False
            self.data_remaining -= len(fragment)
            self.current_message.data += fragment
            if self.data_remaining == 0:
                self.buf.write(self.current_message)
                self.state = self.STATE_HEADER

        return True

    def process_header(self):
        """
        Processes a complete message header.

        The message header format is defined in the struct rdsock_msghdr.
        One additional byte is added for the cluster index.
        """
        self.current_message = Message()
        self.data_remaining = struct.unpack('>L', self.partial_header[8:12])[0]


class CoverageWriter:
    """
    The callable object responsible for writing data to disk.
    """
    def __init__(self, buf, output_dir):
        self.buf = buf
        self.output_dir = output_dir
        self.lock = threading.Lock()
        self.idx = 0

    def __call__(self):
        """
        Reads from a shared buffer and writes message data to the correct
        trace file.

        Runs until the shutdown_threads threading event is set.

        The use of __call__ makes instances of this class callable, i.e.
        one can call instance() and it will invoke this method.
        """
        try:
            while not shutdown_threads.is_set():
                time.sleep(1)
                if self.buf.empty():
                    continue

                msgs = self.buf.read()
                with self.lock:
                    for msg in msgs:
                        self.process_message(msg)

        except Exception as e:
            log(str(e))

    def process_message(self, msg):
        """
        Processes a message.

        This must be protected with self.lock when called to protect against
        the possibility of ill-timed POST requests changing state while we
        are processing.
        """
        if self.output_dir is None:
            return

        cov_file = 'cov_data_%d' % self.idx
        self.idx += 1
        cov_file = os.path.join(self.output_dir, cov_file)
        try:
            with open(cov_file, 'ab') as fh:
                fh.write(msg.data)
        except Exception as e:
            log('Failed to write to %s: exception was %s' % (cov_file,
                                                             e.message))

    def start_new_run(self, new_dir):
        """
        Tells the writer to restart its internal count
        and to write data to the specified directory.

        In theory, this may be called while the writer is dumping data
        so we'll take precautions. In practice, the request should come
        tens of seconds after all data has been processed.
        """
        with self.lock:
            self.output_dir = new_dir

    def end_run(self):
        """
        Does cleanup work.

        Clears the output directory, which stops message processing from
        writing to files. This ensures that races between the invocation
        of start_new_run and the arrival of messages from the new run
        cannot cause corruption of previous output directories.
        """
        # Try a few times to get the buffer completely written out: at
        # times of high load the disk may not be able to cope with all
        # the writes.
        for i in range(0, 5):
            with self.lock:
                if self.buf.empty():
                    self.output_dir = None
                    return
            time.sleep(1)

        self.output_dir = None
        log('Failed to write all data')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cov-ip', type=str,
                        help='IP address for FunOS traffic',
                        default='60.1.1.1')
    parser.add_argument('--cov-port', type=int,
                        help='Port to listen on for FunOS traffic',
                        default=53077)
    parser.add_argument('--http-port', type=int,
                        help='Port to listen on for HTTP requests',
                        default=59333)
    parser.add_argument('--idle-timeout', type=int,
                        help='Time in seconds that an already-connected '
                             'socket can be silent before we assume it has'
                             'dropped the connection',
                        default=100)

    # If we're running on a standard fun-on-demand setup then the FPG
    # setup process is handled by the startup scripts.
    parser.add_argument('--do-fpg-setup',
                        action='store_true',
                        help='Run the FPG setup process',
                        default=False)
    args = parser.parse_args()
    logging.basicConfig(filename='cov_listener_%d.log' % args.http_port,
                        level=logging.INFO,
                        format='%(asctime)s %(message)s')

    global catastrophic_timeout
    catastrophic_timeout = args.idle_timeout

    # The source directory where all the trace logs are written to.
    cov_dir = '.'
    quit_if_dumps_exist(cov_dir)

    listener_lib.setup_network(args.do_fpg_setup)

    tcp_serv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_serv_socket.bind((args.cov_ip, args.cov_port))
    tcp_serv_socket.listen(1)
    log('Listening on IP %s and port %d' % (args.cov_ip, args.cov_port))

    buf = Buffer()
    rdsock_serv = RdsockServer(tcp_serv_socket, buf, RdsockHandler,
                               shutdown_threads)
    cov_writer = CoverageWriter(buf, cov_dir)
    writer_thread = threading.Thread(target=cov_writer)

    http_serv = ThreadedHTTPServer(('', args.http_port),
                                   HTTPRequestHandler,
                                   cov_writer)

    register_signal_handler(http_serv, args.do_fpg_setup)

    log('Starting threads')
    rdsock_serv.start()
    writer_thread.start()
    http_serv.serve_forever(poll_interval=TIMEOUT_INTERVAL)


def quit_if_dumps_exist(source_dir):
    """
    Bail out early if we already have trace dumps in the directory.

    This prevents the tool from appending to existing trace dumps, and
    lets users know that they will destroy existing dumps.
    """
    path = os.path.join(source_dir, 'cov_data_*')
    files = glob.glob(path)
    if files:
        print ('ERROR: Coverage dumps already exist in %s\n'
               'Exiting to prevent overwriting of trace data. '
               'Remove the cov_data_* files if you want to '
               'start a new run.\n' % source_dir)
        sys.exit(1)


def register_signal_handler(http_serv, do_fpg_setup):
    """
    Treat a SIGTERM/SIGHUP as an indication that we should stop.

    This must be called from the main thread, per signal documentation.
    """
    wrapped_handler = partial(shutdown_handler, http_serv, do_fpg_setup)
    signal.signal(signal.SIGTERM, wrapped_handler)
    signal.signal(signal.SIGHUP, wrapped_handler)


def shutdown_handler(http_serv, do_fpg_setup, sig, frame):
    """
    Shuts down the server and copies files from the source directory
    to the specified target directory.

    Note that this handler must not write to standard streams, or indefinite
    blocking will occur during termination on ssh hangup (which is how this
    server tends to be run). It is unclear what causes this: perhaps
    termination of the parent process closes standard streams?
    """
    log('Shutting down with signal %d' % sig)

    # The shutdown method must be called from a different thread from
    # the one that is running the HTTP server. Because the shutdown
    # handler and the server run on the main thread, we need to invoke
    # server shutdown from a different thread.
    #
    # We avoid calling join() because this handler must give way to the
    # HTTP server, or there will be deadlock. There is no apparent
    # requirement in Python to join all threads prior to exit.
    serv_close_thread = threading.Thread(target=http_serv.shutdown)
    serv_close_thread.start()
    log('Requested HTTP server shutdown')

    listener_lib.teardown_network(do_fpg_setup)
    log('Network down')

    shutdown_rdsock_and_writer_threads()
    log('Writer and rdsock down')

    log('Shutdown complete')


def log(msg):
    """ Simple wrapper around logging.info """
    logging.info(msg)


def shutdown_rdsock_and_writer_threads():
    """
    Shuts down the threads
    """
    shutdown_threads.set()


if __name__ == '__main__':
    main()
