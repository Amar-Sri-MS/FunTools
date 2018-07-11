#!/usr/bin/env python
# coding=utf-8
"""A simple example demonstrating how to use Argparse to support subcommands.


This example shows an easy way for a single command to have many subcommands, each of which takes different arguments
and provides separate contextual help.
"""
import cmd2
from cmd2 import with_argparser
import argparse
import string, json, collections
import os
import argparse as ap
import argcomplete
from i2c_peek_poke import i2c_csr_peek, i2c_csr_poke
from array import array
import binascii

def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

@singleton
class csr_metadata:
    def __init__(self):
        print "Loading csr metadata!"
        loc = get_file_abs_path("csr_metadata.json")
        print "Metadata file: {}".format(loc)
        self.metadata = json.load(open(loc))

    def set_metadata(self, metadata):
        self.metadata = metadata

    def csr_equal(self, x, rn_class, rn_inst, an_path, an):
        if rn_class:
            if x["ring_name"] != rn_class:
                return False
        if rn_inst:
            if x["ring_inst"] != rn_inst:
                return False
        if an:
            if x["an"] != an:
                return False
        if an_path:
            if x["an_path"] != an_path:
                return False

        return True

    def get_csr_def(self, csr_name, rn_class=None, rn_inst=None, an_path=None, an=None):
        csr_defs_lst = self.metadata.get(csr_name, [])
        if not csr_defs_lst:
            return None
        else:
            csr_defs_lst = [x for x in csr_defs_lst        \
                            if self.csr_equal(x, rn_class, \
                            rn_inst, an_path, an)]

        return csr_defs_lst

    def get_csr_list(self):
        return list(self.metadata.keys())

    def csr_inst_verify(self, csr_name):
        csr_list = self.get_csr_def(csr_name=csr_name)


def get_csr_list():
    return csr_metadata().get_csr_list()

def get_file_abs_path(loc):
    if not os.path.isabs(loc):
        loc = os.path.join(os.getcwd(), loc)
    assert os.path.exists(loc), "{}: directory does not exist!".format(loc)
    return loc


class MyFormatter(argparse.HelpFormatter):
    # use defined argument order to display usage
    def _format_usage(self, usage, actions, groups, prefix):
        if prefix is None:
            prefix = 'usage: '

        # if usage is specified, use that
        if usage is not None:
            usage = usage % dict(prog=self._prog)

        # if no optionals or positionals are available, usage is just prog
        elif usage is None and not actions:
            usage = '%(prog)s' % dict(prog=self._prog)
        elif usage is None:
            prog = '%(prog)s' % dict(prog=self._prog)
            # build full usage string
            action_usage = self._format_actions_usage(actions, groups) # NEW
            usage = ' '.join([s for s in [prog, action_usage] if s])
            # omit the long line wrapping code
        # prefix with 'usage:'
        return '%s%s\n\n' % (prefix, usage)


def csr_get_args(args):
    input_args = dict()
    input_args["csr_name"] = args.csr[0]
    input_args["csr_inst"] = int(args.csr_inst[0], 10) if args.csr_inst else None
    input_args["csr_entry"] = int(args.csr_entry[0], 10) if args.csr_entry else None
    input_args["ring_name"] = args.ring[0] if args.ring else None
    input_args["ring_inst"] = None
    if args.ring and len(args.ring) > 1:
        input_args["ring_inst"] = int(args.ring[1], 10)
    input_args["anode_name"] = args.anode[0] if args.anode else None
    input_args["anode_inst"] = None
    if args.anode and len(args.anode) > 1:
        input_args["anode_inst"] = int(args.anode[1], 10)
    input_args["anode_path"] = args.an_path[0] if args.an_path else None
    input_args["field_list"] = args.fields

    return input_args


