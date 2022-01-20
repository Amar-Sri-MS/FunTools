#!/usr/bin/env python2.7

"""
HBM read/write/copy utilities

Usage from python shell:
-----------------------
>>> from dbgmacros.hbmutils import *
>>> connect('TPOD28', 'i2c')
>>> connect('FS2-F1_1', 'pcie')
>>> hbm_dump(0x4000, 0x100)

Usage as a standalone script:
----------------------------
python hbmutils.py --dut FS1_1 --mode pcie  copy --start 0x100000 --size 0x100000 --file /tmp/t.txt
python hbmutils.py --dut FS1_1 --mode pcie  write --start 0x100100 --data 0x11 0x22 0x33 0x44 0x1234567812345678 0x6 0x77 0x88
python hbmutils.py --dut FS1_1 --mode pcie  dump  --start 0x100000 --size 0x200
"""

from csrutils.csrutils import *

logger = logging.getLogger("hbmutils")
logger.setLevel(logging.ERROR)

def hbm_read(start_addr, num_bytes, chip_inst=None):
    if (num_bytes & 0xFF != 0):
       logger.error('num_bytes should be multiples of 256')
       return None

    if (start_addr & 0xFF != 0):
       logger.error('start_addr should be 256 byte aligned')
       return None
    cache_line_addr = start_addr >> 6;
    csr_replay_data = list()
    # Round of to 256 byte boundary
    # Number of 64-byte words to read
    if (num_bytes & 0xff):
        logger.info('Rounded-off num_bytes:{0} to {1}'.format(
            num_bytes, (num_bytes+255) & ~0xff))
    num_reads_256bytes = (num_bytes + 255) >> 8
    num_64bit_words = num_reads_256bytes * 32
    num_reads = num_reads_256bytes * 4
    logger.info('num_reads_256bytes: {0}'
            ' num_reads: {1} num_words:{2}'.format(
            num_reads_256bytes, num_reads, num_64bit_words))

    read_data_words = [None] * num_64bit_words
    cnt = 0
    while (cnt < num_reads):
        skip_addr = 0
        if(cnt & 0x2):
            skip_addr = constants.MUH_RING_SKIP_ADDR
        if (cnt & 0x1):
            skip_addr += constants.MUH_SNA_ANODE_SKIP_ADDR
        csr_addr = constants.MEM_RW_CMD_CSR_ADDR
        csr_addr += skip_addr
        muh_sna_cmd_addr = (cache_line_addr/4) + (cnt/4)
        csr_val = muh_sna_cmd_addr << 37;
        csr_val |= 0x1 << 63; #READ
        logger.debug('csr_val: {0}'.format(csr_val))
        (status, data) = dbgprobe().csr_poke(chip_inst=chip_inst,
                                             csr_addr=csr_addr,
                                             word_array=[csr_val])
        if status is True:
            logger.debug("Poke:{0} addr: {1} Success!".format(cnt, hex(muh_sna_cmd_addr)))
        else:
            error_msg = data
            logger.error("CSR Poke failed! Addr: {0} Error: {1}".format(hex(csr_addr), error_msg))
            return None

        csr_addr = constants.MEM_RW_STATUS_CSR_ADDR
        csr_addr += skip_addr
        (status, data) = dbgprobe().csr_peek(chip_inst=chip_inst,
                                             csr_addr=csr_addr,
                                             csr_width_words = 1)
        if status is True:
            word_array = data
            if word_array is None or not word_array:
                logger.error("Failed get cmd status! Error in csr peek!!!")
                return None
            cmd_status_done = word_array[0]
            cmd_status_done = cmd_status_done >> 63
            if cmd_status_done != 1:
                logger.error("Failed cmd status != Done!")
                return None
            else:
                logger.debug('Data ready!')
        else:
            error_msg = data
            logger.error('Error! {0}!'.format(error_msg))
            return None

        for i in range(8):
            csr_addr = constants.MEM_RW_DATA_CSR_ADDR + skip_addr
            csr_addr += i * 8
            (status, data) = dbgprobe().csr_peek(chip_inst = chip_inst,
                                                 csr_addr = csr_addr,
                                                 csr_width_words =1)
            if status is True:
                logger.debug('peek word:{0} success!!!'.format(i))
                logger.debug('Read value:{0}'.format(data))
                read_data_words[(cnt * 8) + i] = data[0]
            else:
                error_msg = data
                logger.error("Error! {0}!".format(error_msg))

        cnt += 1

    if (cnt == num_reads):
        logger.info('Succesfully read {0} words! starting from {1}'.format(
                                                num_reads * 8, hex(start_addr)))

        for i in range(num_64bit_words):
            logger.debug('Address: {0}  Data: 0x{1}'.format(
                hex(start_addr+(i*8)), hex(read_data_words[i])[2:].zfill(16)));

        byte_array = list()
        for i in range(num_64bit_words):
            byte_array.extend([ord(c) for c in struct.pack('>Q', read_data_words[i])])
        logger.debug(byte_array)
        return byte_array
    else:
        logger.error('Read un-successful')
        return None

