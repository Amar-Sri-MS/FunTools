#!/usr/bin/env python3

#
# Telemetry receiver.
#
# There are two ways to use this receiver.
#    1. Start it on an attached network host before booting FunOS. Shut it
#       down with a SIGTERM or SIGHUP after FunOS exits. Data files will be
#       left next to the listener.
#    2. Start it on an attached network host and leave it running "forever".
#       Send POST requests to the HTTP server to signal the start of a new
#       run, and to signal the end of the current run.
#
# The first method supports manual use of this listener, perhaps on custom
# setups. The second method is for fun-on-demand where we want to avoid the
# problem of having the listener be ready before FunOS starts sending data.
#
# There are three threads of note in the listener:
#
# The reader thread reads from the socket as fast as it can and dumps
# the data into a buffer. It does not do any processing of the data
# to ensure that it gobbles up datagrams at the fastest possible rate
# to avoid drops.
#
# The writer thread checks the buffer and takes ownership of the data at
# regular intervals. Processing is done on the data after that.
#
# The HTTP server thread listens on a specified port on the machine's
# IP address for POST requests. A "start" POST request tells the listener to
# accept data from a new run of FunOS, and where to write the data to.
# An "end" POST request tells the listener to stop writing data.
#
# This module is similar to the perf listener. Sadly, they do not share code.
# This is a conscious decision to minimize dependencies so that manual use
# of this listener is easier.
# TODO: find a way to fix this
#
# Usage: telemetry_listener.py -h for help on usage
#
# Copyright (c) 2019 Fungible Inc. All rights reserved.
#

import argparse
import http.server
import glob
import json
import os
import re
import signal
import socket
import socketserver
import sys
import threading
import time
import urllib.parse

from functools import partial

# The maximum telemetry datagram length
MAX_DGRAM_LEN = 131072

# Telemetry samples only come every 2 seconds
DATAGRAM_INTERVAL_SECS = 2

# Shutdown event, used to end threads gracefully
shutdown_threads = threading.Event()

# Logging file handle
log_fh = None


class CommandRunner:
    """
    Layer that runs a command. Exists so we can swap this out
    with a mock for testing purposes.
    """

    def __init__(self):
        pass

    def execute(self, cmd):
        """ Executes the command """
        log('+ {}\n'.format(cmd))
        if os.system(cmd) != 0:
            log('FAIL: {}\n'.format(cmd))


# Replace this with mocks for testing
command_runner = CommandRunner()


class Buffer:
    """
    Shared buffer between reader and writer threads.
    """
    def __init__(self):
        self.buf = []
        self.lock = threading.Lock()

    def write(self, data):
        with self.lock:
            self.buf.append(data)

    def read(self):
        with self.lock:

            # A word about what is going on here:
            # First, a reference to the internal buffer is returned to the
            # caller, which takes ownership.
            #
            # Second, the internal buffer ref is pointed to a new empty list.
            data = self.buf
            self.buf = []
            return data

    def empty(self):
        with self.lock:
            empty = not self.buf
        return empty


class ThreadedHTTPServer(socketserver.ThreadingMixIn,
                         http.server.HTTPServer):
    """
    Handles requests in a separate thread.
    """
    def __init__(self, server_address, RequestHandlerClass, telemetry_writer):
        """
        Allows the telemetry writer to be passed as an argument, so that
        handlers can get at it.

        One would think that the handler will accept parameters, but we
        pass the handler class to the server and not an object. So it
        is impossible to determine how the server will instantiate the
        handler.
        """
        http.server.HTTPServer.__init__(self,
                                           server_address,
                                           RequestHandlerClass)
        self.telemetry_writer = telemetry_writer


class HTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """
    Handles requests that delineate the start and end of a telemetry
    run.
    """
    def do_POST(self):
        """
        Respond to a POST request.

        Valid URLS are:
        /start?dir=<directory-for-telemetry-data-dumps>
        /end
        """
        url = urllib.parse.urlparse(self.path)
        query_components = urllib.parse.parse_qs(url.query)

        match = re.match('/start$', url.path)
        if match:
            self.handle_start_post(query_components)

        match = re.match('/end$', url.path)
        if match:
            self.handle_end_post()

    def handle_start_post(self, query_components):
        """
        For a start POST request tell the telemetry writer to start a new run
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

        log('POST start request with dir=%s\n' % output_dir)
        self.send_success_response_json()
        self.server.telemetry_writer.start_new_run(output_dir)

    def handle_end_post(self):
        """
        For an end POST request tell the telemetry writer to end the current
        run.
        """
        log('POST end request\n')
        self.send_success_response_json()
        self.server.telemetry_writer.end_run()

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
        url = urllib.parse.urlparse(self.path)
        if url.path == '/funhealth':
            self.handle_funhealth()

    def handle_funhealth(self):
        """ Standard, basic funhealth response """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write('OK')


class TelemetryFileWriter:
    """
    The callable object responsible for writing telemetry datagrams to disk.
    """
    def __init__(self, buf, output_dir):
        self.buf = buf
        self.count = 0
        self.output_dir = output_dir
        self.lock = threading.Lock()

    def __call__(self):
        """
        Reads from a shared buffer and writes datagrams to disk.

        Runs until the shutdown_threads threading event is set.

        The use of __call__ makes instances of this class callable, i.e.
        one can call instance() and it will invoke this method.
        """
        try:
            while not shutdown_threads.is_set():
                time.sleep(DATAGRAM_INTERVAL_SECS)
                if self.buf.empty():
                    continue

                data_items = self.buf.read()

                # This is a fairly long time to hold a lock, but we'd love
                # all received datagrams to be written to the current
                # output directory if anyone tries to start a new run
                # prematurely.
                with self.lock:
                    for data in data_items:
                        self.process_datagram(data)
        except Exception as e:
            log(str(e))

    def process_datagram(self, data):
        """
        Processes a datagram.

        Each datagram represents a telemetry sample. For ease of decoding
        using the in-house binary JSON tool, we'll keep each sample in
        a separate file.

        This must be protected with self.lock when called.
        """
        if self.output_dir is None:
            return

        telemetry_file = 'telemetry_dump_%08d' % self.count
        telemetry_file = os.path.join(self.output_dir, telemetry_file)
        try:
            with open(telemetry_file, 'wb') as fh:
                fh.write(''.join(data))
            self.count += 1
        except Exception as e:
            log('Failed to write to %s: exception was %s\n' % (telemetry_file,
                                                               e.message))

    def start_new_run(self, new_dir):
        """
        Tells the telemetry writer to restart its internal count
        and to write data to the specified directory.

        In theory, this may be called while the writer is dumping data
        so we'll take precautions. In practice, the request should come
        tens of seconds after all data has been processed.
        """
        with self.lock:
            self.count = 0
            self.output_dir = new_dir

    def end_run(self):
        """
        Does cleanup work.

        Clears the output directory, which stops datagram processing from
        writing to files. This ensures that races between the invocation
        of start_new_run and the arrival of datagrams from the new run
        cannot cause corruption of previous output directories.
        """
        with self.lock:
            self.output_dir = None


def main():

    # This file is closed in the shutdown handler. See shutdown_handler()
    # comments for the reason why we log to a file instead of stdout.
    global log_fh

    parser = argparse.ArgumentParser()
    parser.add_argument('--telemetry-ip', type=str,
                        help='IP address for FunOS traffic',
                        default='60.1.1.1')
    parser.add_argument('--telemetry-port', type=int,
                        help='Port to listen on for FunOS traffic',
                        default=51234)
    parser.add_argument('--http-port', type=int,
                        help='Port to listen on for HTTP requests',
                        default=53333)

    # If we're running on a standard fun-on-demand setup then the FPG
    # setup process is handled by the startup scripts.
    parser.add_argument('--do-fpg-setup',
                        action='store_true',
                        help='Run the FPG setup process',
                        default=False)
    args = parser.parse_args()
    log_fh = open('telemetry_listener_%d.log' % args.http_port, 'a')

    # The directory where all the trace logs are written to. This
    # defaults to the current directory.
    dump_dir = '.'
    quit_if_telemetry_dumps_exist(dump_dir)

    setup_network(args.do_fpg_setup)

    udp_serv_socket = start_udp_serv_socket(args.telemetry_ip,
                                            args.telemetry_port)

    buf = Buffer()
    reader = threading.Thread(target=socket_reader,
                              kwargs={'serv_socket': udp_serv_socket,
                                      'buf': buf})
    # Make the socket reader a daemon because I don't want to mess around
    # with non-blocking selects and timeouts so that it does not block
    # indefinitely.
    # TODO: fix this by messing around with selects
    reader.daemon = True

    tfw = TelemetryFileWriter(buf, dump_dir)
    writer = threading.Thread(target=tfw)

    http_serv = ThreadedHTTPServer(('', args.http_port),
                                   HTTPRequestHandler,
                                   tfw)

    register_signal_handler(http_serv, args.do_fpg_setup)

    log('Starting threads\n')
    reader.start()
    writer.start()
    http_serv.serve_forever(poll_interval=5.0)


def quit_if_telemetry_dumps_exist(dump_dir):
    """
    Safety net in case someone runs the telemetry gathering in a directory
    that already has data.
    """
    path = os.path.join(dump_dir, 'telemetry_dump_*')
    files = glob.glob(path)
    if files:
        print('Telemetry dumps already exist in %s\n'
               'Exiting to prevent overwriting of telemetry data\n'
               'Please delete the telemetry_dump_* files if you want to\n'
               'start a new run' % dump_dir)
        sys.exit(1)


def start_udp_serv_socket(telemetry_ip, telemetry_port):
    """
    Starts the UDP server socket that listens for FunOS datagrams.
    """
    serv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serv_socket.bind((telemetry_ip, telemetry_port))
    log('Serving UDP on IP %s and port %d\n' % (telemetry_ip, telemetry_port))
    return serv_socket


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
    Shuts down the server.

    Note that this handler must not write to standard streams, or indefinite
    blocking will occur during termination on ssh hangup (which is how this
    server tends to be run). It is unclear what causes this: perhaps
    termination of the parent process closes standard streams?
    """
    log('Shutting down with signal %d\n' % sig)

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
    log('Requested HTTP server shutdown\n')

    teardown_network(do_fpg_setup)
    log('Network down\n')

    shutdown_file_writer_thread()
    log('Writer down\n')

    log('Shutdown complete\n')
    log_fh.close()


