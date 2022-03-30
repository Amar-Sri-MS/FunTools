#!/usr/bin/env python3

#
# Tests for the telemetry receiver.
#
# Copyright (c) 2019 Fungible Inc. All rights reserved.
#

import os
import shutil
import tempfile
import threading
import unittest

import telemetry_listener


# TODO figure out how to test the HTTP server


class TestBuffer(unittest.TestCase):
    """ Tests for the buffer """

    def test_write_then_read(self):
        self.buf = telemetry_listener.Buffer()
        self.buf.write(['a', 'b', 'c'])
        self.assertFalse(self.buf.empty())
        self.assertEqual([['a', 'b', 'c']], self.buf.read())
        self.assertTrue(self.buf.empty())

    def test_write_then_read_multiple(self):
        self.buf = telemetry_listener.Buffer()
        self.buf.write(['a', 'b', 'c'])
        self.assertEqual([['a', 'b', 'c']], self.buf.read())

        self.buf.write(['d', 'e', 'f'])
        self.assertEqual([['d', 'e', 'f']], self.buf.read())

    def test_write_multiple_then_read(self):
        self.buf = telemetry_listener.Buffer()
        self.buf.write(['a', 'b', 'c'])
        self.buf.write(['d', 'e', 'f'])
        self.assertFalse(self.buf.empty())
        self.assertEqual([['a', 'b', 'c'], ['d', 'e', 'f']], self.buf.read())
        self.assertTrue(self.buf.empty())


class MockCommandRunner():

    def __init__(self):
        self.commands_seen = []

    def execute(self, cmd):
        self.commands_seen.append(cmd)


class TestTelemetryWriter(unittest.TestCase):
    """ Tests for the telemetry writer """

    def setUp(self):
        telemetry_listener.command_runner = MockCommandRunner()
        self.output_dir = tempfile.mkdtemp('telemetry', 'unittest')
        self.buf = telemetry_listener.Buffer()
        self.writer = telemetry_listener.TelemetryFileWriter(self.buf,
                                                             self.output_dir)

    def tearDown(self):
        shutil.rmtree(self.output_dir)

    def test_writes_one_file_per_datagram(self):
        self.writer.process_datagram('wombat')
        self.writer.process_datagram('pangalacticgargleblaster')

        files = os.listdir(self.output_dir)
        self.assertEqual(2, len(files), 'number of files')
        self.assertIn('telemetry_dump_00000000', files)
        self.assertIn('telemetry_dump_00000001', files)

    def test_writes_to_specified_dir(self):
        self.output_dir = tempfile.mkdtemp('telemetry', 'unittest')
        self.writer.start_new_run(self.output_dir)
        self.writer.process_datagram('0')

        files = os.listdir(self.output_dir)
        self.assertIn('telemetry_dump_00000000', files)

    def test_start_new_run_restarts_file_naming(self):
        self.writer.process_datagram('0')
        self.writer.process_datagram('1')

        self.output_dir = tempfile.mkdtemp('telemetry', 'unittest')
        self.writer.start_new_run(self.output_dir)

        self.writer.process_datagram('2')
        files = os.listdir(self.output_dir)
        self.assertIn('telemetry_dump_00000000', files)
        self.assertNotIn('telemetry_dump_00000001', files)

    def test_writer_pulls_datagrams_from_buffer(self):
        thread = threading.Thread(target=self.writer)
        thread.start()

        files = os.listdir(self.output_dir)
        self.assertEqual(0, len(files), 'should be empty dir')
        self.buf.write('vogon poetry')

        telemetry_listener.shutdown_threads.set()
        thread.join()
        files = os.listdir(self.output_dir)
        self.assertEqual(1, len(files), 'should have file')

    def test_end_run_stops_writing_to_files(self):
        self.writer.end_run()
        self.writer.process_datagram('how many roads')

        files = os.listdir(self.output_dir)
        self.assertEqual(0, len(files))

    def test_start_run_restarts_writing_to_files(self):
        """
        Ensures that a start_new_run() call after an end_run() resumes
        file writing.
        """
        self.writer.end_run()
        self.writer.start_new_run(self.output_dir)
        self.writer.process_datagram('how many roads')

        files = os.listdir(self.output_dir)
        self.assertEqual(1, len(files))

    def test_ending_run_twice_has_same_effect(self):
        """
        To support cases where waiter.py may invoke this twice.
        (it's easier just to invoke without checking whether it has already
        been called during the shutdown sequence)
        """
        self.writer.end_run()
        self.writer.end_run()

        self.writer.process_datagram('how many roads')
        files = os.listdir(self.output_dir)
        self.assertEqual(0, len(files))
