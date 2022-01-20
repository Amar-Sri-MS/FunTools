#!/usr/bin/env python2.7
'''
csr find/list/peek/poke utilities
To issue csr peek/poke, connection to one of the debug interfaces(i2c/jtag/pcie/dpc)
is needed before issuing the commands
'''
import argparse, json
import string, os
import collections
import binascii
import socket
import jsocket
import time
import logging
import traceback
import tempfile
import urllib
import tarfile
import shutil
from array import array
from probeutils.dbgclient import *
from probeutils.dut import *

logger = logging.getLogger("csrutils")
logger.setLevel(logging.ERROR)

class constants(object):
    WORD_SIZE_BITS = 64
    MAX_WORD_VALUE = 0xFFFFFFFFFFFFFFFF
    CSR_CFG_DIR = "FunSDK/config/csr/"
    TMP_DIR = '/tmp'
    CSR_METADATA_FILE = 'csr_metadata.json'
    MEM_RW_CMD_CSR_ADDR = 0x90001900f0
    MEM_RW_STATUS_CSR_ADDR = 0x90001900f8
    MEM_RW_DATA_CSR_ADDR = 0x9000190100
    MUH_RING_SKIP_ADDR = 0x800000000
    MUH_SNA_ANODE_SKIP_ADDR = 0x10000
    MUH_SNA_CMD_ADDR_START = 0x1000
    IMAGE_START_PHYS_ADDR = 1024 * 1024
    UPLOAD_FULL_IMAGE = True

class actions(object):
    CSR_WR = 1
    CSR_POLL = 2
    CUT_RESET = 3


# csr peek handler for command line interface
def csr_peek(args):
    input_args = csr_get_peek_args(args)
    csr_name = input_args.get("csr_name", None)
    csr_inst = input_args.get("csr_inst", None)
    chip_inst = input_args.get("chip_inst", None)
    csr_entry = input_args.get("csr_entry", None)
    ring_name = input_args.get("ring_name", None)
    ring_inst = input_args.get("ring_inst", None)
    anode_name = input_args.get("anode_name", None)
    anode_inst = input_args.get("anode_inst", None)
    anode_path = input_args.get("anode_path", None)
    field_list = input_args.get("field_list", None)

    csr_data = csr_get_metadata(csr_name.lower(), ring_name=ring_name,
                                ring_inst=ring_inst, anode_name=anode_name,
                                anode_path=anode_path)

    if csr_data is None:
        print("Error! Failed to get metadata for csr:{} !!!".format(csr_name.lower()))
        return

    csr_addr = csr_get_addr(csr_data, anode_inst=anode_inst,
                            csr_inst=csr_inst, csr_entry=csr_entry)
    if csr_addr is None:
        print("Error getting csr address!!!")
        return
    logger.debug("csr address: {0}".format(hex(csr_addr)))

    csr_width_bytes = csr_get_width_bytes(csr_data)
    csr_width_words = csr_width_bytes >> 3
    (status, data) = dbgprobe().csr_peek(
            chip_inst=chip_inst, csr_addr=csr_addr,
            csr_width_words=csr_width_words)
    if status is True:
        word_array = data
        if word_array is None or not word_array:
            print("Error in csr peek!!!")
            return None
        logger.debug("Peeked value: {0}".format(hex_word_dump(word_array)))
        logger.debug("CSR Peek is success!")
        csr_show(csr_data, word_array, field_list)
    else:
        error_msg = data
        print("Error! {0}!".format(error_msg))

# csr poke handler for commandline interface
def csr_poke(args):
    input_args = csr_get_poke_args(args)
    chip_inst = input_args.get("chip_inst", None)
    csr_name = input_args.get("csr_name", None)
    csr_inst = input_args.get("csr_inst", None)
    csr_entry = input_args.get("csr_entry", None)
    ring_name = input_args.get("ring_name", None)
    ring_inst = input_args.get("ring_inst", None)
    anode_name = input_args.get("anode_name", None)
    anode_inst = input_args.get("anode_inst", None)
    anode_path = input_args.get("anode_path", None)
    field_list = input_args.get("field_list", None)
    raw_value = input_args.get("raw_value", None)

    csr_data = csr_get_metadata(csr_name.lower(), ring_name=ring_name,
                                ring_inst=ring_inst, anode_name=anode_name,
                                anode_path=anode_path)

    if csr_data is None:
        print("Error! Failed to get metadata for csr:{} !!!".format(csr_name))
        return

    csr_addr = csr_get_addr(csr_data, anode_inst=anode_inst,
                            csr_inst=csr_inst, csr_entry=csr_entry)
    if csr_addr is None:
        print("Error getting csr address!!!")
        return

    csr_width_bytes = csr_get_width_bytes(csr_data)
    csr_width_words = csr_width_bytes >> 3

    if raw_value is not None:
        word_array = list()
        for word in raw_value:
            value = str_to_int(word)
            if value is None:
                print(('Invalid field input value: "{0}". Must be positive'
                       'integer or hexadecimal').format(word))
                return None
            word_array.append(value)

        if len(word_array) != csr_width_words:
            print(("Number of raw value words should match csr width.\n"
                  " csr: {0}.\nExpected {1} word(s) but given {2}.").format(
                  json_obj_pretty(csr_data), csr_width_words, len(word_array)))
            return None
        logger.info(hex_word_dump(word_array))
    elif field_list is not None:
        (status, data) = dbgprobe().csr_peek(chip_inst=chip_inst,
                                             csr_addr=csr_addr,
                                             csr_width_words=csr_width_words)
        if status is not True:
            print("csr poke failed!. remote peek error while doing read/modify/write!!!")
            error_msg = data
            print("Error! {0}".format(error_msg))
            return None
        word_array = data
        logger.debug("Peeked value: {0}".format(hex_word_dump(word_array)))
        valid_field_list = csr_get_valid_field_list(csr_data)
        for field in field_list:
            field_name = field[0]
            if field_name not in valid_field_list:
                print("Invalid field name: {0}."
                      " Valid fields are: {1}".format(field_name,
                                                      valid_field_list.keys()))
                return None
            str_word_array = field[1:]
            field_word_array = list()
            for word in str_word_array:
                value = str_to_int(word)
                if value is None:
                    print('Invalid field input value: "{0}". Must be positive'
                          ' integer or hexadecimal'.format(word))
                    return None
                field_word_array.append(value)

            field_obj = valid_field_list.get(field_name, None)
            field_width = field_obj.get("fld_width", None)
            field_width_words = (field_width + 63) / 64
            field_offset = field_obj.get("fld_offset", None)
            if not field_width_words:
                sys.exit(1)
            if len(field_word_array) > field_width_words:
                print(("Number of field value words should match the length"
                       " for the field. csr:\n{0}.\nExpected {1} words"
                       " but given {2}.").format(json_obj_pretty(csr_data),
                       field_width_words, len(field_word_array)))
                return None
            csr_set_field(field_offset, field_width, word_array, field_word_array)
            logger.debug(field_name)
            logger.debug(field_word_array)
            logger.debug(hex_word_dump(word_array))
    else:
        print("Invalid input values! poke should"
              " have either field list with values or raw values")
        return None
    (status, data) = dbgprobe().csr_poke(chip_inst=chip_inst,
                                         csr_addr=csr_addr,
                                         word_array=word_array)
    if status is True:
        logger.debug("Poke Success!")
    else:
        error_msg = data
        print("CSR Poke failed! Error: {0}".format(error_msg))
        return


# csr list handler for commandline interface
def csr_list(args):
    csr_name = args.csr[0]
    if not csr_name:
        print("csr name is empty! Provide valid csr name!")
        return
    ring_name = args.ring[0] if args.ring else None
    anode_name = args.anode[0] if args.anode else None

    csr_list = csr_metadata().get_csr_def(csr_name.lower(), rn_class=ring_name, an=anode_name)
    if csr_list is None:
        print("csr: {} doesnot exist in database!.".format(csr_name))
        return
    print("Matching csr entries for csr:{0}".format(csr_name))
    print(json_obj_pretty(csr_list))

# csr decode handler for commandline interface
def csr_decode(args):
    input_args = csr_get_decode_args(args)
    csr_name = input_args.get("csr_name", None)
    raw_value = input_args.get("raw_value", None)

    csr_metadata = csr_metadata_objs(csr_name.lower())
    if type(csr_metadata) is not list:
        print(("Error! Failed to get metadata list"
              " for csr:{} !!!").format(csr_name.lower()))
        return

    csr_metadata = csr_metadata[0]
    csr_width_bytes = csr_get_width_bytes(csr_metadata)
    csr_width_words = csr_width_bytes >> 3

    word_array = list()
    if raw_value is not None:
        for word in raw_value:
            value = str_to_int(word)
            if value is None:
                print(('Invalid field input value: "{0}". Must be positive'
                       'integer or hexadecimal').format(word))
                return None
            word_array.append(value)

        if len(word_array) != csr_width_words:
            print(("Number of raw value words should match csr width.\n"
                  " csr: {0}.\nExpected {1} word(s) but given {2}.").format(
                  json_obj_pretty(csr_metadata), csr_width_words, len(word_array)))
            return None
        logger.info(hex_word_dump(word_array))

    csr_show(csr_metadata, word_array)

