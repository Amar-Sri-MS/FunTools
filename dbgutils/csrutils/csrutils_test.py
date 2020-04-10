#
# Unit tests for the csr utilities
#
# Copyright (c) 2020 Fungible Inc.  All rights reserved.
#

import unittest

import csrutils


class RecordingProbe(object):
    """
    Pretends to be a DBG_Client.

    Records all transactions so tests can see if the code did the right
    thing.
    """
    def __init__(self):
        self.peeks = []
        self.pokes = []

    def clear(self):
        del self.peeks[:]
        del self.pokes[:]

    def csr_fast_poke(self, csr_addr, word_array, chip_inst=None):
        self.pokes.append((csr_addr, word_array))
        return True, None

    def csr_peek(self, csr_addr, csr_width_words, chip_inst=None):
        self.peeks.append((csr_addr, csr_width_words))

        # The only peek is for the status register: always return True with
        # successful completion for now.
        data = [(1 << csrutils.DDR.STATUS_BIT_SHIFT)]
        return True, data


class DDRTest(unittest.TestCase):
    """
    Ensures DDR writes work.
    """
    def setUp(self):
        self.probe = RecordingProbe()
        self.ddr = csrutils.DDR(self.probe)

    def test_write_sequence(self):
        """
        Ensures a write triggers the appropriate CSR pokes and peeks
        """
        test_data = [0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7]
        ret = self.ddr.write(csrutils.constants.IMAGE_START_PHYS_ADDR, test_data)
        self.assertTrue(ret)

        self.assertEqual(10, len(self.probe.pokes))

        for i in range(8):
            expected_addr = (csrutils.DDR.MUD0_SNA +
                             csrutils.DDR.DATA_REG_OFFSET +
                             i * 8)
            poke = self.probe.pokes.pop(0)
            self.assertEqual(expected_addr, poke[0], 'csr addr {}'.format(i))
            self.assertEqual([test_data[i]], poke[1], 'csr data {}'.format(i))

        expected_addr = (csrutils.DDR.MUD0_SNA +
                         csrutils.DDR.CMD_REG_OFFSET)
        poke = self.probe.pokes.pop(0)
        self.assertEqual(expected_addr, poke[0])

        # the magic address should be // 128 (see comments in source for reasoning)
        self.assertEqual([csrutils.constants.IMAGE_START_PHYS_ADDR // 128],
                         poke[1])

        self.assertEqual(1, len(self.probe.peeks))
        peek = self.probe.peeks.pop(0)
        expected_addr = csrutils.DDR.MUD0_SNA + csrutils.DDR.STATUS_REG_OFFSET
        self.assertEqual(expected_addr, peek[0])

    def test_write_sharding(self):
        """
        Ensures we shard data to the correct MUD.
        """
        test_data = [0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7]

        # shard 0
        phys_addr = csrutils.constants.IMAGE_START_PHYS_ADDR
        self.ddr.write(phys_addr, test_data)
        self._check_shard(csrutils.DDR.MUD0_SNA)
        self.probe.clear()

        # shard 1
        phys_addr += self.ddr.line_width
        self.ddr.write(phys_addr, test_data)
        self._check_shard(csrutils.DDR.MUD1_SNA)
        self.probe.clear()

        # shard 0 again
        phys_addr += self.ddr.line_width
        self.ddr.write(phys_addr, test_data)
        self._check_shard(csrutils.DDR.MUD0_SNA)
        self.probe.clear()

    def _check_shard(self, mud_addr):
        addr_poke_index = 8
        poke = self.probe.pokes[addr_poke_index]
        expected_addr = mud_addr + csrutils.DDR.CMD_REG_OFFSET
        self.assertEqual(expected_addr, poke[0])

