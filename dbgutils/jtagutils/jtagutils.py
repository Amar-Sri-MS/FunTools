#!/usr/bin/env python3

import sys, os
sys.path.append('/home/'+os.environ["USER"]+'/.local/opt/imgtec/Codescape-8.6/lib/python2.7/lib-dynload')
sys.path.append('/home/'+os.environ["USER"]+'/.local/opt/imgtec/Codescape-8.6/lib/python2.7/site-packages')
sys.path.append('/home/'+os.environ["USER"]+'/.local/opt/imgtec/Codescape-8.6/lib/python2.7/site-packages/sitepackages.zip')

from imgtec.console.support import command
from imgtec.console import *
import logging
import time

logger = logging.getLogger('jtagutils')
#logger.setLevel(logging.INFO)
logger.setLevel(logging.ERROR)

class constants(object):
    CSR_RING_TAP_SELECT = 0x01C1
    CSR_RING_TAP_SELECT_WIDTH = 10
    TCKRATE = 10000000
    EMULATION = True
    #Note: for emulation, reduce this to 25000
    EMU_TCKRATE = 25000

class ChipJTAG(object):
    """ Base class for all chips with JTAG """
    def __init__(self):
        """
        Subclasses should set values for the member variables
        """
        self.wide_reg_ctrl_addr = None
        self.wide_reg_data_addr = None

    def prepare_csr_acc_cmd(self, read, csr_addr, csr_width):
        """
        Prepares the access command part of the JTAG DR value.

        This, for F1 and S1, is the upper 64-bit word of the 128-bit DR
        shift value.
        """
        pass

    def prepare_csr_ctrl(self, read, csr_addr, csr_width):
        """
        Prepares the control value for an indirect register access through the
        wide registers (e.g. on S1 this prepares the value for the csrctl.ctrl
        register).

        For JTAG we do not do direct access i.e. fast mode. Use I2C for that.
        """
        pass

    def decode_status(self, status):
        """
        Decodes the 128-bit status response from the DR shift.
        Returns a tuple of (ack, resp, running, status) values.
        """
        pass


class CSR1JTAG(ChipJTAG):
    def __init__(self):
        super(CSR1JTAG, self).__init__()

        # Pick the wide register at 0x0 on F1 (probably maps to the JTAG
        # master's wide register)
        self.wide_reg_ctrl_addr = 0x0
        self.wide_reg_data_addr = 0x8

    def prepare_csr_acc_cmd(self, read, csr_addr, csr_width):
        assert read is not None
        assert csr_addr is not None

        ring_sel = csr_addr >> 35
        cmd = ((csr_addr & 0xffffffffff) |
                (((0x2 if read is True else 0x3) << 60) |
                ((csr_width & 0x3F) << 54) |
                (ring_sel << 49)))
        return cmd

    def prepare_csr_ctrl(self, read, csr_addr, csr_width):
        assert read is not None
        assert csr_addr is not None

        # F1's control register layout is the same as its access command layout
        val = self.prepare_csr_acc_cmd(read, csr_addr, csr_width)
        return val

    def decode_status(self, status):
        jtag_resp = status[0] >> 124
        jtag_status = (status[0] >> 96) & 0xFF
        jtag_ack = (status[0] >> 64) & 0x1
        jtag_running = (status[0] >> 65) & 0x1
        return jtag_ack, jtag_resp, jtag_running, jtag_status


class CSR2JTAG(ChipJTAG):
    def __init__(self):
        super(CSR2JTAG, self).__init__()

        # On S1, pick the first wide register (apparently they are all
        # accessible by any master).
        self.wide_reg_ctrl_addr = 0x58
        self.wide_reg_data_addr = 0x0

    def prepare_csr_acc_cmd(self, read, csr_addr, csr_width):
        assert read is not None
        assert csr_addr is not None

        cmd = (((0x2 if read is True else 0x3) << 44) |
               ((csr_width & 0x3F) << 38) |
               (csr_addr & 0xffffffff))
        return cmd

    def prepare_csr_ctrl(self, read, csr_addr, csr_width):
        assert read is not None
        assert csr_addr is not None

        val = (((csr_width & 0x3F) << 36) |
               ((0x2 if read is True else 0x3) << 32) |
               (csr_addr & 0xffffffff))
        return val

    def decode_status(self, status):
        jtag_resp = (status[0] >> 96) & 0xFFFF
        jtag_status = (status[0] >> 124) & 0xF
        jtag_ack = (status[0] >> 64) & 0x1
        jtag_running = (status[0] >> 65) & 0x1
        return jtag_ack, jtag_resp, jtag_running, jtag_status


def _get_chip_jtag(chip):
    if chip == 'f1':
        return CSR1JTAG()
    else:
        return CSR2JTAG()


def _ir_shiftin(width, data):
    cmd = '%u 0x%04x'%(width, data)
    logger.debug('shift-in cmd: \"{}\"'.format(cmd))
    status = tapi(cmd)
    logger.debug('shift-in cmd status: {}'.format(status))
    status = status[0]
    if not status:
        logger.error('Failed to shiftin ir!')
        return False
    return True