#import pdb
# Find csr medata matching an address
def csr_find_addr_metadata(caddr):
    csr_dict =  csr_metadata().get_metadata()
    if not csr_dict:
        print "Can't get csr metadata!"
        return None
    print "Done Loading"
    for k, v in csr_dict.iteritems():
        if k == 'psw_sch_qsch_cfg_extrabw_sp_queues_fp':
            pass
            #pdb.set_trace()
        for csr_data in v:
            address = caddr
            anode_addr = csr_data.get("an_addr", None)
            if anode_addr is None:
                print("Invalid csr metadata! anode_addr is missing in metadata!")
                sys.exit(1)
            anode_addr = int(anode_addr, 16)
            start_anode_addr = anode_addr
            anode_inst_cnt = csr_data.get("an_inst_cnt", None)
            if anode_inst_cnt is None:
                print("Invalid csr metadata! an_inst_cnt is missing in metadata!")
                sys.exit(1)

            anode_skip_addr = 0
            anode_inst = 0
            if anode_inst_cnt > 1:
                anode_skip_addr = csr_data.get("an_skip_addr", None)
                if anode_skip_addr is None:
                    print("Invalid csr metadata! an_skip_addr is missing in metadata!")
                    sys.exit(1)
                anode_skip_addr = int(anode_skip_addr, 16)
                end_anode_addr = start_anode_addr + (anode_skip_addr *
                                                     anode_inst_cnt);

                if address < start_anode_addr or address >= end_anode_addr:
                    continue

                x = address - start_anode_addr
                anode_inst = x / anode_skip_addr
                address = address - (anode_inst * anode_skip_addr)

            csr_addr = csr_data.get("csr_addr", None)
            if csr_addr is None:
                print("Invalid csr metadata! csr_addr is missing in metadata!")
                sys.exit(1)
            csr_addr = int(csr_addr, 16)

            csr_inst_start_addr = csr_addr
            csr_width = csr_data.get("csr_width", None)
            if csr_width is None:
                print("Invalid csr metadata! csr_width is missing in metadata!")
                sys.exit(1)
            csr_width_bytes = csr_width >> 0x3

            csr_n_entries = csr_data.get("csr_n_entries", None)
            if csr_n_entries is None:
                print("Invalid csr metadata! csr_n_entries is missing in metadata!")
                sys.exit(1)
            csr_inst_skip_addr = csr_width_bytes * csr_n_entries

            csr_inst_count = csr_data.get("csr_count", None)
            if csr_inst_count is None:
                print("Invalid csr metadata! csr_inst_count is missing in metadata!")
                sys.exit(1)

            address -= start_anode_addr
            csr_inst_end_addr = csr_inst_start_addr
            if csr_inst_count > 0:
                csr_inst_end_addr += csr_inst_skip_addr * csr_inst_count

            if address < csr_inst_start_addr or address >= csr_inst_end_addr:
                continue

            address -= csr_inst_start_addr
            csr_inst = address / csr_inst_skip_addr
            address -= csr_inst * csr_inst_skip_addr

            csr_start_addr = address
            csr_end_addr = csr_start_addr
            if csr_n_entries > 0:
                csr_end_addr = csr_start_addr + (csr_width_bytes * csr_n_entries)

            if address < csr_start_addr or address >= csr_end_addr:
                continue
            csr_index = address / csr_width_bytes

            print json_obj_pretty({k:csr_data})
            print ("csr: {0} anode_inst: {1} csr_inst: {2} csr_index:"
                " {3}").format(k, anode_inst, csr_inst, csr_index)
            return ({k:csr_data, "anode_inst": anode_inst,
                    "csr_inst": csr_inst, "csr_index": csr_index})
    print "Invalid address: {0}. No valid csr found!".format(hex(caddr))
    return None

# csr find handler for commandline interface.
# Returnds names of all the csrs which contain input substring
def csr_find(args):
    csr_name = args.substring[0] if args.substring else None
    csr_address = args.csr_address[0] if args.csr_address else None

    if csr_name:
        csr_list = csr_metadata().get_csr_list()
        matched_csr_list = list()
        for x in csr_list:
            if csr_name.lower() in x.lower():
                matched_csr_list.append(x)
        if not matched_csr_list:
            print('There are no csrs in database matching "{0}"!'.format(csr_name))
            return
        print('Matching csr entries for "{0}"'.format(csr_name))
        print(json_obj_pretty(matched_csr_list))
    elif csr_address:
        address = str_to_int(csr_address)
        if address and address > 0:
            csr_find_addr_metadata(address)
        else:
            print "Invalid address!"
            return
    else:
        print('Invalid argument! args:{0}'.format(args))
        return

def csr_metadata_dochub():
    url = 'http://dochub/doc/jenkins/master/funsdk/latest/Linux/csr-cfg.tgz'
    file_tmp = urllib.urlretrieve(url, filename=None)[0]
    base_name = os.path.basename(url)
    file_name, file_extension = os.path.splitext(base_name)
    tar = tarfile.open(file_tmp)
    temp_dir = tempfile.mkdtemp()
    output_dir = os.path.join(temp_dir, constants.CSR_CFG_DIR)
    tar.extract('./'+ constants.CSR_CFG_DIR + constants.CSR_METADATA_FILE, temp_dir)
    metadata_file = os.path.join(output_dir, constants.CSR_METADATA_FILE)

    return metadata_file

def csr_load_metadata(args):
    if args.default:
        status = csr_metadata().load_metadata_from_dochub()
        if not status:
            print 'Failed to load metadata from dochub!'
            return
    elif args.sdk_root_dir:
        sdk_root_dir = args.sdk_root_dir[0]
        sdk_root_dir = os.path.abspath(sdk_root_dir)
        if not os.path.exists(sdk_root_dir):
            print  'SDK root dir: "{}": does not exist!'.format(sdk_root_dir)
            return
        status = csr_metadata().load_metadata_from_sdk(sdk_root_dir)
        if not status:
            print 'Failed to load metadata from sdk dir: {}!'.format(sdk_root_dir)
            return
    else:
        print "Invalid metadta arguments!"
        return
    return

def load_srec_image(chip_inst, input_file):
    csr_replay_data = list()
    with open(input_file) as fp:
        line = fp.readline()
        cnt = 0
        line_num = 0
        while line:
            line = line.rstrip()
            line_num += 1
            logger.debug("Line {}: {}".format(line_num, line.strip()))
            csr_tokens = line.split(' ')
            if len(csr_tokens) != 2:
                logger.error('Invalid line: "{0}"'.format(line))
                sys.exit(1)
            #logger.info("Address: {0} data: {1}".format(csr_tokens[0][1:], csr_tokens[1]))
            skip_addr = 0
            if(cnt & 0x2):
                skip_addr = constants.MUH_RING_SKIP_ADDR
            if (cnt & 0x1):
                skip_addr += constants.MUH_SNA_ANODE_SKIP_ADDR
            for i in range(8):
                csr_val = int(csr_tokens[1][i*16:(i+1)*16],16)
                csr_addr = constants.MEM_RW_DATA_CSR_ADDR + skip_addr
                csr_addr += i * 8
                (status, data) = dbgprobe().csr_fast_poke(chip_inst, csr_addr, [csr_val])
                if status is True:
                    logger.info('Write value:{0}'.format(hex(csr_val)))
                    logger.debug("poke success!!!")
                else:
                    error_msg = data
                    logger.error("Error! {0}!".format(error_msg))
                    sys.exit(1)

            csr_addr = constants.MEM_RW_CMD_CSR_ADDR
            csr_addr += skip_addr
            muh_sna_cmd_addr = csr_tokens[0][1:]
            muh_sna_cmd_addr = constants.MUH_SNA_CMD_ADDR_START + (cnt/4)
            csr_val = muh_sna_cmd_addr << 37;
            csr_val |= 0x0 << 63;
            logger.debug('csr_val: {0}'.format(csr_val))
            (status, data) = dbgprobe().csr_fast_poke(chip_inst, csr_addr, [csr_val])
            if status is True:
                logger.info("Poke:{0} addr: {1} Success!".format(cnt, hex(muh_sna_cmd_addr)))
            else:
                error_msg = data
                logger.error("CSR Poke failed! Addr: {0} Error: {1}".format(hex(csr_addr), error_msg))
                sys.exit(1)
            csr_addr = constants.MEM_RW_STATUS_CSR_ADDR
            csr_addr += skip_addr
            (status, data) = dbgprobe().csr_peek(chip_inst=chip_inst,
                                                 csr_addr=csr_addr,
                                                 csr_width_words=1)
            if status is True:
                word_array = data
                if word_array is None or not word_array:
                    logger.error("Failed get cmd status! Error in csr peek!!!")
                    sys.exit(1)
                cmd_status_done = word_array[0]
                cmd_status_done = cmd_status_done >> 63
                if cmd_status_done != 1:
                    logger.error("Failed cmd status != Done!")
                    sys.exit(1)
                else:
                    logger.info('Data ready!')
            else:
                error_msg = data
                logger.error('Error! {0}!'.format(error_msg))
                sys.exit(1)

            cnt += 1
            if constants.UPLOAD_FULL_IMAGE == False and cnt == 16:
                break
            line = fp.readline()
    if cnt > 0:
        logger.info('Succesfully wrote {0} lines!'.format(cnt))
    else:
        logger.error('No valid lines found in {}').format(input_file)
        sys.exit(1)
    return


