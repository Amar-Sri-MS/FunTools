#!/usr/bin/env python3

#
# Unit tests for the log parsers
#

import datetime
import unittest

from blocks.log_parsers import FunOSInput
from blocks.log_parsers import GenericInput
from blocks.log_parsers import JSONInput
from blocks.log_parsers import KeyValueInput
from blocks_test.common import lines_to_iterable
from blocks_test.common import msg_tuple_to_dict
from blocks_test.common import process

from utils import timeline


class FunOSInputTest(unittest.TestCase):
    """ Unit tests for the FunOS input parser """

    def setUp(self):
        self.block = FunOSInput()
        timeline.init('test')

    def test_skips_uboot_lines(self):
        """ Ensures that we only read FunOS log lines and not uboot """
        lines = ['[5004883 microseconds]: (4003907169 cycles) MMC INIT',
                 'Firmware authentication OK',
                 '[5412284 microseconds]: (4329827486 cycles) Start ELF',
                 '[5.413910 8.0.0] [kernel] Welcome to FunOS!']

        output = process(self.block, lines_to_iterable(lines))
        self.assertEqual(1, len(output))

        log = msg_tuple_to_dict(output[0])['line']
        self.assertIn('Welcome to FunOS', log)

    def test_can_read_funos_timestamps(self):
        lines = ['[1596621622.940236 5.5.2] NOTICE rdsvol "Deleting RDS volume with uuid 4205b45709b24559']

        output = process(self.block, lines_to_iterable(lines))
        self.assertEqual(1, len(output))

        timestamp = msg_tuple_to_dict(output[0])['datetime']
        expected = datetime.datetime.utcfromtimestamp(1596621622.940236)
        self.assertEqual(expected, timestamp)

    def test_sets_usec(self):
        lines = ['[1596621622.940236 5.5.2] NOTICE rdsvol "Deleting RDS volume with uuid 4205b45709b24559']
        output = process(self.block, lines_to_iterable(lines))

        usecs = msg_tuple_to_dict(output[0])['usecs']
        self.assertEqual(940236, usecs)

    def test_formats_vp_and_line(self):
        """ Ensures that we remove the timestamp from the log line """
        lines = ['[5.505736 8.0.0] setting up chario async']
        output = process(self.block, lines_to_iterable(lines))

        log = msg_tuple_to_dict(output[0])['line']
        self.assertEqual('[8.0.0]  setting up chario async', log)


class GenericInputTest(unittest.TestCase):
    """ Unit tests for the generic input parser """
    def setUp(self):
        self.block = GenericInput()
        timeline.init('test')

    def test_can_convert_to_datetime(self):
        """ check if the date and time strings are converted to datetime """
        lines = ['2020-08-05 03:14:56,774 - Dpu(c8:2c:2b:00:33:c8):execute_command']
        output = process(self.block, lines_to_iterable(lines))

        timestamp = msg_tuple_to_dict(output[0])['datetime']
        expected = datetime.datetime.strptime('2020-08-05 03:14:56,774',
                                              '%Y-%m-%d %H:%M:%S,%f')
        self.assertEqual(expected, timestamp)

    def test_can_parse_different_format_timestamp(self):
        """ check if the date and time strings are converted to datetime """
        lines = ["25/03/2022 14:02:33 MCTP: ERROR - dest eid doesn't match (74 1)"]
        output = process(self.block, lines_to_iterable(lines))

        timestamp = msg_tuple_to_dict(output[0])['datetime']
        expected = datetime.datetime.strptime('25/03/2022 14:02:33',
                                              '%d/%m/%Y %H:%M:%S')
        self.assertEqual(expected, timestamp)

    def test_can_read_go_msecs(self):
        """ go microservice style """
        lines = ['2020/08/05 03:37:00.607 INFO    restmq  waitForResponses']
        output = process(self.block, lines_to_iterable(lines))

        timestamp = msg_tuple_to_dict(output[0])['datetime']
        expected = datetime.datetime.strptime('2020/08/05 03:37:00.607',
                                              '%Y/%m/%d %H:%M:%S.%f')
        self.assertEqual(expected, timestamp)

    def test_can_read_msg(self):
        """ check if the log message is read and datetime string is removed from it """
        lines = ['2020-08-05 03:14:56,774 - Dpu(c8:2c:2b:00:33:c8):execute_command']
        output = process(self.block, lines_to_iterable(lines))

        msg = msg_tuple_to_dict(output[0])['line']
        expected = '- Dpu(c8:2c:2b:00:33:c8):execute_command'

        self.assertEqual(expected, msg)

    def test_can_read_file_name(self):
        """ check if the file name is extracted from the log and added in the msg """
        lines = [
            '[physical_resources.go:1771] 2020-09-27 08:33:59.131131012 -0700 PDT m=+606939.398355152 eror c8:2c:2b:00:18:94'
        ]
        output = process(self.block, lines_to_iterable(lines))

        msg = msg_tuple_to_dict(output[0])['line']
        expected = '[physical_resources.go:1771] PDT m=+606939.398355152 eror c8:2c:2b:00:18:94'

        self.assertEqual(expected, msg)


