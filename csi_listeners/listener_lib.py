#!/usr/bin/env python2.7

#
# Common classes that are shared by listeners.
#
# Copyright (c) 2019 Fungible Inc. All rights reserved.
#

import logging
import os
import select
import threading
import time

# Time in seconds for select and polling intervals
TIMEOUT_INTERVAL = 5.0


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
            # Second, the internal buffer ref is pointed to a new empty buffer.
            data = self.buf
            self.buf = []
            return data

    def empty(self):
        with self.lock:
            empty = not self.buf
        return empty


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
        1. It must have a one-parameter constructor (excepting the self)
           that takes a Buffer.
        2. It must have a recv(sock) method that loops until terminated
           by a shutdown event, and handles received data from the socket.

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
                handler = self.handler_cls(self.buf)
                recv_thread = threading.Thread(target=handler.recv,
                                               kwargs={'sock': sock})
                recv_thread.start()


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