class DDR(object):
    """
    Sole purpose in life: write to DDR in S1.

    Assumes DDR is in spray mode: the target MUD is swapped for each 64-byte
    line. Also assumes lines written to a MUD are hashed between two channels.
    This means that bit 7 of the physical address determines the channel, and
    is mapped to bit 28 (the QSN bit).

    Those assumptions will change if the DDR CSR config values are changed.

    Example:
        0x100000 - MUD0, channel 0, addr 0x00001000
        0x100040 - MUD1, channel 0, addr 0x00001000
        0x100080 - MUD0, channel 1, addr 0x10001000
        0x1000c0 - MUD1, channel 1, addr 0x10001000
        0x100100 - MUD0, channel 0, addr 0x00001001

    If you need to extend this for future chips, and the SNA registers have
    not changed, consider a configuration parameter in the constructor that
    sets the SNA register addresses and offsets.
    """

    MUD0_SNA = 0x1b0411c0
    MUD1_SNA = 0x1c0411c0
    CMD_REG_OFFSET = 0x1f8
    STATUS_REG_OFFSET = 0x200
    DATA_REG_OFFSET = 0x208

    STATUS_BIT_SHIFT = 1

    def __init__(self, dbg_probe):
        self.probe = dbg_probe
        self.log2_line_width = 6
        self.sna_addrs = [self.MUD0_SNA, self.MUD1_SNA]
        self.line_width = 1 << self.log2_line_width

    def write(self, phys_addr, data):
        res = self._write_data(phys_addr, data)
        if res:
            res = self._issue_write_command(phys_addr)
        if res:
            res = self._check_success(phys_addr)
        self._clear_status_reg(phys_addr)
        return res

    def _write_data(self, phys_addr, wdata):
        sna_addr = self._get_sna_addr(phys_addr)

        for i in range(8):
            csr_addr = sna_addr + self.DATA_REG_OFFSET + (i * 8)
            csr_val = wdata[i]
            (status, ret_data) = self.probe.csr_fast_poke(csr_addr, [csr_val])
            if status:
                logger.debug('Wrote data value: {0}'.format(hex(csr_val)))
            else:
                error_msg = ret_data
                logger.error('Error writing data value: {0}'.format(error_msg))
                return False

        return True

    def _get_sna_addr(self, phys_addr):
        """ Which SNA address to write to for the specified phys address """
        mud = (phys_addr & self.line_width) >> self.log2_line_width
        return self.sna_addrs[mud]

    def _issue_write_command(self, phys_addr):
        sna_addr = self._get_sna_addr(phys_addr)

        csr_addr = sna_addr + self.CMD_REG_OFFSET

        # The addresses are divided across the MUDs, so we divide the
        # physical address by the number of MUDs to get the DDR shard address.
        ddr_addr = phys_addr // len(self.sna_addrs)

        # Divide by 2, which is the number of channels per MUD
        ddr_addr = ddr_addr // 2

        # And then we divide again to turn bytes into words
        ddr_addr = ddr_addr // self.line_width

        # Within each MUD, a hash function sets bit 28 on the shard address to
        # determine which channel is used. This is simply bit 7 of the physical
        # address or equivalently, bit 0 of the shard address before we divide
        # by the number of channels (bit notation is 0-indexed).
        qsn_bit = (phys_addr >> 7) & 0x1
        ddr_addr = ddr_addr | (qsn_bit << 28)

        csr_val = ddr_addr & 0xbfffffff   # set bit 30 to 0 for write request
        (status, data) = self.probe.csr_fast_poke(csr_addr, [csr_val])
        if status:
            logger.info('Wrote address: {0} as {1}'.format(hex(phys_addr), hex(ddr_addr)))
        else:
            error_msg = data
            logger.error('Error writing address: {0}'.format(hex(csr_addr), error_msg))
            return False

        return True

    def _check_success(self, phys_addr):
        sna_addr = self._get_sna_addr(phys_addr)

        csr_addr = sna_addr + self.STATUS_REG_OFFSET
        (status, data) = self.probe.csr_peek(chip_inst=0,
                                             csr_addr=csr_addr,
                                             csr_width_words=1)
        if status:
            word_array = data
            if not word_array:
                logger.error('Error reading command status: empty data')
                return False

            cmd_status = word_array[0]
            cmd_status_done = cmd_status >> self.STATUS_BIT_SHIFT
            if cmd_status_done != 1:
                logger.error('Failed to issue write: command status not done')
                return False
            else:
                logger.debug('Write issued')
                return True
        else:
            error_msg = data
            logger.error('Error reading command status: {0}'.format(error_msg))
            return False

    def _clear_status_reg(self, phys_addr):
        sna_addr = self._get_sna_addr(phys_addr)
        csr_addr = sna_addr + self.STATUS_REG_OFFSET

        (status, data) = self.probe.csr_fast_poke(csr_addr, [0x0])
        if status:
            logger.debug('Status cleared')
        else:
            logger.error('Error clearing status: {0}'.format(data))


def load_image_s1(input_file):
    """
    Loads the data into DDR memory of S1, starting from physical address 1MB.

    The input file format is a "64-big" format file with address and
    data fields for each record. Fields are separated with a space.

    @<address> <512-bit data as ASCII hex>

    Returns True on success, False on failure.

    TODO (jimmy): merge the F1 code with this when we have time
    """
    num_lines = 0
    ddr = DDR(dbgprobe())

    with open(input_file) as fp:
        # This loads the lines one at a time: the file handle is a generator,
        # as is the enumerate function.
        for line_idx, line in enumerate(fp):
            line = line.rstrip()

            csr_tokens = line.split(' ')
            if len(csr_tokens) != 2:
                logger.error('Invalid line: "{0}"'.format(line))
                return False

            data = []
            for i in range(8):
                data.append(int(csr_tokens[1][i*16:(i+1)*16], 16))

            phys_addr = constants.IMAGE_START_PHYS_ADDR + (line_idx * 64)
            ret = ddr.write(phys_addr, data)
            if not ret:
                logger.error('Failed to write phys addr {0}'.format(hex(phys_addr)))
                return False

            num_lines = line_idx + 1
            if not constants.UPLOAD_FULL_IMAGE and num_lines == 16:
                break

    if num_lines > 0:
        logger.info('Successfully wrote {0} lines!'.format(num_lines))
    else:
        logger.error('No valid lines found in {}').format(input_file)
        return False

    return True


