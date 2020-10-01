#!/usr/bin/env python3

#
# Unit tests for the log parsers
#

import datetime
import unittest

from blocks.log_parsers import FunOSInput
from blocks.log_parsers import MsecInput
from blocks.log_parsers import KeyValueInput
from blocks_test.common import msg_tuple_to_dict
from blocks_test.common import process


def _lines_to_iterable(lines):
    iter = [(None, None, 'uid', None, line) for line in lines]
    return iter


class FunOSInputTest(unittest.TestCase):
    """ Unit tests for the FunOS input parser """

    def setUp(self):
        self.block = FunOSInput()

    def test_skips_uboot_lines(self):
        """ Ensures that we only read FunOS log lines and not uboot """
        lines = ['[5004883 microseconds]: (4003907169 cycles) MMC INIT',
                 'Firmware authentication OK',
                 '[5412284 microseconds]: (4329827486 cycles) Start ELF',
                 '[5.413910 8.0.0] [kernel] Welcome to FunOS!']

        output = process(self.block, _lines_to_iterable(lines))
        self.assertEqual(1, len(output))

        log = msg_tuple_to_dict(output[0])['line']
        self.assertIn('Welcome to FunOS', log)

    def test_can_read_funos_timestamps(self):
        lines = ['[1596621622.940236 5.5.2] NOTICE rdsvol "Deleting RDS volume with uuid 4205b45709b24559']

        output = process(self.block, _lines_to_iterable(lines))
        self.assertEqual(1, len(output))

        timestamp = msg_tuple_to_dict(output[0])['datetime']
        expected = datetime.datetime.fromtimestamp(1596621622.940236)
        self.assertEqual(expected, timestamp)

    def test_sets_usec(self):
        lines = ['[1596621622.940236 5.5.2] NOTICE rdsvol "Deleting RDS volume with uuid 4205b45709b24559']
        output = process(self.block, _lines_to_iterable(lines))

        usecs = msg_tuple_to_dict(output[0])['usecs']
        self.assertEqual(940236, usecs)

    def test_formats_vp_and_line(self):
        """ Ensures that we remove the timestamp from the log line """
        lines = ['[5.505736 8.0.0] setting up chario async']
        output = process(self.block, _lines_to_iterable(lines))

        log = msg_tuple_to_dict(output[0])['line']
        self.assertEqual('[8.0.0]  setting up chario async', log)


class MsecInputTest(unittest.TestCase):
    """ Unit tests for the millisecond input parser """
    def setUp(self):
        self.block = MsecInput()

    def test_can_read_python_msecs(self):
        """ python logging style, oddball """
        lines = ['2020-08-05 03:14:56,774 - Dpu(c8:2c:2b:00:33:c8):execute_command']
        output = process(self.block, _lines_to_iterable(lines))

        timestamp = msg_tuple_to_dict(output[0])['datetime']
        expected = datetime.datetime.strptime('2020-08-05 03:14:56,774',
                                              '%Y-%m-%d %H:%M:%S,%f')
        self.assertEqual(expected, timestamp)

    def test_can_read_go_msecs(self):
        """ go microservice style """
        lines = ['2020/08/05 03:37:00.607 INFO    restmq  waitForResponses']
        output = process(self.block, _lines_to_iterable(lines))

        timestamp = msg_tuple_to_dict(output[0])['datetime']
        expected = datetime.datetime.strptime('2020/08/05 03:37:00.607',
                                              '%Y/%m/%d %H:%M:%S.%f')
        self.assertEqual(expected, timestamp)


class KeyValueInputTest(unittest.TestCase):
    """ Unit tests for Key Value input parser """
    def setUp(self):
        self.block = KeyValueInput()

    def test_can_convert_nsecs(self):
        """ check if nanoseconds are converted to microseconds """
        lines = ['time="2020-08-04T23:09:14.705144973-07:00" level=info msg="Relay for module: dataplane_interface key openconfig-fun-global:fun-global"']
        output = process(self.block, _lines_to_iterable(lines))

        timestamp = msg_tuple_to_dict(output[0])['usecs']
        expected = 705144

        self.assertEqual(expected, timestamp)

    # def test_can_convert_to_utc(self):
    #     """ check if timestamp is converted to UTC based on the timezone offset """
    #     lines = ['time="2020-08-04T23:09:14.705144973-07:00" level=info msg="Relay for module: dataplane_interface key openconfig-fun-global:fun-global"']
    #     output = process(self.block, _lines_to_iterable(lines))

    #     timestamp = msg_tuple_to_dict(output[0])['datetime']
    #     expected = datetime.datetime.strptime('2020-08-04T16:09:14.705144', '%Y-%m-%dT%H:%M:%S.%f')

    #     self.assertEqual(expected, timestamp)

    def test_can_combine_level_with_msg(self):
        """ check if the log level is prepended to the log msg """
        lines = ['time="2020-08-04T23:09:14.705144973-07:00" level=info msg="Relay for module: dataplane_interface key openconfig-fun-global:fun-global"']
        output = process(self.block, _lines_to_iterable(lines))

        msg = msg_tuple_to_dict(output[0])['line']
        expected = "info Relay for module: dataplane_interface key openconfig-fun-global:fun-global"

        self.assertEqual(expected, msg)