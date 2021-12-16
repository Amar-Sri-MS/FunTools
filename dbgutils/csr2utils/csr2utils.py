#!/usr/bin/env python2.7

#
# Implementation of the csr access methods for CSR2
#
# Copyright (c) 2019 Fungible Inc.  All rights reserved.
#

import logging
import os
import re
import subprocess
import sys
import json

from csrutils.csrutils import dbgprobe
from csrutils.csrutils import csr_get_field
from csrutils.csrutils import csr_set_field
from csrutils.csrutils import hex_word_dump
from csrutils.csrutils import str_to_int


# Use the WORKSPACE environment variable to import the csr2 module.
# TODO (jimmy): we need a better way to import our favourite modules
WS = os.environ.get('WORKSPACE', None)
if WS is None:
    print 'Need WORKSPACE environment variable to be set: exiting'
    sys.exit(1)
sys.path.append(os.path.join(WS, 'FunHW/csr2api/v2'))

import csr2py2

#
# Use a global logger to match the convention set by related modules.
#
logger = logging.getLogger("csr2utils")
logger.setLevel(logging.ERROR)

csr2_chip_types = ['s1', 'f1d1']

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

    def as_json(self):
        js = {
            # keep the output similar to that for CSR1 register dump
            # it's not the same as a lot of information doesn't exist
            # in this structure, but keep matching fields to make them
            # as compatible as possible
            'an_addr':hex(self.addr),
            'fld_list': [
                { 'fld_width':f.width(),
                  'fld_name':f.name(),
                  'fld_offset':f.offset() } for f in self.fields
            ]
        }
        return json.dumps(js, indent=4)


class Field(object):
    """ Bitfield in a register """
    def __init__(self, name, lsb, msb):
        self.__name = name
        self.__lsb = lsb
        self.__msb = msb

    def __str__(self):
        return '%s [%d:%d]' % (self.__name, self.__msb, self.__lsb)

    def width(self):
        return self.__msb - self.__lsb + 1

    def offset(self):
        return self.__lsb

    def msb(self):
        return self.__msb

    def name(self):
        return self.__name