# Process each line in the <csr_replay_input_file> statrting with string "CSRWR" and creates list all the CSRs
# Expected valid line format:  CSRWR:<csr_address>:<csr_width>:[<list of csr values in 64 bit big endian words>]
# Returns the dict of all the csrs
def csr_replay_config(csr_replay_input_file, srec_file = None):
    if not os.path.isabs(csr_replay_input_file):
        csr_replay_input_file = os.path.join(os.getcwd(), csr_replay_input_file)
    if not os.path.isfile(csr_replay_input_file):
        print 'Path: "{0}" is not a regular file!'.format(csr_replay_input_file)
        return

    if srec_file:
        if not os.path.isabs(srec_file):
            srec_file = os.path.join(os.getcwd(), srec_file)
        if not os.path.isfile(srec_file):
            print 'Path: "{0}" is not a regular file!'.format(srec_file)
            return

    csr_replay_data = list()
    with open(csr_replay_input_file) as fp:
        line = fp.readline()
        cnt = 0
        line_num = 0
        while line:
            line = line.rstrip()
            line_num += 1
            csr_tokens = line.split(':')
            logger.info("Line {}: {}".format(line_num, line.strip()))
            #print csr_tokens
            if not csr_tokens:
                logger.debug('Skipping empty line {0}: "{1}"'.format(line_num, line))
                line = fp.readline()
                continue

            valid_keywords = ['CSR_WR', 'CSR_POLL', 'Reset CUT!']
            if csr_tokens[0] not in valid_keywords:
                logger.debug('Skipping non-matching line {0}: "{1}"'.format(line_num, line))
                line = fp.readline()
                continue

            print('#####ACTION#####{0}'.format(csr_tokens[0]))
            if csr_tokens[0] == 'CSR_WR':
                if len(csr_tokens) < 5:
                    logger.error('Invalid CSRWR tokens in line {0}: "{1}"'.format(line_num, line))
                    return

                for count, token in enumerate(csr_tokens[1:], start=1):
                    #print str_to_int(csr_tokens[count])
                    csr_tokens[count] =  str_to_int(csr_tokens[count])
                    if csr_tokens[count] is None:
                        logger.error('Invalid csr replay data! line {0}: "{1}"'.format(line_num, line))
                        return

                csr_address = csr_tokens[2]
                csr_width = csr_tokens[3]
                if not csr_width:
                    print 'Invalid csr width in input data: "{0}"'.format(line)
                    return
                csr_width_words = (csr_width + 63) / 64
                csr_val_words = csr_tokens[4:]
                if csr_width_words != len(csr_val_words):
                    print 'Mismatch in csr width and value. "{0}"'.format(line)
                    return
                logger.debug('csr_address: {0} csr_width: {1}'
                        ' word_array:{2}'.format(csr_address,
                            csr_width, [hex(x) for x in csr_val_words]))

                csr_info = dict()
                csr_info['action'] = actions.CSR_WR
                csr_info["csr_address"] = csr_address
                csr_info["csr_width"] = csr_width
                csr_info["csr_val_words"] = csr_val_words
                csr_replay_data.append(csr_info)
                logger.debug('Succesfully added "{0}" to replay data!'.format(line))
            elif csr_tokens[0] == 'CSR_POLL':
                if len(csr_tokens) < 5:
                    logger.error('Invalid CSR_POLL tokens in line {0}: "{1}"'.format(line_num, line))
                    return

                for count, token in enumerate(csr_tokens[1:4], start=1):
                    csr_tokens[count] =  str_to_int(csr_tokens[count])
                    if csr_tokens[count] is None:
                        logger.error('Invalid csr poll data! line {0}: "{1}"'.format(line_num, line))
                        return

                logger.info('CSR POLL tokens: {0}'.format(csr_tokens))
                csr_address = csr_tokens[1]
                csr_width = csr_tokens[2]
                timeout = csr_tokens[3]
                if not csr_width:
                    logger.error('Invalid csr width in line{0}: "{1}"'.format(line_num, line))
                    return
                csr_width_words = (csr_width + 63) / 64
                csr_poll_data = csr_tokens[4:]
                if csr_width_words != len(csr_poll_data):
                    logger.error('CSR width and poll data mismatch in line{0}: "{1}"'.format(line_num, line))
                    return
                csr_val_mask_list = list()
                for i in range(csr_width_words):
                    csr_val_mask = csr_poll_data[i].split('-')
                    if len(csr_val_mask) != 2:
                        logger.error('Invalid csr poll val & mask in line {0}: "{1}"'.format(line_num, line))
                        return
                    csr_val_mask[0] = str_to_int(csr_val_mask[0])
                    csr_val_mask[1] = str_to_int(csr_val_mask[1])
                    csr_val_mask_list.append(tuple(csr_val_mask))

                logger.debug('CSR POLL csr_address: {0} csr_width: {1} timeout: {2}'
                        ' csr_val_mask_list:{3}'.format(csr_address,
                            csr_width, timeout, csr_val_mask_list))

                csr_info = dict()
                csr_info['action'] = actions.CSR_POLL
                csr_info["csr_address"] = csr_address
                csr_info["timeout"] = timeout
                csr_info["csr_width"] = csr_width
                csr_info["csr_val_words"] = csr_val_mask_list
                csr_replay_data.append(csr_info)
                logger.debug('Succesfully added "{0}" to replay data!'.format(line))
            elif csr_tokens[0] == 'Reset CUT!':
                csr_info = dict()
                csr_info['action'] = actions.CUT_RESET
                csr_replay_data.append(csr_info)
                logger.debug('Succesfully added CUT RESET"{0}" to replay data!'.format(line))
            else:
                logger.error('Unsupported action!')
            cnt += 1
            line = fp.readline()
    if cnt > 0:
        print('Succesfully added {0} lines! to replay data.'.format(cnt))
        return csr_replay_data
    else:
        print('No valid csrreplay data is found in {}').format(input_file)
        return None

# Dumps the json dict of all the csrs returned by csr_replay_config() into a file in the directory <dest_dir>
def csr_replay_config_to_file(input_file, dest_dir):
    if not os.path.isabs(input_file):
        input_file = os.path.join(os.getcwd(), input_file)
    if not os.path.isfile(input_file):
        print 'Path: "{0}" is not a regular file!'.format(input_file)
        return

    if not os.path.isabs(dest_dir):
        dest_dir = os.path.join(os.getcwd(), dest_dir)
    if not os.path.exists(dest_dir):
        print 'Path: "{0}" does not exist!'.format(dest_dir)
        return

    replay_config = csr_replay_config(input_file)
    if replay_config is None:
        print('No valid csrreplay data is found in {}.').format(input_file)
        return False

    csr_replay_data = list()
    for x in replay_config:
        csr_info = dict()
        csr_address = x.get("csr_address", None)
        if not csr_address:
            print("Invalid csr_address in input data! csr_address: {0}".format(csr_address))
            return False
        csr_width = x.get("csr_width", None)
        if not csr_width:
            print("Invalid in csr_width in input data! csr_width: {0}".format(csr_width))
            return False
        csr_val_words = x.get("csr_val_words", None)
        if not csr_val_words:
            print("Invalid in csr_val_words in input data! csr_val_words: {0}".format(csr_val_words))
            return False
        csr_info["csr_address"] = hex(csr_address)
        csr_info["csr_width_words"] = (csr_width + 63 ) >> 6
        csr_val_words_hex = list()
        remaining_width = csr_width
        for x in csr_val_words:
            if remaining_width >= 64:
                csr_val_words_hex.append('0x{0:0{1}X}'.format(x,16))
                remaining_width -= 64
            else:
                mask = (0xFFFFFFFFFFFFFFFF >> (64 - remaining_width)) \
                        << (64 - remaining_width)
                csr_val_words_hex.append('0x{0:0{1}X}'.format(x & mask,16))
                remaining_width = 0
        csr_info["csr_val_words"] = csr_val_words_hex
        csr_replay_data.append(csr_info)

    dest_file = os.path.join(dest_dir, "csr_replay_data.cfg")
    f = open(dest_file, "w")
    f.write(json.dumps(csr_replay_data, indent=4))
    f.close()
    print('Succesfully created csr replay data file: {0}'.format(dest_file))

