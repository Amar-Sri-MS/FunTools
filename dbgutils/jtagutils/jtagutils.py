#!/usr/bin/env python

import sys, os
sys.path.append('/home/'+os.environ["USER"]+'/.local/opt/imgtec/Codescape-8.6/lib/python2.7/lib-dynload')
sys.path.append('/home/'+os.environ["USER"]+'/.local/opt/imgtec/Codescape-8.6/lib/python2.7/site-packages')
sys.path.append('/home/'+os.environ["USER"]+'/.local/opt/imgtec/Codescape-8.6/lib/python2.7/site-packages/sitepackages.zip')

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
    status = probe(dev_type, ip_addr, force_disconnect=True, verbose=True)
    status = str(status)
    if (("SysProbe" not in status) or ("Firmware" not in status) or
        ("ECONNREFUSED" in status) or ("InvalidArgError" in status)):
        return (False, status)
    logger.info('Connected to Codescape Jtag probe!\n{0}'.format(status))
    cmd = '%u 0x%04x'%(constants.CSR_RING_TAP_SELECT_WIDTH,
                     constants.CSR_RING_TAP_SELECT)
    logger.debug('tap select cmd: \"{}\"'.format(cmd))
    status = tapi(cmd)
    logger.info('tap select status: {}'.format(status))

    status = status[0]
    if not status:
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
   # TODO(@nponugoti): If needed, write default tap select
   # Right now, there is no default tap select to write
   pass

# prepares csr access command bytes
def _prepare_csr_acc_cmd(read, csr_addr, csr_width):
    assert(read != None)
    assert(csr_addr != None)
    ring_sel = csr_addr >> 35
    cmd = ((csr_addr & 0xffffffffff) |
            (((0x2 if read is True else 0x3) << 60) |
            ((csr_width & 0x3F) << 54) |
            (ring_sel << 49)))

    return cmd

# Shifts-in data into csr tap controller dr
# Returns status and response data
def _jtag_shift_in_csr_acc_bytes(bytes_hex_str):
    length = len(bytes_hex_str)
    assert(length == (32 + 2)) #32 nibbles + length('0x')
    dr = '128 ' + bytes_hex_str
    status = tapd(dr)
    jtag_resp = status[0] >> 124
    jtag_status = (status[0] >> 96) & 0xFF
    jtag_ack = (status[0] >> 64) & 0x1
    jtag_running = (status[0] >> 65) & 0x1
    logger.debug('shift-in data: {} status: {}'.format(dr, status))

    logger.debug("jtag response: {}".format(jtag_resp))
    logger.debug("jtag status: {}".format(jtag_status))
    logger.debug("jtag ack: {}".format(jtag_ack))
    logger.debug("jtag running: {}".format(jtag_running))
    if jtag_status != 0:
        logger.error("jtag shift-in data error!: {}".format(jtag_status))
        return (False, None)

    logger.debug('shift-in zeros for respose data')
    dr = "128 0x0"
    status = tapd(dr)
    jtag_resp = status[0] >> 124
    jtag_status = (status[0] >> 96) & 0xFF
    jtag_ack = (status[0] >> 64) & 0x1
    jtag_running = (status[0] >> 65) & 0x1
    data = status[0] & 0xFFFFFFFFFFFFFFFF
    logger.debug('response data: {}'.format(status))

    logger.debug("jtag response: {}".format(jtag_resp))
    logger.debug("jtag status: {}".format(jtag_status))
    logger.debug("jtag ack: {}".format(jtag_ack))
    logger.debug("jtag running: {}".format(jtag_running))
    logger.debug("Data: {}".format(hex(data)))
    if jtag_ack != 1:
        logger.error("jtag cmd shift-in ack error!: {} bytes: {}".format(
            jtag_ack, bytes_hex_str))
        return (False, None)

    return (True, data)

