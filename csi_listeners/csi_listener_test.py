#!/usr/bin/env python3

#
# Tests for the CSI listener.
#
# Copyright (c) 2021 Fungible Inc. All rights reserved.
#

import os
import shutil
import struct
import tempfile
import threading
import unittest

import csi_listener


class TestDirLookup(unittest.TestCase):
    """ Tests for the directory lookup """

    def test_basic_functions(self):
        """ Basic lookup table functionality """
        self.dir_lookup = csi_listener.DirLookup()
        ip = '10.1.1.1'
        dir = 'my_fake_directory'

        self.dir_lookup.put(ip, dir)
        self.assertEqual(dir, self.dir_lookup.get(ip))

        self.dir_lookup.remove(ip)
        self.assertIsNone(self.dir_lookup.get(ip))

    def test_default(self):
        """ Ensures we support a default value for trace directories """
        default = 'phony'
        self.dir_lookup = csi_listener.DirLookup(default_dir=default)
        self.assertEqual(default, self.dir_lookup.get('10.1.1.1'))


class TestWriter(unittest.TestCase):
    """ Tests that check writer functionality """

    def setUp(self):
        self.dir_lookup = csi_listener.DirLookup()
        self.ip = '192.168.2.1'
        self.outdir = tempfile.mkdtemp('utest', 'perf')
        self.dir_lookup.put(self.ip, self.outdir)
        self.writer = csi_listener.CSIWriter(self.ip, self.dir_lookup)

    def tearDown(self):
        shutil.rmtree(self.outdir)

    def test_process_one_message(self):
        msg = csi_listener.Message()
        msg.cluster = bytes('\x02', 'utf8')
        msg.type = bytes('\x00', 'utf8')
        msg.data = bytes('vogon poetry', 'utf8')
        self.run_message_processing(msg)
        self.check_file_contents('trace_cluster_02_type_00', '\x02vogon poetry')

    def run_message_processing(self, msg):
        self.writer.write(msg)

    def check_file_contents(self, filename, expected_contents):
        expected_file = os.path.join(self.outdir, filename)
        self.assertTrue(os.path.exists(expected_file))
        with open(expected_file, 'r') as fh:
            self.assertEqual(expected_contents, fh.read())

    def test_cluster_is_only_written_once(self):
        msg0 = csi_listener.Message()
        msg0.cluster = bytes('\x02', 'utf8')
        msg0.type = bytes('\x01', 'utf8')
        msg0.data = bytes('mice', 'utf8')
        self.run_message_processing(msg0)

        msg1 = csi_listener.Message()
        msg1.cluster = bytes('\x02', 'utf8')
        msg1.type = bytes('\x01', 'utf8')
        msg1.data = bytes('dolphins', 'utf8')
        self.run_message_processing(msg1)
        self.check_file_contents('trace_cluster_02_type_01', '\x02micedolphins')

    def test_process_messages_from_different_clusters(self):
        """
        Ensures we write messages from different clusters to different files.
        """
        msg0 = csi_listener.Message()
        msg0.cluster = bytes('\x02', 'utf8')
        msg0.type = bytes('\x01', 'utf8')
        msg0.data = bytes('mice', 'utf8')
        self.run_message_processing(msg0)

        msg1 = csi_listener.Message()
        msg1.cluster = bytes('\x04', 'utf8')
        msg1.type = bytes('\x01', 'utf8')
        msg1.data = bytes('dolphins', 'utf8')
        self.run_message_processing(msg1)

        self.check_file_contents('trace_cluster_02_type_01', '\x02mice')
        self.check_file_contents('trace_cluster_04_type_01', '\x04dolphins')