def csr_replay(args):
    input_file = args.replay_file[0]
    if not os.path.isabs(input_file):
        input_file = os.path.join(os.getcwd(), input_file)
    if not os.path.isfile(input_file):
        print 'Path: "{0}" is not a regular file!'.format(input_file)
        return

    srec_file = args.image[0]
    if not os.path.isabs(srec_file):
        srec_file = os.path.join(os.getcwd(), srec_file)
    if not os.path.isfile(srec_file):
        print 'Path: "{0}" is not a regular file!'.format(srec_file)
        return

    chip_inst = int(args.chip_inst[0], 10) if args.chip_inst else None
    chip_type = args.chip_type

    replay_config = csr_replay_config(input_file)
    if replay_config is None:
        print('No valid csrreplay data is found in {}').format(input_file)
        return False

    cnt = 0
    for x in replay_config:
        if x.get('action') == actions.CSR_WR:
            csr_info = dict()
            csr_address = x.get("csr_address", None)
            if not csr_address:
                print("Invalid csr_address in input data! csr_address: {0}".format(csr_address))
                return False
            csr_width = x.get("csr_width", None)
            if not csr_width:
                print("Invalid in csr_width in input data! csr_width: {0}".format(csr_width))
                return False
            csr_val_words = x.get("csr_val_words", None)
            if not csr_val_words or len(csr_val_words) < 1:
                print("Invalid in csr_val_words in input data! csr_val_words: {0}".format(csr_val_words))
                return False
            csr_width_words = (csr_width + 63 ) >> 6
            logger.debug('csr_address: {0} csr_width_words: {1}'
                    'word_array:{2}'.format(csr_address,
                        csr_width_words, csr_val_words))
            (status, status_msg) = dbgprobe().csr_poke(chip_inst=chip_inst,
                                                       csr_addr=csr_address,
                                                       word_array=csr_val_words)
            if status == True:
                print('Replay count:{0} data:"{1}"!'.format(cnt, x))
                cnt += 1
            else:
                print('Replay failed! "{0}"! Replay stopped! Error:{1}'.format(x, status_msg))
                return
        elif x.get('action') == actions.CSR_POLL:
            csr_info = dict()
            csr_address = x.get("csr_address", None)
            if not csr_address:
                print("Invalid csr_address in input data! csr_address: {0}".format(csr_address))
                #return False
                sys.exit(1)

            csr_width = x.get("csr_width", None)
            if not csr_width:
                print("Invalid in csr_width in input data! csr_width: {0} @{1}".format(csr_width, csr_address))
                #return False
                sys.exit(1)

            timeout = x.get("timeout", None)
            if not timeout:
                print("Invalid in timeout in input data! timeout: {0} @{1}".format(timeout, csr_address))
                #return False
                sys.exit(1)

            csr_val_words = x.get("csr_val_words", None)
            if not csr_val_words or len(csr_val_words) < 1:
                print("Invalid in csr_val_words in input data! "
                      "csr_val_words: {0} @{1}".format(csr_val_words, csr_address))
                sys.exit(1)
            csr_width_words = (csr_width + 63 ) >> 6
            logger.debug('csr_address: {0} csr_width_words: {1}'
                    ' word_array:{2} timeout:{3}'.format(csr_address,
                        csr_width_words, csr_val_words, timeout))

            retry = 0
            poll_status = False
            start_time = time.time()

            # For F1, the timeout is the number of retries.
            # For S1, the timeout is number of microseconds. This needs to
            # be scaled for emulation. 1ms of S1 emulation time is ~ 10s, so
            # 1us should be ~ 10ms. This does not work in practice: 1us ~ 10s
            # works better.
            time_scale = 10 if args.emulation else 1e-6
            if chip_type == 's1':
                timeout = timeout * time_scale

            while ((retry < timeout) or (timeout == 0)):
                status = csr_poll_status(chip_inst, csr_address,
                                         csr_width_words, csr_val_words)
                if status == False:
                    retry += 1
                    if chip_type == 's1':
                        retry = (time.time() - start_time)
                    print('Retrying csr status poll "{0}"!'.format(retry))
                else:
                    print('csr status poll done! cnt: {0} data:"{1}"!'.format(cnt, retry))
                    poll_status = True
                    break
            if poll_status == False:
                logger.error("csr status poll timedout!")
                sys.exit(1)
            cnt += 1
        elif x.get('action') == actions.CUT_RESET:
            if chip_type == 'f1':
                status = load_srec_image(chip_inst, srec_file)
            elif chip_type == 's1':
                image_64big = srec_file
                status = load_image_s1(image_64big)
            if status == False:
                logger.error('Failed to copy FunOS/u-boot image!')
                sys.exit(1)
            logger.info('Successfully copied FunOS/u-boot image! cnt:{0}'.format(cnt))
            cnt += 1
        else:
            logger.error('Invalid action!')
            sys.exit(1)
    print('Succesfully replayed {0} CSRs!'.format(cnt))

def csr_poll_status(chip_inst, csr_address, csr_width_words, value_mask):
    (status, data) = dbgprobe().csr_peek(chip_inst=chip_inst,
                                         csr_addr=csr_address,
                                         csr_width_words=csr_width_words)
    if status == False:
        logger.error('csr_peek failed!')
        sys.exit(1)

    logger.debug('status: {0} data: {1}'.format(status, data))
    if len(data) != csr_width_words:
        logger.error('csr poll: csr peek returned insufficient data!'
                ' expected: {0} received: {1}'.format(csr_width_words, len(data)))
        sys.exit(1)

    for i,x in enumerate(value_mask):
        mask = x[1]
        value = x[0]
        if (data[i] & mask) != value:
            logger.error('Expected: {0}/{1} Actual: {2}'.format(hex(value),
                                                                hex(mask),
                                                                hex(data[i])))
            return False
    return True

# connect handler for commandline interface.
# Connects to remote server
def server_connect(args):
    logger.debug('args: {}'.format(args))
    dut_name = args.dut[0]
    if dut_name is None:
        print("Invalid dut!")
        return

    mode = None
    if args.mode is None or args.mode[0] is None:
        mode = 'i2c'
    else:
        logger.debug('mode: {0}'.format(args.mode[0]))
        mode = args.mode[0]

    force_connect = False
    if args.force:
        force_connect = True
        logger.info('Force connection: {0}'.format(force_connect))

    probe = connect(dut_name, mode, force_connect)
    if probe is None:
        print('Failed to connect to dut: {0}'.format(dut_name, mode))
        return

def connect(dut_name, mode, force_connect=False):
    logger.debug('dut: {0} mode: {1}'.format(dut_name, mode))
    if mode == 'i2c':
        dut_i2c_info = dut().get_i2c_info(dut_name)
        if dut_i2c_info is None:
            print('Failed to get i2c connection details!')
            return None
        # if not board with bmc (emulation and socketed test boards do not have
        # bmc)
        if dut_i2c_info[0] is False:
            i2c_probe_serial = dut_i2c_info[1]
            i2c_probe_ip = dut_i2c_info[2]
            i2c_slave_addr = dut_i2c_info[3]
            i2c_bitrate = dut_i2c_info[4]
            chip_type = dut_i2c_info[5]
            status = dbgprobe().connect(mode='i2c', bmc_board=False,
                                        probe_ip_addr=i2c_probe_ip,
                                        probe_id=i2c_probe_serial,
                                        slave_addr=i2c_slave_addr,
                                        force=force_connect,
                                        chip_type=chip_type,
                                        i2c_bitrate=i2c_bitrate)
        else:
            bmc_ip = dut_i2c_info[1]
            chip_type = dut_i2c_info[2]
            status = dbgprobe().connect(mode='i2c', bmc_board=True,
                                        bmc_ip_address=bmc_ip,
                                        chip_type=chip_type)
    elif mode == 'jtag':
        dut_jtag_info = dut().get_jtag_info(dut_name)
        if dut_jtag_info is None:
            print('Failed to get jtag connection details!')
            return None
        if dut_jtag_info[0] is False:
            jtag_probe_id = dut_jtag_info[1]
            jtag_probe_ip = dut_jtag_info[2]
            chip_type = dut_jtag_info[3]
            jtag_bitrate = dut_jtag_info[4]
            status = dbgprobe().connect(mode='jtag', bmc_board=False,
                                        probe_ip_addr = jtag_probe_ip,
                                        probe_id = jtag_probe_id,
                                        jtag_bitrate = jtag_bitrate,
                                        chip_type=chip_type)
        else:
            bmc_ip = dut_jtag_info[1]
            jtag_probe_id = dut_jtag_info[2]
            jtag_probe_ip = dut_jtag_info[3]
            chip_type = dut_jtag_info[4]
            status = dbgprobe().connect(mode='jtag', bmc_board=True,
                                        bmc_ip_address=bmc_ip,
                                        probe_ip_addr=jtag_probe_ip,
                                        probe_id = jtag_probe_id,
                                        chip_type=chip_type)
    elif mode == 'pcie':
        dut_pcie_info = dut().get_pcie_info(dut_name)
        if dut_pcie_info is None:
            print('Failed to get pcie connection details!')
            return None
        pcie_ccu_bar = dut_pcie_info[0]
        pcie_probe_ip = dut_pcie_info[1]
        pcie_mem_offset = dut_pcie_info[2]
        chip_type = dut_pcie_info[3]
        status = dbgprobe().connect(mode='pcie', bmc_board=False,
                                    probe_ip_addr = pcie_probe_ip,
                                    probe_id = pcie_ccu_bar,
                                    chip_type=chip_type,
                                    slave_addr = pcie_mem_offset)
    else:
        print('Mode: {} is not yet supported!'.format(mode))
        return
    if status is True:
        logger.debug("Connection to probe successful!")
        return dbgprobe()
    else:
        logger.error("Connection to probe is failed!")
        return None


# disconnect handler for commandline interface.
# Disconnects from remote server
def server_disconnect(args):
    status = dbgprobe().disconnect()
    if status is not True:
        logger.error("Probe disconnect failed!")
    else:
        logger.info("Probe is disconnected!");
    return

# Read peek input args
def csr_get_peek_args(args):
    input_args = dict()
    input_args["csr_name"] = args.csr[0]
    input_args["csr_inst"] = int(args.csr_inst[0], 10) if args.csr_inst else None
    input_args["chip_inst"] = int(args.chip_inst[0], 10) if args.chip_inst else None
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

# Read poke input args
def csr_get_poke_args(args):
    input_args = dict()
    input_args["csr_name"] = args.csr[0]
    input_args["chip_inst"] = int(args.chip_inst[0], 10) if args.chip_inst else None
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
    input_args["raw_value"] = args.raw_value

    return input_args

# Read decode input args
def csr_get_decode_args(args):
    input_args = dict()
    input_args["csr_name"] = args.csr[0]
    input_args["raw_value"] = args.raw_value

    return input_args



