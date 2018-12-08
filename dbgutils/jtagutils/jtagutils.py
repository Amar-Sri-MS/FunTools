#!/usr/bin/env python

import sys, os
from imgtec.console.support import command
from imgtec.console import *
import logging

logger = logging.getLogger('jtagutils')
logger.setLevel(logging.INFO)

class constants(object):
    CSR_RING_TAP_SELECT = 0x01C1
    CSR_RING_TAP_SELECT_WIDTH = 10

# Connects to Codescape jtag probe and enables csr tap select
@command()
def csr_probe(dev_type, ip_addr):
    '''Connects to Codescape jtag probe and enables csr tap select'''
    status = probe(dev_type, ip_addr)
    status = str(status)
    if (("SysProbe" not in status) or ("Firmware" not in status) or
        ("ECONNREFUSED" in status) or ("InvalidArgError" in status)):
        return (False, status)
    logger.info('Connected to Codescape Jtag probe!\n{0}'.format(status))
    cmd = '%u 0x%04x'%(constants.CSR_RING_TAP_SELECT_WIDTH,
                     constants.CSR_RING_TAP_SELECT)
    logger.debug('tap select cmd: \"{}\"'.format(cmd))
    status = tapi(cmd)
    logger.debug('tap select status: {}'.format(status))
    status = status[0]
    if (status != 0x201):
        # Not sure what does each bit in status = 0x21 indicate.
        status_msg = (('Failed select csr tap controller! Error:' +
                ' {}').format(hex(status)))
        logger.error(status_msg)
        return (False, status_msg)
    status_msg = 'jtag is connected and csr tap select is enabled!'
    logger.info(status_msg)
    return (True, status_msg)

@command()
def disconnect():
   '''Disconnect Codescape jtag debugger'''
   pass

