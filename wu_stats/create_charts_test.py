#
# Tests for create_charts.py
#
# Copyright (c) 2019 Fungible Inc.  All rights reserved.
#

import json
import io
import unittest

import create_charts


class TestCreateCharts(unittest.TestCase):

    def test_faddr_to_ccv_conversion(self):
        self.assertEqual('6.3.0',
                         create_charts.faddr_to_ccv_id({'gid': 6, 'lid': 20}))
        self.assertEqual('4.0.0',
                         create_charts.faddr_to_ccv_id({'gid': 4, 'lid': 8}))
        self.assertEqual('2.0.1',
                         create_charts.faddr_to_ccv_id({'gid': 2, 'lid': 9}))
        self.assertEqual('3.5.3',
                         create_charts.faddr_to_ccv_id({'gid': 3, 'lid': 31}))

    def test_faddr_is_ignored_as_metric(self):
        in_file = io.StringIO(
            '[{"faddr": {"lid": 8, "queue": 0, "gid": 0}},'
            '{"faddr": {"lid": 9, "queue": 0, "gid": 0}}]'
        )
        result = TestCreateCharts.do_chart_creation(in_file)
        self.assertDictEqual({}, result)

    @staticmethod
    def do_chart_creation(in_file):
        out_file = io.StringIO()
        create_charts.produce_summary_charts(in_file, out_file)
        out_file.seek(0)
        return json.loads(out_file.getvalue())

    def test_chart_has_correct_metric(self):
        in_file = io.StringIO(
            '[{"beans": 5, "faddr": {"lid": 8, "queue": 0, "gid": 0}},'
            '{"beans": 7, "faddr": {"lid": 9, "queue": 0, "gid": 0}}]'
        )
        result = TestCreateCharts.do_chart_creation(in_file)
        self.assertIn('beans', result, 'missing metric')

    def test_chart_has_correct_data_values(self):
        in_file = io.StringIO(
            '[{"beans": 5, "faddr": {"lid": 8, "queue": 0, "gid": 0}},'
            '{"beans": 7, "faddr": {"lid": 9, "queue": 0, "gid": 0}}]'
        )
        result = TestCreateCharts.do_chart_creation(in_file)
        data_series = result['beans']['data'][0]
        self.assertListEqual([5, 7], data_series['y'], 'y data')
        self.assertListEqual(['0.0.0', '0.0.1'], data_series['x'], 'x data')

    def test_chart_has_layout(self):
        in_file = io.StringIO(
            '[{"beans": 5, "faddr": {"lid": 8, "queue": 0, "gid": 0}},'
            '{"beans": 7, "faddr": {"lid": 9, "queue": 0, "gid": 0}}]'
        )
        result = TestCreateCharts.do_chart_creation(in_file)
        self.assertIn('layout', result['beans'])

    def test_two_metrics_produce_two_charts(self):
        in_file = io.StringIO(
            '[{"beans": 5, "gravy": 3, '
            '"faddr": {"lid": 8, "queue": 0, "gid": 0}},'
            '{"beans": 7, "gravy": 9, '
            '"faddr": {"lid": 9, "queue": 0, "gid": 0}}]'
        )
        result = TestCreateCharts.do_chart_creation(in_file)
        self.assertIn('beans', result)
        self.assertIn('gravy', result)

        # sanity check on the second metric
        data_series = result['gravy']['data'][0]
        self.assertListEqual([3, 9], data_series['y'], 'y data')
        self.assertListEqual(['0.0.0', '0.0.1'], data_series['x'], 'x data')

    def test_exit_with_nonzero_code_for_empty_input(self):
        """
        The JSON input file is often empty if the run terminated unexpectedly.

        Check that we handle that case gracefully by printing to stderr
        and exiting with a non-zero return code.
        """
        in_file = io.StringIO()
        with self.assertRaises(SystemExit) as cm:
            TestCreateCharts.do_chart_creation(in_file)

        self.assertEqual(1, cm.exception.code)

    def test_throws_exception_for_malformed_json_input(self):
        """
        If the JSON input is malformed (parser bugs) it should be okay
        to throw an exception.

        Script failure does not result in job failure, it only means
        a chart does not get displayed in the job page.
        """
        in_file = io.StringIO(
            '[{"beans": 6 '
        )
        self.assertRaises(ValueError,
                          TestCreateCharts.do_chart_creation,
                          in_file)
