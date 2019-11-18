#!/usr/bin/env python2.7

#
# Implementation of the csr access methods for CSR2
#
# Copyright (c) 2019 Fungible Inc.  All rights reserved.
#

import re

import csr2api

from csrutils import dbgprobe
from csrutils import hex_word_dump
from csrutils import str_to_int


class CSR2DevTable(object):

    def __init__(self):
        self.devtab = None
        self.addr_by_path = dict()
        self.reg_by_path = dict()

    def lazy_populate(self):
        if self.devtab is None:
            self.devtab = csr2api.get_device_table()
            if self.devtab is not None:
                self.populate_maps()

    def populate_maps(self):
       for dev_name in self.devtab:
            dev = self.devtab[dev_name]
            for instance in dev['instances']:
                inst_path = instance.get_dpath()
                inst_addr = instance.get_address()
                for reg in dev['regs']:
                    # Ignore the dimensions here, we'll fix em up later
                    reg_addr = int(reg.address, 16)
                    reg_path = inst_path + '.' + reg.short_name
                    self.addr_by_path[reg_path] = inst_addr + reg_addr
                    self.reg_by_path[reg_path] = reg

    def get_reg(self, csr_path):
        reg = self.reg_by_path.get(csr_path, None)
        return reg

    def get_address(self, dimensionless_path, dims):
        addr = self.addr_by_path.get(dimensionless_path, None)
        reg = self.reg_by_path.get(dimensionless_path)

        if addr is None:
            return None

        # do the dimension offsets, if any
        addr += self.calc_dim_offset(reg, dims)

        return addr

    def get_width(self, csr_path):
        reg = self.reg_by_path.get(csr_path, None)
        return reg.padded_size

    def potential_paths(self, csr_path):
        csr_regex = re.compile(csr_path)
        paths = []
        for path in self.reg_by_path:
            if csr_regex.match(path):
                potential_path = self.fixup_dimensions(path)
                paths += [potential_path]
        return paths

    def fixup_dimensions(self, path):
        reg = self.reg_by_path[path]
        for dim in reg.rpt_dims:
            # TODO (jimmy): this should look at bounds
            path += '[%d..%d]' % (0, dim.count - 1)
        return path

    @staticmethod
    def calc_dim_offset(reg, idx_list=None):
        offset = 0
        if not idx_list:
            return offset

        # if this is an array, add the index offsets
        for i, dim in enumerate(reg.rpt_dims):
            offset += dim.stride * idx_list[i]
        return offset


csr_dev_table = CSR2DevTable()


def csr2_peek(args):
    """
    Handles the csr peek comand.

    For CSR2, we only allow specification of a unambiguous path.

    Paths correspond to the hierarchy as described in fundamental docs,
    separated by dots, e.g. root.pc0.soc_clk_ring.cfg.pc_cfg_scratchpad.
    """
    csr_dev_table.lazy_populate()

    csr_path = args.csr[0]

    # TODO (jimmy): need to handle dimensions anywhere
    dimensionless_path, dims = extract_trailing_dimensions(csr_path)

    reg = csr_dev_table.get_reg(dimensionless_path)
    if reg is None:
        print 'Cannot find register for %s' % csr_path
        print_potential_paths(dimensionless_path)
        return

    addr = csr_dev_table.get_address(dimensionless_path, dims)
    if addr is None:
        print 'Cannot find address for %s' % csr_path
        return

    width = csr_dev_table.get_width(dimensionless_path)
    csr_width_bytes = width >> 3
    csr_width_words = csr_width_bytes >> 3
    print '%s %s %d' % (csr_path, hex(addr), csr_width_words)
    (status, data) = dbgprobe().csr_peek(chip_inst=0,
                                         csr_addr=addr,
                                         csr_width_words=csr_width_words)

    if status is True:
        word_array = data
        if word_array is None or not word_array:
            print("Error in csr peek")
            return None
        print_data(word_array)
    else:
        error_msg = data
        print("Error: {0}".format(error_msg))


def extract_trailing_dimensions(csr_path):
    dims = []

    bra = csr_path.rfind('[')
    ket = csr_path.rfind(']')

    while bra < ket and bra != -1 and ket != -1:
        dim = int(csr_path[bra+1:ket])
        dims.append(dim)
        csr_path = csr_path[:bra]

        bra = csr_path.rfind('[')
        ket = csr_path.rfind(']')

    return csr_path, dims


def print_potential_paths(csr_path):
    print 'Potential paths are:'
    potential_paths = csr_dev_table.potential_paths(csr_path)
    potential_paths.sort()
    print '\n'.join(potential_paths)


def print_data(word_array):
    print("csr raw: {0}".format(hex_word_dump(word_array)))


def csr2_poke(args):
    """
    Handles the csr poke comand.

    For CSR2, we only allow specification of an unambiguous path or address.
    """
    csr_dev_table.lazy_populate()

    csr_path = args.csr[0]
    dimensionless_path, dims = extract_trailing_dimensions(csr_path)

    reg = csr_dev_table.get_reg(dimensionless_path)
    if reg is None:
        print 'Error: cannot find register for %s' % csr_path
        print_potential_paths(dimensionless_path)
        return

    addr = csr_dev_table.get_address(dimensionless_path, dims)
    if addr is None:
        print 'Error: cannot find address for %s' % csr_path
        return

    width = csr_dev_table.get_width(dimensionless_path)
    csr_width_bytes = width >> 3
    csr_width_words = csr_width_bytes >> 3

    values = [str_to_int(v) for v in args.vals]
    print '%s %s %d' % (csr_path, hex(addr), csr_width_words)
    if len(values) != csr_width_words:
        print ('Error: cannot write %d words for a register '
               'which has %d words' % (len(values), csr_width_words))
        return

    (status, data) = dbgprobe().csr_poke(chip_inst=0,
                                         csr_addr=addr,
                                         word_array=values)
    if not status:
        print("Error: CSR poke failed! {0}".format(data))
        return




