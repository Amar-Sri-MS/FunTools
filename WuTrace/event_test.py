#!/usr/bin/env python3
#
# event_test.py: unit tests for event.py.
#
# Copyright (c) 2019 Fungible Inc. All Rights Reserved.
#

import unittest

import event

class TestParseFabricAddress(unittest.TestCase):
    def testSimple(self):
        faddr = event.FabricAddress.from_string('FA0:16:00[CCV3.2.0]')
        self.assertEqual(0, faddr.gid)
        self.assertEqual(16, faddr.lid)
        self.assertEqual(0, faddr.queue)
        self.assertEqual(16384, faddr.raw_value)
        self.assertEqual('VP0.2.0', str(faddr))

    def testEquality(self):
        self.assertEqual(event.FabricAddress.from_string('FA3:16:0[CCV3.2.0]'),
                         event.FabricAddress.from_string('FA3:16:0[CCV3.2.0]'))

        self.assertNotEqual(event.FabricAddress.from_string('FA3:16:0[CCV3.2.0]'),
                            event.FabricAddress.from_string('FA0:24:0[CCV0.4.0]'))

        self.assertNotEqual(event.FabricAddress.from_string('FA3:16:0[CCV3.2.0]'),
                            event.FabricAddress.from_string('FA3:17:0[CCV3.2.0]'))

    def testHash(self):
        self.assertEqual(
            hash(event.FabricAddress.from_string('FA3:16:0[CCV3.2.0]')),
            hash(event.FabricAddress.from_string('FA3:16:0[CCV3.2.0]')))

        self.assertNotEqual(
            hash(event.FabricAddress.from_string('FA3:16:0[CCV3.2.0]')),
            hash(event.FabricAddress.from_string('FA0:24:0[CCV0.4.0]')))

    def testOrdinal(self):
        self.assertEqual('VP1.0.0', str(event.FabricAddress.from_ordinal(24)))
        self.assertEqual('VP7.4.1', str(event.FabricAddress.from_ordinal(185)))
        self.assertEqual('VP8.0.1', str(event.FabricAddress.from_ordinal(193)))

    def testAddressFromString(self):

        self.assertEqual('VP0.0.0',
                         str(event.FabricAddress.from_string('FA0:8:0[CCV0.0.0]')))

        self.assertEqual('VP4.2.0',
                         str(event.FabricAddress.from_string('FA4:16:1[CCV3.6.1]')))

        self.assertEqual('VP2.2.2',
                         str(event.FabricAddress.from_string('FA2:18:0[CCV3.6.1]')))

        self.assertEqual('VP6.5.3',
                         str(event.FabricAddress.from_string('FA6:31:0[CCV0.0.1]')))

        self.assertEqual('VP8.3.3',
                         str(event.FabricAddress.from_string('FA8:23:1[CCV2.2.2]')))

    def testFaddrFromString(self):
        faddr = event.FabricAddress.from_string('FA8:23:1[CCV2.2.2]')

        self.assertEqual('FA8:23:1[VP]', faddr.as_faddr_str())

    def testFaddrFromInt(self):
        faddr = event.FabricAddress.from_faddr(0x1c800)
        self.assertEqual('VP3.2.2', str(faddr))

        faddr = event.FabricAddress.from_faddr(0x45c08)
        self.assertEqual('VP8.3.3', str(faddr))

        faddr = event.FabricAddress.from_faddr(0x2000)
        self.assertEqual('VP0.0.0', str(faddr))


    def testVP(self):
        faddr = event.FabricAddress.from_string('FA2:18:0[CCV3.6.1]')
        self.assertTrue(faddr.is_cluster())
        self.assertFalse(faddr.is_accelerator())
        self.assertFalse(faddr.is_hu())
        self.assertFalse(faddr.is_nu())
        self.assertEqual('VP2.2.2', str(faddr))

    def testHU(self):
        self.assertEqual('HU0',
                         str(event.FabricAddress.from_string('FA16:0:99[HU]')))
        self.assertEqual('HU2',
                         str(event.FabricAddress.from_string('FA18:0:99[HU]')))

    def testNU(self):
        self.assertEqual('NU0',
                         str(event.FabricAddress.from_string('FA9:0:999[HU]')))
        self.assertEqual('NU2',
                         str(event.FabricAddress.from_string('FA11:0:88[HU]')))

    def testHighPriority(self):
        fa = event.FabricAddress.from_string('FA2:18:0[CCV3.6.1]')
        self.assertFalse(fa.is_high_priority_queue())

        fa = event.FabricAddress.from_string('FA2:18:1[CCV3.6.1]')
        self.assertTrue(fa.is_high_priority_queue())

        fa = event.FabricAddress.from_string('FA3:3:0[DMA]')
        self.assertFalse(fa.is_high_priority_queue())

    def testDMA(self):
        faddr = event.FabricAddress.from_string('FA6:3:0[DMA]')
        self.assertTrue(faddr.is_accelerator())
        self.assertTrue(faddr.is_cluster())
        self.assertEqual('DMA6', str(faddr))

    def testRegex(self):
        faddr = event.FabricAddress.from_string('FA3:4:0[RGX]')
        self.assertTrue(faddr.is_accelerator())
        self.assertTrue(faddr.is_cluster())
        self.assertEqual('RGX3', str(faddr))


if __name__ == '__main__':
  unittest.main()