# Returns csr address
def csr_get_addr(csr_data, anode_inst=None, csr_inst=None, csr_entry=None):
    if type(csr_data) is not dict:
        print(('csr_data is expected to be dictionary.\n'
              'csr_data: {0}').format(json.dumps(csr_data, indent=4)))
        return

    an_name = csr_data.get("an", None)
    if an_name is None:
        print("Invalid csr metadata! an_name is missing in metadata!")
        sys.exit(1)

    anode_inst_cnt = csr_data.get("an_inst_cnt", None)
    if anode_inst_cnt is None:
        print("Invalid csr metadata! an_inst_cnt is missing in metadata!")
        sys.exit(1)

    if not anode_inst_cnt > 0:
        print("Inconsistant csr metadata parsing!"
                " anode inst count should be non-zero positive integer!")
        return

    if anode_inst_cnt > 1 and anode_inst is None:
        print("csr objs:\n{}\n".format(json_obj_pretty(csr_data)))
        print(("csr exists in multiple instances of anode: {}."
               " Give appropriate anode option!"
               " valid anode instances: {}").format(an_name,
                                            range(0,anode_inst_cnt)))
        return

    if (anode_inst is not None) and (anode_inst < 0 or anode_inst >= anode_inst_cnt):
        print("csr objs:\n{}\n".format(json_obj_pretty(csr_data)))
        print(("Invalid anode instance for csr: anode: {}."
            "\nGive appropriate anode details!"
            " Valid anode instances: {}").format(an_name,
                                    range(0,anode_inst_cnt)))
        return

    csr_inst_cnt = csr_data.get("csr_count", None)
    if csr_inst_cnt is None:
        print("Invalid csr metadata! csr_inst_cnt is missing in metadata!")
        sys.exit(1)

    if csr_inst_cnt > 1:
        if csr_inst is None:
            print("csr objs:\n{}\n".format(json.dumps(csr_data, indent=4)))
            print(("There are {} instances of csr."
                   "\nProvide csr instance number!".format(csr_inst_cnt)))
            return
        if csr_inst < 0 or csr_inst >= csr_inst_cnt:
            print("csr objs:\n{}\n".format(json.dumps(csr_data, indent=4)))
            print(("Invalid instance of csr!"
                   "\nProvide csr instance number in the"
                   " range [0 - {}]!").format(csr_inst_cnt - 1))
            return

    if csr_inst_cnt == 1 and csr_inst is not None:
        logger.debug("**** Ignoring option csr instance number: {}!!! ****".format(csr_inst))

    csr_n_entries = csr_data.get("csr_n_entries", None)
    if csr_n_entries is None:
        print("Invalid csr metadata! csr_n_entries is missing in metadata!")
        sys.exit(1)

    if csr_n_entries > 1:
        if csr_entry is None:
            print("csr objs:\n{}\n".format(json.dumps(csr_data, indent=4)))
            print(("There are {} entries in table csr!"
                   "\nProvide csr entry index number!").format(csr_n_entries))
            return
        logger.debug("csr entry index: {} csr_n_entries: {}".format(csr_entry, csr_n_entries))
        if csr_entry < 0 or csr_entry >= csr_n_entries:
            print("csr objs:\n{}\n".format(json.dumps(csr_data, indent=4)))
            print(("Invalid entry index of csr!"
                   "\nProvide csr entry index in the"
                   " range of [0 - {}]!".format(csr_n_entries - 1)))
            return

    if csr_n_entries == 1 and csr_entry is not None:
        logger.debug("**** Ignoring option csr entry index: {}!!! ****".format(csr_entry))

    anode_addr = csr_data.get("an_addr", None)
    if anode_addr is None:
        print("Invalid csr metadata! anode_addr is missing in metadata!")
        sys.exit(1)
    anode_addr = int(anode_addr, 16)

    if anode_inst_cnt > 1:
        if anode_inst is None:
            print("Expetced anode_inst argument!")
            return None

        if anode_inst < 0 or anode_inst >= anode_inst_cnt:
            print("Invalid anode_inst: {}!".format(anode_inst))
            return None

        anode_skip_addr = csr_data.get("an_skip_addr", None)
        if anode_skip_addr is None:
            print("Invalid csr metadata! an_skip_addr is missing in metadata!")
            sys.exit(1)

        anode_addr += int(anode_skip_addr, 16) * anode_inst;

    csr_addr = csr_data.get("csr_addr", None)
    if csr_addr is None:
        print("Invalid csr metadata! csr_addr is missing in metadata!")
        sys.exit(1)

    csr_addr = int(csr_addr, 16)
    csr_width = csr_data.get("csr_width", None)
    if csr_width is None:
        print("Invalid csr metadata! csr_width is missing in metadata!")
        sys.exit(1)

    csr_stride_width = csr_data.get("csr_stride_width", None)
    if csr_stride_width is None:
        print("Invalid csr metadata! csr_stride_width is missing in metadata!")
        sys.exit(1)

    csr_width_bytes = csr_width >> 0x3
    if (csr_stride_width < csr_width_bytes):
        print('Invalid csr metadata! csr_stride_width({})'
              ' < csr_width({})!'.format(csr_stride_width, csr_width))
        sys.exit(1)

    assert(csr_n_entries >= 0)
    if csr_n_entries > 1:
        if csr_entry is None:
            print("Expetced csr_entry argument!")
            return None

        if csr_entry < 0 or csr_entry >= csr_n_entries:
            print("Invalid csr_entry: {}!".format(csr_entry))
            return None
        csr_addr += csr_stride_width * csr_entry;

    csr_inst_size = csr_data.get("csr_inst_size", None)
    if csr_inst_size is None:
        print("Invalid csr metadata! csr_inst_size is missing in metadata!")
        sys.exit(1)

    if (csr_inst_size <  (csr_stride_width * csr_n_entries)):
        print('Invalid csr metadata! "csr_inst_size < csr_stride_width * csr_n_entries"')
        sys.exit(1)

    if csr_inst_cnt > 1:
        if csr_inst is None:
            print("Expetced csr_inst argument!")
            return None

        if csr_inst < 0 or csr_inst >= csr_inst_cnt:
            print("Invalid csr_inst: {}!".format(csr_inst))
            return None
        csr_addr += csr_inst_size * csr_inst

    return (anode_addr + csr_addr)

# Returns width of a csr in bytes
def csr_get_width_bytes(csr_data):
    csr_width = csr_data.get("csr_width", None)
    if csr_width is None:
        print("Invalid csr metadata! csr_width is missing in metadata!")
        sys.exit(1)

    csr_width_bytes = csr_width >> 0x3

    return csr_width_bytes

# Reads the field from input word array and returns field value as word array
def csr_get_field(fld_pos, fld_size, word_array):
    constants.WORD_SIZE_BITS = 64
    reg_padded_size = len(word_array) * constants.WORD_SIZE_BITS
    if not (reg_padded_size >= fld_size + fld_pos):
        print(("Invalid arguments! fld_pos: {0} + fld_size: {1} exceeds"
               " csr word array length: {2}").format(fld_pos, fld_size,
                                len(word_array) * constants.WORD_SIZE_BITS))
        sys.exit(1)

    if not fld_size > 0:
        print(("Invalid argument! fld_size: {0}"
               " should non-zero positive number").format(fld_size))
        sys.exit(1)

    out_idx = 0
    rem_size = fld_size

    # compute the last word of the output buffer because big endian
    out_idx = (fld_size - 1) / constants.WORD_SIZE_BITS
    logger.debug("first output word: {0}".format(out_idx))

    fld_size_words = (fld_size + (constants.WORD_SIZE_BITS - 1)) / constants.WORD_SIZE_BITS
    fld_word_array = [0x0] * fld_size_words

    # count up bits from fld_pos
    while rem_size > 0:
        # clear the output word
        if not (out_idx >= 0):
            sys.exit(1)
        fld_word_array[out_idx] = 0

        # find the input word for the lowest significant bit
        if not ((reg_padded_size - fld_pos - fld_size + rem_size) > 0):
            sys.exit(1)
        in_idx = (reg_padded_size - fld_pos - fld_size + rem_size - 1) / constants.WORD_SIZE_BITS

        # calculate the base bit position in this word
        in_pos = fld_pos % constants.WORD_SIZE_BITS

        # trim the size for this input word
        in_size = rem_size
        read_upper = False
        if (in_size + in_pos > constants.WORD_SIZE_BITS):
            in_size = constants.WORD_SIZE_BITS - in_pos
            read_upper = True

        # calculate a mask
        if (in_size == constants.WORD_SIZE_BITS):
            mask = constants.MAX_WORD_VALUE
        else:
            mask = (0x1 << in_size) - 1

        logger.debug("in_idx: {0}".format(in_idx))
        logger.debug("mask: {0}".format(hex(mask)))
        logger.debug("fld_size: {0} -> {1}".format(fld_size, in_size))

        # copy in the first part of the word
        fld_word_array[out_idx] |= (word_array[in_idx] >> in_pos) & mask

        # determine if we need to read part of the next word
        if (read_upper):
            # need to read the remaining bits in this input word
            if (constants.WORD_SIZE_BITS < rem_size):
                in_size_hi = constants.WORD_SIZE_BITS - in_size
            else:
                in_size_hi = rem_size - in_size
            if not (in_size_hi < constants.WORD_SIZE_BITS): # can't be constants.WORD_SIZE_BITS, would be read above
                sys.exit(1)
            # construct the mask
            mask = (0x1 << in_size_hi) - 1

            # or in the value
            if not ((in_idx - 1) >= 0):
                sys.exit(1)
            fld_word_array[out_idx] |= (word_array[in_idx-1] & mask) << in_size
        else:
            in_size_hi = 0

        logger.debug(("rem_size: {0}, in_size: {1}, in_size_hi: {2}").format(rem_size,
                in_size, in_size_hi, (rem_size -  in_size + in_size_hi)))

        # next output word
        out_idx -= 1
        rem_size -= in_size + in_size_hi
    return fld_word_array