def csr_get_addr(csr_data, anode_inst=None, csr_inst=None, csr_entry=None):
    anode_addr = csr_data.get("an_addr", None)
    if anode_addr is None:
        print "Invalid csr metadata! anode_addr is missing in metadata!"
        sys.exit(1)
    anode_addr = int(anode_addr, 16)
    anode_inst_cnt = csr_data.get("an_inst_cnt", None)
    if anode_inst_cnt is None:
        print "Invalid csr metadata! an_inst_cnt is missing in metadata!"
        sys.exit(1)

    if anode_inst_cnt > 1:
        if anode_inst is None:
            print "Expetced anode_inst argument!"
            return None

        if anode_inst < 0 or anode_inst >= anode_inst_cnt:
            print "Invalid anode_inst: {}!".format(anode_inst)
            return None

        anode_skip_addr = csr_data.get("an_skip_addr", None)
        if anode_skip_addr is None:
            print "Invalid csr metadata! an_skip_addr is missing in metadata!"
            sys.exit(1)

        anode_addr = anode_skip_addr * anode_inst;

    csr_addr = csr_data.get("csr_addr", None)
    if csr_addr is None:
        print "Invalid csr metadata! csr_addr is missing in metadata!"
        sys.exit(1)

    csr_addr = int(csr_addr, 16)
    csr_width = csr_data.get("csr_width", None)
    if csr_width is None:
        print "Invalid csr metadata! csr_width is missing in metadata!"
        sys.exit(1)

    csr_width_bytes = csr_width >> 0x3

    csr_n_entries = csr_data.get("csr_n_entries", None)
    if csr_n_entries is None:
        print "Invalid csr metadata! csr_n_entries is missing in metadata!"
        sys.exit(1)

    if csr_n_entries > 1:
        if csr_entry is None:
            print "Expetced csr_entry argument!"
            return None

        if csr_entry < 0 or csr_entry >= csr_n_entries:
            print "Invalid csr_entry: {}!".format(csr_entry)
            return None
        csr_addr += csr_width_bytes * csr_entry;

    csr_inst_count = csr_data.get("csr_count", None)
    if csr_inst_count is None:
        print "Invalid csr metadata! csr_inst_count is missing in metadata!"
        sys.exit(1)

    if csr_inst_count > 1:
        if csr_inst is None:
            print "Expetced csr_inst argument!"
            return None

        if csr_inst < 0 or csr_inst >= csr_inst_count:
            print "Invalid csr_inst: {}!".format(csr_inst)
            return None
        csr_addr += csr_width_bytes * csr_n_entries * csr_inst

    return (anode_addr + csr_addr)


def csr_get_width_bytes(csr_data):
    csr_width = csr_data.get("csr_width", None)
    if csr_width is None:
        print "Invalid csr metadata! csr_width is missing in metadata!"
        sys.exit(1)

    csr_width_bytes = csr_width >> 0x3

    return csr_width_bytes


def byte_array_to_8byte_words_be(byte_array):
    words = list()
    byte_attay_size = len(byte_array)
    word_array_size = byte_attay_size / 8
    for i in range(word_array_size):
        val = int(binascii.hexlify(byte_array[i:i+8]), 16)
        words.extend([val])
        i += 8

    remaining_bytes = len(byte_array)%8
    if remaining_bytes != 0:
        last_word = byte_array[-remaining_bytes:]
        last_word.extend(array('B', [0x00]*(8 - remaining_bytes)))
        val = int(binascii.hexlify(byte_array[i, i+8]), 16)
        words.extend(val)

    #print [hex(x) for x in words]
    return words


