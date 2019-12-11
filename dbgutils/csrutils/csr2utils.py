#!/usr/bin/env python2.7

#
# Implementation of the csr access methods for CSR2
#
# Copyright (c) 2019 Fungible Inc.  All rights reserved.
#

import logging
import os
import re
import sys

from csrutils import dbgprobe
from csrutils import csr_get_field
from csrutils import hex_word_dump
from csrutils import str_to_int


# Use the WORKSPACE environment variable to import the csr2 module.
# TODO (jimmy): we need a better way to import our favourite modules
WS = os.environ.get('WORKSPACE', None)
if WS is None:
    print 'Need WORKSPACE environment variable'
    sys.exit(1)
sys.path.append(os.path.join(WS, 'FunHW/csr2api/v2'))

import csr2

#
# Use a global logger to match the convention set by related modules.
#
logger = logging.getLogger("csr2utils")
logger.setLevel(logging.INFO)


class Register(object):
    """
    Represents a register.

    The fields in this register have been "flattened" from the CSR2
    hierarchy, so array and struct groupings are no longer visible.
    """
    def __init__(self, name, addr, width_bytes):
        self.name = name
        self.addr = addr
        self.width_bytes = width_bytes
        self.fields = []

    def add_field(self, field):
        self.fields.append(field)

    def __str__(self):
        s = list()
        s.append('%s @ %s' % (self.name, hex(self.addr)))
        s.append('------ Fields ------')
        for f in self.fields:
            s.append(str(f))
        return '\n'.join(s)

    def print_data(self, word_array):
        logger.info("Raw data: {0}".format(hex_word_dump(word_array)))
        logger.info('------ Field values ------')

        for fld in self.fields:
            fld_offset = fld.lsb
            fld_width = fld.msb - fld.lsb + 1
            val_array = csr_get_field(fld_offset, fld_width, word_array)
            val = hex_word_dump(val_array)
            logger.info('    {0}: {1}'.format(fld.name, val))


class Field(object):
    """ Bitfield in a register """
    def __init__(self, name, lsb, msb):
        self.name = name
        self.lsb = lsb
        self.msb = msb

    def __str__(self):
        return '%s [%d:%d]' % (self.name, self.msb, self.lsb)


class RegisterFinder(object):
    """
    Finds a register given a path.
    """
    def __init__(self, bundle):
        """
        Initializes from a csr2 json bundle.
        """
        self.bundle = bundle

    def find_reg(self, path):
        """
        Attempts to find the register at the specified path.

        Returns a tuple of (register, error_string). If the error string
        is not None then the register is invalid.
        """
        root_name = self.bundle.roots[0]

        root_type = self.bundle.defs_dict[root_name]
        root_cursor = root_type.cursor()

        tokenizer = PathSplitter()
        parts = tokenizer.split(path)

        # strip the root name
        parts = parts[1:]

        reg_cursor, error = self._descend(root_cursor, parts)
        if error:
            return None, error

        reg = Register(reg_cursor.prettyname(),
                       reg_cursor.offset('addr'),
                       reg_cursor.size('addr'))

        self._add_reg_fields(reg, reg_cursor)
        return reg, None

    def _descend(self, cursor, remaining_parts):
        if not remaining_parts:
            # Found the target register if all parts have been matched and
            # we landed on a register.
            if isinstance(cursor.typ, csr2.Reg):
                return cursor, None
            return None, 'Failed to find register: possibly incomplete path?'

        try:
            # The cursor.child(key) method descends the graph until it finds a
            # named layer. At that point if the key matches a node it returns
            # a cursor to that child, otherwise it throws a KeyError.
            child_cursor = cursor.child(remaining_parts[0])
        except KeyError as e:
            # TODO (jimmy): improve error by reporting the matching parts
            return None, 'Failed to match %s' % remaining_parts[0]

        return self._descend(child_cursor, remaining_parts[1:])

    def _add_reg_fields(self, reg, reg_cursor):

        # Get the size in bytes first, then multiply to turn into a bit width
        reg_width = reg_cursor.size('addr') * 8

        # Walk all children of the register, but only look at Logic and Union
        # types which represent the lowest level (i.e. bitfields).
        for child in reg_cursor.child().walk(explode=True):
            if isinstance(child.typ, (csr2.Logic, csr2.Union)):
                fname = child.crumb.name
                msb = reg_width - child.offset('bit') - 1
                lsb = reg_width - (child.offset('bit') + child.size('bit'))
                field = Field(fname, lsb, msb)
                reg.add_field(field)


class PathSplitter(object):
    """
    Splits a path to a register.

    A path may include indices, so foo.bar[1].baz[0] will turn into
    a list containing strings and ints [ 'foo', 'bar', 1, 'baz', 0 ].

    The split list is useful when walking the csr graph because each element
    is a key into the next level of the graph when walking from the root.

    TODO (jimmy): consider using Phil's idea of a class with "dunder" methods
                  to implement . and [] instead.
    """
    def split(self, path):
        """ Splits a path """
        parts = path.split('.')

        result = []
        for p in parts:
            result.extend(self._split_indices(p))

        return result

    def _split_indices(self, part):
        """
        Splits reg[0][3][4] into ['reg', 0, 3, 4].

        The indices are always at the end of the path fragment.
        """
        result = []
        start = 0

        bra = part.find('[', start)
        ket = part.find(']', start)
        if bra < ket:
            result.append(part[:bra])
        else:
            result.append(part)

        while bra < ket:
            dim_index_str = part[bra+1:ket]
            dim_index = int(dim_index_str)
            result.append(dim_index)

            bra = part.find('[', ket+1)
            ket = part.find(']', ket+1)

        return result