def write_hbm(start_addr, data_words, chip_inst=None):
    if (start_addr & 0x3F != 0):
       logger.error('start_addr should be 64 byte aligned for cache line alignment')
       return False
    if len(data_words) != 8:
        logger.error('Number of words should be 8 to match one cache line length')
        return False

    cache_line_addr = start_addr >> 6;
    skip_addr = 0
    if(cache_line_addr & 0x2):
        skip_addr = constants.MUH_RING_SKIP_ADDR
    if (cache_line_addr & 0x1):
        skip_addr += constants.MUH_SNA_ANODE_SKIP_ADDR
    csr_addr = constants.MEM_RW_CMD_CSR_ADDR
    csr_addr += skip_addr
    for i in range(8):
        csr_val = data_words[i]
        csr_addr = constants.MEM_RW_DATA_CSR_ADDR + skip_addr
        csr_addr += i * 8
        (status, data) = dbgprobe().csr_fast_poke(csr_addr, [csr_val])
        if status is True:
            logger.info('Write value:{0}'.format(hex(csr_val)))
            logger.debug("poke success!!!")
        else:
            error_msg = data
            logger.error("Error! {0}!".format(error_msg))
            return False

    csr_addr = constants.MEM_RW_CMD_CSR_ADDR
    csr_addr += skip_addr
    muh_sna_cmd_addr = cache_line_addr/4
    csr_val = muh_sna_cmd_addr << 37;
    csr_val |= 0x0 << 63;
    logger.debug('csr_val: {0}'.format(csr_val))
    (status, data) = dbgprobe().csr_fast_poke(csr_addr, [csr_val])
    if status is True:
        logger.info("Poke:addr: {0} Success!".format(hex(muh_sna_cmd_addr)))
    else:
        error_msg = data
        logger.error("CSR Poke failed! Addr: {0} Error: {1}".format(hex(csr_addr), error_msg))
        return False
    csr_addr = constants.MEM_RW_STATUS_CSR_ADDR
    csr_addr += skip_addr
    (status, data) = dbgprobe().csr_peek(csr_addr, 1)
    if status is True:
        word_array = data
        if word_array is None or not word_array:
            logger.error("Failed get cmd status! Error in csr peek!!!")
            return False
        cmd_status_done = word_array[0]
        cmd_status_done = cmd_status_done >> 63
        if cmd_status_done != 1:
            logger.error("Failed cmd status != Done!")
            return False
        else:
            logger.info('Data ready!')
    else:
        error_msg = data
        logger.error('Error! {0}!'.format(error_msg))
        return False

    logger.info('Succesfully wrote cache line!')
    return True

def hbm_copy(start_addr, size, file_path, chip_inst=None):
        #start_offset and end_offset are within 256 byte arrays
        start_offset = start_addr & 0xff
        end_offset = (start_offset + size) & 0xFF
        end_offset = end_offset if end_offset else 256;

        start_addr = start_addr & ~0xff
        read_size = (size + start_offset + 255) & ~0xff
        read_offset = 0
        logger.info(('start_addr: {0} start_offset:{1} end_offset: {2} size:{3}'
                     ' read_size:{4}').format(start_addr, start_offset,
                                        end_offset, size, read_size))

        if os.path.exists(file_path):
            os.remove(file_path)

        f = open(file_path, 'w+b')
        while read_offset < read_size:
            data = hbm_read(start_addr+read_offset, 256, chip_inst)
            if not data:
                logger.error("Failed to read hbm!")
                return
            if (read_offset < 256):
                if read_size <= 256:
                    byte_array = bytearray(data[start_offset:end_offset])
                else:
                    byte_array = bytearray(data[start_offset:256])
            elif ((read_offset+256) >= read_size):
                byte_array = bytearray(data[0:end_offset])
            else:
                    byte_array = bytearray(data)
            f.write(byte_array)
            read_offset += 256
        f.close()

        #with open(file_path, 'rb') as f:
        #    for chunk in iter(lambda: f.read(16), b''):
        #        print chunk.encode('hex')
        #f.close()