def csr_get_field(fld_pos, fld_size, in_reg):
    BPW = 64
    reg_padded_size = len(in_reg) * BPW
    if not (reg_padded_size >= fld_size + fld_pos):
        print ("Invalid arguments! fld_pos: {0} + fld_size: {1} exceeds"
               " csr word array length: {2}").format(fld_pos, fld_size, len(in_reg) * BPW)
        sys.exit(1)

    if not fld_size > 0:
        print ("Invalid argument! fld_size: {0} should non-zero positive number").format(fld_size)
        sys.exit(1)

    out_idx = 0
    rem_size = fld_size

    # compute the last word of the output buffer because big endian
    out_idx = (fld_size - 1) / BPW
    #print "first output word: {0}".format(out_idx)

    fld_size_words = (fld_size + (BPW - 1)) / BPW
    out_fld = [0x0] * fld_size_words

    # count up bits from fld_pos
    while rem_size > 0:
        # clear the output word
        if not (out_idx >= 0):
            sys.exit(1)
        out_fld[out_idx] = 0

        # find the input word for the lowest significant bit
        if not ((reg_padded_size - fld_pos - fld_size + rem_size) > 0):
            sys.exit(1)
        in_idx = (reg_padded_size - fld_pos - fld_size + rem_size - 1) / BPW

        # calculate the base bit position in this word
        in_pos = fld_pos % BPW

        # trim the size for this input word
        in_size = rem_size
        read_upper = False
        if (in_size + in_pos > BPW):
            in_size = BPW - in_pos
            read_upper = True

        # calculate a mask
        if (in_size == BPW):
            mask = 0xFFFFFFFFFFFFFFFF
        else:
            mask = (0x1 << in_size) - 1

        #print "in_idx: {0}".format(in_idx)
        #print "mask: {0}".format(hex(mask))
        #print "fld_size: {0} -> {1}".format(fld_size, in_size)

        # copy in the first part of the word
        out_fld[out_idx] |= (in_reg[in_idx] >> in_pos) & mask

        # determine if we need to read part of the next word
        if (read_upper):
            # need to read the remaining bits in this input word
            if (BPW < rem_size):
                in_size_hi = BPW - in_size
            else:
                in_size_hi = rem_size - in_size
            if not (in_size_hi < BPW): # can't be BPW, would be read above
                sys.exit(1)
            # construct the mask
            mask = (0x1 << in_size_hi) - 1

            # or in the value
            if not ((in_idx - 1) >= 0):
                sys.exit(1)
            out_fld[out_idx] |= (in_reg[in_idx-1] & mask) << in_size
        else:
            in_size_hi = 0

        #print ("rem_size: {0}, in_size: {1}, in_size_hi: {2}").format(rem_size,
        #        in_size, in_size_hi, (rem_size -  in_size + in_size_hi))

        # next output word
        out_idx -= 1
        rem_size -= in_size + in_size_hi
    return out_fld

def csr_set_field(fld_pos, fld_size, out_reg, in_fld):
    BPW = 64
    reg_padded_size = len(out_reg) * BPW

    if not (reg_padded_size >= fld_size + fld_pos):
        print ("Invalid arguments! fld_pos: {0} + fld_size: {1} exceeds"
               "csr word array length: {2}").format(fld_pos, fld_size, len(out_reg) * BPW)
        sys.exit(1)

    if not fld_size > 0:
        print ("Invalid argument! fld_size: {0} should non-zero positive number").format(fld_size)
        sys.exit(1)

    rem_size = fld_size
    in_idx = (fld_size - 1) / BPW
    while (rem_size > 0):
        # find the LSB word on the output register
        if not ((reg_padded_size - fld_pos - fld_size + rem_size) > 0):
            sys.exit(1)
        out_idx = (reg_padded_size - fld_pos - fld_size + rem_size - 1) / BPW

        # calculate the base bit position in this word
        out_pos = fld_pos % BPW

        # trim the size for this input word
        out_size = rem_size
        write_upper = False
        if (out_size + out_pos > BPW):
            out_size = BPW - out_pos
            write_upper = True

        # calculate a mask
        if (out_size == BPW):
            mask = 0xFFFFFFFFFFFFFFFF
        else:
            mask = (0x1 << out_size) - 1

        #print "out_idx: {0}, in_idx: {1}".format(out_idx, in_idx)
        #print "mask: {0}".format(mask)
        #print "fld_size: {0} -> {1}".format(fld_size, out_size)

        # copy in the first part of the word, masking out the rest
        out_reg[out_idx] &= ~(mask << out_pos)
        out_reg[out_idx] |= (in_fld[in_idx] & mask) << out_pos

        # determine if we need to read part of the next word
        if (write_upper):
            # need to read the remaining bits in this input word
            if (BPW < rem_size):
                out_size_hi = BPW - out_size
            else:
                out_size_hi = rem_size - out_size
            if not (out_size_hi < BPW): # can't be BPW, would be read above
                sys.exit(1)

            # construct the mask
            mask = (0x1 << out_size_hi) - 1

            # or in the value
            if not (out_idx > 0):
                sys.exit(1)
            out_reg[out_idx-1] &= ~mask
            out_reg[out_idx-1] |= (in_fld[in_idx] >> out_size) & mask
        else:
            out_size_hi = 0

        print ("rem_size: {0}, in_size: {1}, in_size_hi: {2} = {3}").format(
               rem_size, out_size, out_size_hi, rem_size -  out_size + out_size_hi)

        # next output word
        in_idx -= 1
        rem_size -= out_size + out_size_hi

    return out_reg

