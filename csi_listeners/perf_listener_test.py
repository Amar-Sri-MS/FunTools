#!/usr/bin/env python3

#
# Tests for the perf listener.
#
# Copyright (c) 2019 Fungible Inc. All rights reserved.
#

import os
import shutil
import struct
import tempfile
import threading
import unittest

import perf_listener


class TestBuffer(unittest.TestCase):
    """ Tests for the buffer """

    def test_write_then_read(self):
        self.buf = perf_listener.Buffer()
        self.buf.write(['a', 'b', 'c'])
        self.assertFalse(self.buf.empty())
        self.assertEqual([['a', 'b', 'c']], self.buf.read())
        self.assertTrue(self.buf.empty())

    def test_write_then_read_multiple(self):
        self.buf = perf_listener.Buffer()
        self.buf.write(['a', 'b', 'c'])
        self.assertEqual([['a', 'b', 'c']], self.buf.read())

        self.buf.write(['d', 'e', 'f'])
        self.assertEqual([['d', 'e', 'f']], self.buf.read())

    def test_write_multiple_then_read(self):
        self.buf = perf_listener.Buffer()
        self.buf.write(['a', 'b', 'c'])
        self.buf.write(['d', 'e', 'f'])
        self.assertFalse(self.buf.empty())
        self.assertEqual([['a', 'b', 'c'], ['d', 'e', 'f']], self.buf.read())
        self.assertTrue(self.buf.empty())


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
        self.buf = perf_listener.Buffer()
        self.shutdown_event = threading.Event()
        self.handler = perf_listener.RdsockHandler(self.buf,
                                                   self.shutdown_event)
        self.sock = MockSocket()

    def test_process_complete_message(self):
        """
        Checks processing when the complete message is in the socket.
        """
        # the struct is { magic_id, cluster_len, data_len, cluster_id }
        hdr = struct.pack('>LHxxLB', 0xf1fdf1fd, 1, 8, 4)
        payload = 'abcdefgh'
        self.sock.data = hdr + payload

        # Once for the header, once for the data
        self.handler.process_one_recv(self.sock)
        self.handler.process_one_recv(self.sock)

        msgs = self.buf.read()
        self.assertEqual(1, len(msgs))
        self.assertEqual('\x04', msgs[0].cluster)
        self.assertEqual('abcdefgh', msgs[0].data)

    def test_process_header_in_chunks(self):
        """
        Checks processing when the header arrives in pieces
        """
        chunks = [struct.pack('>L', 0xf1fdf1fd),
                  struct.pack('>Hx', 1),
                  struct.pack('>xLB', 8, 2),
                  'deadbeef']

        for chunk in chunks:
            self.sock.data = chunk
            self.handler.process_one_recv(self.sock)

        msgs = self.buf.read()
        self.assertEqual(1, len(msgs))
        self.assertEqual('\x02', msgs[0].cluster)
        self.assertEqual('deadbeef', msgs[0].data)

    def test_process_data_in_chunks(self):
        """
        Checks processing when the data arrives in pieces
        """
        chunks = [struct.pack('>LHxxLB', 0xf1fdf1fd, 1, 32, 7),
                  'how many ',
                  'roads mu',
                  'st a man ',
                  'walk dow',
                  'n 42']
        for chunk in chunks:
            self.sock.data = chunk
            self.handler.process_one_recv(self.sock)

        msgs = self.buf.read()
        self.assertEqual(1, len(msgs))
        self.assertEqual('\x07', msgs[0].cluster)
        self.assertEqual('how many roads must a man walk d', msgs[0].data)

    def test_process_multiple_messages(self):
        chunks = [struct.pack('>LHxxLB', 0xf1fdf1fd, 1, 8, 4),
                  'dead',
                  'beef',
                  struct.pack('>LHxxLB', 0xf1fdf1fd, 1, 4, 5),
                  'cafe']
        for chunk in chunks:
            self.sock.data = chunk
            self.handler.process_one_recv(self.sock)
        msgs = self.buf.read()
        self.assertEqual(2, len(msgs))
        self.assertEqual('deadbeef', msgs[0].data)
        self.assertEqual('cafe', msgs[1].data)


class TestPerfWriter(unittest.TestCase):
    """ Tests that check perf writer functionality """

    def setUp(self):
        self.outdir = tempfile.mkdtemp('utest', 'perf')
        self.writer = perf_listener.PerfWriter(None, self.outdir)

    def tearDown(self):
        shutil.rmtree(self.outdir)

    def test_process_one_message(self):
        msg = perf_listener.Message()
        msg.cluster = '\x02'
        msg.data = 'vogon poetry'
        self.run_message_processing(msg)
        self.check_file_contents('trace_cluster_02', '\x02vogon poetry')

    def run_message_processing(self, msg):
        self.writer.process_message(msg)

    def check_file_contents(self, filename, expected_contents):
        expected_file = os.path.join(self.outdir, filename)
        self.assertTrue(os.path.exists(expected_file))
        with open(expected_file, 'r') as fh:
            self.assertEqual(expected_contents, fh.read())

    def test_cluster_is_only_written_once(self):
        msg0 = perf_listener.Message()
        msg0.cluster = '\x02'
        msg0.data = 'mice'
        self.run_message_processing(msg0)

        msg1 = perf_listener.Message()
        msg1.cluster = '\x02'
        msg1.data = 'dolphins'
        self.run_message_processing(msg1)
        self.check_file_contents('trace_cluster_02', '\x02micedolphins')

    def test_process_messages_from_different_clusters(self):
        """
        Ensures we write messages from different clusters to different files.
        """
        msg0 = perf_listener.Message()
        msg0.cluster = '\x02'
        msg0.data = 'mice'
        self.run_message_processing(msg0)

        msg1 = perf_listener.Message()
        msg1.cluster = '\x04'
        msg1.data = 'dolphins'
        self.run_message_processing(msg1)

        self.check_file_contents('trace_cluster_02', '\x02mice')
        self.check_file_contents('trace_cluster_04', '\x04dolphins')