def hbm_dump(start_addr, size, file_path, chip_inst=None):
        #start_offset and end_offset are within 256 byte arrays
        start_addr = start_addr & ~0xff
        size = (size + 255) & ~0xff
        read_offset = 0
        logger.info(('Alliged start_addr: {0} size:{1}').format(start_addr, size))

        while read_offset < size:
            data = hbm_read(start_addr+read_offset, 256, chip_inst)
            if not data:
                logger.error("Failed to read hbm!")
                return

            for i in range(256/8):
                byte_array = array('B', data[(i*8):(i*8)+8])
                word = int(binascii.hexlify(byte_array), 16)
                print('Address: {0} Data: {1}'.format(
                    hex(start_addr+read_offset+(i*8)),
                    hex(word)[2:].zfill(16)))
            read_offset += 256

def _hbm_dump(args):
    start_address = args.start_address[0]
    size = args.size[0]
    chip_inst = args.chip
    logger.info('start address: {0} size: {1}'.format(hex(start_address), hex(size)))
    hbm_dump(start_address, size, chip_inst)

def _hbm_write(args):
    start_address = args.start_address[0]
    word_array = args.data
    chip_inst = args.chip
    logger.info('start address: {0} data: {1}'.format(hex(start_address),
                                            [hex(x) for x in word_array]))
    status = write_hbm(start_address, word_array, chip_inst)
    if status:
        print('**** Poke successful! start address: {0} **** '.format(hex(start_address)))
    else:
        print('***Poke Failed***! start address: {0}'.format(hex(start_address)))


def _hbm_copy(args):
    start_address = args.start_address[0]
    size = args.size[0]
    file_path = args.file[0]
    chip_inst = args.chip

    if not os.path.isdir(os.path.dirname(file_path)):
        logger.error('Invalid directory: {}'.format(os.path.dirname(file_path)))
        return

    logger.info('start address: {0} size: {1} file:{2}'.format(
                hex(start_address), hex(size), file_path))
    hbm_copy(start_address, size, file_path, chip_inst)

def main():
    parser = argparse.ArgumentParser(
        description="HBM memory read/write utilities")

    parser.add_argument("--dut", required=True, type=str, help="Dut name")
    parser.add_argument("--mode", required=True, type=str, help="Dut name")
    parser.add_argument("--chip", type=int, choices=range(0, 2), help="chip instance")

    subparsers = parser.add_subparsers(help='hbm sub-command help')
    parser_dump = subparsers.add_parser('dump', help='dump help')
    parser_dump.add_argument('--start', required=True, nargs=1, metavar=('start_address'),
                           dest='start_address', type=lambda x: int(x,0),
                           help="start address in decimal or hex")
    parser_dump.add_argument('--size', required=True, nargs=1, metavar=('size'),
                           dest='size', type=lambda x: int(x,0),
                           help="size in decimal or hex(should be muliples of 256).")
    parser_dump.set_defaults(func=_hbm_dump)

    parser_write = subparsers.add_parser('write', help='write help')
    parser_write.add_argument('--start', required=True, nargs=1, metavar=('start_address'),
                           dest='start_address', type=lambda x: int(x,0), help=("start address in decimal or hex"
                           "(should be mulitples of 64 for cache-line alignment)"))
    parser_write.add_argument('--data', required=True, nargs=8,
                metavar=('data'), dest='data', type=lambda x: int(x,0),
                        help="8 words of 64-bit data in big-endian(i.e.whole cache line)")
    parser_write.set_defaults(func=_hbm_write)

    parser_copy = subparsers.add_parser('copy', help='copy help')
    parser_copy.add_argument('--start', required=True, nargs=1, metavar=('start_address'),
                           dest='start_address', type=lambda x: int(x,0), help=("start address in decimal or hex"))
    parser_copy.add_argument('--size', required=True, nargs=1, metavar=('size'),
                           dest='size', type=lambda x: int(x,0),
                           help="size in decimal or hex.")
    parser_copy.add_argument('--file', required=True, nargs=1, type=str,
                        help="Relative or absolute path to hbm memory dump file")
    parser_copy.set_defaults(func=_hbm_copy)

    args = parser.parse_args()

    probe = connect(dut_name=args.dut, mode=args.mode, force_connect=True)
    if not probe:
        logger.error('Failed to connect to dut:{0}'.format(args.dut))
        return

    args.func(args)

    probe.disconnect()

if __name__== "__main__":
    main()
