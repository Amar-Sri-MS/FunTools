#!/usr/bin/env python2.7

#
# Unit tests for dequeuer trace message parser
#
# Copyright (c) 2019 Fungible Inc.  All rights reserved.
#

import StringIO
import unittest

import parse_dqr_tm


class TestFraming(unittest.TestCase):
    """ Checks for correct grouping into frames """

    def setUp(self):
        self.fh = StringIO.StringIO()

    def _init_fh(self, msgs):
        self.fh.write(msgs)
        self.fh.seek(0)

    def test_basic_framing(self):
        msg = ('6.2: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu2 te=1 tm=1 va[64]=0xFFFFFFFFFFFFFC02\n'
               '7.0: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0xDEADBEEFDEAFBF03\n'
               '7.1: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0xFCAFEFFF00000003\n'
               '7.2: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0xFBABEFFC00000001\n'
               '8.0: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0xFFEEDFFC00000001\n')

        self._init_fh(msg)
        frames = parse_dqr_tm.parse_and_group_trace_formats(self.fh)
        self.assertEqual(3, len(frames), 'frame count')

        self.assertEqual(1, len(frames[0].tfs), 'frame 0 length')
        self.assertEqual(3, len(frames[1].tfs), 'frame 1 length')
        self.assertEqual(1, len(frames[2].tfs), 'frame 2 length')

    def test_overflow_frames_are_marked(self):
        msg = ('6.2: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu2 te=1 tm=1 va[64]=0xFFFFFFFFFFFFFC02\n'
               '7.1:  0x00000000_0x0000001C TF5 overflow\n')

        self._init_fh(msg)
        frames = parse_dqr_tm.parse_and_group_trace_formats(self.fh)
        self.assertFalse(frames[0].overflow, 'frame 0 overflow')
        self.assertTrue(frames[1].overflow, 'frame 1 overflow')