# Connects to Codescape jtag probe and enables csr tap select
@command()
def csr_probe(dev_type, ip_addr, jtag_bitrate):
    '''Connects to Codescape jtag probe and enables csr tap select'''
    logger.info('Connecting to SysProbe:{}[{}] jtag_bitrate:{}'.format(
        ip_addr, dev_type, jtag_bitrate))
    status = probe(dev_type, ip_addr, force_disconnect=True, verbose=True)
    status = str(status)
    if (("SysProbe" not in status) or ("Firmware" not in status) or
        ("ECONNREFUSED" in status) or ("InvalidArgError" in status)):
        return (False, status)
    if jtag_bitrate:
        jtag_tckrate = jtag_bitrate
    else:
        jtag_tckrate = constants.EMU_TCKRATE \
                if constants.EMULATION == True \
                else constants.TCKRATE
    status = tckrate(jtag_tckrate)
    logger.info('Connecting to Codescape jtag probe'
            ' (tckrate: {0})! statu: {1}'.format(jtag_tckrate, status))
    status = _ir_shiftin(constants.CSR_RING_TAP_SELECT_WIDTH,
                constants.CSR_RING_TAP_SELECT)
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


def _jtag_shift_in_csr_acc_bytes(bytes_hex_str, chip_jtag):
    """
    Shifts-in data into csr tap controller dr.
    Returns status and response data.
    """
    length = len(bytes_hex_str)
    assert(length == (32 + 2)) # 32 nibbles + length('0x')
    dr = '128 ' + bytes_hex_str

    status = tapd(dr)
    jtag_ack, jtag_resp, jtag_running, jtag_status = chip_jtag.decode_status(status)

    logger.debug('shift-in data: {} status: {}'.format(dr, status))
    logger.debug("jtag response: {}".format(jtag_resp))
    logger.debug("jtag status: {}".format(jtag_status))
    logger.debug("jtag ack: {}".format(jtag_ack))
    logger.debug("jtag running: {}".format(jtag_running))

    if jtag_status != 0:
        logger.error("jtag shift-in data error!: {}".format(jtag_status))
        return (False, None)

    status = _ir_shiftin(constants.CSR_RING_TAP_SELECT_WIDTH,
                constants.CSR_RING_TAP_SELECT)
    if not status:
        logger.error("Failed in shiftin IR\n")
        return (False, None)

    # Enable if needed in emulation
    # time.sleep(1)

    logger.debug('shift-in zeros for response data')
    dr = "128 0x0"
    status = tapd(dr)
    jtag_ack, jtag_resp, jtag_running, jtag_status = chip_jtag.decode_status(status)

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

    status = _ir_shiftin(constants.CSR_RING_TAP_SELECT_WIDTH,
                constants.CSR_RING_TAP_SELECT)
    if not status:
        logger.error("Failed in shiftin IR\n")
        return (False, None)

    return (True, data)


# jtag csr read
@command()
def csr_peek(csr_addr, csr_width, chip='f1'):
    '''Peek csr_width number of 64-bit words from csr_addr.

    The chip argument allows selection between ['f1', 's1'].
    '''
    logger.debug(('csr peek csr_addr:{0}'
        ' csr_width:{1} chip:{2}').format(
            hex(csr_addr), csr_width, chip))

    if csr_width == 0 or csr_width > 8:
        logger.error(('Invalid csr width:'
                     ' {}\n').format(csr_width) +
                     'Csr width(64-bit words) should be in the range 1-8!')
        return None

    # Indirect wide register access:
    #     Perform a write to the control register, followed by reads from the
    #     data registers.
    logger.debug("\nWriting read cmd...........:")

    chip_jtag = _get_chip_jtag(chip)
    cmd = chip_jtag.prepare_csr_acc_cmd(False, chip_jtag.wide_reg_ctrl_addr, 1)
    ctrl = chip_jtag.prepare_csr_ctrl(True, csr_addr, csr_width)

    dr_byte_str = '0x' + '%016x' % cmd + '%016x' % ctrl
    (status, data) = _jtag_shift_in_csr_acc_bytes(dr_byte_str, chip_jtag)
    if not status:
        logger.error('peek csr cmd failed!')
        return None

    # Enable if needed in emulation
    # time.sleep(1)

    word_array = list()
    for i in range(csr_width):
        logger.debug("\nReading Data[{}/{}]...........:".format(i+1,
                    csr_width))
        csr_data_addr = chip_jtag.wide_reg_data_addr + i * 8
        cmd = chip_jtag.prepare_csr_acc_cmd(True, csr_data_addr, 1)

        cmd_str = hex(cmd)[2:].zfill(16)
        dr_byte_str = '0x' + cmd_str + '0'*16
        logger.debug('dr: {}'.format(dr_byte_str))
        (status, data) = _jtag_shift_in_csr_acc_bytes(dr_byte_str, chip_jtag)

        if not status:
            logger.error('peek: csr data read failed!')
            return None
        word_array.append(data)
    logger.debug('Peeked word_array: {0}'.format([hex(x) for x in word_array]))
    return word_array