"""
def csr_get_field(fld_offset, fld_width, byte_array):
    if (fld_offset + fld_width) > (len(byte_array) * 8):
        print ("Invalid arguments! fld_offset: {0} + fld_width: {1} exceeds"
               " byte array length: {2}").format(fld_offset, fld_width, len(byte_array) * 8)
        return None

    byte_array = array('B', reversed(byte_array))
    print "fld_offset: {0} fld_width: {1} byte_array: {2}".format(fld_offset, fld_width,  [hex(x) for x in byte_array])
    field_byte_array = array('B')
    rshift_bits = fld_offset % 8
    start_byte = fld_offset >> 0x3
    last_byte = ((fld_offset + fld_width - 1) >> 0x3)
    print "start_byte: {0} last_byte:{1} rshift_bits:{2}".format(start_byte, last_byte, rshift_bits)
    for i in range(start_byte, last_byte):
        if rshift_bits:
            byte = (byte_array[i] >> rshift_bits) | ((byte_array[i+1] << (8-rshift_bits)) & 0xFF)
        else:
            byte = byte_array[i]
        print hex(byte)
        field_byte_array.extend([byte])
    print "start_byte: {0} last_byte:{1} rshift_bits:{2}".format(start_byte, last_byte, rshift_bits)
    byte_mask = 0xFF >> (8 - (fld_width & 0x7))
    print "byte_mask"
    print byte_mask
    byte = (byte_array[last_byte] >> rshift_bits) & byte_mask
    print "byte"
    print byte
    field_byte_array.extend([byte])
    print "field: offset: {0} width: {1} byte_array: {2}".format(
                   fld_offset, fld_width, [hex(x) for x in field_byte_array])
    return field_byte_array

def csr_set_field(fld_offset, fld_width, field_byte_array, byte_array):
    if (fld_offset + fld_width) > (len(byte_array) * 8):
        print ("Invalid arguments! fld_offset: {0} + fld_width: {1} exceeds"
               " byte array length: {2}").format(fld_offset, fld_width, len(byte_array) * 8)
        return None

    width_in_bytes = (fld_width + 7) >> 0x3
    if (width_in_bytes != len(field_byte_array)):
        print ("Invalid arguments! fld_width: {0} not matcing"
               " field byte array length: {1}").format(fld_width, len(field_byte_array) * 8)
        return None

	left_bits = fld_width
	bytemask = 0xFF
	bit_shift = fld_offset & 0x7
	byte_idx = fld_offset >> 0x3
	fld_byte_array_idx = 0
	if bit_shift != 0:
		if fld_width > 7:
			bytemask = 0xFF
		else:
			bytemask = ((1 << fld_width) - 1)
		byte_array[byte_idx] &= ~(bytemask << bit_shift)
		byte_array[byte_idx] |= (field_byte_array[fld_byte_array_idx] << bit_shift) & bytemask
		left_bits -= (8-bit_shift)
		byte_idx += 1

	while (left_bits >= 8):
		byte_array[byte_idx] = ((field_byte_array[fld_byte_array_idx] >> (8-bit_shift)) |
			(field_byte_array[fld_byte_array_idx + 1] << bit_shift))
		fld_byte_array_idx += 1;
		byte_idx += 1
		left_bits -= 8

	if (left_bits > 0):
		byte_array[byte_idx] &= (0xFF << bits_left)
		byte_array[byte_idx] |= field_byte_array[fld_byte_array_idx] >> (8-bit_shift)

    print ("field: offset: {0} width: {1} field_byte_array: {2} byte_array: {3}").format(
                   fld_offset, fld_width, field_byte_array, byte_array)

    return byte_array
"""

def csr_get_valid_field_list(csr_data):
    field_list_obj = csr_data.get("fld_lst", None)
    field_list = dict()
    for f in field_list_obj:
        fld_name = f.get('fld_name', None)
        #if fld_name is not '__rsvd' or fld_name is not None:
        if fld_name is not None:
            field_list[fld_name] = f
    return field_list

def csr_show(csr_data, word_array, field_list=None):
    if len(word_array) != (csr_get_width_bytes(csr_data) >> 3):
        print "csr_width: {0} word_array length: {1}".format(csr_get_width_bytes(csr_data),
                                                             len(word_array))
        print "Invalid arguments! word array length should match csr width!"
        return

    if field_list is not None:
        field_list = list(set(field_list))

    print "csr raw: {0}".format(hex_word_dump(word_array))
    fields_objs = csr_data.get("fld_lst", None)
    for f in fields_objs:
        fld_name = f.get('fld_name', None)
        if field_list is not None and fld_name not in field_list:
            continue
        fld_width = f.get('fld_width', None)
        fld_offset = f.get('fld_offset', None)
        field_word_array = csr_get_field(fld_offset, fld_width, word_array)
        if not field_word_array:
            print "Error! Failed to extract field:{0}".format(fld_name)
            return
        print "\t{0}: {1}".format(fld_name, hex_word_dump(field_word_array))
        if field_list:
            field_list.remove(fld_name)
    if field_list:
        field_list_valid = csr_get_valid_field_list(csr_data).keys()
        print "Skipped invalid fields: {0}\nvalid fields: {1}".format(field_list, field_list_valid)