def teardown_network(do_fpg_setup):
    """ Cleans up the network setup """
    if not do_fpg_setup:
        return

    # Cleanup interfaces
    run_cmd('sudo arp -d 18.0.5.2')
    run_cmd('sudo ip addr flush dev {}'.format('fpg2'))
    run_cmd('sudo route del -net 18.0.5.0 netmask 255.255.255.0')


def run_cmd(cmd):
    """ A thin wrapper around the command runner """
    command_runner.execute(cmd)


def log(msg):
    """ Logs a message to the log file handle """
    log_fh.write(msg)
    log_fh.flush()


def shutdown_file_writer_thread():
    """
    Shuts down the file writer thread.

    TODO: find a good way to shut down the socket reader (recvfrom blocks)
    """
    shutdown_threads.set()


def setup_network(do_fpg_setup):
    """
    Sets up the network to receive packets on FPG2.

    This is not required for running on fun-on-demand infrastructure because
    it sets up the network for us. This is only required for users running
    on custom setups.
    """

    # The magic IP and MAC dest addresses for packets coming over FPG2
    # given csr_replay settings.
    ip = '60.1.1.1'
    mac = 'fe:dc:ba:44:55:99'
    intf = 'fpg2'

    # Display parameters of the interface
    run_cmd('ethtool {}'.format(intf))

    if do_fpg_setup:
        run_cmd('sudo ip link set {} down'.format(intf))
        time.sleep(1)

        _flush_cmd = 'sudo ip addr flush dev {}'.format(intf)
        _addr_cmd = 'sudo ip addr add {}/32 dev {}'.format(ip, intf)
        _mac_cmd = 'sudo ip link set {} address {}'.format(intf, mac)
        _up_cmd = 'sudo ip link set {} up'.format(intf)
        _route_cmd = 'sudo route add -net 18.0.5.0/24 gw {}'.format(ip)
        _arp_cmd = 'sudo arp -s 18.0.5.2 00:de:ad:be:ef:00'

        run_cmd(_flush_cmd)
        run_cmd(_addr_cmd)
        run_cmd(_mac_cmd)
        run_cmd(_up_cmd)
        time.sleep(5)

        run_cmd(_route_cmd)
        run_cmd(_arp_cmd)
        time.sleep(2)

    # Print some diagnostics after the setup is done
    run_cmd('ifconfig {}'.format(intf))
    run_cmd('route -n')
    run_cmd('arp -n')
    run_cmd('netstat -plnt')


def socket_reader(serv_socket, buf):
    """
    Reads datagrams from a socket, writes to a shared buffer.
    """
    try:
        while True:
            # This has to grab the entire datagram or we'll be sorry.
            data, _ = serv_socket.recvfrom(MAX_DGRAM_LEN)
            buf.write(data)
    except Exception as e:
        log(str(e))


if __name__ == '__main__':
    main()