class TestPerfParser(unittest.TestCase):
    """ Tests for perf parsing """

    # An up-front example of what a perf sample in trace messages
    basic_sample = (' 6.252: 82 00030000 48918577 6F03FF00  TF3 ic[3]=ni  tt=tu2 te=1 tm=1  va[64]=0x0000489185776F03\n'
                    ' 7.090: 82 00030000 000E77A0 2003FE00  TF3 ic[3]=ni  tt=tu1 te=1 tm=1  va[64]=0x0000000E77A02003\n'
                    ' 7.171: 82 00030000 1D300000 1E0BFE00  TF3 ic[3]=ni  tt=tu1 te=1 tm=1  va[64]=0x00001D3000001E0B\n'
                    ' 7.252: 82 00030000 000C0000 0107FE00  TF3 ic[3]=ni  tt=tu1 te=1 tm=1  va[64]=0x0000000C00000107\n'
                    '8.090: 82 00030000 0EC40000 33A3FE00  TF3 ic[3]=ni  tt=tu1 te=1 tm=1  va[64]=0x00000EC4000033A3\n')

    def setUp(self):
        self.fh = StringIO.StringIO()
        self.parser = parse_dqr_tm.PerfParser(cluster=7, core=5)

    def _init_fh(self, msgs):
        self.fh.write(msgs)
        self.fh.seek(0)

    def test_can_parse_contiguous_sample(self):
        self._init_fh(self.basic_sample)
        self.parser.parse_trace_messages(self.fh)
        self.assertEqual(1, len(self.parser.samples), 'sample count')

        sample = self.parser.samples[0]
        self.assertEqual(3, sample.vp, 'vpid value')
        self.assertEqual(0x782, sample.wuid, 'wuid value')
        self.assertEqual(0x1224615ddb, sample.timestamp, 'timestamp')
        self.assertEqual(0x1d30, sample.perf_counts[0], 'perf 0')
        self.assertEqual(0x3, sample.perf_counts[1], 'perf 1')
        self.assertEqual(0x41, sample.perf_counts[2], 'perf 2')
        self.assertEqual(0x3b1, sample.perf_counts[3], 'perf 3')
        self.assertEqual(0xce8, sample.cp0_count, 'cp0 count')

    def test_can_extract_msb_sample_values(self):
        """
        Crafted values so that off-by-one errors in shift-and-mask operations
        can be caught. This sets patterns in the high-order bits.
        """
        msg = ('6.2: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu2 te=1 tm=1 va[64]=0xFFFFFFFFFFFFFC02\n'
               '7.0: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0xDEADBEEFDEAFBF02\n'
               '7.1: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0xFCAFEFFF00000002\n'
               '7.2: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0xFBABEFFC00000002\n'
               '8.0: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0xFFEEDFFC00000002\n')
        self._init_fh(msg)
        self.parser.parse_trace_messages(self.fh)
        self.assertEqual(1, len(self.parser.samples), 'sample count')

        sample = self.parser.samples[0]
        self.assertEqual(2, sample.vp, 'vpid value')
        self.assertEqual(0x3fffffffffffff, sample.timestamp, 'timestamp value')
        self.assertEqual(0xdeadbeefdeafbf, sample.arg0, 'arg0 value')
        self.assertEqual(0, sample.wuid, 'wuid value')
        self.assertEqual(0xfcafefff, sample.perf_counts[0], 'perf0 value')
        self.assertEqual(0x3eeafbff, sample.perf_counts[1], 'perf1 value')
        self.assertEqual(0, sample.perf_counts[2], 'perf2 value')
        self.assertEqual(0x3ffbb7ff, sample.perf_counts[3], 'perf3 value')
        self.assertEqual(0, sample.cp0_count, 'cp0 value')

    def test_can_extract_lsb_sample_values(self):
        """
        Crafted values so that off-by-one errors in shift-and-mask operations
        can be caught. This sets patterns in the low-order bits.
        """
        msg = ('6.2: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu2 te=1 tm=1 va[64]=0x00000000000003FD\n'
               '7.0: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000001\n'
               '7.1: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x000000000003FFFD\n'
               '7.2: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x00000003FFFFFFFD\n'
               '8.0: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x00000003CAFEBABD\n')
        self._init_fh(msg)
        self.parser.parse_trace_messages(self.fh)
        self.assertEqual(1, len(self.parser.samples), 'sample count')

        sample = self.parser.samples[0]
        self.assertEqual(1, sample.vp, 'vpid value')
        self.assertEqual(0, sample.timestamp, 'timestamp value')
        self.assertEqual(0xff00000000000000, sample.arg0, 'arg0 value')
        self.assertEqual(0xffff, sample.wuid, 'wuid value')
        self.assertEqual(0, sample.perf_counts[0], 'perf0 value')
        self.assertEqual(0, sample.perf_counts[1], 'perf1 value')
        self.assertEqual(0xffffffff, sample.perf_counts[2], 'perf2 value')
        self.assertEqual(0, sample.perf_counts[3], 'perf3 value')
        self.assertEqual(0xf2bfaeaf, sample.cp0_count, 'cp0 value')

    def test_can_parse_interleaved_samples(self):
        """
        The sample write is not atomic: it comprises multiple 64-bit words.
        Interleaving is theoretically possible, so we support it although
        it has not been seen in a trace as yet.
        TODO: try to cause/find interleaving on a real app
        """
        msg = ('2.252: 82 00000000 48BBDFBA 7B00FF00  TF3 ic[0]=ni  tt=tu2 te=1 tm=1 va[64]=0x000048BBDFBA7B00\n'
               '3.090: 82 00000000 000D3B40 2000FE00  TF3 ic[0]=ni  tt=tu1 te=1 tm=1 va[64]=0x0000000D3B402000\n'
               '3.096: 82 00030000 48BB6248 CC03FF00  TF3 ic[3]=ni  tt=tu2 te=1 tm=1 va[64]=0x000048BB6248CC03\n'
               '3.171: 82 00000000 1CC80000 1E08FE00  TF3 ic[0]=ni  tt=tu1 te=1 tm=1 va[64]=0x00001CC800001E08\n'
               '5.091: 82 00030000 00000000 0003FE00  TF3 ic[3]=ni  tt=tu1 te=1 tm=1 va[64]=0x0000000000000003\n'
               '3.252: 82 00000000 00100000 00FCFE00  TF3 ic[0]=ni  tt=tu1 te=1 tm=1 va[64]=0x00000010000000FC\n'
               '4.172: 82 00030000 02930000 0003FE00  TF3 ic[3]=ni  tt=tu1 te=1 tm=1 va[64]=0x0000029300000003\n'
               '5.090: 82 00000000 0EA80000 32F8FE00  TF3 ic[0]=ni  tt=tu1 te=1 tm=1 va[64]=0x00000EA8000032F8\n'
               '5.253: 82 00030000 00140000 0017FE00  TF3 ic[3]=ni  tt=tu1 te=1 tm=1 va[64]=0x0000001400000017\n'
               '6.090: 82 000300D6 C030006B 6373FE00  TF3 ic[3]=ni  tt=tu1 te=1 tm=1 va[64]=0x00D6C030006B6373\n')
        self._init_fh(msg)
        self.parser.parse_trace_messages(self.fh)
        self.assertEqual(2, len(self.parser.samples), 'sample count')

        sample0 = self.parser.samples[0]
        self.assertEqual(0, sample0.vp, 'vp for sample0')
        self.assertEqual(0xc00000000d3b4020, sample0.arg0, 'arg0 for sample0')
        self.assertEqual(0xcbe, sample0.cp0_count, 'cp0 for sample0')

        sample1 = self.parser.samples[1]
        self.assertEqual(3, sample1.vp, 'vp for sample1')
        self.assertEqual(0x5, sample1.perf_counts[2], 'perf2 for sample1')

    def test_overflow_frame_is_ignored(self):
        msg = ('1563.090: 41          00000000 00126D00  TF3 ic[0]=ni  tt=tmo te=1 tm=0     '
               'va[26]=         0x0000093      mmid=0000 pom=k10 isam=1 sync=0 ibt=1 vid=0\n'
               '1563.130:  0x00000000_0x0000001C TF5 overflow\n'
               '1563.134: 09                   00000002  TF2 ic[0]=ni\n'
               '1563.142: 09                   0000005A  TF2 ic[0]=ilb\n'
               '1563.150: 16                   00000024  TF6           tcbcode=2 tcbinfo=0\n'
               '1563.165: 82 00002449 C54BFB81 FF80F000  TF3 ic[0]=ni  tt=nt  te=0 tm=1  va[64]=0x2449C54BFB81FF80\n'
               '1563.246: 74 00000000 00000000 0000C000  TF3 ic[0]=ni  tt=nt  te=0 tm=0  va[56]=  0x00000000000000\n')
        self._init_fh(msg)
        self.parser.parse_trace_messages(self.fh)
        self.assertEqual(0, len(self.parser.samples))

    def test_sample_ending_in_overflow_frame_is_dropped(self):
        msg = ('6.0: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu2 te=1 tm=1 va[64]=0x0000000000000001\n'
               '6.1: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000001\n'
               '6.2: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000001\n'
               '6.4: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000001\n'
               '7.5: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000001\n'
               '7.6:  0x00000000_0x0000001C TF5 overflow\n')
        self._init_fh(msg)
        self.parser.parse_trace_messages(self.fh)
        self.assertEqual(0, len(self.parser.samples))

    def test_sample_straddling_overflow_frame_is_dropped(self):
        msg = ('6.0: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu2 te=1 tm=1 va[64]=0x0000000000000003\n'
               '6.1: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000003\n'
               '6.2: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000003\n'
               '7.3:  0x00000000_0x0000001C TF5 overflow\n'
               '7.4: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000003\n'
               '8.5: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000003\n'
               '8.6: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000003\n'
               '8.7: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000003\n')
        self._init_fh(msg)
        self.parser.parse_trace_messages(self.fh)
        self.assertEqual(0, len(self.parser.samples))

    def test_state_is_reset_for_all_vps_on_overflow(self):
        """
        Ensures that the parser state is reset so that it hunts for TU2
        again instead of trying to complete the previous sample.

        This occurs for all VPs once an overflow is seen.
        """
        msg = ('6.0: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu2 te=1 tm=1 va[64]=0x0000000000000003\n'
               '6.1: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000003\n'
               '6.2: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000003\n'
               '6.3: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000003\n'
               '6.4: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu2 te=1 tm=1 va[64]=0x0000000000000002\n'
               '6.5: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000002\n'
               '6.6: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000002\n'
               '6.7: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000002\n'
               '7.0:  0x00000000_0x0000001C TF5 overflow\n'
               '8.0: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000003\n'
               '8.1: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000002\n')
        self._init_fh(msg)
        self.parser.parse_trace_messages(self.fh)
        self.assertEqual(0, len(self.parser.samples))

    def test_frame_tail_is_dropped_after_tmoas(self):
        msg = ('6.0: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu2 te=1 tm=1 va[64]=0x0000000000000001\n'
               '6.1: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000001\n'
               '6.2: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000001\n'
               '6.4: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000001\n'
               '6.5: 41          00000000 00126D01  TF3 ic[1]=ni  tt=tmo te=1 tm=0     '
               'va[26]=         0x0000093      mmid=0000 pom=k10 isam=1 sync=0 ibt=1 vid=0\n'
               '6.6: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000001\n')
        self._init_fh(msg)
        self.parser.parse_trace_messages(self.fh)
        self.assertEqual(0, len(self.parser.samples))

    def test_frame_head_is_not_dropped_after_tmoas(self):
        msg = ('6.0: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu2 te=1 tm=1 va[64]=0x0000000000000001\n'
               '6.1: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000001\n'
               '6.2: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000001\n'
               '6.4: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000001\n'
               '6.5: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000001\n'
               '6.6: 41          00000000 00126D01  TF3 ic[1]=ni  tt=tmo te=1 tm=0     '
               'va[26]=         0x0000093      mmid=0000 pom=k10 isam=1 sync=0 ibt=1 vid=0\n')
        self._init_fh(msg)
        self.parser.parse_trace_messages(self.fh)
        self.assertEqual(1, len(self.parser.samples))


class TestPerfParserIntegration(unittest.TestCase):
    """ Integration-style tests on real data files """

    def test_on_dqr_trace_message(self):
        parser = parse_dqr_tm.PerfParser(cluster=7, core=5)

        with open('testdata/dqr_07_5_trace.tm') as fh:
            parser.parse_trace_messages(fh)

        self.assertEqual(2747, len(parser.samples))
