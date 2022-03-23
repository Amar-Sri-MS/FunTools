#!/usr/bin/env python3

#
# Unit tests for HW wu trace parsing.
#
# Copyright (c) 2019 Fungible Inc.  All rights reserved.
#

import struct
import unittest

from hw_wu_trace import NormalWU
from hw_wu_trace import StackGrouper
from hw_wu_trace import TraceFileParser
from hw_wu_trace import WUFactory


class NormalWUTest(unittest.TestCase):
    """
    Tests the normal WU object.
    """

    def setUp(self):
        self.wu_list = [{'name': 'idle'},
                        {'name': 'foo'},
                        {'name': 'bar'}]

    def test_correct_wu_name_from_wuid(self):
        wu0 = NormalWU(0, 0x0, 0x0, 0x0, self.wu_list)
        wu1 = NormalWU(1, 0x0, 0x0, 0x0, self.wu_list)

        self.assertEqual('idle', wu0.wu_name)
        self.assertEqual('foo', wu1.wu_name)

    def test_get_src_faddr(self):
        wuid = 2
        sgid = 4
        slid = 8
        action = (sgid << 51) | (slid << 46) | wuid

        wu = NormalWU(action, 0x0, 0x0, 0x0, self.wu_list)
        faddr = wu.get_src_faddr()

        # Prone to changes in string formats, urgh.
        self.assertEqual('FA4:8:0[VP]', faddr.as_faddr_str())

    def test_get_dst_faddr(self):
        wuid = 2
        dgid = 5
        dlid = 5
        action = (dgid << 41) | (dlid << 36) | wuid

        wu = NormalWU(action, 0x0, 0x0, 0x0, self.wu_list)
        faddr = wu.get_dst_faddr()

        # Prone to changes in string formats, urgh.
        self.assertEqual('FA5:5:0[LE]', faddr.as_faddr_str())


class StackGrouperTest(unittest.TestCase):
    """
    Tests the grouping of WUs into common stacks.
    """

    def setUp(self):
        self.wu_list = [{'name': 'idle'}, {'name': 'woowoo'}]

    def test_same_stack_wus_have_same_group(self):
        wu0 = NormalWU(1, 0x0, 0x0, 0x0, self.wu_list)
        wu1 = NormalWU(1, 0x7ff, 0x0, 0x0, self.wu_list)

        grouper = StackGrouper([wu0, wu1])
        groups = grouper.group()
        self.assertEqual(1, len(groups))

        group = groups[0]
        self.assertEqual(wu0, group[0])
        self.assertEqual(wu1, group[1])

    def test_different_stack_wus_have_different_groups(self):
        wu0 = NormalWU(1, 0x0, 0x0, 0x0, self.wu_list)
        wu1 = NormalWU(1, 0x800, 0x0, 0x0, self.wu_list)

        grouper = StackGrouper([wu0, wu1])
        groups = grouper.group()
        self.assertEqual(2, len(groups))

        group0 = groups[0]
        self.assertEqual(wu0, group0[0])
        group1 = groups[1]
        self.assertEqual(wu1, group1[0])


class WUFactoryTest(unittest.TestCase):
    """
    Tests the WU factory behaviour.
    """

    def setUp(self):
        self.factory = WUFactory()
        self.wu_list = [{'name': 'idle'}]

        normal_wu_cmd = 16
        action = (normal_wu_cmd << 59)
        self.wu_data = struct.pack('>QQQQ', action, 0x0, 0x0, 0x0)

        src = 1
        partial_timestamp = 8675309
        metadata_int = (src << 60) | partial_timestamp
        self.metadata = struct.pack('>Q', metadata_int)

    def test_normal_wu_creation(self):
        wu = self.factory.create(self.wu_data, self.metadata, self.wu_list)
        self.assertTrue(isinstance(wu, NormalWU))

    def test_wu_has_time(self):
        wu = self.factory.create(self.wu_data, self.metadata, self.wu_list)
        self.assertEqual(8675309 << 2, wu.time)

    def test_wu_has_trace_source(self):
        wu = self.factory.create(self.wu_data, self.metadata, self.wu_list)
        self.assertEqual(1, wu.trace_location)
