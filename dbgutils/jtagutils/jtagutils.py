#!/usr/bin/env python

import sys, os
from imgtec.console.support import command
from imgtec.lib.namedenum import namedenum
from imgtec.lib.namedbitfield import namedbitfield
from imgtec.console import *
from imgtec.console import CoreFamily
from array import array
import binascii
import time
import logging
import traceback

logger = logging.getLogger('jtagutils')
logger.setLevel(logging.INFO)

class constants(object):
    CSR_RING_TAP_SELECT = 0x01C1
    CSR_RING_TAP_SELECT_WIDTH = 10

# Connects Codescape jtag debugger
# Returns the device handle
@command()
def connect(dev_type, ip_addr):
    '''Connect to Codescape jtag probe'''
    status = probe(dev_type, ip_addr)
    status = str(status)
    logger.info('jtag is connected!\n{0}'.format(status))
    if (("SysProbe" not in status) or ("Firmware" not in status) or
        ("ECONNREFUSED" in status) or ("InvalidArgError" in status)):
        return (False, status)
    cmd = '%u 0x%04x'%(constants.CSR_RING_TAP_SELECT_WIDTH,
                     constants.CSR_RING_TAP_SELECT)
    logger.info('tap select cmd: \"{}\"'.format(cmd))
    status = tapi(cmd)
    logger.info('tap select status: {}'.format(status))
    status = status[0]
    if (status != 0x201):
        # Not sure what does each bit in status = 0x21 indicate.
        status_msg = (('Failed select csr tap controller! Error:' +
                ' {}').format(hex(status)))
        logger.error(status_msg)
        return (False, status_msg)
    return (True, "Jtag is connected")

@command()
def disconnect():
   '''Disconnect Codescape jtag debugger'''
   pass