class RegisterNames(object):
    """
    A collection of register names.

    To use, build(), then call find_matching() to locate matching
    register names.
    """
    def __init__(self, bundle):
        self.bundle = bundle
        self.names = set()

    def build(self):
        """
        Build the collection of names.

        Subsequent calls will not rebuild the collection.
        """
        if self.names:
            return

        root_name = self.bundle.roots[0]

        root_type = self.bundle.defs_dict[root_name]
        root_cursor = root_type.cursor()

        # Avoid exploding the graph: we typically do not need to expand
        # arrays to search for a partial path.
        for cursor in root_cursor.walk():
            if isinstance(cursor.typ, csr2.Reg):
                reg_name = ''
                for precursor in cursor.trail():
                    crumb = precursor.crumb
                    reg_name = self._extend_regname(reg_name, crumb)

                self.names.add(reg_name)

    def _extend_regname(self, reg_name, crumb):
        """
        For a named crumb, add a dotted fragment. For an indexed crumb,
        add the bounds [left..right].
        """
        if isinstance(crumb, csr2.NamedCrumb):
            fragment = crumb.prettyname
            if fragment:
                if reg_name:
                    reg_name += '.'
                reg_name += fragment
        elif isinstance(crumb, csr2.IndexedCrumb):
            for left, right in crumb.arr.bounds:
                reg_name += '[%d..%d]' % (left, right)
        return reg_name

    def find_matching(self, regex):
        """ Find all names that match the regex """
        result = []
        for reg in self.names:
            if re.match(regex, reg):
                result.append(reg)
        return result


class CSRAccessor(object):

    def __init__(self, dbg_client, reg_finder):
        """
        Creates an accessor to peek and poke registers with the specified
        debug client.
        """
        self.dbgprobe = dbg_client
        self.reg_finder = reg_finder

    def peek(self, path):
        reg, error = self.reg_finder.find_reg(path)
        if error:
            print error
            return

        addr = reg.addr
        csr_width_words = reg.width_bytes >> 3
        logger.info('Peeking register at {0} '
                    'with length {1}'.format(hex(addr), csr_width_words))

        (status, data) = self.dbgprobe.csr_peek(chip_inst=0,
                                                csr_addr=addr,
                                                csr_width_words=csr_width_words)

        if status:
            word_array = data
            if word_array is None or not word_array:
                print("Error in csr peek")
                return None
            reg.print_data(word_array)
            return word_array
        else:
            error_msg = data
            print("Error: CSR peek failed: {0}".format(error_msg))
            return None

    def poke(self, path, values):
        reg, error = self.reg_finder.find_reg(path)
        if error:
            print error
            return

        addr = reg.addr
        csr_width_words = reg.width_bytes >> 3

        if len(values) != csr_width_words:
            print ('Error: cannot write %d words for a register '
                   'which has %d words' % (len(values), csr_width_words))
            return
        logger.info('Poking register at {0} '
                    'with values {1}'.format(hex(addr), values))

        (status, data) = self.dbgprobe.csr_poke(chip_inst=0,
                                                csr_addr=addr,
                                                word_array=values)
        if not status:
            print("Error: CSR poke failed! {0}".format(data))
            return


def load_bundle():
    bundle_path = os.path.join(WS, 'FunHW/csr2api/v2/s1_bundle.json')
    return csr2.load_bundle(bundle_path)


bundle = load_bundle()
csr_names = RegisterNames(bundle)


def csr2_peek(args):
    """
    Handles the csr peek comand.

    For CSR2, we allow specification of a path. If a wildcard * is present,
    we display a list of matching registers.

    Paths correspond to the hierarchy as described in fundamental docs,
    separated by dots, e.g. root.pc0.soc_clk_ring.cfg.pc_cfg_scratchpad.
    """
    csr_path = args.csr[0]

    if '*' in csr_path:
        print_matching_regs(csr_path)
    else:
        finder = RegisterFinder(bundle)
        accessor = CSRAccessor(dbgprobe(), finder)
        accessor.peek(csr_path)


def print_matching_regs(csr_path):
    regex = csr_path.replace('*', '.*')
    csr_names.build()
    result = csr_names.find_matching(regex)
    result.sort()
    print '\n'.join(result)


def csr2_poke(args):
    """
    Handles the csr poke comand.

    For CSR2, we allow specification of a path. If a wildcard * is present,
    we display a list of matching registers.

    Paths correspond to the hierarchy as described in fundamental docs,
    separated by dots, e.g. root.pc0.soc_clk_ring.cfg.pc_cfg_scratchpad.
    """
    csr_path = args.csr[0]

    if '*' in csr_path:
        print_matching_regs(csr_path)
    else:
        values = [str_to_int(v) for v in args.vals]
        finder = RegisterFinder(bundle)
        accessor = CSRAccessor(dbgprobe(), finder)
        accessor.poke(csr_path, values)