# jtag csr read
@command()
def csr_peek(csr_addr, csr_width):
    '''Peek csr_width number of 64-bit words from csr_addr'''
    logger.info(('csr peek csr_addr:{0}'
           ' csr_width:{1}').format(hex(csr_addr), csr_width))

    if csr_width == 0 or csr_width > 8:
        logger.error(('Invalid number csr width:'
                     ' {}\n').format(csr_width) +
                     'Csr width(64-bit words) should be in the range 1-8!')
        return None

    logger.debug("\nWriting read cmd...........:")
    ring_sel = csr_addr >> 35
    cmd = ((csr_addr & 0xffffffffff) |
                ((0x2 << 60) |
                ((csr_width & 0x3F) << 54) |
                (ring_sel << 49)))

    dr = '128 ' + '0x' + '%016x'%((0x3 << 60) | (1 << 54)) + '%016x'%(cmd)
    logger.debug('dr: {}'.format(dr))
    status = tapd(dr)
    logger.debug('peek tapd status: {}'.format(status))
    read_resp = status[0] >> 124
    read_status = (status[0] >> 96) & 0xFF
    jtag_ack = (status[0] >> 64) & 0x1
    jtag_running = (status[0] >> 65) & 0x1

    logger.debug("read response: {}".format(read_resp))
    logger.debug("read status: {}".format(read_status))
    logger.debug("jtag ack: {}".format(jtag_ack))
    logger.debug("jtag running: {}".format(jtag_running))
    if read_status != 0:
        logger.error("jtag csr peek cmd write status error!: {}".format(read_status))
        return None

    logger.debug('peek shifting cmd first time')
    dr = "128 0x0"
    status = tapd(dr)
    logger.debug('peek cmd shift tapd status: {}'.format(status))
    read_resp = status[0] >> 124
    read_status = (status[0] >> 96) & 0xFF
    jtag_ack = (status[0] >> 64) & 0x1
    jtag_running = (status[0] >> 65) & 0x1
    logger.debug('peek tapd status: {}'.format(status))
    data = status[0] & 0xFFFFFFFFFFFFFFFF

    logger.debug("read response: {}".format(read_resp))
    logger.debug("read status: {}".format(read_status))
    logger.debug("jtag ack: {}".format(jtag_ack))
    logger.debug("jtag running: {}".format(jtag_running))
    logger.debug("Data: {}".format(hex(data)))
    if jtag_ack != 1:
        logger.error("jtag csr peek cmd write ack error!: {}".format(jtag_ack))
        return None

    word_array = list()
    for i in range(csr_width):
        logger.debug("\nReading Data[{}/{}]...........:".format(i+1,
                    csr_width))
        csr_data_addr = (i+1) * 8
        ring_sel = csr_data_addr >> 35
        cmd = ((csr_data_addr & 0xffffffffff) |
            ((0x2 << 60) | (0x1 << 54) |
             (ring_sel << 49)))

        cmd_str = hex(cmd)[2:].zfill(16)
        dr = '128 ' + '0x' + cmd_str + '0'*16
        logger.debug('dr: {}'.format(dr))
        status = tapd(dr)
        logger.debug('peek tapd status: {}'.format(status))
        read_resp = status[0] >> 124
        read_status = (status[0] >> 96) & 0xFF
        jtag_ack = (status[0] >> 64) & 0x1
        jtag_running = (status[0] >> 65) & 0x1
        logger.debug('peek tapd status: {}'.format(status))
        data = status[0] & 0xFFFFFFFFFFFFFFFF

        logger.debug("read response: {}".format(read_resp))
        logger.debug("read status: {}".format(read_status))
        logger.debug("jtag ack: {}".format(jtag_ack))
        logger.debug("jtag running: {}".format(jtag_running))
        logger.debug("Data: {}".format(hex(data)))
        if read_status != 0:
            logger.error("jtag csr peek data read status error!: {}".format(read_status))
            return None

        logger.debug('peek shifting data-first time')
        dr = "128 0x0"
        status = tapd(dr)
        logger.debug('peek zero shift tapd status: {}'.format(status))
        read_resp = status[0] >> 124
        read_status = (status[0] >> 96) & 0xFF
        jtag_ack = (status[0] >> 64) & 0x1
        jtag_running = (status[0] >> 65) & 0x1
        logger.debug('peek tapd status: {}'.format(status))
        data = status[0] & 0xFFFFFFFFFFFFFFFF

        logger.debug("read response: {}".format(read_resp))
        logger.debug("read status: {}".format(read_status))
        logger.debug("jtag ack: {}".format(jtag_ack))
        logger.debug("jtag running: {}".format(jtag_running))
        logger.debug("Data: {}".format(hex(data)))
        if jtag_ack != 1:
            logger.error("jtag csr peek data read ack error!: {}".format(jtag_ack))
            return None

        word_array.append(data)

    logger.debug('Peeked word_array: {0}'.format([hex(x) for x in word_array]))
    return word_array