# jtag csr read
@command()
def csr_peek(csr_addr, csr_width):
    '''Peek csr_width number of 64-bit words from csr_addr'''
    logger.info(('csr peek csr_addr:{0}'
           ' csr_width:{1}').format(hex(csr_addr), csr_width))

    if csr_width == 0 or csr_width > 8:
        logger.error(('Invalid csr width:'
                     ' {}\n').format(csr_width) +
                     'Csr width(64-bit words) should be in the range 1-8!')
        return None

    logger.debug("\nWriting read cmd...........:")
    cmd = _prepare_csr_acc_cmd(True, csr_addr, csr_width)
    dr_byte_str = '0x' + '%016x'%((0x3 << 60) | (1 << 54)) + '%016x'%(cmd)
    (status, data) = _jtag_shift_in_csr_acc_bytes(dr_byte_str)
    if not status:
        logger.error('peek csr cmd failed!')
        return None

    word_array = list()
    for i in range(csr_width):
        logger.debug("\nReading Data[{}/{}]...........:".format(i+1,
                    csr_width))
        csr_data_addr = (i+1) * 8
        cmd = _prepare_csr_acc_cmd(True, csr_data_addr, 1)
        cmd_str = hex(cmd)[2:].zfill(16)
        dr_byte_str = '0x' + cmd_str + '0'*16
        logger.debug('dr: {}'.format(dr_byte_str))
        (status, data) = _jtag_shift_in_csr_acc_bytes(dr_byte_str)

        if not status:
            logger.error('peek: csr data read failed!')
            return None
        word_array.append(data)
    logger.debug('Peeked word_array: {0}'.format([hex(x) for x in word_array]))
    return word_array

# csr write
@command()
def csr_poke( csr_addr, word_array):
    '''Poke word_array(an array of 64-bit words) at csr_addr'''
    logger.info(('csr poke addr:{0}'
                 ' words:{1}').format(hex(csr_addr),
                   [hex(x) for x in word_array]))

    if csr_addr is None or word_array is None:
        logger.error(('Invalid csr poke arguments! csr_addr: {0} word_array:'
                     '{1}').format(csr_addr, word_array))
        return False
    csr_width = len(word_array)
    if csr_width == 0 or csr_width > 8:
        logger.error(('Invalid data width:'
                     ' {}\n').format(csr_width) +
                     'Data size(in 64-bit words) should be in the range 1-8!')
        return False

    for i in range(csr_width):
        logger.debug("\nWriting Data[{}/{} = {}]...........:".format(i+1,
                       csr_width, hex(word_array[i])))
        csr_data_addr = (i+1) * 8
        cmd = _prepare_csr_acc_cmd(False, csr_data_addr, 1)
        cmd_str = hex(cmd)[2:].zfill(16)
        dr_byte_str = '0x' + cmd_str + "%016x"%word_array[i]
        logger.debug('dr: {}'.format(dr_byte_str))
        (status, data) = _jtag_shift_in_csr_acc_bytes(dr_byte_str)
        if not status:
            logger.error("jtag csr poke data write failed!")
            return None

    logger.debug("\nWriting write command....")
    cmd = _prepare_csr_acc_cmd(False, csr_addr, len(word_array))
    dr_byte_str = '0x' + '%016x'%((0x3 << 60) | (1 << 54)) + '%016x'%(cmd)
    logger.debug('dr: {}'.format(dr_byte_str))
    (status, data) = _jtag_shift_in_csr_acc_bytes(dr_byte_str)
    if not status:
        logger.error('peek csr cmd failed!')

    return True

def csr_peek_poke_test():
    csr_probe('sp55e', '10.1.23.132')
    print('\n************POKE***************')
    print csr_poke(0x4883160000, [0x1111111111111111, 0x2222222222222222,
                                     0x3333333333333333, 0x4444444444444444,
                                     0x5555555555555555, 0x6666666666666666,
                                    ])
    print csr_poke(0xb000000078, [0xabcdabcdabcdabcd])
    print csr_poke(0xb800000078, [0xdeadbeefdeadbeef])

    print('\n************PEEK***************')
    word_array = csr_peek(0xb000000078, 1)
    print("{}".format([hex(x) for x in word_array] if word_array else None))
    word_array = csr_peek(0xb800000078, 1)
    print("{}".format([hex(x) for x in word_array] if word_array else None))
    word_array = csr_peek(0x4883160000, 6)
    print("{}".format([hex(x) for x in word_array] if word_array else None))

if __name__== "__main__":
    csr_peek_poke_test()
