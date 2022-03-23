#!/usr/bin/env python3

#
# Listener for CSI data.
#
# There are two ways to use this receiver.
#    1. Start it on a host before booting FunOS. Shut it down with a
#       SIGTERM or SIGHUP after FunOS exits. Data files will be
#       left next to the listener.
#    2. Start it on a host and leave it running "forever".
#       Send POST requests to the HTTP server to signal the start of a new
#       run (and where to write data to), and to signal the end of the
#       current run.
#
# The first method supports manual use of this listener, perhaps on custom
# setups. The second method is for fun-on-demand where we want to avoid the
# problem of having the listener be ready before FunOS starts sending data.
#
# The server thread listens for and accepts incoming connections.
# It starts a handler on a new thread for an accepted connection.
# The handler reads messages from the socket and writes these messages
# to files.
#
# The HTTP server thread listens on a specified port on the machine's
# IP address for POST requests. A "start" POST request tells the listener to
# accept data from a new run of FunOS, and where to write the data to.
# An "end" POST request tells the listener to stop writing data.
#
# Usage: csi_listener.py -h for help on usage
#
# Copyright (c) 2021 Fungible Inc. All rights reserved.
#

import argparse
import datetime
import glob
import http.server
import json
import logging
import os
import re
import select
import socketserver
import struct
import threading
import urllib.parse


# Time in seconds for select and polling intervals
TIMEOUT_INTERVAL = 5.0

# Time in seconds for a connected client to remain quiet before we assume it has
# failed.
# TODO (jimmy): consider passing as arbitrary key-value arguments to the server,
#               which will then pass those arguments to the handler
catastrophic_timeout = 100


class DirLookup(object):
    """
    Thread-safe lookup for trace directory by ip address.

    This may not be required in CPython because of the GIL, but paranoia wins
    the day.

    TODO(jimmy): consider emulating a dict instead of providing custom accessors
    """

    def __init__(self, default_dir=None):
        self.lock = threading.Lock()
        self.default_dir = default_dir
        self.dir_by_ip = {}

    def put(self, ip, dir):
        with self.lock:
            if ip in self.dir_by_ip:
                logging.warning('Changing directory for %s from'
                                ' %s to %s' % (ip, self.dir_by_ip[ip], dir))
            self.dir_by_ip[ip] = dir

    def remove(self, ip):
        with self.lock:
            if ip in self.dir_by_ip:
                del self.dir_by_ip[ip]

    def get(self, ip):
        with self.lock:
            return self.dir_by_ip.get(ip, self.default_dir)


class Message(object):
    """
    Cluster identifier and message data for that cluster.

    The cluster identifier is of type bytes.
    """
    def __init__(self):
        self.cluster = None
        self.data = bytearray()


class CSIMessageHandler(socketserver.BaseRequestHandler):
    """
    Handler for a connected CSI client.

    The handler should be run in a new thread, and will exit once the
    client breaks the connection. It will also exit if the client times
    out by not sending any packets.
    """

    # Header length for messages that we receive. This is one byte for
    # the cluster, 4 bytes for the length (big-endian).
    HDR_LEN = 5

    # Possible state values for message processing.
    STATE_HEADER = 0
    STATE_DATA = 1

    def setup(self):
        # Message processing state
        self.state = self.STATE_HEADER
        self.partial_header = bytearray()
        self.data_remaining = 0
        self.current_message = None
        self.writer = None

    def handle(self):
        """
        Reads from a socket, writes to a file.
        """
        global catastrophic_timeout
        total_timeout = 0
        sock = self.request
        self.writer = CSIWriter(self.client_address[0], self.server.dir_lookup)

        if self.server.auto_dir:
            self.create_auto_dir()

        try:
            while True:
                ready_for_read, _, _ = select.select([sock], [], [], TIMEOUT_INTERVAL)
                if ready_for_read:
                    alive = self.process_one_recv(sock)
                    if not alive:
                        logging.info('Client disconnection')
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
                        logging.info('Failed to recv for %f seconds. '
                                     'Assuming catastrophic '
                                     'failure of client' % total_timeout)
                        sock.close()
                        return
        except Exception as e:
            logging.error(str(e))
            sock.close()
            return
        finally:
            if self.server.auto_dir:
                self.server.dir_lookup.remove(self.client_address[0])

    def create_auto_dir(self):
        """
        Creates an automatically named directory based on client IP and time.
        TODO(jimmy): consider adding some form of UID to CSI configuration
        """
        current_time = datetime.datetime.utcnow().strftime('%Y_%m_%d_%H:%M:%SZ')
        dirname = '%s_UTC%s' % (self.client_address[0], current_time)
        dirpath = os.path.join('csi_raw_data', dirname)

        os.makedirs(dirpath, exist_ok=True)
        self.server.dir_lookup.put(self.client_address[0], dirpath)

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
                self.partial_header = bytearray()
                self.state = self.STATE_DATA

        elif self.state == self.STATE_DATA:
            fragment = sock.recv(self.data_remaining)
            if not fragment:
                return False
            self.data_remaining -= len(fragment)
            self.current_message.data += fragment
            if self.data_remaining == 0:
                self.writer.write(self.current_message)
                self.state = self.STATE_HEADER

        return True

    def process_header(self):
        """
        Processes a complete message header.

        The message header format is defined in the platform agent.
        """
        self.current_message = Message()

        # python funkiness: slice to ensure we get a bytes() object, not an int
        self.current_message.cluster = self.partial_header[0:1]
        self.data_remaining = struct.unpack('>L', self.partial_header[1:5])[0]