def csr_set_field(fld_pos, fld_size, csr_word_array, fld_word_array):
    constants.WORD_SIZE_BITS = 64
    reg_padded_size = len(csr_word_array) * constants.WORD_SIZE_BITS

    if not (reg_padded_size >= fld_size + fld_pos):
        print(("Invalid arguments! fld_pos: {0} + fld_size: {1} exceeds"
               "csr word array length: {2}").format(fld_pos, fld_size,
                len(csr_word_array) * constants.WORD_SIZE_BITS))
        sys.exit(1)

    if not fld_size > 0:
        print(("Invalid argument! fld_size: {0}"
               " should non-zero positive number").format(fld_size))
        sys.exit(1)

    rem_size = fld_size
    in_idx = (fld_size - 1) / constants.WORD_SIZE_BITS
    while (rem_size > 0):
        # find the LSB word on the output register
        if not ((reg_padded_size - fld_pos - fld_size + rem_size) > 0):
            sys.exit(1)
        out_idx = (reg_padded_size - fld_pos - fld_size + rem_size - 1) / constants.WORD_SIZE_BITS

        # calculate the base bit position in this word
        out_pos = fld_pos % constants.WORD_SIZE_BITS

        # trim the size for this input word
        out_size = rem_size
        write_upper = False
        if (out_size + out_pos > constants.WORD_SIZE_BITS):
            out_size = constants.WORD_SIZE_BITS - out_pos
            write_upper = True

        # calculate a mask
        if (out_size == constants.WORD_SIZE_BITS):
            mask = constants.MAX_WORD_VALUE
        else:
            mask = (0x1 << out_size) - 1

        logger.debug("out_idx: {0}, in_idx: {1}".format(out_idx, in_idx))
        logger.debug("mask: {0}".format(mask))
        logger.debug("fld_size: {0} -> {1}".format(fld_size, out_size))

        # copy in the first part of the word, masking out the rest
        csr_word_array[out_idx] &= ~(mask << out_pos)
        csr_word_array[out_idx] |= (fld_word_array[in_idx] & mask) << out_pos

        # determine if we need to read part of the next word
        if (write_upper):
            # need to read the remaining bits in this input word
            if (constants.WORD_SIZE_BITS < rem_size):
                out_size_hi = constants.WORD_SIZE_BITS - out_size
            else:
                out_size_hi = rem_size - out_size
            if not (out_size_hi < constants.WORD_SIZE_BITS): # can't be constants.WORD_SIZE_BITS, would be read above
                sys.exit(1)

            # construct the mask
            mask = (0x1 << out_size_hi) - 1

            # or in the value
            if not (out_idx > 0):
                sys.exit(1)
            csr_word_array[out_idx-1] &= ~mask
            csr_word_array[out_idx-1] |= (fld_word_array[in_idx] >> out_size) & mask
        else:
            out_size_hi = 0

        logger.debug(("rem_size: {0}, in_size: {1}, in_size_hi: {2} = {3}").format(
               rem_size, out_size, out_size_hi, rem_size -  out_size + out_size_hi))

        # next output word
        in_idx -= 1
        rem_size -= out_size + out_size_hi

    return csr_word_array

def csr_get_valid_field_list(csr_data):
    field_list_obj = csr_data.get("fld_lst", None)
    field_list = dict()
    for f in field_list_obj:
        fld_name = f.get('fld_name', None)
        #if fld_name is not '__rsvd' or fld_name is not None:
        if fld_name is not None:
            field_list[fld_name] = f
    return field_list

def csr_get_field_val(csr_data, word_array, field_name):
    if len(word_array) != (csr_get_width_bytes(csr_data) >> 3):
        print("csr_width: {0} word_array length: {1}".format(
            csr_get_width_bytes(csr_data), len(word_array)))
        print("Invalid arguments! word array length should match csr width!")
        return None

    if field_name is None:
        print("Invalid arguments! Empty field name")
        return None

    logger.debug("csr raw: {0}".format(hex_word_dump(word_array)))
    fields_objs = csr_data.get("fld_lst", None)
    for f in fields_objs:
        name = f.get('fld_name', None)
        if name  != field_name:
            continue
        fld_width = f.get('fld_width', None)
        fld_offset = f.get('fld_offset', None)
        field_word_array = csr_get_field(fld_offset, fld_width, word_array)
        if not field_word_array:
            print("Error! Failed to extract field:{0}".format(field_name))
            return None
        logger.debug("\t{0}: {1}".format(field_name, hex_word_dump(field_word_array)))
        return field_word_array
    print("Invalid arguments! field name:{} not valid".format(field_name))
    return None

def csr_show(csr_data, word_array, field_list=None):
    if len(word_array) != (csr_get_width_bytes(csr_data) >> 3):
        print("csr_width: {0} word_array length: {1}".format(
            csr_get_width_bytes(csr_data), len(word_array)))
        print("Invalid arguments! word array length should match csr width!")
        return

    if field_list is not None:
        field_list = list(set(field_list))

    print("csr raw: {0}".format(hex_word_dump(word_array)))
    fields_objs = csr_data.get("fld_lst", None)
    for f in fields_objs:
        fld_name = f.get('fld_name', None)
        if field_list is not None and fld_name not in field_list:
            continue
        fld_width = f.get('fld_width', None)
        fld_offset = f.get('fld_offset', None)
        field_word_array = csr_get_field(fld_offset, fld_width, word_array)
        if not field_word_array:
            print("Error! Failed to extract field:{0}".format(fld_name))
            return
        print("\t{0}: {1}".format(fld_name, hex_word_dump(field_word_array)))
        if field_list:
            field_list.remove(fld_name)
    if field_list:
        field_list_valid = csr_get_valid_field_list(csr_data).keys()
        print(("Skipped invalid fields:"
              " {0}\nvalid fields: {1}").format(field_list, field_list_valid))

# prints as array of hex integers
def hex_word_dump(word_array):
    hex_word_array = '['
    for w in word_array:
        hex_word_array += ' 0x{:016x}'.format(w)
    hex_word_array =  hex_word_array
    hex_word_array += ' ]'
    return hex_word_array

# Treat string digit as decimal and string prefixed with "0x" as hex
# and convert it as an integer
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

# Returns json pretty string
def json_obj_pretty(json_obj):
    return json.dumps(json_obj, indent=4)

# Returns all list of csrs from csr metadata
def get_csr_list():
    return csr_metadata().get_csr_list()

# Returns abosolute path for a file
def get_file_abs_path(loc):
    if not os.path.isabs(loc):
        loc = os.path.join(os.getcwd(), loc)
    assert os.path.exists(loc), "{}: directory does not exist!".format(loc)
    return loc

def csr_metadata_objs(csr_name, ring_name=None, ring_inst=None):
    csr_list = csr_metadata().get_csr_def(csr_name, rn_class=ring_name, rn_inst=ring_inst)
    if csr_list is None:
        print("csr: {} doesnot exist in database!.".format(csr_name))
        return
    return csr_list