def hex_word_dump(word_array):
    hex_word_array = '['
    for w in word_array:
        hex_word_array += '0x{:016x}'.format(w)
    hex_word_array =  hex_word_array
    hex_word_array += ']'
    return hex_word_array


def csr_peek(args):
    input_args = csr_get_args(args)
    csr_name = input_args.get("csr_name", None)
    csr_inst = input_args.get("csr_inst", None)
    csr_entry = input_args.get("csr_entry", None)
    ring_name = input_args.get("ring_name", None)
    ring_inst = input_args.get("ring_inst", None)
    anode_name = input_args.get("anode_name", None)
    anode_inst = input_args.get("anode_inst", None)
    anode_path = input_args.get("anode_path", None)
    field_list = input_args.get("field_list", None)

    csr_data = csr_get_metadata(csr_name, csr_inst=csr_inst, csr_entry=csr_entry,
            ring_name=ring_name, ring_inst=ring_inst, anode_name=anode_name,
            anode_inst=anode_inst, anode_path=anode_path)

    if csr_data is None:
        print "Error! Failed to get metadata for csr:{} !!!".format(csr_name)
        return

    csr_addr = csr_get_addr(csr_data, anode_inst=anode_inst,
                            csr_inst=csr_inst, csr_entry=csr_entry)
    if csr_addr is None:
        print "Error get csr address!!!"
        return
    #print "csr address: {0}".format(hex(csr_addr))

    csr_width_bytes = csr_get_width_bytes(csr_data)
    word_array = i2c_csr_peek(csr_addr, csr_width_bytes)
    if word_array is None:
        print "Error in csr i2c peek!!!"
        return None
    csr_show(csr_data, word_array, field_list)

def csr_poke(args):
    input_args = csr_get_args(args)
    csr_name = input_args.get("csr_name", None)
    csr_inst = input_args.get("csr_inst", None)
    csr_entry = input_args.get("csr_entry", None)
    ring_name = input_args.get("ring_name", None)
    ring_inst = input_args.get("ring_inst", None)
    anode_name = input_args.get("anode_name", None)
    anode_inst = input_args.get("anode_inst", None)
    anode_path = input_args.get("anode_path", None)
    field_list = input_args.get("field_list", None)

    csr_data = csr_get_metadata(csr_name, csr_inst=csr_inst, csr_entry=csr_entry,
            ring_name=ring_name, ring_inst=ring_inst, anode_name=anode_name,
            anode_inst=anode_inst, anode_path=anode_path)

    if csr_data is None:
        print "Error! Failed to get metadata for csr:{} !!!".format(csr_name)
        return

    csr_addr = csr_get_addr(csr_data, anode_inst=anode_inst,
                            csr_inst=csr_inst, csr_entry=csr_entry)
    if csr_addr is None:
        print "Error get csr address!!!"
        return
    #print "csr address: {0}".format(hex(csr_addr))

    csr_width_bytes = csr_get_width_bytes(csr_data)
    csr_width_words = csr_width_bytes >> 3
    word_array = i2c_csr_peek(csr_addr, csr_width_words)
    if word_array is None or not word_array:
        print "Error in csr i2c peek!!!"
        return None

    print "Peeked value: {0}".format(hex_word_dump(word_array))

    valid_field_list = csr_get_valid_field_list(csr_data)
    print field_list
    for field in field_list:
        field_name = field[0]
        if field_name not in valid_field_list:
            print "Invalid field name: {0}. Valid fields are: {1}".format(field_name, valid_field_list.keys())
            return None
        str_word_array = field[1:]
        field_word_array = list()
        for word in str_word_array:
            value = str_to_int(word)
            if value is None:
                print "Invalid field input value: \"{0}\". Must be positive integer or hexadecimal".format(word)
                return None
            field_word_array.append(value)

        field_obj = valid_field_list.get(field_name, None)
        field_width = field_obj.get("fld_width", None)
        field_width_words = (field_width + 63) / 64
        field_offset = field_obj.get("fld_offset", None)
        if not field_width_words:
            sys.exit(1)
        if len(field_word_array) > field_width_words:
            print "Number of field value words should match the length for field: {0}. Expected {1} words but given {2}.".format(field_name, field_width_words, len(field_word_array))
            return None
        csr_set_field(field_offset, field_width, word_array, field_word_array)
        print field_name
        print field_word_array
        print hex_word_dump(word_array)

    status = i2c_csr_poke(csr_addr, csr_width_words, word_array)
    if not status:
        print "Error! i2c csr poke failed!"
    else:
        print "csr poke success!"