class RegisterValue(object):
    """
    Represents a value in a register.
    """
    def __init__(self, register, word_array):
        self.reg = register
        self.word_array = word_array

    def set_field_val(self, fld_name, fld_word_array):
        """
        Sets the field with the specified value (as an array of 64-bit words).

        Linear search through the fields, which is yuck, but probably not
        performance critical.

        Returns True on success, else False.
        """
        for fld in self.reg.fields:
            if fld.name == fld_name:
                fld_offset = fld.lsb
                fld_width = fld.msb - fld.lsb + 1
                csr_set_field(fld_offset, fld_width,
                              self.word_array, fld_word_array)
                return True

        # Failed to find a field with the specified name
        return False

    def __str__(self):
        s = list()
        s.append("  Raw data: {0}".format(hex_word_dump(self.word_array)))
        s.append('  Fields:')

        for fld, val in self._list_field_vals():
            s.append('    {0}: {1}'.format(fld, val))
        return '\n'.join(s)

    def _list_field_vals(self):
        fields_and_vals = []
        for fld in self.reg.fields:
            fld_offset = fld.offset()
            fld_width = fld.msb() - fld.offset() + 1
            val_array = csr_get_field(fld_offset, fld_width, self.word_array)
            val = hex_word_dump(val_array)
            fields_and_vals.append((fld.name(), val))

        return fields_and_vals


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
            if isinstance(cursor.typ, csr2py2.Arrayed):
                logger.debug("bounds: {0}".format(cursor.typ.bounds[0]))
                logger.debug("count_stride: {0}".format(cursor.typ.count_stride))
                logger.debug("count: {0}".format(cursor.typ.count))
                logger.debug("strides: {0}".format(cursor.typ.strides))
                logger.debug("offset: {0}".format(cursor.offset('addr')))
                logger.debug("width: {0}".format(cursor.size('addr')))
            # Found the target register if all parts have been matched and
            # we landed on a register.
            if isinstance(cursor.typ, csr2py2.Reg):
                return cursor, None
            return None, 'Failed to find the register(possibly incomplete path?)'

        try:
            # The cursor.child(key) method descends the graph until it finds a
            # named layer. At that point if the key matches a node it returns
            # a cursor to that child, otherwise it throws a KeyError.
            child_cursor = cursor.child(remaining_parts[0]).skip()
        except KeyError as e:
            # TODO (jimmy): improve error by reporting the matching parts
            #               or drawing squiggly lines under the unmatched part
            return None, 'Failed to match %s' % remaining_parts[0]

        return self._descend(child_cursor, remaining_parts[1:])

    def _add_reg_fields(self, reg, reg_cursor):

        # Get the size in bytes first, then multiply to turn into a bit width
        reg_width = reg_cursor.size('addr') * 8

        # Walk all children of the register, but only look at Logic and Union
        # types which represent the lowest level (i.e. bitfields).
        for child in reg_cursor.child().walk(explode=True):
            if isinstance(child.typ, (csr2py2.Logic, csr2py2.Union)):
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
            if isinstance(cursor.typ, csr2py2.Reg):
                reg_name = ''
                for precursor in cursor.trail():
                    crumb = precursor.crumb
                    reg_name = self._extend_regname(reg_name, crumb)

                prefix_pattern = re.compile(r'^chip_(.*)::root.(.*)')
                name_groups = re.search(prefix_pattern, reg_name)
                if name_groups.lastindex == 2:
                    self.names.add(name_groups.group(2))
                else:
                    logger.error("Unexpected reg name:{0}".reg_name)
                    self.names.add(reg_name)

    def _extend_regname(self, reg_name, crumb):
        """
        For a named crumb, add a dotted fragment. For an indexed crumb,
        add the bounds [left..right].
        """
        if isinstance(crumb, csr2py2.NamedCrumb):
            fragment = crumb.prettyname
            if fragment:
                if reg_name:
                    reg_name += '.'
                reg_name += fragment
        elif isinstance(crumb, csr2py2.IndexedCrumb):
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
    """
    Accesses CSRs through peek and poke functions.
    """

    def __init__(self, dbg_client, reg_finder):
        """
        Creates an accessor to peek and poke registers with the specified
        debug client.
        """
        self.dbgprobe = dbg_client
        self.reg_finder = reg_finder

    def peek(self, path):
        """
        Peek at the register with the specified path.

        Returns a RegisterValue object on success, else returns None and
        logs an error.
        """
        logger.info('csr: {}'.format(path))
        reg, error = self.reg_finder.find_reg(path)
        if error:
            logger.error('csr_path: {0} Error: {1}'.format(path, error))
            return None

        addr = reg.addr
        csr_width_words = reg.width_bytes >> 3
        logger.info('Peeking register Addr: {0}'
                ' Width: {1}'.format(hex(addr), csr_width_words))

        (status, data) = self.dbgprobe.csr_peek(chip_inst=0,
                                                csr_addr=addr,
                                                csr_width_words=csr_width_words)

        if status:
            word_array = data
            if not word_array:
                logger.error('Peeked data is empty')
                return None

            regval = RegisterValue(reg, word_array)
            return regval
        else:
            error_msg = data
            logger.error('Peek failed: {0}'.format(error_msg))
            return None

    def raw_peek(self, addr, length):
        """
        Peek at the register with the specified address and length
        (in 64-bit words).

        This is a fallback for when all else fails.

        Returns the data as an array of 64-bit words on success, else None.
        """
        (status, data) = self.dbgprobe.csr_peek(chip_inst=0,
                                                csr_addr=addr,
                                                csr_width_words=length)
        if status:
            return data
        else:
            logger.error('Raw peek failed: {0}'.format(data))
            return None

    def poke(self, path, values):
        """
        Poke the values into the register with the specified path.
        Values should be an array of 64-bit words.

        Returns True on successful completion, False on errors.
        """
        reg, error = self.reg_finder.find_reg(path)
        if error:
            logger.error(error)
            return False

        addr = reg.addr
        csr_width_words = reg.width_bytes >> 3

        if len(values) != csr_width_words:
            logger.error('Cannot write %d words for a register '
                         'which has %d words' % (len(values), csr_width_words))
            return False
        logger.debug('Poking register at {0} '
                    'with values {1}'.format(hex(addr), values))

        (status, data) = self.dbgprobe.csr_poke(chip_inst=0,
                                                csr_addr=addr,
                                                word_array=values)
        if not status:
            logger.error('Poke failed: {0}'.format(data))
            return False

        return True

    def raw_poke(self, addr, values):
        """
        Poke the values into the register with the specified address. The
        values should be 64-bit words and len(values) should be equal to
        the register length.

        The fallback version of poke, when the path lookup fails.

        Returns True on successful completion, False on errors.
        """
        (status, data) = self.dbgprobe.csr_poke(chip_inst=0,
                                                csr_addr=addr,
                                                word_array=values)
        if not status:
            logger.error('Raw poke failed: {0}'.format(data))
            return False
        return True


class RawValuesFormatter(object):
    """
    Formats raw values from a register as best as it can.
    """
    def __init__(self):
        pass

    def format(self, data):
        """
        data is an array of 64-bit values from the register.
        (ordered left to right).

        Returns a string.
        """
        dump = hex_word_dump(data)

        # oh quantum mechanics, how I miss thee
        bra = dump.find('[')
        ket = dump.rfind(']')

        if bra == -1 or ket == -1:
            return dump

        empty_spaces = ket - bra

        msb = len(data) * 64 - 1
        lsb = 0

        # account for the space taken up by the msb
        empty_spaces = empty_spaces - len(str(msb))
        header = str(msb) + ' ' * empty_spaces + str(lsb) + '\n'
        return header + dump


#
# Global csr2 json containing register spec information
#
bundle = None
csr_names = None