class CSIWriter(object):
    """
    The object responsible for writing CSI data to disk.
    """
    def __init__(self, client_ip, dir_lookup):
        self.client_ip = client_ip
        self.dir_lookup = dir_lookup
        self.seen_clusters = {}
        self.output_dir = None
        self.missing_dir_reported = False

    def write(self, msg):
        """
        Writes message data to the correct trace file.
        """
        self.output_dir = self.dir_lookup.get(self.client_ip)
        if self.output_dir is None:
            # only log once
            if not self.missing_dir_reported:
                logging.error('Unknown directory for %s' % self.client_ip)
            self.missing_dir_reported = True
            return

        try:
            self.process_message(msg)
        except Exception as e:
            logging.error(str(e))

    def process_message(self, msg):
        """
        Processes a message.

        We write the cluster id once to the per-cluster trace log.
        All subsequent message data is appended to the log.
        """
        if self.output_dir is None:
            return

        cluster_hex = msg.cluster.hex()
        written = cluster_hex in self.seen_clusters
        if not written:
            self.seen_clusters[cluster_hex] = True

        trace_file = 'trace_cluster_%s' % cluster_hex
        trace_file = os.path.join(self.output_dir, trace_file)
        try:
            with open(trace_file, 'ab') as fh:
                if not written:
                    fh.write(msg.cluster)
                fh.write(msg.data)
        except Exception as e:
            logging.error('Failed to write to %s: '
                          'exception was %s' % (trace_file, e.message))


class HTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """
    Handles requests that delineate the start and end of a
    performance-gathering run.

    Expects the server to have an instance of a DirLookup object.
    """
    def do_POST(self):
        """
        Respond to a POST request.

        Valid URLS are:
        /start?dir=<directory-for-data-dumps>&ip=<client-ip>
        /end?ip=<client-ip>
        """
        url = urllib.parse.urlparse(self.path)
        query_components = urllib.parse.parse_qs(url.query)

        match = re.match('/start$', url.path)
        if match:
            self.handle_start_post(query_components)

        match = re.match('/end$', url.path)
        if match:
            self.handle_end_post(query_components)

    def handle_start_post(self, query_components):
        """
        For a start POST request, put the entry in the lookup table.
        """
        output_dir = query_components.get('dir', [None])[0]
        if not output_dir:
            self.send_response(404)
            self.send_json_message('dir not specified')
            return

        if not os.path.isdir(output_dir):
            self.send_response(404)
            self.send_json_message('dir does not exist')
            return

        ip = query_components.get('ip', [None])[0]
        if not ip:
            self.send_response(404)
            self.send_json_message('ip not specified')
            return

        logging.info('POST start request with dir=%s and ip=%s' % (output_dir,
                                                                   ip))
        self.send_success_response_json()
        self.server.dir_lookup.put(ip, output_dir)

    def handle_end_post(self, query_components):
        """
        For an end POST request remove the entry from the lookup table.
        """
        logging.info('POST end request')
        ip = query_components.get('ip', [None])[0]
        if not ip:
            self.send_response(404)
            self.send_json_message('ip not specified')
            return

        logging.info('POST end request with ip=%s' % ip)
        self.send_success_response_json()
        self.server.dir_lookup.remove(ip)

    def send_success_response_json(self):
        self.send_response(200)
        self.send_json_message('success')

    def send_json_message(self, msg):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'text/json')
        self.end_headers()
        self.wfile.write(json.dumps({'msg': msg}).encode())

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
        self.wfile.write('OK'.encode())


class ThreadingHTTPServer(socketserver.ThreadingMixIn,
                          http.server.HTTPServer):
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csi-port', type=int,
                        help='Port to listen on for CSI traffic',
                        default=12121)
    parser.add_argument('--http-port', type=int,
                        help='Port to listen on for HTTP requests',
                        default=22001)
    parser.add_argument('--idle-timeout', type=int,
                        help='Time in seconds that an already-connected CSI '
                             'client can be silent before we assume it has'
                             'dropped the connection',
                        default=100)
    parser.add_argument('--auto-dir', action='store_true',
                        help='Stores client data in an automatically-created'
                             'directory.')

    args = parser.parse_args()
    logging.basicConfig(filename='csi_listener_%d.log' % args.http_port,
                        level=logging.INFO,
                        format='%(asctime)s %(message)s')

    global catastrophic_timeout
    catastrophic_timeout = args.idle_timeout

    # The default directory where all the traces are written to.
    trace_dir = '.'
    quit_if_trace_dumps_exist(trace_dir)

    # Build lookup
    dir_lookup = DirLookup(trace_dir)

    csi_serv = socketserver.ThreadingTCPServer(('', args.csi_port),
                                               CSIMessageHandler)
    csi_serv.dir_lookup = dir_lookup
    csi_serv.auto_dir = args.auto_dir

    http_serv = ThreadingHTTPServer(('', args.http_port),
                                    HTTPRequestHandler)
    http_serv.dir_lookup = dir_lookup

    csi_thread = threading.Thread(target=csi_serv.serve_forever)
    csi_thread.start()

    log('Serving on port %d' % args.http_port)
    http_serv.serve_forever(poll_interval=TIMEOUT_INTERVAL)


def quit_if_trace_dumps_exist(source_dir):
    """
    Bail out early if we already have trace dumps in the directory.

    This prevents the tool from appending to existing trace dumps, and
    lets users know that they will destroy existing dumps.
    """
    path = os.path.join(source_dir, 'trace_cluster_*')
    files = glob.glob(path)
    if files:
        print('ERROR: Trace cluster dumps already exist in %s\n'
               'Exiting to prevent overwriting of trace data. '
               'Remove the trace_cluster_* files if you want to '
               'start a new run.\n' % source_dir)
        sys.exit(1)


def log(msg):
    """ Simple wrapper around logging.info """
    logging.info(msg)


if __name__ == '__main__':
    main()
