#!/usr/bin/env python3

# This file defines the base JTAG methods to initialize, read and write data to and from
# JTAG transport.
# The user interface of options will be driver by another utility.

# This actively used the code-scape8.6 python libraries.
# Hence the CodeScape-8.6 need to be installed on the probe server.
# This libraries, utilities and methods are imported via PYTHONPATH


import sys, os
# importing PYTHONPATH essential from installed area
sys.path.append('/home/'+os.environ["USER"]+'/.local/opt/imgtec/Codescape-8.6/lib/python2.7/lib-dynload')
sys.path.append('/home/'+os.environ["USER"]+'/.local/opt/imgtec/Codescape-8.6/lib/python2.7/site-packages')
sys.path.append('/home/'+os.environ["USER"]+'/.local/opt/imgtec/Codescape-8.6/lib/python2.7/site-packages/sitepackages.zip')

from imgtec.console.support import command
from imgtec.console import *
import logging
import time

logger = logging.getLogger('jtagcsr')
logger.setLevel(logging.DEBUG)

class constants(object):
    CSR_RING_TAP_SELECT = 0x01C1
    CSR_RING_TAP_SELECT_WIDTH = 10
    SBP_CMD_EXE_TIME_WAIT = 4
    SBP_CMD_EXE_ROM_TIME_WAIT = 6
    GLOBAL_EMULATION_ROM_MODE = False

def _ir_shiftin(width, data):
    cmd = '%u 0x%04x'%(width, data)
    logger.debug('re-initialize the TAP with cmd: \"{}\"'.format(cmd))
    status = tapi(cmd)
    logger.debug('tapi: shift-out status: {}'.format(status))
    status = status[0]
    if not status:
        logger.error('Failed to shiftin ir!')
        return False
    return True

def csr_probe_init():
    status = _ir_shiftin(constants.CSR_RING_TAP_SELECT_WIDTH, constants.CSR_RING_TAP_SELECT)
    if not status:
        status_msg = (('Failed select csr tap controller! Error:{}').format(hex(status)))
        logger.error(status_msg)
        return (False, status_msg)

    logger.info('Connected to Codescape Jtag probe! status={0}'.format(status))
    status_msg = 'jtag is connected and csr tap select is enabled!'
    logger.info(status_msg)
    return (True, status_msg)

# Connects to Codescape jtag probe and enables csr tap select
@command()
def local_csr_probe(dev_type, ip_addr, in_rom=None, flag=None):
    '''Connects to Codescape jtag probe and enables csr tap select'''
    logger.debug('Connect JTAG CSR ip={} with force_disconnect={} ...'.format(ip_addr, flag))
    status = probe(dev_type, ip_addr, force_disconnect=flag, verbose=True)
    status = str(status)
    if (("SysProbe" not in status) or ("Firmware" not in status) or
        ("ECONNREFUSED" in status) or ("InvalidArgError" in status)):
        return (False, status)
    JTAG_TCKRATE = 5000 if in_rom else 5000
    status = tckrate(JTAG_TCKRATE)
    logger.info('Set tckrate to {0}! status: {1}'.format(JTAG_TCKRATE, status))
    logger.info('local_csr_probe: calling csr_probe_init ...')
    return csr_probe_init()

    ### changed because it same as csr_probe_init()
    #status = _ir_shiftin(constants.CSR_RING_TAP_SELECT_WIDTH, constants.CSR_RING_TAP_SELECT)
    #if not status:
    #    status_msg = (('Failed select csr tap controller! Error:{}').format(hex(status)))
    #    logger.error(status_msg)
    #    return (False, status_msg)

    #logger.info('Connected to Codescape Jtag probe! status={0}'.format(status))
    #status_msg = 'jtag is connected and csr tap select is enabled!'
    #logger.info(status_msg)
    #return (True, status_msg)

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
    cmd =  ((0x2 if read is True else 0x3) << 44) | ((csr_width & 0x3F)<< 38) | (csr_addr & 0xffffffff)

    logger.info("_prepare_csr_acc_cmd:cmd=%016x" % cmd)
    return cmd