# csr write
@command()
def csr_poke(csr_addr, word_array, chip='f1'):
    '''Poke word_array(an array of 64-bit words) at csr_addr'''
    chip_jtag = _get_chip_jtag(chip)

    logger.debug(('csr poke addr:{0}'
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
        csr_data_addr = chip_jtag.wide_reg_data_addr + i * 8
        cmd = chip_jtag.prepare_csr_acc_cmd(False, csr_data_addr, 1)

        cmd_str = hex(cmd)[2:].zfill(16)
        dr_byte_str = '0x' + cmd_str + "%016x" % word_array[i]
        logger.debug('dr: {}'.format(dr_byte_str))
        (status, data) = _jtag_shift_in_csr_acc_bytes(dr_byte_str, chip_jtag)
        if not status:
            logger.error("jtag csr poke data write failed!")
            return None

    # Enable if needed in emulation
    # time.sleep(6)

    logger.debug("\nWriting write command....")
    cmd = chip_jtag.prepare_csr_acc_cmd(False, chip_jtag.wide_reg_ctrl_addr, 1)
    ctrl = chip_jtag.prepare_csr_ctrl(False, csr_addr, len(word_array))
    dr_byte_str = '0x' + '%016x' % cmd + '%016x' % ctrl
    logger.debug('dr: {}'.format(dr_byte_str))
    (status, data) = _jtag_shift_in_csr_acc_bytes(dr_byte_str, chip_jtag)
    if not status:
        logger.error('peek csr cmd failed!')

    return True

def csr_peek_poke_test():
    print("Connecting to Probe")
    csr_probe('sp55e', '10.1.40.84')
    print('\n************POKE***************')
    print(csr_poke(0x4883160000, [0x1111111111111111, 0x2222222222222222,
                                     0x3333333333333333, 0x4444444444444444,
                                     0x5555555555555555, 0x6666666666666666,
                                    ]))
    print(csr_poke(0xb000000078, [0xabcdabcdabcdabcd]))
    print(csr_poke(0xb800000078, [0xdeadbeefdeadbeef]))

    print('\n************PEEK***************')
    word_array = csr_peek(0xb000000078, 1)
    print("{}".format([hex(x) for x in word_array] if word_array else None))
    word_array = csr_peek(0xb800000078, 1)
    print("{}".format([hex(x) for x in word_array] if word_array else None))
    word_array = csr_peek(0x4883160000, 6)
    print("{}".format([hex(x) for x in word_array] if word_array else None))

###########   JTAG    ##################################################################

def jtag_probe(name, ip, in_rom=None):
    try:
        probe(name, ip)
        JTAG_TCKRATE = constants.EMU_TCKRATE if constants.EMULATION == True \
            else constants.TCKRATE
        JTAG_TCKRATE = JTAG_TCKRATE / 5 if in_rom else JTAG_TCKRATE
        logger.info("\nconnecting to JTAG probe with TCKRATE(%s)..." % JTAG_TCKRATE)
        tckrate(JTAG_TCKRATE)
        scanonly()
    except Exception as e:
        logger.error('Error connecting to probe: %s' % e)
        raise Exception("Error connecting to probe")

def mdh_read_old(byte_address):
    tapscan("5 %d" % IR_DEVICEADDR, "32 %d" % (byte_address & 0xf80) )
    tapscan("5 %d" % IR_APBACCESS, "39 %d" % ((byte_address & 0x7c) | 0x3) )
    result = tapd("39 %d" % ((byte_address & 0x7c) | 0x2) )
    if (result[0] & 0x3) == 0x3:
        return result[0] >> 7
    raise RuntimeError("APB read failed try a lower TCK clock")

def mdh_write_old(byte_address, word):
    tapscan("5 %d" % IR_DEVICEADDR, "32 %d" % (byte_address & 0xf80) )
    result = tapscan("5 %d" % IR_APBACCESS, "39 %d" % (word << 7|(byte_address & 0x7c)|0x1))

    if (result[0] & 0x3) == 0x3:
        return
    raise RuntimeError("APB read failed try a lower TCK clock")

mdh_read_ = mdh_read_old
mdh_write_ = mdh_write_old

def esecure_read():
    """ internal only """
    mdh_write_(CONTROL,RD_REQ)
    timeout = 0
    while (mdh_read_(CONTROL) & RD_REQ) == 0: #wait for RD_REQ=1
        timeout+=1
        if timeout == TIMEOUT:
            raise RuntimeError("esecure_read: timeout waiting for RD_REQUEST to go high")
    data = mdh_read_(RDATA)
    mdh_write_(CONTROL,RD_ACK)
    timeout = 0
    while (mdh_read_(CONTROL) & RD_REQ) != 0: #wait for RD_REQ=0
        timeout+=1
        if timeout == TIMEOUT:
            raise RuntimeError("esecure_read: timeout waiting for RD_REQUEST to go low")
    mdh_write_(CONTROL,0)
    return data


if __name__== "__main__":
    csr_peek_poke_test()

