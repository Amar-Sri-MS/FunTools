#!/usr/bin/env python2.7

#
# Unit tests for trace formats.
#
# Copyright (c) 2019 Fungible Inc.  All rights reserved.
#

import unittest

import tr_formats


class TestTF3(unittest.TestCase):

    def setUp(self):
        self.tf = tr_formats.TF3()

    def test_can_parse_tu1_message(self):
        m = ' 61.252: 82 00000000 47D80000 3FB4FE00  TF3 ic[0]=ni  tt=tu1 te=1 tm=1      va[64]=0x000047D800003FB4'
        self.tf.init_from_msg(m)
        self.assertEqual('ni', self.tf.inscomp, 'inscomp value')
        self.assertEqual('tu1', self.tf.ttype, 'ttype value')
        self.assertEqual(0x000047D800003FB4, self.tf.addr, 'addr value')

    def test_can_parse_tu2_message(self):
        m = '70.171: 82 00020000 48913FDD C802FF00  TF3 ic[2]=ni  tt=tu2 te=1 tm=1      va[64]=0x000048913FDDC802'
        self.tf.init_from_msg(m)
        self.assertEqual('ni', self.tf.inscomp, 'inscomp value')
        self.assertEqual('tu2', self.tf.ttype, 'ttype value')
        self.assertEqual(0x000048913FDDC802, self.tf.addr, 'addr value')

    def test_can_parse_corrupted_inscomp_for_tu_message(self):
        """
        Check that we can parse corrupted values when overflow or TMOAS
        occurs without raising exceptions. Higher-level code deals with
        these oddball cases.
        """
        m = '184.221: 26          00000878  TF3 ic[0]=?   tt=nt  te=1 tm=0      va[08]=              0x00'
        self.tf.init_from_msg(m)
        self.assertEqual('?', self.tf.inscomp, 'inscomp value')

    def test_can_parse_corrupted_vpid_for_tu_message(self):
        """ Sometimes the value in ic[VPID] goes insane """
        m = '184.221: 26          00000878  TF3 ic[2567]=?   tt=nt  te=1 tm=0      va[08]=              0x00'
        self.tf.init_from_msg(m)
        self.assertEqual('?', self.tf.inscomp, 'inscomp value')

    def test_can_parse_tmoas_message(self):
        m = ('  1686.018: 41          00000000 00126D00  TF3 ic[0]=ni  tt=tmo te=1 tm=0      '
             'va[26]=         0x0000093      mmid=0000 pom=k10 isam=1 sync=0 ibt=1 vid=0')
        self.tf.init_from_msg(m)

    def test_can_parse_tla_type(self):
        m = ('   426.246: 74 000000A8 000003B8 1180DA00  TF3 ic[0]=ni  tt=tla te=1 tm=1      '
             'va[56]=0xA800000003B81180')
        self.tf.init_from_msg(m)
        self.assertEqual('ni', self.tf.inscomp, 'inscomp value')
        self.assertEqual('tla', self.tf.ttype, 'ttype value')
        self.assertEqual(0xA800000003B81180, self.tf.addr, 'addr value')

    def test_can_parse_tpc_type(self):
        m = ('    68.149: 74 000000A8 00000045 A390D900  TF3 ic[0]=ni  tt=tpc te=1 tm=1      '
             'va[56]=0xA80000000045A390      abs=0xA80000000045A390')
        self.tf.init_from_msg(m)
        self.assertEqual('tpc', self.tf.ttype, 'ttype value')
        self.assertEqual(0xA80000000045A390, self.tf.addr, 'addr value')

    def test_raises_exception_for_unparseable_message(self):
        """
        Ensure explosion if message is unexpected: this lets us improve the
        parser, and detect odd cases easily.
        """
        m = '  1686.018: 41 00000000 00126D00  TF3 ic[?]=  tt=? te=? tm=? '
        self.assertRaises(ValueError, self.tf.init_from_msg, m)


class TestUtilityMethods(unittest.TestCase):

    def test_is_tu1(self):
        tf = tr_formats.TF3();
        tf.ttype = 'tu1'
        self.assertTrue(tr_formats.is_tu1(tf))

    def test_is_tu2(self):
        tf = tr_formats.TF3();
        tf.ttype = 'tu2'
        self.assertTrue(tr_formats.is_tu2(tf))

    def test_is_tmoas(self):
        tf = tr_formats.TF3();
        tf.ttype = 'tmo'
        self.assertTrue(tr_formats.is_tmoas(tf))