def csr_get_metadata(csr_name, ring_name=None, ring_inst=None, anode_name=None, anode_path=None):
    if not csr_name:
        print("csr name is empty! Provide valid csr name!")
        return

    csr_list = csr_metadata().get_csr_def(csr_name)
    if csr_list is None:
        print("csr: {} doesnot exist in database!.".format(csr_name))
        return

    rings = dict()
    logger.debug("Preparing ring list")
    for csr in csr_list:
        rname = csr.get("ring_name", None)
        if rings.get(rname, None) is None:
            rings[rname] = list()
        if csr.get("ring_inst", None) not in rings[rname]:
            rings[rname].append(csr.get("ring_inst", None))
        logger.debug("ring name:{} inst:{}".format(rname, csr.get("ring_inst", None)))

    if len(rings) == 0:
        print("Inconsistant csr metadata parsing!")
        return

    logger.debug("rings: {}".format(rings))
    if len(rings) > 0:
        logger.debug("csr_name: {} ring_name: {}".format(csr_name, ring_name))
        if len(rings) > 1 and ring_name is None:
            print("csr objs:\n{}\n".format(json_obj_pretty(csr_list)))
            print(("csr: {} exists in multiple rings."
                   " Give appropriate ring option! valid rings: {}").format(csr_name, rings))
            return
        if ring_name and ring_name not in rings:
            print("csr objs:\n{}\n".format(json_obj_pretty(csr_list)))
            print(("Invalid ring:{} for csr: {}."
                   " Give appropriate ring option! valid rings: {}").format(ring_name,
                                                                            csr_name, rings))
            return

        csr_list = csr_metadata().get_csr_def(csr_name = csr_name, rn_class=ring_name)
        if ring_name is None:
            ring_name = rings.keys()[0]
        ring_inst_list = rings.get(ring_name, None)

        if ring_inst_list is None:
            print(("Inconsistant csr metadata parsing. ring_name: {}"
                    " There should be atleast one ring inst!").format(ring_name))
            return

        logger.debug("ring: {} instace list: {}".format(ring_name, ring_inst_list))
        if len(ring_inst_list) > 0:
            if len(ring_inst_list) > 1 and ring_inst is None:
                print("csr objs:\n{}\n".format(json_obj_pretty(csr_list)))
                print(("csr: {} exists in multiple instances of ring: {}."
                       "\nGive appropriate ring option! valid rings instances:"
                       "{}").format(csr_name, ring_name, ring_inst_list))
                return
            logger.debug("ring name: {}  inst: {}".format(ring_name, ring_inst))
            if ring_inst is not None and ring_inst not in ring_inst_list:
                print("csr objs:\n{}\n".format(json_obj_pretty(csr_list)))
                print(("Invalid ring instance for csr: {} ring: {}."
                      "\nGive appropriate ring details! valid rings instances:"
                       "{}").format(csr_name, ring_name, ring_inst_list))
                return

    anodes = dict()
    csr_list = csr_metadata().get_csr_def(csr_name = csr_name,
                                rn_class=ring_name, rn_inst=ring_inst)
    logger.debug("Preparing anode list")
    for csr in csr_list:
        if ring_name == csr.get("ring_name", None):
            an_name = csr.get("an", None)
            logger.debug(an_name)
            an_path = csr.get("an_path", None)
            an_inst_cnt = csr.get("an_inst_cnt", None)
            if an_path is None or an_inst_cnt is None:
                print(("Invalid csr metadata! csr: {}"
                        " an_path:{} an_inst_cnt:{}").format(csr_name,
                            an_path, an_inst_cnt))
                return
            anode_path_inst = anodes.get(an_name, None)
            if anode_path_inst is None:
                anode_path_inst = dict()
                anodes[an_name] = anode_path_inst
            anode_path_inst[an_path] = an_inst_cnt
    logger.debug("anodes: {}".format(anodes))
    if len(anodes) == 0:
        print("Inconsistant csr metadata parsing."
                " There should be atleast one an_node inst!")
        return

    anodes_list = None
    if len(anodes) > 1:
        if anode_name is None:
            print("csr objs:\n{}\n".format(json_obj_pretty(csr_list)))
            print(("csr: {} exists in multiple anodes."
                  "\nGive appropriate anode option! valid anodes: {}").format(csr_name, anodes))
            return
        if anode_name not in anodes:
            print("csr objs:\n{}\n".format(json_obj_pretty(csr_list)))
            print(("Invalid anode:{} for csr: {}."
                   "\nGive appropriate anode option! valid anodes: {}").format(anode_name,
                                                                csr_name, anodes))
            return
        anodes_list = anodes.get(anode_name, None)
    else:
        anode_names = anodes.keys()
        if len(anode_names) != 1:
            print(("Inconsistant csr metadata parsing. anode_names: {}"
                    " There should be one anode name!").format(anode_names))
            return
        anode_name = anode_names[0]
        anodes_list = anodes.get(anode_name, None)
    if len(anodes_list) == 0:
        print("Inconsistant csr metadata parsing."
              " There should be atleast one an_inst!")
        return

    csr_list = csr_metadata().get_csr_def(csr_name = csr_name,
            rn_class=ring_name, rn_inst=ring_inst,
            an=anode_name)

    if len(anodes_list) > 1:
        if anode_path is None:
            print("csr objs:\n{}\n".format(json_obj_pretty(csr_list)))
            print(("csr: {} exists in multiple an_paths."
                   " Give appropriate an_path option!"
                   " valid an_paths: {}").format(csr_name, anodes_list))
            return

    anode_paths = anodes_list.keys()
    if not len(anode_paths) > 0:
        print("Inconsistant csr metadata parsing."
                " There should be atleast one an_path!")
        return

    if anode_path is not None:
        if anode_path not in anode_paths:
            print(("Invalid anode_path:{} for csr: {}."
                "\nGive appropriate anod path option!"
                " valid anode paths: {}").format(anode_path,
                    csr_name, anode_paths))
            return

    csr_list = csr_metadata().get_csr_def(csr_name = csr_name,
            rn_class=ring_name, rn_inst=ring_inst,
            an=anode_name, an_path=anode_path)

    if len(csr_list) != 1:
        print("csr objs:\n{}\n".format(json.dumps(csr_list, indent=4)))
        print("more than one csr instance! Inconsistant csr metadata parsing!")
        return

    csr = csr_list[0]
    logger.debug("Found CSR: \n{}\n".format(json.dumps(csr, indent=4)))

    return csr

def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

@singleton
class dbgprobe(DBG_Client):
    def __init__(self):
        DBG_Client.__init__(self)

# Create single instance of csr metadata
@singleton
class csr_metadata:
    def __init__(self):
        status = self.load_metadata_from_dochub()
        if not status:
             print('Failed to load csr metadata!')
             sys.exit(1)

    def _load_metadata_file(self, metadata_file):
        if not os.path.exists(metadata_file):
            print "Failed to find matadata file: {}".format(metadata_file)
            return False
        print("Loading csr metadata: {0}".format(metadata_file))
        self.metadata = json.load(open(metadata_file))
        return True

    def download_metadata_from_dochub(self):
        metadata_file = None
        try:
            metadata_file = csr_metadata_dochub()
        except Exception as e:
            logging.error(traceback.format_exc())
            print('Failed to get csr metadata from dochub!'
                  'Make sure that "dochub.fungible.local" accessable.')
            return None
        if not os.path.exists(metadata_file):
            print "Failed to find matadata file: {} after download!".format(metadata_file)
            return None
        return metadata_file

    def load_metadata_from_dochub(self):
        metadata_file = self.download_metadata_from_dochub()
        if not metadata_file:
             print('Failed to download csr metadata!')
             return False
        if not os.path.exists(metadata_file):
            print "Failed to find matadata file: {} after download!".format(metadata_file)
            return None
        status = self._load_metadata_file(metadata_file)
        tmp_dir_path =  os.path.join('/', *(metadata_file.split(os.path.sep)[:3]))
        if tmp_dir_path.startswith("/tmp/"):
            shutil.rmtree(tmp_dir_path)
        else:
            logger.error('Invalid temp dir path: {}'.format(tmp_dir_path))
        if not status:
            return False
        return True

    def load_metadata_from_sdk(self, sdk_root):
        metadata_file = os.path.join(sdk_root, constants.CSR_CFG_DIR,
                constants.CSR_METADATA_FILE)
        if not os.path.exists(metadata_file):
            print "Failed to find matadata file: {}".format(metadata_file)
            return None
        status = self._load_metadata_file(metadata_file)
        if not status:
            print "Failed to load matadata file: {}".format(metadata_file)
            return False
        return True

    def get_metadata(self):
        return self.metadata

    def csr_equal(self, x, rn_class, rn_inst, an_path, an):
        if rn_class:
            if x["ring_name"] != rn_class:
                return False
        if rn_inst is not None:
            if x["ring_inst"] != rn_inst:
                return False
        if an:
            if x["an"] != an:
                return False
        if an_path:
            if x["an_path"] != an_path:
                return False

        return True

    def get_csr_def(self, csr_name, rn_class=None, rn_inst=None,
                    an_path=None, an=None):
        csr_defs_lst = self.metadata.get(csr_name, [])
        if not csr_defs_lst:
            return None
        else:
            csr_defs_lst = [x for x in csr_defs_lst        \
                            if self.csr_equal(x, rn_class, \
                            rn_inst, an_path, an)]
        logger.debug(("csr_name: {}, rn_class: {}, rn_inst: {}"
                " an_path: {}, an: {}").format(csr_name, rn_class,
                rn_inst, an_path, an))
        return csr_defs_lst

    def get_csr_list(self):
        return list(self.metadata.keys())

    def csr_inst_verify(self, csr_name):
        csr_list = self.get_csr_def(csr_name=csr_name)

