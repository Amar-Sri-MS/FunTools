#
# Integration tests for the parser and chart creator.
#
# Copyright (c) 2019 Fungible Inc.  All rights reserved.
#

import json
import io
import unittest

import create_charts
import parse_funos_log


class TestActualLogs(unittest.TestCase):

    @staticmethod
    def produce_charts(filepath):
        parse_result = io.StringIO()
        chart_result = io.StringIO()

        with open(filepath, 'r') as log_fh:
            parse_funos_log.parse_log_file(log_fh, parse_result)

            parse_result.seek(0)
            create_charts.produce_summary_charts(parse_result, chart_result)

            chart_result.seek(0)
            return json.loads(chart_result.getvalue())

    def test_dima_log(self):
        charts = TestActualLogs.produce_charts('testdata/dima.log')
        self.assertIn('wus_sent', charts)
        self.assertIn('wus_recvd', charts)
        self.assertIn('util_pct', charts)

    def test_f1_log(self):
        charts = TestActualLogs.produce_charts('testdata/f1.log')
        self.assertIn('wus_sent', charts)
        x_data = charts['wus_sent']['data'][0]['x']
        self.assertEqual(32, len(x_data), 'number of entries for x-data')
