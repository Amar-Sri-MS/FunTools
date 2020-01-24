#
# Unit tests for the csr2 peek and poke utilities
#
# Copyright (c) 2019 Fungible Inc.  All rights reserved.
#

import os
import unittest

import csr2utils


class MockDebugProbe(object):

    def __init__(self):
        self.peek_vals_queue = []
        self.peek_args_queue = []
        self.poke_args_queue = []

    def csr_peek(self, chip_inst, csr_addr, csr_width_words):
        vals = self.peek_vals_queue.pop(0)
        self.peek_args_queue.append((chip_inst, csr_addr, csr_width_words))

        if vals:
            return True, vals
        return False, []

    def csr_poke(self, chip_inst, csr_addr, word_array):
        self.poke_args_queue.append((chip_inst, csr_addr, word_array))
        return True, None

    def pop_peek_args(self):
        # cruel and slow on an array, but this is just a mock
        return self.peek_args_queue.pop(0)

    def pop_poke_args(self):
        return self.poke_args_queue.pop(0)

    def queue_peek_vals(self, return_vals):
        """
        Sets up the return value for a peek.

        Can be called multiple times in advance before a series of peeks..

        return_vals is a list of 64-bit return values. If the list is empty
        we'll return an error result (False, []).
        """
        self.peek_vals_queue.append(return_vals)


class CSR2AccessorTest(unittest.TestCase):
    """
    Checks the functionality of the csr2 accessor methods.
    """

    bundle = None

    @classmethod
    def setUpClass(cls):
        """
        We only want to run this expensive setup method once for the entire
        test class: the bundle should remain the same for each test
        (immutable in practice).
        """
        global bundle
        csr2utils.init_bundle_lazily()
        bundle = csr2utils.bundle

    def setUp(self):
        self.dbg_client = MockDebugProbe()
        self.finder = csr2utils.RegisterFinder(bundle)

        self.accessor = csr2utils.CSRAccessor(self.dbg_client, self.finder)

    def test_peek_decodes_correct_address(self):
        self.dbg_client.queue_peek_vals([0xdeadbeefcafebabe])
        self.accessor.peek('chip_s1::root.mio2.scratchpad')
        chip, addr, width = self.dbg_client.pop_peek_args()

        self.assertEqual(0x1e008408, addr)
        self.assertEqual(1, width)

    def test_peek_returns_correct_value(self):
        self.dbg_client.queue_peek_vals([0xdeadbeefcafebabe])
        result = self.accessor.peek('chip_s1::root.mio2.scratchpad')

        self.assertEqual([0xdeadbeefcafebabe], result)

    def test_peek_multi_word_access(self):
        self.dbg_client.queue_peek_vals([0xaabbccdd, 0x11223344])
        result = self.accessor.peek('chip_s1::root.pc1.fep_ring.fep.ldn_unknown_dest_log')

        chip, addr, width = self.dbg_client.pop_peek_args()
        self.assertEqual(0x80002b8, addr)
        self.assertEqual(2, width)
        self.assertEqual([0xaabbccdd, 0x11223344], result)

    def test_peek_nonexistent_register(self):
        self.dbg_client.queue_peek_vals([0x3456])
        result = self.accessor.peek('chip_s1::root.this_does_not_exist')

        self.assertIsNone(result)

    def test_peek_arrayed_register(self):
        """
        Ensure we can peek at a specific register in an array.
        """
        self.dbg_client.queue_peek_vals([0xcafebabe])
        result = self.accessor.peek('chip_s1::root.ocm0.ocm.ocm_sna_rd_cntr[1]')

        chip, addr, width = self.dbg_client.pop_peek_args()
        self.assertEqual(0x190000d0, addr)
        self.assertEqual(1, width)
        self.assertEqual([0xcafebabe], result)

    def test_peek_repeated_instance(self):
        """
        Ensure we can peek at a register within an array of module instances.
        """
        self.dbg_client.queue_peek_vals([0xf00baa])
        result = self.accessor.peek('chip_s1::root.mud0.soc_clk_ring.qsys[1].mud_qsys_sch_cfg_0')

        chip, addr, width = self.dbg_client.pop_peek_args()
        self.assertEqual(0x1b0410d0, addr)
        self.assertEqual([0xf00baa], result)

    def test_poke_arguments(self):
        self.accessor.poke('chip_s1::root.mio2.scratchpad', [0xdeadbeef])

        chip, addr, vals = self.dbg_client.pop_poke_args()
        self.assertEqual(0x1e008408, addr)
        self.assertEqual([0xdeadbeef], vals)


class RegisterValueTest(unittest.TestCase):
    """
    Checks functionality of the register value object.
    """
    def setUp(self):
        self.reg = csr2utils.Register('grand_poohbah', 0xa800, 8)
        self.reg.add_field(csr2utils.Field('a', 0, 5))
        self.reg.add_field(csr2utils.Field('b', 6, 20))
        self.reg.add_field(csr2utils.Field('c', 21, 21))
        self.reg.add_field(csr2utils.Field('d', 22, 31))

    def test_register_value_print(self):
        """
        Admittedly a lame test with no assertions.
        TODO (jimmy): expose field values for testing instead of hiding them
                      in a print?
        """
        val = csr2utils.RegisterValue(self.reg, [0xcafebabe])
        print val

    def test_set_one_register_field(self):
        val = csr2utils.RegisterValue(self.reg, [0xcafebabe])
        val.set_field_val('a', [0x2a])

        self.assertEqual([0xcafebaaa], val.word_array)

    def test_set_multiple_register_fields(self):
        val = csr2utils.RegisterValue(self.reg, [0x1ebabe])
        val.set_field_val('a', [0x2a])
        val.set_field_val('b', [0x7fff])
        val.set_field_val('c', [0x0])

        self.assertEqual([0x1fffea], val.word_array)

    def test_set_field_return_values(self):
        val = csr2utils.RegisterValue(self.reg, [0xcafebabe])
        self.assertFalse(val.set_field_val('e', [0xfffffff]))
        self.assertEqual([0xcafebabe], val.word_array)

        self.assertTrue(val.set_field_val('d', [0x0]))