class KeyValueInputTest(unittest.TestCase):
    """ Unit tests for Key Value input parser """
    def setUp(self):
        self.block = KeyValueInput()
        timeline.init('test')

    def test_can_convert_nsecs(self):
        """ check if nanoseconds are converted to microseconds """
        lines = ['time="2020-08-04T23:09:14.705144973-07:00" level=info msg="Relay for module: dataplane_interface key openconfig-fun-global:fun-global"']
        output = process(self.block, lines_to_iterable(lines))

        timestamp = msg_tuple_to_dict(output[0])['usecs']
        expected = 705144

        self.assertEqual(expected, timestamp)

    def test_can_convert_to_datetime(self):
        """ check if log time is converted to python datetime """
        lines = [
            'time="2020-08-04T23:09:14.705144973-07:00" level=info msg="Relay for module: dataplane_interface key openconfig-fun-global:fun-global"'
        ]
        output = process(self.block, lines_to_iterable(lines))

        timestamp = msg_tuple_to_dict(output[0])['datetime']
        expected = datetime.datetime.strptime('2020-08-04T23:09:14.705144', '%Y-%m-%dT%H:%M:%S.%f')

        self.assertEqual(expected, timestamp)

    # def test_can_convert_to_utc(self):
    #     """ check if timestamp is converted to UTC based on the timezone offset """
    #     lines = ['time="2020-08-04T23:09:14.705144973-07:00" level=info msg="Relay for module: dataplane_interface key openconfig-fun-global:fun-global"']
    #     output = process(self.block, lines_to_iterable(lines))

    #     timestamp = msg_tuple_to_dict(output[0])['datetime']
    #     expected = datetime.datetime.strptime('2020-08-04T16:09:14.705144', '%Y-%m-%dT%H:%M:%S.%f')

    #     self.assertEqual(expected, timestamp)

    def test_can_parse_log_level(self):
        """ check if the log level can be parsed from the log line """
        lines = ['time="2020-08-04T23:09:14.705144973-07:00" level=info msg="Relay for module: dataplane_interface key openconfig-fun-global:fun-global"']
        output = process(self.block, lines_to_iterable(lines))

        level = msg_tuple_to_dict(output[0])['level']
        expected = "info"

        self.assertEqual(expected, level)

    def test_can_parse_custom_key_values(self):
        """ check if the custom key value pairs can be parsed """
        lines = ['ts="2020-08-04T23:09:14.705144973-07:00" lvl=info msg="Relay for module: dataplane_interface key openconfig-fun-global:fun-global"']
        self.block.set_config({
            'key_name_mappings': {
                'level': 'lvl',
                'time': 'ts'
            }
        })
        output = process(self.block, lines_to_iterable(lines))

        level = msg_tuple_to_dict(output[0])['level']
        expected = "info"

        self.assertEqual(expected, level)

class JSONInputTest(unittest.TestCase):
    """ Unit tests for JSON input parser """
    def setUp(self):
        self.block = JSONInput()
        timeline.init('test')

    def test_can_convert_nsecs(self):
        """ check if nanoseconds are converted to microseconds """
        lines = ['{"level":"info","msg":"Validating kafka brokers","time":"2021-06-20 05:10:43.619987"}']
        output = process(self.block, lines_to_iterable(lines))

        timestamp = msg_tuple_to_dict(output[0])['usecs']
        expected = 619987

        self.assertEqual(expected, timestamp)

    def test_can_convert_to_datetime(self):
        """ check if log time is converted to python datetime """
        lines = [
            '{"level":"info","msg":"Validating kafka brokers","time":"2021-06-20 05:10:43.619987"}'
        ]
        output = process(self.block, lines_to_iterable(lines))

        timestamp = msg_tuple_to_dict(output[0])['datetime']
        expected = datetime.datetime.strptime('2021-06-20 05:10:43.619987', '%Y-%m-%d %H:%M:%S.%f')

        self.assertEqual(expected, timestamp)

    def test_can_parse_log_level(self):
        """ check if the log level can be parsed from the log line """
        lines = ['{"level":"info","msg":"Validating kafka brokers","time":"2021-06-20 05:10:43.619987"}']
        output = process(self.block, lines_to_iterable(lines))

        level = msg_tuple_to_dict(output[0])['level']
        expected = "info"

        self.assertEqual(expected, level)

    def test_can_parse_custom_key_values(self):
        """ check if the custom key value can be parsed """
        lines = ['{"lvl":"info","msg":"Validating kafka brokers","ts":"2021-06-20 05:10:43.619987"}']
        self.block.set_config({
            'key_name_mappings': {
                'level': 'lvl',
                'time': 'ts'
            }
        })
        output = process(self.block, lines_to_iterable(lines))

        level = msg_tuple_to_dict(output[0])['level']
        expected = "info"

        self.assertEqual(expected, level)