def str_to_int(s):
    if s.isdigit():
        try:
            return int(s, 10)
        except ValueError:
            return None
    try:
        return int(s, 0)
    except ValueError:
        return None

    return None



def required_length_append(nmin):
    class CustomAction(argparse.Action):
        def __init__(self,
                     option_strings,
                     dest,
                     nargs=None,
                     const=None,
                     default=None,
                     type=None,
                     choices=None,
                     required=False,
                     help=None,
                     metavar=None):
            argparse.Action.__init__(self,
                                     option_strings=option_strings,
                                     dest=dest,
                                     nargs=nargs,
                                     const=const,
                                     default=default,
                                     type=type,
                                     choices=choices,
                                     required=required,
                                     help=help,
                                     metavar=metavar,
                                     )
            print 'Initializing CustomAction'
            for name,value in sorted(locals().items()):
                if name == 'self' or value is None:
                    continue
                print '  %s = %r' % (name, value)
            print
            return

        def __call__(self, parser, namespace, values,
                     option_string=None):
            print 'Processing CustomAction for "%s"' % self.dest
            print '  parser = %s' % id(parser)
            print '  values = %r' % values
            print '  option_string = %r' % option_string

            if not nmin<=len(values):
                msg='"{f}" option requires atleast {nmin} arguments'.format(
                        f=option_string,nmin=nmin)
                raise argparse.ArgumentTypeError(msg)
            # Do some arbitrary processing of the input values
            x = getattr(namespace, self.dest)
            if x is None:
                x = list()
            print x
            if isinstance(values, list):
                x.append([ v for v in values ])
            else:
                x.append(values)
            # Save the results in the namespace using the destination
            # variable given to our constructor.
            setattr(namespace, self.dest, x)
    return CustomAction

sparser = argparse.ArgumentParser(prog='csr', formatter_class=MyFormatter)
subparsers = sparser.add_subparsers(help='sub-command help')

parser_peek = subparsers.add_parser('peek', help="help peek", formatter_class=MyFormatter)
#parser_peek.add_argument('csr', choices=get_csr_list(), help="csr name")
parser_peek.add_argument('csr', nargs=1, help="csr name")
parser_peek.set_defaults(func=csr_peek)
parser_peek.add_argument('-i', nargs=1, metavar=('csr_inst'), dest='csr_inst', type=str, help="csr instance")
parser_peek.add_argument('-e', nargs=1, metavar=('csr_entry'), dest='csr_entry', type=str, help="csr entry")
parser_peek.add_argument('-f', nargs='+',  metavar=('csr_field'), dest='fields', type=str, help="field_name")
parser_peek.add_argument('-a', nargs=2, metavar=('anode_name', 'anode_inst'), dest='anode', help="anode details")
parser_peek.add_argument('-r', nargs=2, metavar=('ring_name', 'ring_inst'), dest='ring', type=str, help="ring details")
parser_peek.add_argument('-p', nargs=1, metavar=('anode_path'), dest='an_path', type=str, help="anode path")

parser_poke = subparsers.add_parser('poke', help="help poke", formatter_class=MyFormatter)
parser_poke.set_defaults(func=csr_poke)
parser_poke.add_argument('csr', nargs=1, type=str, help="csr name")
parser_poke.add_argument('-i', nargs=1, metavar=('csr_inst'), dest='csr_inst', type=str, help="csr instance")
parser_poke.add_argument('-e', nargs=1, metavar=('csr_entry'), dest='csr_entry', type=str, help="csr entry")
parser_poke.add_argument('-a', nargs=2, metavar=('anode_name', 'anode_inst'), dest='anode', help="anode details")
parser_poke.add_argument('-r', nargs=2, metavar=('ring_name', 'ring_inst'), dest='ring', type=str, help="ring details")
parser_poke.add_argument('-p', nargs=1, metavar=('anode_path'), dest='an_path', type=str, help="anode path")
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-f', nargs='+',  metavar=('csr_field'), dest='fields', type=str, action=required_length_append(2), help="field_name")
group.add_argument('-v', nargs='+',  metavar=('raw_value'), dest='raw_value', type=str, help="csr value in big-endian 64-bit words")