# jtag csr read
@command()
def csr_peek(csr_addr, csr_width):
    '''Peek csr_width number of 64-bit words from csr_addr'''
    '''Example: csr_peek(0x4883160000, 6)'''
    logger.info(('csr peek csr_addr:{0}'
           ' csr_width:{1}').format(hex(csr_addr), csr_width))

    if csr_width == 0 or csr_width > 8:
        logger.error(('Invalid number csr width:'
                     ' {}\n').format(csr_width) +
                     'Csr width(64-bit words) should be in the range 1-8!')
        return None

    logger.info("\nWriting read cmd...........:")
    ring_sel = csr_addr >> 35
    cmd = ((csr_addr & 0xffffffffff) |
                ((0x2 << 60) |
                ((csr_width & 0x3F) << 54) |
                (ring_sel << 49)))

    dr = '128 ' + '0x' + '%016x'%((0x3 << 60) | (1 << 54)) + '%016x'%(cmd)
    logger.info('dr: {}'.format(dr))
    status = tapd(dr)
    logger.info('peek tapd status: {}'.format(status))
    read_resp = status[0] >> 124
    read_status = (status[0] >> 96) & 0xFF
    jtag_ack = (status[0] >> 64) & 0x1
    jtag_running = (status[0] >> 65) & 0x1

    logger.info("read response: {}".format(read_resp))
    logger.info("read status: {}".format(read_status))
    logger.info("jtag ack: {}".format(jtag_ack))
    logger.info("jtag running: {}".format(jtag_running))
    if read_status != 0:
        logger.error("jtag csr peek cmd write status error!: {}".format(read_status))
        return None

    logger.info('peek shifting cmd first time')
    dr = "128 0x0"
    status = tapd(dr)
    logger.info('peek cmd shift tapd status: {}'.format(status))
    read_resp = status[0] >> 124
    read_status = (status[0] >> 96) & 0xFF
    jtag_ack = (status[0] >> 64) & 0x1
    jtag_running = (status[0] >> 65) & 0x1
    logger.info('peek tapd status: {}'.format(status))
    data = status[0] & 0xFFFFFFFFFFFFFFFF

    logger.info("read response: {}".format(read_resp))
    logger.info("read status: {}".format(read_status))
    logger.info("jtag ack: {}".format(jtag_ack))
    logger.info("jtag running: {}".format(jtag_running))
    logger.info("Data: {}".format(hex(data)))
    if jtag_ack != 1:
        logger.error("jtag csr peek cmd write ack error!: {}".format(jtag_ack))
        return None

    word_array = list()
    for i in range(csr_width):
        logger.info("\nReading Data[{}/{}]...........:".format(i+1,
                    csr_width))
        csr_data_addr = (i+1) * 8
        ring_sel = csr_data_addr >> 35
        cmd = ((csr_data_addr & 0xffffffffff) |
            ((0x2 << 60) | (0x1 << 54) |
             (ring_sel << 49)))

        cmd_str = hex(cmd)[2:].zfill(16)
        dr = '128 ' + '0x' + cmd_str + '0'*16
        logger.info('dr: {}'.format(dr))
        status = tapd(dr)
        logger.info('peek tapd status: {}'.format(status))
        read_resp = status[0] >> 124
        read_status = (status[0] >> 96) & 0xFF
        jtag_ack = (status[0] >> 64) & 0x1
        jtag_running = (status[0] >> 65) & 0x1
        logger.info('peek tapd status: {}'.format(status))
        data = status[0] & 0xFFFFFFFFFFFFFFFF

        logger.info("read response: {}".format(read_resp))
        logger.info("read status: {}".format(read_status))
        logger.info("jtag ack: {}".format(jtag_ack))
        logger.info("jtag running: {}".format(jtag_running))
        logger.info("Data: {}".format(hex(data)))
        if read_status != 0:
            logger.error("jtag csr peek data read status error!: {}".format(read_status))
            return None

        logger.info('peek shifting data-first time')
        dr = "128 0x0"
        status = tapd(dr)
        logger.info('peek zero shift tapd status: {}'.format(status))
        read_resp = status[0] >> 124
        read_status = (status[0] >> 96) & 0xFF
        jtag_ack = (status[0] >> 64) & 0x1
        jtag_running = (status[0] >> 65) & 0x1
        logger.info('peek tapd status: {}'.format(status))
        data = status[0] & 0xFFFFFFFFFFFFFFFF

        logger.info("read response: {}".format(read_resp))
        logger.info("read status: {}".format(read_status))
        logger.info("jtag ack: {}".format(jtag_ack))
        logger.info("jtag running: {}".format(jtag_running))
        logger.info("Data: {}".format(hex(data)))
        if jtag_ack != 1:
            logger.error("jtag csr peek data read ack error!: {}".format(jtag_ack))
            return None

        word_array.append(data)

    logger.info('Peeked word_array: {0}'.format([hex(x) for x in word_array]))
    return word_array