def load_csr_spec(chip_type):
    """
    load csr2 metadata spec.
    """

    if chip_type not in csr2_chip_types:
        logger.error('Invalid chip type: {}'.format(chip_type))
        sys.exit(1)

    global bundle
    global csr_names

    csr2_dir = os.path.join(WS, 'FunHW', 'csr2api', 'v2')
    bin_path = os.path.join(csr2_dir, 'csr2bundle.py')
    bundle_path = os.path.join(csr2_dir, 'bundle.json')

    logger.info('Creating CSR2 bundle at %s' % bundle_path)

    json_dir = os.path.join(WS, 'FunSDK', 'FunSDK', 'chip', chip_type, 'csr')
    bundle_cmd = [bin_path, 'chip_{}::root'.format(chip_type),
                  '-I', json_dir,
                  '-o', bundle_path,
                  '-n', chip_type]
    try:
        subprocess.check_output(bundle_cmd)
    except subprocess.CalledProcessError as e:
        logger.error('Failed to create bundle: %s' % e.output)
        return False

    logger.info('Loading CSR2 bundle from %s' % bundle_path)
    bundle = csr2py2.load_bundle(bundle_path)
    csr_names = RegisterNames(bundle)
    return True

def csr2_peek(csr_path):
    """
    Handles the csr peek comand.

    Paths correspond to the hierarchy as described in fundamental docs,
    separated by dots, e.g. pc0.soc_clk_ring.cfg.pc_cfg_scratchpad.
    """

    if not csr_path:
        logger.error('Invalid(Null) csr path argument!')
        return

    finder = RegisterFinder(bundle)
    accessor = CSRAccessor(dbgprobe(), finder)
    regval = accessor.peek(csr_path)
    if regval is not None:
        print str(regval)

def csr2_peek_args(args):
    """
    Handles the csr peek comand with args dict.

    For CSR2, we allow specification of a path. If a wildcard * is present,
    we display a list of matching registers.

    Paths correspond to the hierarchy as described in fundamental docs,
    separated by dots, e.g. pc0.soc_clk_ring.cfg.pc_cfg_scratchpad.
    """
    csr_path = args.csr[0]

    if '*' in csr_path:
        regex = csr_path.replace('*', '.*')
        csr_names.build()
        matched_csrs = csr_names.find_matching(regex)
        matched_csrs.sort()

        print('\nTotal matched csrs:{}\n'.format(len(matched_csrs)))
        for csr in matched_csrs:
            print('\n{}'.format(csr))
            csr2_peek(csr)
    else:
        csr2_peek(csr_path)

def print_matching_regs(csr_path):
    regex = csr_path.replace('*', '.*')
    csr_names.build()
    result = csr_names.find_matching(regex)
    result.sort()
    print '\n'.join(result)

def csr2_raw_peek_args(args):
    """
    Handles the raw peek command.

    This version of peek takes an address and length (64-bit words).
    """
    accessor = CSRAccessor(dbgprobe(), None)
    data = accessor.raw_peek(str_to_int(args.addr),
                             str_to_int(args.length))

    if data is not None:
        formatter = RawValuesFormatter()
        print formatter.format(data)

def csr2_poke(csr_path, values):
    """
    Handles the csr poke comand.

    Paths correspond to the hierarchy as described in fundamental docs,
    separated by dots, e.g. root.pc0.soc_clk_ring.cfg.pc_cfg_scratchpad.
    """

    if not csr_path:
        logger.error('Invalid(Null) csr path argument!')
        return

    if not values or len(values) == 0:
        logger.error('Invalid(Null or empty list) csr value argument argument!')
        return

    finder = RegisterFinder(bundle)
    accessor = CSRAccessor(dbgprobe(), finder)
    accessor.poke(csr_path, values)

def csr2_poke_args(args):
    """
    Handles the csr poke comand with args dict input.

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

    csr2_poke(csr_path, values)

def csr2_raw_poke_args(args):
    """
    Handles the raw poke command.
    """
    accessor = CSRAccessor(dbgprobe(), None)
    addr = str_to_int(args.addr)
    values = [str_to_int(v) for v in args.vals]
    accessor.raw_poke(addr, values)

def csr2_find_by_name(csr_path):
    if '*' in csr_path:
        regex = csr_path.replace('*', '.*')
    else:
        regex = '.*' + csr_path + '.*'

    csr_names.build()
    matched_csrs = csr_names.find_matching(regex)
    matched_csrs.sort()
    print '\n'.join(matched_csrs)

def csr2_find(args):
    """
    Handles the csr find comand.

    For CSR2, we allow specification of a path. If a wildcard * is present,
    we display a list of matching registers.
    If wildcard is not there, any register with matcing substring are
    displayed.

    Paths correspond to the hierarchy as described in fundamental docs,
    separated by dots, e.g. root.pc0.soc_clk_ring.cfg.pc_cfg_scratchpad.
    """
    csr_path = args.substring[0] if args.substring else None

    if csr_path:
        csr2_find_by_name(csr_path)
    else:
        print('Invalid argument! args:{0}'.format(args))
        return

def csr2_list(args):
    csr_name = args.csr[0]

    finder = RegisterFinder(bundle)

    reg, error = finder.find_reg(csr_name)
    if error:
        logger.error('csr_path: {0} Error: {1}'.format(path, error))
        return None

    print(reg.as_json())