parser_find = subparsers.add_parser('find', help="help find")
parser_find.add_argument('csr', choices=get_csr_list(), help="csr name")
parser_poke.add_argument('-a', nargs=1, metavar=('anode_name'), dest='anode', help="anode name")
parser_poke.add_argument('-r', nargs=1, metavar=('ring_name'), dest='ring', type=str, help="ring name")
argcomplete.autocomplete(sparser)



def csr_get_metadata(csr_name, csr_inst=None, csr_entry=None, ring_name=None,
                ring_inst=None, anode_name=None, anode_inst=None, anode_path=None):
    if not csr_name:
        print "csr name is empty! Provide valid csr name!"
        return

    csr_list = csr_metadata().get_csr_def(csr_name)
    if csr_list is None:
        print "csr: {} doesnot exist in database!.".format(csr_name)
        return

    rings = dict()
    print "Preparing ring list"
    for csr in csr_list:
        rname = csr.get("ring_name", None)
        if rings.get(rname, None) is None:
            rings[rname] = list()
        if csr.get("ring_inst", None) not in rings[rname]:
            rings[rname].append(csr.get("ring_inst", None))
        #print "ring name:{} inst:{}".format(rname, csr.get("ring_inst", None))

    if len(rings) == 0:
        print "Inconsistant csr metadata parsing!"
        return

    print "rings: {}".format(rings)
    if len(rings) > 0:
        print "csr_name: {} ring_name: {}".format(csr_name, ring_name)
        if len(rings) > 1 and ring_name is None:
            print "csr objs:\n{}\n".format(dump_json_obj(csr_list))
            print "csr: {} exists in multiple rings. Give appropriate ring option! valid rings: {}".format(csr_name, rings)
            return
        if ring_name not in rings:
            print "csr objs:\n{}\n".format(dump_json_obj(csr_list))
            print "Invalid ring:{} for csr: {}. Give appropriate ring option! valid rings: {}".format(ring_name, csr_name, rings)
            return

        csr_list = csr_metadata().get_csr_def(csr_name = csr_name, rn_class=ring_name)
        ring_inst_list = rings.get(ring_name)
        print "ring: {} instace list: {}".format(ring_name, ring_inst_list)
        if len(ring_inst_list) > 0:
            if len(ring_inst_list) > 1 and ring_inst is None:
                print "csr objs:\n{}\n".format(dump_json_obj(csr_list))
                print "csr: {} exists in multiple instances of ring: {}. Give appropriate ring option! valid rings instances: {}".format(csr_name, ring_name, ring_inst_list)
                return
            print "ring name: {}  inst: {}".format(ring_name, ring_inst)
            if ring_inst not in ring_inst_list:
                print "csr objs:\n{}\n".format(dump_json_obj(csr_list))
                print "Invalid ring instance for csr: {} ring: {}. Give appropriate ring details! valid rings instances: {}".format(csr_name, ring_name, ring_inst_list)
                return

    anodes = dict()
    csr_list = csr_metadata().get_csr_def(csr_name = csr_name, rn_class=ring_name, rn_inst=ring_inst)
    print "Preparing anode list"
    for csr in csr_list:
        if ring_name == csr.get("ring_name", None):
            an_name = csr.get("an", None)
            #print an_name
            anodes[an_name] = csr.get("an_inst_cnt", None)
    print "anodes: {}".format(anodes)
    if anodes and len(anodes) > 1:
        if anode_name is None:
            print "csr objs:\n{}\n".format(dump_json_obj(csr_list))
            print "csr: {} exists in multiple anodes. Give appropriate anode option! valid anodes: {}".format(csr_name, anodes)
            return
        if anode_name not in anodes:
            print "csr objs:\n{}\n".format(dump_json_obj(csr_list))
            print "Invalid anode:{} for csr: {}. Give appropriate anode option! valid anodes: {}".format(anode_name, csr_name, anodes)
            return

    csr_list = csr_metadata().get_csr_def(csr_name = csr_name, rn_class=ring_name, rn_inst=ring_inst, an=anode_name)

    anode_inst_count = 0;
    if anode_name is not None:
        anode_inst_count = anodes.get(anode_name, 0)
        print "anode: {} inst count: {}".format(anode_name, anode_inst_count)
        if not anode_inst_count > 0:
            print "Inconsistant csr metadata parsing!"
            return
    if anode_inst_count > 0:
        if anode_inst_count > 1 and anode_inst is None:
            print "csr objs:\n{}\n".format(dump_json_obj(csr_list))
            print "csr: {} exists in multiple instances of anode: {}. Give appropriate anode option! valid anode instances: {}".format(csr_name, anode_name, range(0,anode_inst_count))
            return

        if (anode_inst is not None) and (anode_inst < 0 or anode_inst >= anode_inst_count):
            print "csr objs:\n{}\n".format(dump_json_obj(csr_list))
            print ("Invalid anode instance for csr: {} anode: {}."
                "\nGive appropriate anode details!"
                " Valid anode instances: {}").format(csr_name,
                anode_name, range(0,anode_inst_count))
            return

    if len(csr_list) != 1:
        print "csr objs:\n{}\n".format(json.dumps(csr_list, indent=4))
        print "more than one csr instance! Inconsistant csr metadata parsing!"
        return

    csr = csr_list[0]
    csr_count = csr.get("csr_count", None)
    if csr_count > 1:
        if csr_inst is None:
            print "csr objs:\n{}\n".format(json.dumps(csr, indent=4))
            print "There are {} instances of csr:{}. Provide csr instance number!".format(csr_count, csr_name)
            return
        if csr_inst < 0 or csr_inst >= csr_count:
            print "csr objs:\n{}\n".format(json.dumps(csr, indent=4))
            print "Invalid instances of csr:{}. Provide csr instance number in the range [0 - {}]!".format(csr_name, csr_count - 1)
            return
    if csr_count == 1 and csr_inst is not None:
        print "**** Ignoring option csr instance number: {}!!! ****".format(csr_inst)


    csr_n_entries = csr.get("csr_n_entries", None)
    if csr_n_entries > 1:
        if csr_entry is None:
            print "csr objs:\n{}\n".format(json.dumps(csr_list, indent=4))
            print "There are {} entries in table csr:{}. Provide csr entry index number!".format(csr_n_entries, csr_name)
            return
        print "csr entry index: {} csr_n_entries: {}".format(csr_entry, csr_n_entries)
        if csr_entry < 0 or csr_entry >= csr_n_entries:
            print "csr objs:\n{}\n".format(json.dumps(csr, indent=4))
            print "Invalid entry index of csr:{}. Provide csr entry index in the range of [0 - {}]!".format(csr_name, csr_n_entries - 1)
            return
    if csr_n_entries == 1 and csr_entry is not None:
        print "**** Ignoring option csr entry index: {}!!! ****".format(csr_entry)

    #print "Found CSR: \n{}\n".format(json.dumps(csr, indent=4))
    return csr

def dump_json_obj(json_obj):
    return json.dumps(json_obj, indent=4)

class DEBUG(cmd2.Cmd):
    intro = 'Welcome to the fun shell.   Type help or ? to list commands.\n'
    #prompt = '(csr)'
    @with_argparser(sparser)
    def do_csr(self, args):
        'CSR peek/poke utility tool'
        print args
        """
        csr_get_metadata(csr_name=csr_name, csr_inst=csr_inst, csr_entry=csr_entry,
                         ring_name=ring_name, ring_inst=ring_inst,
                         anode_name=anode_name, anode_inst=anode_inst, anode_path=anode_path)
        """
        args.func(args)

    def complete_csr(self, text, line, start_index, end_index):
        if text:
            metadata = csr_metadata().get_csr_list()
            return [x for x in metadata if x.startswith(text)]
        else:
            tags = line.split()
            if tags[-1] == 'peek' or tags[-1] == 'poke' or tags[-1] == 'list':
                return csr_metadata().get_csr_list()

    def do_quit(self, args):
        """Quits the program."""
        print "Quitting."
        raise SystemExit


if __name__ == '__main__':
    c = DEBUG()
    c.prompt = '> '
    c.cmdloop()