# csr write
@command()
def csr_poke( csr_addr, csr_width, word_array):
    '''Poke csr_width number of 64-bit words from word_array at csr_addr'''
    """
    Example: csr_poke(0x4883160000, 6, [0x1111111111111111,
            0x2222222222222222, 0x333333333333333333, 0x4444444444444444,
            0x55555555555555, 0x6666666666666666])'''
    """
    logger.info(('csr poke addr:{0}'
                 ' csr_width:{1} words:{2}').format(hex(csr_addr),
                        csr_width,
                        [hex(x) for x in word_array]))

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
        logger.info("\nWriting Data[{}/{} = {}]...........:".format(i+1,
                       csr_width, hex(word_array[i])))
        csr_data_addr = (i+1) * 8
        ring_sel = csr_data_addr >> 35
        cmd = ((csr_data_addr & 0xffffffffff) |
            ((0x3 << 60) | (0x1 << 54) |
             (ring_sel << 49)))

        cmd_str = hex(cmd)[2:].zfill(16)
        dr = '128 ' + '0x' + cmd_str + "%016x"%word_array[i]
        logger.info('dr: {}'.format(dr))
        status = tapd(dr)
        logger.info('poke data tapd status: {}'.format(status))
        write_resp = status[0] >> 124
        write_status = (status[0] >> 96) & 0xFF
        jtag_ack = (status[0] >> 64) & 0x1
        jtag_running = (status[0] >> 65) & 0x1
        data = status[0] & 0xFFFFFFFFFFFFFFFF

        logger.info("write response: {}".format(write_resp))
        logger.info("write status: {}".format(write_status))
        logger.info("jtag ack: {}".format(jtag_ack))
        logger.info("jtag running: {}".format(jtag_running))
        logger.info("Data: {}".format(hex(data)))
        if write_status != 0:
            logger.error("jtag csr poke cmd write status error!: {}".format(write_status))
            return None

        logger.info('poke shifting data-first time')
        dr = "128 0x0"
        status = tapd(dr)
        logger.info('poke zero shift tapd status: {}'.format(status))
        write_resp = status[0] >> 124
        write_status = (status[0] >> 96) & 0xFF
        jtag_ack = (status[0] >> 64) & 0x1
        jtag_running = (status[0] >> 65) & 0x1
        data = status[0] & 0xFFFFFFFFFFFFFFFF

        logger.info("write response: {}".format(write_resp))
        logger.info("write status: {}".format(write_status))
        logger.info("jtag ack: {}".format(jtag_ack))
        logger.info("jtag running: {}".format(jtag_running))
        logger.info("Data: {}".format(hex(data)))
        if jtag_ack != 1:
            logger.error("jtag csr poke data write ack error!: {}".format(jtag_ack))
            return None

    logger.info("\nWriting write command....")
    ring_sel = csr_addr >> 35
    cmd = ((csr_addr & 0xffffffffff) |
                ((0x3 << 60) |
                ((csr_width & 0x3F) << 54) |
                (ring_sel << 49)))

    dr = '128 ' + '0x' + '%016x'%((0x3 << 60) | (1 << 54)) + '%016x'%(cmd)
    logger.info('dr: {}'.format(dr))
    status = tapd(dr)
    logger.info('peek tapd status: {}'.format(status))
    write_resp = status[0] >> 124
    write_status = (status[0] >> 96) & 0xFF
    jtag_ack = (status[0] >> 64) & 0x1
    jtag_running = (status[0] >> 65) & 0x1

    logger.info("write response: {}".format(write_resp))
    logger.info("write status: {}".format(write_status))
    logger.info("jtag ack: {}".format(jtag_ack))
    logger.info("jtag running: {}".format(jtag_running))
    if write_status != 0:
        logger.error("jtag csr poke cmd write status error!: {}".format(write_status))
        return None

    logger.info('poke shifting cmd first time')
    dr = "128 0x0"
    status = tapd(dr)
    logger.info('poke tapd status: {}'.format(status))
    write_resp = status[0] >> 124
    write_status = (status[0] >> 96) & 0xFF
    jtag_ack = (status[0] >> 64) & 0x1
    jtag_running = (status[0] >> 65) & 0x1
    data = status[0] & 0xFFFFFFFFFFFFFFFF

    logger.info("write response: {}".format(write_resp))
    logger.info("write status: {}".format(write_status))
    logger.info("jtag ack: {}".format(jtag_ack))
    logger.info("jtag running: {}".format(jtag_running))
    logger.info("Data: {}".format(hex(data)))
    if jtag_ack != 1:
        logger.error("jtag csr poke cmd write ack error!: {}".format(jtag_ack))
        return None

    return True

if __name__== "__main__":
    connect('sp55e', '10.1.23.132')
    logger.info('\n\n\n************POKE***************')
    csr_poke(0x4883160000, 6, [0x1111, 0x2222, 0x3333, 0x4444, 0x5555, 0x6666])
    csr_poke(0xb000000078, 1, [0xabcdabcdabcdabcd])
    csr_poke(0xb800000078, 1, [0xdeadbeefdeadbeef])

    logger.info('\n\n\n************PEEK***************')
    csr_peek(0xb000000078, 1)
    csr_peek(0xb800000078, 1)
    csr_peek(0x4883160000, 6)
