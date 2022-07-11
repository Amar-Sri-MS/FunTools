#!/usr/bin/env python3

#
# Common classes that are shared by listeners.
#
# Copyright (c) 2019 Fungible Inc. All rights reserved.
#

import http.server
import json
import logging
import os
import re
import select
import socketserver
import threading
import time
import urllib.parse

# Time in seconds for select and polling intervals
TIMEOUT_INTERVAL = 5.0


class Buffer(object):
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
            # Second, the internal buffer ref is pointed to a new empty buffer.
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
    def __init__(self, server_address, RequestHandlerClass, writer):
        """
        Allows the writer to be passed as an argument, so that
        handlers can get at it.

        One would think that the handler will accept parameters, but we
        pass the handler class to the server and not an object. So it
        is impossible to determine how the server will instantiate the
        handler.
        """
        http.server.HTTPServer.__init__(self,
                                           server_address,
                                           RequestHandlerClass)
        self.writer = writer


class HTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    """
    Handles requests that delineate the start and end of a
    performance-gathering run.

    Expects the server to have an instance of a BaseWriter named "writer"
    that it can forward start and end requests to.

    Those expectations are really quirky, but we have no control over how this
    handler is instantiated in the server. All handler parameterization must
    be part of the server, and discovered by the handler.
    """
    def do_POST(self):
        """
        Respond to a POST request.

        Valid URLS are:
        /start?dir=<directory-for-data-dumps>
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

        logging.info('POST start request with dir=%s' % output_dir)
        self.send_success_response_json()
        self.server.writer.start_new_run(output_dir)

    def handle_end_post(self):
        """
        For an end POST request tell the writer to end the current
        run.
        """
        logging.info('POST end request')
        self.send_success_response_json()
        self.server.writer.end_run()

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


class RdsockServer:
    """
    Serves rdsock clients, writing their messages to a buffer.

    This is only tested with one concurrent connection from one client
    because that is the current use case. One listener is bound to
    one F1, and an F1 only makes one connection during a perf run.

    However, the server should support a client that makes multiple
    non-overlapping connections during an F1 run.

    Concurrent connections will require the unique identifier of the
    clients to be sent to the writer thread along with the messages.

    The handler_cls must follow the following contract:
        1. It must have a two-parameter constructor (excepting the self)
           that takes a Buffer and threading Event (a shutdown event).
        2. It must have a recv(sock) method that loops until terminated
           by the shutdown event, and handles received data from the socket.

    Each connection gets a new instance of the handler_cls to deal with its
    messages.
    """
    def __init__(self, serv_socket, buf, handler_cls, shutdown_event):
        self.serv_socket = serv_socket
        self.buf = buf
        self.handler_cls = handler_cls
        self.shutdown_event = shutdown_event

    def start(self):
        accept_thread = threading.Thread(target=self.accept_handler)
        accept_thread.start()

    def accept_handler(self):
        """
        Loops until shutdown, accepting connections from clients and starting
        rdsock handlers on new threads.

        TODO (jimmy): This really needs to use non-blocking sockets to avoid
                      a race where the client drops between the select and
                      accept.
        """
        while not self.shutdown_event.is_set():
            # The use of select allows regular checks for shutdown
            ready_to_accept, _, _ = select.select([self.serv_socket], [], [], TIMEOUT_INTERVAL)
            if ready_to_accept:
                sock, _ = self.serv_socket.accept()
                logging.info('Accepted connection from client')

                # Each connection gets a new handler. This ensures that state
                # from one session never leaks to the next.
                #
                # There is one potential vulnerability: each handler writes
                # to the same buffer. Only one handler should be active at
                # any time, but if this becomes an issue consider starting
                # new instances of handler, buffer and writer for each
                # connection.
                handler = self.handler_cls(self.buf, self.shutdown_event)
                recv_thread = threading.Thread(target=handler.recv,
                                               kwargs={'sock': sock})
                recv_thread.start()


class BaseWriter(object):
    """
    Base class for the callable object responsible for writing data to disk.

    Subclasses should override the __call__, start_run, and end_run methods
    to do the appropriate thing for their needs.
    """
    def __init__(self, buf, output_dir):
        self.buf = buf
        self.output_dir = output_dir

    def __call__(self):
        """
        Reads from a shared buffer (buf) and writes message data to the correct
        trace file in the output directory (output_dir).

        The use of __call__ makes instances of this class callable, i.e.
        one can call instance() and it will invoke this method. You should
        expect __call__ to be invoked in its own separate thread.
        """
        pass

    def start_new_run(self, new_dir):
        """
        Tells the writer to start a new run in the specified output
        directory (new_dir).
        """
        pass

    def end_run(self):
        """
        Does cleanup work.
        """
        pass


def setup_network(do_fpg_setup):
    """
    Sets up the network to receive packets on FPG2.

    This is only required for manual usage on custom setups.
    Telemetry/performance servers already have the correct setup.
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
    run_cmd('ps aux | grep perf_listener')
    run_cmd('netstat -plnt')


def teardown_network(do_fpg_setup):
    """
    Cleans the setup we did for the network.
    """
    if not do_fpg_setup:
        return

    # Cleanup interfaces
    run_cmd('sudo arp -d 18.0.5.2')
    run_cmd('sudo arp -d 18.0.5.2')
    run_cmd('sudo arp -d 18.0.5.2')


def run_cmd(cmd):
    logging.info('+ {}'.format(cmd))
    if os.system(cmd) != 0:
        logging.error('FAIL: {}'.format(cmd))

