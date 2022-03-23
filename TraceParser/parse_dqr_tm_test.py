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
    basic_sample = [' 6.252: 82 00030000 48918577 6F03FF00  TF3 ic[3]=ni  tt=tu2 te=1 tm=1  va[64]=0x0000489185776F03',
                    ' 7.090: 82 00030000 000E77A0 2003FE00  TF3 ic[3]=ni  tt=tu1 te=1 tm=1  va[64]=0x0000000E77A02003',
                    ' 7.171: 82 00030000 1D300000 1E0BFE00  TF3 ic[3]=ni  tt=tu1 te=1 tm=1  va[64]=0x00001D3000001E0B',
                    ' 7.252: 82 00030000 000C0000 0107FE00  TF3 ic[3]=ni  tt=tu1 te=1 tm=1  va[64]=0x0000000C00000107',
                    ' 8.090: 82 00030000 0EC40000 33A3FE00  TF3 ic[3]=ni  tt=tu1 te=1 tm=1  va[64]=0x00000EC4000033A3']

    def setUp(self):
        self.fh = StringIO.StringIO()
        self.parser = parse_dqr_tm.PerfParser(cluster=7, core=5)

    def _init_fh(self, msgs):
        msg_str = '\n'.join(msgs)
        self.fh.write(msg_str)
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
        msg = ['6.2: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu2 te=1 tm=1 va[64]=0xFFFFFFFFFFFFFC02',
               '7.0: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0xDEADBEEFDEAFBF02',
               '7.1: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0xFCAFEFFF00000002',
               '7.2: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0xFBABEFFC00000002',
               '8.0: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0xFFEEDFFC00000002']
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
        msg = ['6.2: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu2 te=1 tm=1 va[64]=0x00000000000003FD',
               '7.0: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000001',
               '7.1: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x000000000003FFFD',
               '7.2: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x00000003FFFFFFFD',
               '8.0: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x00000003CAFEBABD']
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
        Interleaving is possible and has been seen on several traces when
        memory latency is higher, so we support it.
        """
        msg = ['2.252: 82 00000000 48BBDFBA 7B00FF00  TF3 ic[0]=ni  tt=tu2 te=1 tm=1 va[64]=0x000048BBDFBA7B00',
               '3.090: 82 00000000 000D3B40 2000FE00  TF3 ic[0]=ni  tt=tu1 te=1 tm=1 va[64]=0x0000000D3B402000',
               '3.096: 82 00030000 48BB6248 CC03FF00  TF3 ic[3]=ni  tt=tu2 te=1 tm=1 va[64]=0x000048BB6248CC03',
               '3.171: 82 00000000 1CC80000 1E08FE00  TF3 ic[0]=ni  tt=tu1 te=1 tm=1 va[64]=0x00001CC800001E08',
               '5.091: 82 00030000 00000000 0003FE00  TF3 ic[3]=ni  tt=tu1 te=1 tm=1 va[64]=0x0000000000000003',
               '3.252: 82 00000000 00100000 00FCFE00  TF3 ic[0]=ni  tt=tu1 te=1 tm=1 va[64]=0x00000010000000FC',
               '4.172: 82 00030000 02930000 0003FE00  TF3 ic[3]=ni  tt=tu1 te=1 tm=1 va[64]=0x0000029300000003',
               '5.090: 82 00000000 0EA80000 32F8FE00  TF3 ic[0]=ni  tt=tu1 te=1 tm=1 va[64]=0x00000EA8000032F8',
               '5.253: 82 00030000 00140000 0017FE00  TF3 ic[3]=ni  tt=tu1 te=1 tm=1 va[64]=0x0000001400000017',
               '6.090: 82 000300D6 C030006B 6373FE00  TF3 ic[3]=ni  tt=tu1 te=1 tm=1 va[64]=0x00D6C030006B6373']
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
        msg = ['1563.130:  0x00000000_0x0000001C TF5 overflow',
               '1563.134: 09                   00000002  TF2 ic[0]=ni',
               '1563.142: 09                   0000005A  TF2 ic[0]=ilb',
               '1563.150: 16                   00000024  TF6           tcbcode=2 tcbinfo=0',
               '1563.165: 82 00002449 C54BFB81 FF80F000  TF3 ic[0]=ni  tt=nt  te=0 tm=1  va[64]=0x2449C54BFB81FF80',
               '1563.246: 74 00000000 00000000 0000C000  TF3 ic[0]=ni  tt=nt  te=0 tm=0  va[56]=  0x00000000000000']
        self._init_fh(msg)
        self.parser.parse_trace_messages(self.fh)
        self.assertEqual(0, len(self.parser.samples))

    def test_sample_ending_in_overflow_frame_is_dropped(self):
        msg = ['6.0: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu2 te=1 tm=1 va[64]=0x0000000000000001',
               '6.1: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000001',
               '6.2: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000001',
               '6.4: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000001',
               '7.5: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000001',
               '7.6:  0x00000000_0x0000001C TF5 overflow']
        self._init_fh(msg)
        self.parser.parse_trace_messages(self.fh)
        self.assertEqual(0, len(self.parser.samples))

    def test_sample_straddling_overflow_frame_is_dropped(self):
        msg = ['6.0: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu2 te=1 tm=1 va[64]=0x0000000000000003',
               '6.1: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000003',
               '6.2: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000003',
               '7.3:  0x00000000_0x0000001C TF5 overflow',
               '7.4: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000003',
               '8.5: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000003',
               '8.6: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000003',
               '8.7: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000003']
        self._init_fh(msg)
        self.parser.parse_trace_messages(self.fh)
        self.assertEqual(0, len(self.parser.samples))

    def test_tmoas_tpc_recovery_from_overflow(self):
        """ Ensures TMOAS-TPC recovery works as expected after overflow """

        msg = list()
        msg.append(self._mock_tf5_overflow('7.3'))
        msg.append(self._mock_tmoas('9.6'))
        msg.append(self._mock_tpc('9.7'))
        msg.append(self._mock_tu2('10.3', 0x5))
        msg.append(self._mock_tu1('10.4', 0x5))
        msg.append(self._mock_tu1('10.5', 0x5))
        msg.append(self._mock_tu1('10.6', 0x5))
        msg.append(self._mock_tu1('10.7', 0x5))

        self._init_fh(msg)
        self.parser.parse_trace_messages(self.fh)
        self.assertEqual(1, len(self.parser.samples))

    @staticmethod
    def _mock_tf5_overflow(frame_pos):
        return '%s:  0x00000000_0x0000001C TF5 overflow' % frame_pos

    @staticmethod
    def _mock_tmoas(frame_pos):
        return ('%s: 41          00000000 00126D01  TF3 ic[1]=ni  tt=tmo te=1 tm=0     '
                'va[26]=         0x0000093      mmid=0000 pom=k10 isam=1 sync=0 ibt=1 vid=0' % frame_pos)

    @staticmethod
    def _mock_tpc(frame_pos):
        return ('%s: 74 000002A8 00000038 660CD900  TF3 ic[2]=ni  tt=tpc te=1 tm=1      '
                'va[56]=0xA80000000038660C      abs=0xA80000000038660C' % frame_pos)

    @staticmethod
    def _mock_tu2(frame_pos, val):
        return '%s: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu2 te=1 tm=1 va[64]=0x%016x' % (frame_pos, val)

    @staticmethod
    def _mock_tu1(frame_pos, val):
        return '%s: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x%016x' % (frame_pos, val)

    def test_ignores_samples_until_tmoas_tpc_recovery_from_overflow(self):
        """
        When overflow occurs, the parser must discard all subsequent traces
        until it sees a TMOAS-TPC pair.
        """
        msg = list()
        msg.append(self._mock_tf5_overflow('1.0'))
        msg.append(self._mock_tu2('1.1', 0x3))
        msg.append(self._mock_tu1('1.2', 0x3))
        msg.append(self._mock_tu1('1.3', 0x3))
        msg.append(self._mock_tu1('1.4', 0x3))
        msg.append(self._mock_tu1('1.5', 0x3))

        msg.append(self._mock_tmoas('3.4'))
        msg.append(self._mock_tpc('3.6'))

        msg.append(self._mock_tu2('4.1', 0x5))
        msg.append(self._mock_tu1('4.2', 0x5))
        msg.append(self._mock_tu1('4.3', 0x5))
        msg.append(self._mock_tu1('4.4', 0x5))
        msg.append(self._mock_tu1('4.5', 0x5))

        self._init_fh(msg)
        self.parser.parse_trace_messages(self.fh)
        self.assertEqual(1, len(self.parser.samples))
        self.assertEqual(1, self.parser.samples[0].vp)

    def test_state_is_reset_for_all_vps_on_overflow(self):
        """
        Ensures that the parser state is reset so that it hunts for TU2
        again instead of trying to complete the previous sample.

        This occurs for all VPs once an overflow is seen.
        """
        msg = list()

        # almost-complete sample on VP3
        msg.append(self._mock_tu2('6.0', 0x3))
        msg.append(self._mock_tu1('6.1', 0x3))
        msg.append(self._mock_tu1('6.2', 0x3))
        msg.append(self._mock_tu1('6.3', 0x3))

        # almost-complete sample on VP1
        msg.append(self._mock_tu2('7.0', 0x1))
        msg.append(self._mock_tu1('7.1', 0x1))
        msg.append(self._mock_tu1('7.2', 0x1))
        msg.append(self._mock_tu1('7.3', 0x1))

        msg.append(self._mock_tf5_overflow('8.0'))
        msg.append(self._mock_tmoas('9.4'))
        msg.append(self._mock_tpc('9.6'))

        # complete VP3 sample after overflow
        msg.append(self._mock_tu1('10.0', 0x3))

        # complete VP1 sample after overflow
        msg.append(self._mock_tu1('10.2', 0x1))

        self._init_fh(msg)
        self.parser.parse_trace_messages(self.fh)
        self.assertEqual(0, len(self.parser.samples))

    def test_tmoas_in_middle_of_sample(self):
        """
        TMOAS may show up from time to time due to processor mode changes,
        but should not affect samples.
        """
        msg = list()

        # almost-complete sample
        msg.append(self._mock_tu2('6.0', 0x2))
        msg.append(self._mock_tu1('6.1', 0x2))
        msg.append(self._mock_tu1('6.2', 0x2))
        msg.append(self._mock_tu1('6.3', 0x2))

        # some processor-mode change TMOAS trace formats
        msg.append(self._mock_tmoas('7.4'))
        msg.append(self._mock_tmoas('7.6'))

        # complete sample after TMOAS
        msg.append(self._mock_tu1('10.0', 0x2))

        self._init_fh(msg)
        self.parser.parse_trace_messages(self.fh)
        self.assertEqual(1, len(self.parser.samples))

    def test_frame_head_is_not_dropped_after_tmoas(self):
        msg = ['6.0: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu2 te=1 tm=1 va[64]=0x0000000000000001',
               '6.1: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000001',
               '6.2: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000001',
               '6.4: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000001',
               '6.5: 82 030000 0000 0000 TF3 ic[3]=ni tt=tu1 te=1 tm=1 va[64]=0x0000000000000001',

               '6.6: 41          00000000 00126D01  TF3 ic[1]=ni  tt=tmo te=1 tm=0     '
               'va[26]=         0x0000093      mmid=0000 pom=k10 isam=1 sync=0 ibt=1 vid=0']
        self._init_fh(msg)
        self.parser.parse_trace_messages(self.fh)
        self.assertEqual(1, len(self.parser.samples))

    def test_custom_data_sample(self):
        msg = [
            ' 6.2: 82 00030000 48918577 6F03FF00  TF3 ic[3]=ni  tt=tu2 te=1 tm=1  va[64]=0x0000489185776F03',
            ' 7.0: 82 00030000 000E77A0 2003FE00  TF3 ic[3]=ni  tt=tu1 te=1 tm=1  va[64]=0x0000000E77A02003',
            ' 7.1: 82 00030000 1D300000 1E0BFE00  TF3 ic[3]=ni  tt=tu1 te=1 tm=1  va[64]=0x000000002B300003',
            ' 7.2: 82 00030000 000C0000 0107FE00  TF3 ic[3]=ni  tt=tu1 te=1 tm=1  va[64]=0xDEADBEEF00000003',
            ' 8.0: 82 00030000 0EC40000 33A3FE00  TF3 ic[3]=ni  tt=tu1 te=1 tm=1  va[64]=0xCAFEBABE00000003']
        self._init_fh(msg)
        self.parser.parse_trace_messages(self.fh)
        self.assertEqual(1, len(self.parser.samples))

        sample = self.parser.samples[0]
        self.assertTrue(sample.is_custom_data)
        self.assertEqual(0xdeadbeefcafebabe, sample.custom_data)

    def test_get_overflow_frames(self):
        msg = ['1.130:  0x00000000_0x0000001C TF5 overflow',
               '1.246: 74 00000000 00000000 0000C000  TF3 ic[0]=ni  tt=nt  te=0 tm=0  va[56]=  0x00000000000000',
               '2.130:  0x00000000_0x0000001C TF5 overflow',
               '3.130:  0x00000000_0x0000001C TF5 overflow',
               '3.604: 74 00000000 00000000 0000C000  TF3 ic[0]=ni  tt=nt  te=0 tm=0  va[56]=  0x00000000000000',
               '3.704: 74 00000000 00000000 0000C000  TF3 ic[0]=ni  tt=nt  te=0 tm=0  va[56]=  0x00000000000000',
               '4.200: 82 00030000 48918577 6F03FF00  TF3 ic[3]=ni  tt=tu2 te=1 tm=1  va[64]=0x0000489185776F03',
               '5.130:  0x00000000_0x0000001C TF5 overflow']
        self._init_fh(msg)
        self.parser.parse_trace_messages(self.fh)
        self.assertEqual(0, len(self.parser.samples))

        overflow_frames = self.parser.get_overflow_frames()
        self.assertEqual(4, len(overflow_frames))


class TestPerfParserIntegration(unittest.TestCase):
    """ Integration-style tests on real data files """

    def test_on_dqr_trace_message(self):
        parser = parse_dqr_tm.PerfParser(cluster=7, core=5)

        with open('testdata/dqr_perf_trace.tm') as fh:
            parser.parse_trace_messages(fh)

        self.assertEqual(1948, len(parser.samples))

    def test_on_cache_miss_trace(self):
        parser = parse_dqr_tm.CacheMissParser()
        with open('testdata/dqr_cache_miss.tm') as fh:
            parser.parse_trace_messages(fh)

        self.assertEqual(697, len(parser.get_entries()))


class TestAddr2LineOutputParsing(unittest.TestCase):
    """ Tests addr2line output parsing """

    def test_parse_with_inlining(self):
        lines = ['0xa800000000427658: /projects/funos/platform/include/platform/lock.h:62\n',
                 '(inlined by) /projects/funos/platform/mips64/chario.c:136\n',
                 '(inlined by) /projects/funos/platform/mips64/chario.c:231\n']

        addrs = {}
        parse_dqr_tm.parse_next_addr(lines, addrs)

        info = addrs[0xa800000000427658]
        self.assertEqual(3, len(info))
        self.assertIn('lock.h:62', info[0])

    def test_parse_with_discriminator(self):
        lines = ['0xa800000000427558: /projects/funos/platform/mips64/bzero.c:58 (discriminator 1)\n']

        addrs = {}
        parse_dqr_tm.parse_next_addr(lines, addrs)

        info = addrs[0xa800000000427558]
        self.assertEqual(1, len(info))
        self.assertIn('bzero.c:58', info[0])