def _prepare_csr_ctrl(read, csr_addr, csr_width):
        assert read is not None
        assert csr_addr is not None

        val = (((csr_width & 0x3F) << 36) |
               ((0x2 if read is True else 0x3) << 32) |
               (csr_addr & 0xffffffff))
        logger.info("_prepare_csr_ctrl:crtl=%016x" % val)
        return val

def _decode_status(status):
        jtag_resp = (status[0] >> 96) & 0xFFFF
        jtag_status = (status[0] >> 124) & 0xF
        jtag_ack = (status[0] >> 64) & 0x1
        jtag_running = (status[0] >> 65) & 0x1
        return jtag_ack, jtag_resp, jtag_running, jtag_status

# Shifts-in data into csr tap controller dr
# Returns status and response data
def _jtag_shift_in_csr_acc_bytes(bytes_hex_str):
    length = len(bytes_hex_str)
    assert(length == (32 + 2)) #32 nibbles + length('0x')
    logger.debug("_jtag_shift_in_csr_acc_bytes hex: {} length={}".format(bytes_hex_str, hex(length)))
    dr = '128 ' + bytes_hex_str
    logger.debug('tapd: shift-in data: {}'.format(dr))
    status = tapd(dr)
    jtag_ack, jtag_resp, jtag_running, jtag_status = _decode_status(status)
    logger.debug('tapd: shift-out data: {} status: {}'.format(dr, status))
    logger.debug("tapd response: 0x{:0x}".format(jtag_resp))
    logger.debug("tapd status: {}".format(jtag_status))
    logger.debug("tapd ack: {}".format(jtag_ack))
    logger.debug("tapd running: {}".format(jtag_running))
    data = status[0] & 0xFFFFFFFFFFFFFFFF
    logger.debug('tapd data: 0x{:0x}'.format(data))
    if jtag_status != 0:
        logger.error("jtag shift-in data error!: {}".format(jtag_status))
        return (False, None)

    status = _ir_shiftin(constants.CSR_RING_TAP_SELECT_WIDTH, constants.CSR_RING_TAP_SELECT)
    if not status:
        logger.error("Failed in shiftin IR\n")
        return (False, None)

    # Enable if needed in emulation
    sleepfor = constants.SBP_CMD_EXE_ROM_TIME_WAIT if constants.GLOBAL_EMULATION_ROM_MODE else constants.SBP_CMD_EXE_TIME_WAIT
    logger.debug('Sleep (%ss) for ir_shiftin ... hw (esp. emulation) to process the command!' % sleepfor)
    time.sleep(sleepfor)

    logger.debug('shift-in zeros for response data')
    dr = "128 0x0"
    status = tapd(dr)
    jtag_ack, jtag_resp, jtag_running, jtag_status = _decode_status(status)

    data = status[0] & 0xFFFFFFFFFFFFFFFF
    logger.debug('response data: {}'.format(status))
    #logger.debug('response data: 0x{0:0{1}x}'.format(status[0], 32))
    logger.debug("jtag response: 0x{:0x}".format(jtag_resp))
    logger.debug("jtag status: {}".format(jtag_status))
    logger.debug("jtag ack: {}".format(jtag_ack))
    logger.debug("jtag running: {}".format(jtag_running))
    logger.debug("Data: {}".format(hex(data)))

    if jtag_ack != 1:
        logger.error("jtag cmd shift-in ack error!: {} bytes: {}".format(
            jtag_ack, bytes_hex_str))
        return (False, None)

    status = _ir_shiftin(constants.CSR_RING_TAP_SELECT_WIDTH,
                constants.CSR_RING_TAP_SELECT)

    if not status:
        logger.error("Failed in shiftin IR\n")
        return (False, None)

    return (True, data)

