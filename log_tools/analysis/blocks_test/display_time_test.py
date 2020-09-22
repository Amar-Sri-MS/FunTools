#!/usr/bin/env python3

#
# Unit tests for the display time block
#

import datetime
import unittest

from blocks.display_time import HumanDateTime
from blocks_test.common import msg_tuple_to_dict
from blocks_test.common import process


class HumanDateTimeTest(unittest.TestCase):

    def setUp(self):
        self.dt = HumanDateTime()

    def test_display_time_is_set(self):
        """ Ensures the tuple element for display time is set """
        input = [(datetime.datetime.now(), 100, 'my-uid', None, 'my-log-line')]

        output = process(self.dt, input)

        self.assertEqual(1, len(output), 'Should only have one item')
        readable_dt = msg_tuple_to_dict(output[0])['display_time']

        self.assertIsNotNone(readable_dt, 'No entry for human readable time')

    def test_other_tuple_elements_are_propagated(self):
        """ Ensures tuple elements are propagated from in to out """
        now = datetime.datetime.now()
        usecs = 100
        uid = 'my-uid'
        log = 'my-log-line'

        input = [(now, usecs, uid, None, log)]
        output = process(self.dt, input)

        tuple = output[0]

        self.assertEqual(now, tuple[0])
        self.assertEqual(usecs, tuple[1])
        self.assertEqual(uid, tuple[2])
        self.assertEqual(log, tuple[4])
