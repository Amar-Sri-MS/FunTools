#!/usr/bin/env python3

#
# Tests for the SW wu trace listener.
#
# Copyright (c) 2019 Fungible Inc. All rights reserved.
#

import os
import shutil
import struct
import tempfile
import threading
import unittest

import listener_lib
import sw_trace_listener


class MockSocket:
    """
    Fake socket.

    Will not work with select etc, but we only need the recv() call.
    """
    def __init__(self):
        self.data = []

    def recv(self, count):
        ret = self.data[:count]
        self.data = self.data[count:]
        return ret


class TestRdsockHandler(unittest.TestCase):
    """
    Tests the rdsock handler.
    """
    def setUp(self):
        self.buf = listener_lib.Buffer()
        self.shutdown_event = threading.Event()
        self.handler = sw_trace_listener.RdsockHandler(self.buf,
                                                       self.shutdown_event)
        self.sock = MockSocket()

    def test_process_complete_message(self):
        """
        Checks processing when the complete message is in the socket.
        """
        # the struct is { magic_id, cluster_len, data_len }
        hdr = struct.pack('>LHxxL', 0xf1fdf1fd, 1, 8)
        payload = 'abcdefgh'
        self.sock.data = hdr + payload

        # Once for the header, once for the data
        self.handler.process_one_recv(self.sock)
        self.handler.process_one_recv(self.sock)

        msgs = self.buf.read()
        self.assertEqual(1, len(msgs))
        self.assertEqual('abcdefgh', msgs[0].data)

    def test_process_multiple_messages(self):
        chunks = [struct.pack('>LHxxL', 0xf1fdf1fd, 1, 8),
                  'dead',
                  'beef',
                  struct.pack('>LHxxL', 0xf1fdf1fd, 1, 4),
                  'cafe']
        for chunk in chunks:
            self.sock.data = chunk
            self.handler.process_one_recv(self.sock)
        msgs = self.buf.read()
        self.assertEqual(2, len(msgs))
        self.assertEqual('deadbeef', msgs[0].data)
        self.assertEqual('cafe', msgs[1].data)


class TestTraceWriter(unittest.TestCase):
    """ Tests that check trace writer functionality """

    def setUp(self):
        self.outdir = tempfile.mkdtemp('utest', 'trace')
        self.writer = sw_trace_listener.TraceWriter(None, self.outdir)

    def tearDown(self):
        shutil.rmtree(self.outdir)

    def test_process_one_message(self):
        msg = sw_trace_listener.Message()
        msg.data = 'vogon poetry'
        self.writer.process_message(msg)
        self.check_file_contents('sw_wu_raw.trace', 'vogon poetry')

    def check_file_contents(self, filename, expected_contents):
        expected_file = os.path.join(self.outdir, filename)
        self.assertTrue(os.path.exists(expected_file))
        with open(expected_file, 'r') as fh:
            self.assertEqual(expected_contents, fh.read())