# jtag csr read
@command()
def local_csr_peek(csr_addr, csr_width):
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
    ctrl = _prepare_csr_ctrl(True, csr_addr, csr_width)
    cmd_str = hex(cmd)[2:].zfill(16)
    dr_byte_str = '0x' + cmd_str + '0'*16
    dr_byte_str = '0x' + '%016x' % cmd + '%016x' % ctrl
    (status, data) = _jtag_shift_in_csr_acc_bytes(dr_byte_str)
    if not status:
        logger.error('peek csr cmd failed!')
        return None

    # Enable if needed in emulation
    sleepfor = constants.SBP_CMD_EXE_ROM_TIME_WAIT if constants.GLOBAL_EMULATION_ROM_MODE else constants.SBP_CMD_EXE_TIME_WAIT
    logger.debug('peek - sleep (%ss) for ir_shiftin ... hw (esp. emulation) to process the command!' % sleepfor)
    time.sleep(sleepfor)

    word_array = list()
    for i in range(csr_width):
        logger.debug("\nReading Data[{}/{}]...........:".format(i, csr_width))
        csr_data_addr = csr_addr + (i * 8)
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
def local_csr_poke( csr_addr, word_array):
    '''Poke word_array(an array of 64-bit words) at csr_addr'''
    #logger.error(('csr poke addr:{0}'
    #             ' words:{1}').format(hex(csr_addr),
    #               [hex(x) for x in word_array]))

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
        #csr_data_addr = (i+1) * 8
        csr_data_addr = csr_addr + (i * 8)
        cmd = _prepare_csr_acc_cmd(False, csr_data_addr, 1)
        cmd_str = hex(cmd)[2:].zfill(16)
        dr_byte_str = '0x' + cmd_str + "%016x"%word_array[i]
        logger.debug('dr: {}'.format(dr_byte_str))
        (status, data) = _jtag_shift_in_csr_acc_bytes(dr_byte_str)
        if not status:
            logger.error("jtag csr poke data write failed!")
            return None

    # Enable if needed in emulation
    sleepfor = constants.SBP_CMD_EXE_ROM_TIME_WAIT if constants.GLOBAL_EMULATION_ROM_MODE else constants.SBP_CMD_EXE_TIME_WAIT
    logger.debug('poke - sleep (%ss) for ir_shiftin ... hw (esp. emulation) to process the command!' % sleepfor)
    time.sleep(sleepfor)

    logger.debug("\nWriting write command.... done")
    cmd = _prepare_csr_acc_cmd(False, csr_addr, len(word_array))
    cmd_str = hex(cmd)[2:].zfill(16)
    ctrl = _prepare_csr_ctrl(False, csr_addr, len(word_array))
    dr_byte_str = '0x' + cmd_str + "%016x"%word_array[i]
    logger.debug('dr: {}'.format(dr_byte_str))
    (status, data) = _jtag_shift_in_csr_acc_bytes(dr_byte_str)
    if not status:
        logger.error('peek csr cmd failed!')

    return True

# unittest-path keep it for debugging
def csr_peek_poke_test():
    print("Connecting to Probe to S1 for csr/avago mode")
    local_csr_probe('sp55e', '10.1.40.86')

    print('\n************POKE MIO SCRATCHPAD ***************')
    print(local_csr_poke(0x440080a0, [0xabcd112299885566]))
    print('\n************PEEK MIO SCRATCHPAD ***************')
    word_array = local_csr_peek(0x440080a0, 1)
    #word_array = local_csr_peek(0x1d00e160, 1)
    #word_array = local_csr_peek(0x1d00e0a0, 1)
    #word_array = local_csr_peek(0x1d00e2c8, 1)
    print("word_array: {}".format([hex(x) for x in word_array] if word_array else None))

    #print('\n************POKE MIO2 SCRATCHPAD ***************')
    #print local_csr_poke(0x1e008408, [0xabcd112299885566])
    #print('\n************PEEK MIO2 SCRATCHPAD ***************')
    #word_array = local_csr_peek(0x1e008408, 1)
    #print("{}".format([hex(x) for x in word_array] if word_array else None))

if __name__== "__main__":
    #csr_peek_poke_test()
    pass
