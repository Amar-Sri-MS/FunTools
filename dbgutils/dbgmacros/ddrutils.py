#!/usr/bin/env python2.7

"""
DDR read/write/copy utilities

Usage:
------
python ddrutils.py --dut TPOD0 --mode jtag  dump  --start 0x100000 --size 0x200
python ddrutils.py --dut TPOD0 --mode jtag  write --start 0x100100 --data 0x11 0x22 0x33 0x44 0x1234567812345678 0x6 0x77 0x88
python ddrutils.py --dut TPOD0 --mode i2c  dump  --start 0x100000 --size 0x200
python ddrutils.py --dut TPOD0 --mode i2c  write --start 0x100100 --data 0x11 0x22 0x33 0x44 0x1234567812345678 0x6 0x77 0x88
"""

from csrutils.csrutils import *
import time

logger = logging.getLogger("ddrutils")
logger.setLevel(logging.INFO)

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
            time.sleep(1)
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

    def dump(self, start_addr, size):
            #start_offset and end_offset are within 256 byte arrays
            start_addr = start_addr & ~0xff
            size = (size + 255) & ~0xff
            read_offset = 0
            logger.info(('Alliged start_addr: {0} size:{1}').format(start_addr, size))

            while read_offset < size:
                data = self.read_bulk(start_addr+read_offset, 256)
                if not data:
                    logger.error("Failed to read ddr!")
                    return

                for i in range(256/8):
                    byte_array = array('B', data[(i*8):(i*8)+8])
                    word = int(binascii.hexlify(byte_array), 16)
                    print('Address: {0} Data: {1}'.format(
                        hex(start_addr+read_offset+(i*8)),
                        hex(word)[2:].zfill(16)))
                read_offset += 256

    def read_bulk(self, start_addr, num_bytes):
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
            data = self.read(start_addr+(64 * cnt))
            if not data:
                break;
            for i in range(8):
                read_data_words[(cnt * 8) + i] = data[i]

            cnt += 1

        if (cnt == num_reads):
            logger.info('Succesfully read {0} words! starting from {1}'.format(
                                                    num_reads * 8, hex(start_addr)))

            for i in range(num_64bit_words):
                logger.debug('Address: {0}  Data: 0x{1}'.format(
                    hex(start_addr+(i*8)), hex(read_data_words[i])));

            byte_array = list()
            for i in range(num_64bit_words):
                byte_array.extend([ord(c) for c in struct.pack('>Q', read_data_words[i])])
            logger.debug(byte_array)
            return byte_array
        else:
            logger.error('Read un-successful at addr: {0}'.format(start_addr+(64 * cnt)))
            return None

    def read(self, phys_addr):
        res = self._issue_read_command(phys_addr)
	if res:
	    res = self._check_success(phys_addr)
	if res:
	    (res, data) = self._read_data(phys_addr)
        self._clear_status_reg(phys_addr)
	if res:
	    return data

        return None

    def _read_data(self, phys_addr):
	sna_addr = self._get_sna_addr(phys_addr)
	read_data_words = [None] * 8

        for i in range(8):
            csr_addr = sna_addr + self.DATA_REG_OFFSET + (i * 8)
	    (status, ret_data) = self.probe.csr_peek(
		    csr_addr = csr_addr, csr_width_words = 1)
            if status:
                logger.debug('Read data value: {0}'.format(ret_data[0]))
		read_data_words[i] = ret_data[0]
            else:
                error_msg = ret_data
                logger.error('Error writing data value: {0}'.format(error_msg))
                return (False, None)

        return (True, read_data_words)

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
            logger.debug('Wrote address: {0} as {1}'.format(hex(phys_addr), hex(ddr_addr)))
        else:
            error_msg = data
            logger.error('Error writing address: {0}'.format(hex(csr_addr), error_msg))
            return False

        return True

    def _issue_read_command(self, phys_addr):
        sna_addr = self._get_sna_addr(phys_addr)

        csr_addr = sna_addr + self.CMD_REG_OFFSET

        # The addresses are divided across the MUDs, so we divide the
        # physical address by the number of MUDs to get the DDR shard address.
        ddr_addr = phys_addr // len(self.sna_addrs)

        # Divide by 2, which is the number of channels per MUD
        channel = ddr_addr & 1
        ddr_addr = ddr_addr // 2

        mud = (phys_addr & self.line_width) >> self.log2_line_width
        logger.debug('phys_addr: {} mud:{} channel:{}'.format(hex(phys_addr), mud, channel))

        # And then we divide again to turn bytes into words
        ddr_addr = ddr_addr // self.line_width

        # Within each MUD, a hash function sets bit 28 on the shard address to
        # determine which channel is used. This is simply bit 7 of the physical
        # address or equivalently, bit 0 of the shard address before we divide
        # by the number of channels (bit notation is 0-indexed).
        qsn_bit = (phys_addr >> 7) & 0x1
        ddr_addr = ddr_addr | (qsn_bit << 28)

        csr_val = ddr_addr | (0x1 << 30)   # set bit 30 to 1 for read request
        (status, data) = self.probe.csr_fast_poke(csr_addr, [csr_val])
        if status:
            logger.debug('Wrote address: {0} as {1}'.format(hex(phys_addr), hex(ddr_addr)))
        else:
            error_msg = data
            logger.error('Error writing read commnd'
                    ' for phy_addr: {0} csr_addr:{1} error:{2}'.format(
                        hex(phys_addr), hex(csr_addr), error_msg))
            return False

        return True


    def _check_success(self, phys_addr):
        sna_addr = self._get_sna_addr(phys_addr)

        csr_addr = sna_addr + self.STATUS_REG_OFFSET
        (status, data) = self.probe.csr_peek(csr_addr=csr_addr,
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
def _ddr_dump(args):
    start_address = args.start_address[0]
    size = args.size[0]
    logger.info('start address: {0} size: {1}'.format(hex(start_address), hex(size)))
    ddr = DDR(dbgprobe())
    ddr.dump(start_address, size)

def _ddr_write(args):
    start_address = args.start_address[0]
    word_array = args.data
    logger.info('start address: {0} data: {1}'.format(hex(start_address),
                                            [hex(x) for x in word_array]))
    ddr = DDR(dbgprobe())
    status = ddr.write(start_address, word_array)
    if status:
        print('**** Poke successful! start address: {0} **** '.format(hex(start_address)))
    else:
        print('***Poke Failed***! start address: {0}'.format(hex(start_address)))

def main():
    parser = argparse.ArgumentParser(
        description="DDR memory read/write utilities")

    parser.add_argument("--dut", required=True, type=str, help="Dut name")
    parser.add_argument("--mode", required=True, type=str, help="Dut name")

    subparsers = parser.add_subparsers(help='ddr sub-command help')
    parser_dump = subparsers.add_parser('dump', help='dump help')
    parser_dump.add_argument('--start', required=True, nargs=1, metavar=('start_address'),
                           dest='start_address', type=lambda x: int(x,0),
                           help="start address in decimal or hex")
    parser_dump.add_argument('--size', required=True, nargs=1, metavar=('size'),
                           dest='size', type=lambda x: int(x,0),
                           help="size in decimal or hex(should be muliples of 256).")
    parser_dump.set_defaults(func=_ddr_dump)

    parser_write = subparsers.add_parser('write', help='write help')
    parser_write.add_argument('--start', required=True, nargs=1, metavar=('start_address'),
                           dest='start_address', type=lambda x: int(x,0), help=("start address in decimal or hex"
                           "(should be mulitples of 64 for cache-line alignment)"))
    parser_write.add_argument('--data', required=True, nargs=8,
                metavar=('data'), dest='data', type=lambda x: int(x,0),
                        help="8 words of 64-bit data in big-endian(i.e.whole cache line)")
    parser_write.set_defaults(func=_ddr_write)

    args = parser.parse_args()

    probe = connect(dut_name=args.dut, mode=args.mode, force_connect=True)
    if not probe:
        logger.error('Failed to connect to dut:{0}'.format(args.dut))
        return

    args.func(args)

    probe.disconnect()

if __name__== "__main__":
    main()