# csr write
@command()
def csr_poke( csr_addr, csr_width, word_array):
    '''Poke csr_width number of 64-bit words from word_array at csr_addr'''
    logger.info(('csr poke addr:{0}'
                 ' csr_width:{1} words:{2}').format(hex(csr_addr),
                   csr_width, [hex(x) for x in word_array]))

    if csr_width == 0 or csr_width > 8:
        logger.error(('Invalid number csr width:'
                     ' {}\n').format(csr_width) +
                     'Csr width(64-bit words) should be in the range 1-8!')
        return False

    if csr_width != len(word_array):
        logger.error(('Insufficient data! Expected: {0}'
               ' data length: {0}').format(csr_width, len(word_array)))
        return False

    for i in range(csr_width):
        logger.debug("\nWriting Data[{}/{} = {}]...........:".format(i+1,
                       csr_width, hex(word_array[i])))
        csr_data_addr = (i+1) * 8
        ring_sel = csr_data_addr >> 35
        cmd = ((csr_data_addr & 0xffffffffff) |
            ((0x3 << 60) | (0x1 << 54) |
             (ring_sel << 49)))

        cmd_str = hex(cmd)[2:].zfill(16)
        dr = '128 ' + '0x' + cmd_str + "%016x"%word_array[i]
        logger.debug('dr: {}'.format(dr))
        status = tapd(dr)
        logger.debug('poke data tapd status: {}'.format(status))
        write_resp = status[0] >> 124
        write_status = (status[0] >> 96) & 0xFF
        jtag_ack = (status[0] >> 64) & 0x1
        jtag_running = (status[0] >> 65) & 0x1
        data = status[0] & 0xFFFFFFFFFFFFFFFF

        logger.debug("write response: {}".format(write_resp))
        logger.debug("write status: {}".format(write_status))
        logger.debug("jtag ack: {}".format(jtag_ack))
        logger.debug("jtag running: {}".format(jtag_running))
        logger.debug("Data: {}".format(hex(data)))
        if write_status != 0:
            logger.error("jtag csr poke cmd write status error!: {}".format(write_status))
            return None

        logger.debug('poke shifting data-first time')
        dr = "128 0x0"
        status = tapd(dr)
        logger.debug('poke zero shift tapd status: {}'.format(status))
        write_resp = status[0] >> 124
        write_status = (status[0] >> 96) & 0xFF
        jtag_ack = (status[0] >> 64) & 0x1
        jtag_running = (status[0] >> 65) & 0x1
        data = status[0] & 0xFFFFFFFFFFFFFFFF

        logger.debug("write response: {}".format(write_resp))
        logger.debug("write status: {}".format(write_status))
        logger.debug("jtag ack: {}".format(jtag_ack))
        logger.debug("jtag running: {}".format(jtag_running))
        logger.debug("Data: {}".format(hex(data)))
        if jtag_ack != 1:
            logger.error("jtag csr poke data write ack error!: {}".format(jtag_ack))
            return None

    logger.debug("\nWriting write command....")
    ring_sel = csr_addr >> 35
    cmd = ((csr_addr & 0xffffffffff) |
                ((0x3 << 60) |
                ((csr_width & 0x3F) << 54) |
                (ring_sel << 49)))

    dr = '128 ' + '0x' + '%016x'%((0x3 << 60) | (1 << 54)) + '%016x'%(cmd)
    logger.debug('dr: {}'.format(dr))
    status = tapd(dr)
    logger.debug('peek tapd status: {}'.format(status))
    write_resp = status[0] >> 124
    write_status = (status[0] >> 96) & 0xFF
    jtag_ack = (status[0] >> 64) & 0x1
    jtag_running = (status[0] >> 65) & 0x1

    logger.debug("write response: {}".format(write_resp))
    logger.debug("write status: {}".format(write_status))
    logger.debug("jtag ack: {}".format(jtag_ack))
    logger.debug("jtag running: {}".format(jtag_running))
    if write_status != 0:
        logger.error("jtag csr poke cmd write status error!: {}".format(write_status))
        return None

    logger.debug('poke shifting cmd first time')
    dr = "128 0x0"
    status = tapd(dr)
    logger.debug('poke tapd status: {}'.format(status))
    write_resp = status[0] >> 124
    write_status = (status[0] >> 96) & 0xFF
    jtag_ack = (status[0] >> 64) & 0x1
    jtag_running = (status[0] >> 65) & 0x1
    data = status[0] & 0xFFFFFFFFFFFFFFFF

    logger.debug("write response: {}".format(write_resp))
    logger.debug("write status: {}".format(write_status))
    logger.debug("jtag ack: {}".format(jtag_ack))
    logger.debug("jtag running: {}".format(jtag_running))
    logger.debug("Data: {}".format(hex(data)))
    if jtag_ack != 1:
        logger.error("jtag csr poke cmd write ack error!: {}".format(jtag_ack))
        return None

    return True

def csr_peek_poke_test():
    csr_probe('sp55e', '10.1.23.132')
    print('\n************POKE***************')
    print csr_poke(0x4883160000, 6, [0x1111111111111111, 0x2222222222222222,
                                     0x3333333333333333, 0x4444444444444444,
                                     0x5555555555555555, 0x6666666666666666,
                                    ])
    print csr_poke(0xb000000078, 1, [0xabcdabcdabcdabcd])
    print csr_poke(0xb800000078, 1, [0xdeadbeefdeadbeef])

    print('\n************PEEK***************')
    word_array = csr_peek(0xb000000078, 1)
    print("{}".format([hex(x) for x in word_array] if word_array else None))
    word_array = csr_peek(0xb800000078, 1)
    print("{}".format([hex(x) for x in word_array] if word_array else None))
    word_array = csr_peek(0x4883160000, 6)
    print("{}".format([hex(x) for x in word_array] if word_array else None))

if __name__== "__main__":
    csr_peek_poke_test()
