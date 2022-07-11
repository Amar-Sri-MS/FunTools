#!/usr/bin/env python3

import sys, os
from aardvark_py import *
from array import array
import binascii
import time
import logging
import traceback
import subprocess
import paramiko
from .i2cdev import *

logger = logging.getLogger('i2cutils')
logger.setLevel(logging.INFO)

class constants(object):
    IC_DEVICE_FEATURE_MASK = 0x1B
    IC_DEVICE_MODE_I2C = 0x2
    IC_DEVICE_MODE_GPIO = 0x0

    # Can be overriden from the dut.cfg file with i2c_bitrate settings
    DEFAULT_I2C_XFER_BIT_RATE = 500
    F1_I2C_ADDR_MODE = 0
    SBP_CMD_EXE_TIME_WAIT = 1
    I2C_CSR_SLEEP_SEC = 0.001

# Converts byte array to big-endian 64-bit words
def byte_array_to_words_be(byte_array):
    #logger.debug('byte_array: {0}'.format(byte_array))
    words = list()
    byte_attay_size = len(byte_array)
    word_array_size = byte_attay_size / 8
    for i in range(word_array_size):
        val = int(binascii.hexlify(byte_array[(i*8):(i*8)+8]), 16)
        words.extend([val])

    remaining_bytes = len(byte_array) % 8
    if remaining_bytes != 0:
        last_word = byte_array[-remaining_bytes:]
        last_word.extend(array('B', [0x00] * (8 - remaining_bytes)))
        val = int(binascii.hexlify(last_word), 16)
        words.extend(val)
    logger.debug('word_array: {0}'.format([hex(x) for x in words]))

    return words


class aardvark:
    def __init__(self, dev_id, slave_addr, bitrate):
        self.dev_id = dev_id
        self.slave_addr = slave_addr
        self.bitrate = bitrate
        self.handle = None

    # Check i2c device presence and open the device.
    # Returns the device handle
    def connect(self):
        dev_idx = aardvark_i2c_spi_dev_index_from_serial(self.dev_id)
        if dev_idx is None:
            dev_list = aardvark_i2c_spi_dev_list()
            status_msg = (('Failed to find i2c device: {0}!'
                           ' Found devices: {1}').format(self.dev_id, dev_list))
            logger.error(status_msg)
            return (False, status_msg)
        dev_in_use = dev_idx & 0x8000
        dev_idx = dev_idx & 0x7FFF
        if dev_in_use != 0:
            logger.info('Device({0}/{1}) already in use! Disconnecting....'.format(self.dev_id, dev_idx))
            status = aa_close(dev_idx)
            logger.info('Device({0}/{1}) is closed with status: {2}!'.format(
                self.dev_id, dev_idx, status))

        n_devs, devs = aa_find_devices(dev_idx+1)
        logger.info('n_devs:{0} devs:{1}:'.format(n_devs, devs))
        if not devs or devs[dev_idx] is None:
            status_msg = 'Failed to detect i2c device! dev_list: {0}'.format(dev_list)
            logger.error(status_msg)
            return (False, status_msg)

        dev_handle =  devs[dev_idx]
        logger.debug('Dev handle: {0}'.format(dev_handle))
        h = aa_open(dev_handle)
        if h == 0x8000:
            status_msg = 'Error opening i2c device. Invalid dev Handle! {0}'.format(h)
            logger.error(status_msg)
            return (False, status_msg)
        if h < 0:
            status_msg = 'Error opening i2c device! {0}({1})'.format(aa_status_string(h), h)
            logger.error(status_msg)
            return (False, status_msg)

        features = aa_features(h)
        if features != constants.IC_DEVICE_FEATURE_MASK:
            status_msg = ('Error validating dev features!'
            ' {0}({1})').format(aa_status_string(features), features)
            logger.error(status_msg)
            return (False, status_msg)

        status = aa_i2c_free_bus(h)
        status_msg = ('Free Bus! {0}({1})').format(
                      aa_status_string(features), features)
        logger.debug(status_msg)
        status = aa_configure(h, 2)
        if status != 2:
            status_msg = ('Error configuring i2c mode:'
                ' {0}({1})').format(aa_status_string(status), status)
            logger.error(status_msg)
            return (False, status_msg)

        logger.info('Connecting to slave: {0} bitrate:{1}'.format(
            hex(self.slave_addr), self.bitrate))
        status = aa_i2c_bitrate(h, self.bitrate)
        if status != self.bitrate:
            status_msg = ('Error Configuring the bitrate!'
                    ' {0}({1})').format(aa_status_string(status), status)
            logger.error(status_msg)
            return (False, status_msg)

        data = array('B', [])
        (status, sent_bytes) = aa_i2c_write_ext(h, self.slave_addr,
                                   constants.F1_I2C_ADDR_MODE, data)
        if status != AA_I2C_STATUS_OK:
            status_msg = ('No device found at addr: {0}'
                          ' Error:{1}({2})'.format(hex(self.slave_addr),
                            aa_status_string(status), status))
            logger.error(status_msg)
            return (False, status_msg)

        logger.info('i2c dev is connected. handle: {0}'.format(h))
        self.handle = h
        return (True, h)

    # Free the i2c bus and close the device handle
    def disconnect(self):
        logger.debug('Disconnect request')
        h = self.handle
        status = aa_i2c_free_bus(h)
        logger.debug('Free Bus: {0}'.format(aa_status_string(status)))
        status = aa_close(h)
        self.handle = None
        logger.debug('Closed i2c handle')

    # i2c csr read
    def i2c_read(self, read_data, chip_inst):
        h = self.handle
        if read_data is None or len(read_data) == 0:
            logger.error('Read array length expected should be non-zero positive number')
            return None
        return aa_i2c_read(h, self.slave_addr, 0, read_data)

    # i2c csr write
    def i2c_write(self, write_data, chip_inst):
        h = self.handle
        logger.info('I2C write. {0}'.format([hex(x) for x in write_data]))
        if write_data is None or len(write_data) == 0:
            logger.error('Write data array length should be non-zero positive number')
            return None
        return aa_i2c_write(h, self.slave_addr, 0, write_data)

    def i2c_wedge_detect(self):
        h = self.handle
        logger.info('Checking i2c wedge condition ...!')
        data = array('B', [])
        (status, sent_bytes) = aa_i2c_write_ext(h, self.slave_addr, 0, data)
        if status == AA_I2C_STATUS_OK:
            logger.info('i2c is not wedged!')
            return False
        return True

    def i2c_unwedge(self):
        h = self.handle
        logger.debug('I2C unwedge start ...')
        status = aa_configure(h, constants.IC_DEVICE_MODE_GPIO)
        status = aa_gpio_direction(h, 0x1)
        for i in range(100):
            status = aa_gpio_set(h, 0x1)
            time.sleep(0.0001)
            status = aa_gpio_set(h, 0x00)
            time.sleep(0.0001)
            status = aa_gpio_set(h, 0x1)
            time.sleep(0.0001)
        status = aa_configure(h, constants.IC_DEVICE_MODE_I2C)
        logger.info('I2C unwedge done!')
        return True

    # Debug function for emulation trigger to collect waveforms
    def gpio_sck_trigger(self):
        h = self.handle
        logger.info('Trigger GPIO....!')
        status = aa_configure(h, 0)
        status = aa_gpio_direction(h, 0x0)
        status = aa_gpio_set(h, 0x8)
        time.sleep(0.00001)
        status = aa_gpio_set(h, 0x00)
        time.sleep(0.00001)
        status = aa_gpio_set(h, 0x8)
        logger.info('GPIO trigger done!')


class bmc:
    def __init__(self, bmc_ip_address):
        self.bmc_ip_address = bmc_ip_address
        self.client = None
        self.slave_addr = 0x70
        self.i2ctransfer_mode = False

    def try_bmc_user_root(self, ip_addr):
        logger.info('bmc connecting as root')
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(self.bmc_ip_address, username = 'root', password='root', timeout = 3)
        except Exception as e:
            status_msg = ('Failed to connect to BMC: {0}! using "root"\n').format(self.bmc_ip_address)
            #status_msg = status_msg + traceback.format_exc()
            logging.error(status_msg)
            return None
        return client

    def try_bmc_user_sysadmin(self, ip_addr):
        logger.info('bmc connecting as "sysadmin"')
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(self.bmc_ip_address, username = 'sysadmin', password='superuser', timeout = 3)
        except Exception as e:
            status_msg = ('Failed to connect to BMC: {0}! using "sysadmin"\n').format(self.bmc_ip_address)
            status_msg = status_msg + traceback.format_exc()
            logging.error(status_msg)
            return None
        return client

    # Check i2c device presence and open the device.
    # Returns the device handle
    def connect(self):
        logger.info('bmc connect')
        client = self.try_bmc_user_root(self.bmc_ip_address)

        if not client:
            client = self.try_bmc_user_sysadmin(self.bmc_ip_address)

        if not client:
            return (False, "Failed to connect to BMC!")

        self.client = client
        self.i2ctransfer_mode = self.check_i2cget_exists();
        logger.info('i2ctransfer_mode: {0}'.format(self.i2ctransfer_mode))

        return (True, "Connected to BMC!")

    # Free the i2c bus and close the device handle
    def disconnect(self):
        if self.client:
            self.client.close()
        logger.info('Disconnected!')

    # prepares csr access command bytes
    def _prepare_i2c_cmd(self, chip_inst, read, num_bytes):
        assert(read != None)
        assert(num_bytes != None and num_bytes != 0)
        assert(chip_inst != None)
        assert(chip_inst >= 0 and chip_inst <=1)
        if chip_inst == 0:
            bus_num = 3
        else:
            bus_num = 5

        cmd = ''
        if self.i2ctransfer_mode:
            cmd = 'i2ctransfer -fy %d %s%d@0x%02x '%(bus_num, 'r' if read else 'w', num_bytes, self.slave_addr)
        else:
            cmd = 'i2c-test -b %02d -s 0x%02x '%(bus_num, self.slave_addr)
            if read is True:
                cmd = cmd + ' -rc %d'%(num_bytes) + ' -r'
            else:
                cmd = cmd + ' -w -d'

        return cmd

    def i2c_decode_read_output(self, output):
        output_lines = output.splitlines()
        logger.debug(output_lines)
        num_output_lines = len(output_lines)
        logger.debug('num_output_lines: {}'.format(num_output_lines))
        bytes_stream = list()
        read_data = list()
        num_bytes_read = 0
        if self.i2ctransfer_mode:
            bytes_stream =  output_lines[0].split()
            for x in bytes_stream:
                read_data.append(int(x, 16))
            num_bytes_read = len(read_data)
        else:
            num_bytes_read = int(output_lines[0].split(':')[1].strip())
            logger.debug('num_bytes_read:{}'.format(num_bytes_read))
            for i in range(1, len(output_lines)):
                byte_array =  output_lines[i].strip().split(' ')
                bytes_stream.extend(byte_array)
            for i in range(num_bytes_read):
                read_data.append(int(bytes_stream[i], 16))
            logger.debug('num_bytes_read: {} data: {}'.format(num_bytes_read, [hex(x) for x in read_data]))

        return (num_bytes_read, read_data)

    def i2c_decode_write_output(self, output):
        output_lines = output.splitlines()
        num_bytes_wrote = int(output_lines[1].split(':')[1].strip())
        bytes_stream =  output_lines[2].strip().split(' ')
        bytes_wrote = [int(x.encode("utf-8"), 16) for x in bytes_stream]
        logger.debug('num_bytes_wrote: {0} bytes_wrote: {1}'.format(num_bytes_wrote, bytes_wrote))
        return num_bytes_wrote

    def check_i2cget_exists(self):
        assert(self.client)
        try:
            cmd = "command -v i2ctransfer"
            logger.debug('checking i2ctransfer exists! cmd: {0}'.format(cmd))
            _, stdout, stderr = self.client.exec_command(cmd)
            err = stderr.read().decode('utf-8')
            if (len(err) != 0):
                logging.error(err)
                return False

            cmd_output = stdout.read().decode('utf-8')
            logging.debug(cmd_output)
            if (len(cmd_output) == 0):
                return False
            return True
        except Exception as e:
            status_msg = traceback.format_exc()
            logging.error(status_msg)
        return False

    # i2c csr read
    def i2c_read(self, read_data, chip_inst):
        assert(self.client)
        cmd = self._prepare_i2c_cmd(chip_inst, True, len(read_data))
        logger.debug('i2c_read cmd: {0}'.format(cmd))
        num_bytes_read = 0
        data = None
        try:
            logger.debug('bmc i2c_read: {0}'.format(cmd))
            _, stdout, stderr = self.client.exec_command(cmd)
            err = stderr.read().decode('utf-8')
            if (len(err) != 0):
                logging.error(err)
                raise Exception(err)
            cmd_output = stdout.read().decode('utf-8')
            logging.debug(cmd_output)
            if (len(cmd_output) == 0):
                err = 'No output for the cmd: {0}'.format(cmd)
                logging.error(err)
                raise Exception(err)
            (num_bytes_read, parsed_data) = self.i2c_decode_read_output(cmd_output)
            logger.debug('i2c_read num_bytes_read: {0} read_data: {1}'.format(num_bytes_read, parsed_data))
            if not num_bytes_read:
                err = 'No output for the cmd: {0}'.format(cmd)
                logging.error(err)
                raise Exception(err)
            if num_bytes_read != len(read_data):
                err = 'Invalid length({0}) of data for cmd: {1}'.format(num_bytes_read, cmd)
                logging.error(err)
                raise Exception(err)
        except Exception as e:
            status_msg = traceback.format_exc()
            logging.error(status_msg)
            return 0

        for i in range(len(parsed_data)):
            read_data[i] = parsed_data[i]

        logger.debug('i2c_read return num_bytes_read: {0} read_data: {1}'.format(num_bytes_read, read_data))
        return (num_bytes_read, read_data)

    # i2c csr write
    def i2c_write(self, write_data, chip_inst):
        assert(self.client)
        cmd_output = None
        num_bytes_wrote = 0
        cmd = self._prepare_i2c_cmd(chip_inst, False, len(write_data))
        for i in write_data:
            cmd = cmd + " 0x%02x"%(i)

        logger.debug('i2c_write cmd: {0}'.format(cmd))
        try:
            logger.debug('bmc i2c_write: {0}'.format(cmd))
            _, stdout, stderr = self.client.exec_command(cmd)
            err = stderr.read().decode('utf-8')
            if (len(err) != 0):
                logging.error(err)
                raise Exception(err)
            cmd_output = stdout.read().decode('utf-8')
            if self.i2ctransfer_mode:
                if (len(cmd_output) != 0):
                    err = 'No putput is expected for the cmd: {0}'.format(cmd)
                    logging.error(err)
                    raise Exception(err)
                else:
                    return len(write_data)
            else:
                if (len(cmd_output) == 0):
                    err = 'No putput for the cmd: {0}'.format(cmd)
                    logging.error(err)
                    raise Exception(err)
                logger.debug(cmd_output)
                num_bytes_wrote = self.i2c_decode_write_output(cmd_output);
                if num_bytes_wrote != len(write_data):
                    err_msg = 'Incorrect read! num_bytes_write:{0} expected: {1}'.format(num_bytes_write, len(write_data))
                    logger.err(err_msg)
                    raise Exception(err_msg)
        except Exception as e:
            status_msg = traceback.format_exc()
            logging.error(status_msg)
            return 0

        return num_bytes_wrote

class i2c(object):
    CSR1_ADDR_WIDTH_BYTES = 5

    def __init__(self, dev_id=None, slave_addr=None,
            bmc_ip_address=None, bitrate=None, chip_type='f1',
            addr_width=CSR1_ADDR_WIDTH_BYTES):
        self.bmc_board = False
        self.bitrate = None
        self.addr_width = addr_width
        if bmc_ip_address:
            self.bmc_board = True
            self.master = bmc(bmc_ip_address)
        else:
            self.bitrate = bitrate
            if not self.bitrate:
                self.bitrate = constants.DEFAULT_I2C_XFER_BIT_RATE
                logger.error('Invalid bitrate!'
                    ' using default {}'.format(self.bitrate))
            self.master = aardvark(dev_id, slave_addr, self.bitrate)

    # Check i2c device presence and open the device.
    # Returns the device handle
    def i2c_connect(self):
        return self.master.connect()

    # Free the i2c bus and close the device handle
    def i2c_disconnect(self):
        logger.debug('Disconnect request')
        return self.master.disconnect()

    # i2c csr read
    def i2c_csr_peek(self, csr_addr, csr_width_words, chip_inst=None):
        """
        Performs the peek operation over i2c.

        Returns a tuple of (data_words, error_code). The error code is either
        0 for success or -1 for failure.
        """
        logger.debug(('I2C peek csr_addr:{0}'
                      ' csr_width_words:{1} chip_inst: {2}').format(
               hex(csr_addr), csr_width_words, chip_inst))
        if csr_width_words == 0:
            logger.error('csr width expected should be non-zero positive number')
            return (None, -1)
        elif csr_width_words == 1: # Fast mode for single wide csr access
            csr_addr = struct.pack('>Q', csr_addr)
            csr_addr = list(struct.unpack('BBBBBBBB', csr_addr))
            csr_addr = csr_addr[(8-self.addr_width):]
            cmd = array('B', [0x00])
            cmd.extend(csr_addr)
            logger.debug(cmd)
            #logger.info('i2c slave addr: {0}'.format(self.slave_addr))
            sent_bytes = self.master.i2c_write(write_data = cmd,  chip_inst=chip_inst)
            logger.debug('sent_bytes: {0}'.format(sent_bytes))
            if sent_bytes != len(cmd):
                logger.error(('Write Error! sent_bytes:{0}'
                       ' Expected: {1}').format(sent_bytes, len(cmd)))
                return (None, -1)
            time.sleep(constants.I2C_CSR_SLEEP_SEC)
            csr_width = csr_width_words * 8
            read_data = array('B', [00]*(csr_width+1))
            read_bytes = self.master.i2c_read(read_data = read_data, chip_inst=chip_inst)
            logger.debug(('read_bytes: {0} read_data: {1}').format(read_bytes, [hex(x) for x in read_data]))
            if read_bytes[0] != (csr_width + 1):
                logger.error(('Read Error!  read_bytes:{0}'
                       ' Expected: {1}').format(read_bytes, (csr_width + 1)))
                return (None, -1)
            if read_data[0] != 0x80:
                logger.error(('Read status returned Error! {0}').format(read_data[0]))
                return (None, read_data[0]&0xf)

            read_data = read_data[1:]
            logger.debug(read_data)
            word_array = byte_array_to_words_be(read_data)
            logger.debug('Peeked word_array: {0}'.format([hex(x) for x in word_array]))
            return (word_array, 0)
        else:
            ring_sel = csr_addr >> 35
            csr_addr = ((csr_addr & 0xffffffffff) |
                    ((0x2 << 60) |
                    ((csr_width_words & 0xf) << 54) |
                    (ring_sel << 49)))
            csr_addr = struct.pack('>Q', csr_addr)
            csr_addr = list(struct.unpack('BBBBBBBB', csr_addr))
            cmd_data = array('B', [0x01])
            csr_data_addr = struct.pack('>Q', 0)
            csr_data_addr = list(struct.unpack('BBBBBBBB', csr_data_addr))
            csr_data_addr = csr_data_addr[(8-self.addr_width):]
            cmd_data.extend(csr_data_addr)
            cmd_data.extend(csr_addr)
            logger.debug('poking bytes: {0}'.format([hex(x) for x in cmd_data]))
            sent_bytes = self.master.i2c_write(write_data = cmd_data, chip_inst=chip_inst)
            logger.debug('sent_bytes: {0}'.format(sent_bytes))
            if sent_bytes != len(cmd_data):
                logger.error(('Write Error! sent_bytes:{0}'
                       ' Expected: {1}').format(sent_bytes, len(cmd_data)))
                return (None, -1)
            try:
                time.sleep(constants.I2C_CSR_SLEEP_SEC)
                status = array('B', [0x01])
                status_bytes = self.master.i2c_read(read_data = status, chip_inst=chip_inst)
                logger.debug('poke status_bytes:{0}'.format(status_bytes))
                if status_bytes[0] != 1:
                    logger.debug('Read Error!  status_bytes:{0} Expected:'
                                 '{1}'.format(status_bytes, 1))
                    return (None, -1)
                if status[0] != 0x80:
                    logger.debug('Write status returned Error!' ' {0}'.format(status[0]))
                    return (None, -1)
            except Exception as e:
                logging.error(traceback.format_exc())
                return (None, -1)
            word_array = list()
            for i in range(csr_width_words):
                csr_data_addr = struct.pack('>Q', (i+1) * 8)
                csr_data_addr = list(struct.unpack('BBBBBBBB', csr_data_addr))
                csr_data_addr = csr_data_addr[(8-self.addr_width):]
                cmd_data = array('B', [0x00])
                cmd_data.extend(csr_data_addr)
                sent_bytes = self.master.i2c_write(write_data = cmd_data, chip_inst=chip_inst)
                logger.debug('sent_bytes: {0}'.format(sent_bytes))
                if sent_bytes != len(cmd_data):
                    logger.error(('Write Error! sent_bytes:{0}'
                       ' Expected: {1}').format(sent_bytes, len(cmd_data)))
                    return (None, -1)
                time.sleep(constants.I2C_CSR_SLEEP_SEC)
                csr_width = 8
                read_data = array('B', [00]*(csr_width+1))
                read_bytes = self.master.i2c_read(read_data = read_data, chip_inst=chip_inst)
                logger.debug(('read_data: {0}').format([hex(x) for x in read_data]))
                if read_bytes[0] != (csr_width + 1):
                    logger.error(('Read Error!  read_bytes:{0}'
                           ' Expected: {1}').format(read_bytes, (csr_width + 1)))
                    return (None, -1)
                if read_data[0] != 0x80:
                    logger.error(('Read status returned Error! {0}').format(read_data[0]))
                    return (None, -1)
                read_data = read_data[1:]
                word_array.extend(byte_array_to_words_be(read_data))
            logger.info('Peeked word_array: {0}'.format([hex(x) for x in word_array]))
            return (word_array, 0)

    # i2c csr write
    def i2c_csr_poke(self, csr_addr, word_array, chip_inst=None):
        """
        Performs the poke operation over i2c.

        Returns True if operation succeeded, else False.
        """
        logger.info(('I2C poke! chip_inst: {0} csr_addr: {1} word_array:{2}').format(
            chip_inst, hex(csr_addr), [hex(x) for x in word_array]))
        csr_width_words = len(word_array)
        if not (csr_width_words > 0):
            logger.error(('Invalid data length: {0}').format(csr_width_words))
            return False
        elif csr_width_words == 1: #Fast mode for single wide csr access
            csr_addr = struct.pack('>Q', csr_addr)
            csr_addr = list(struct.unpack('BBBBBBBB', csr_addr))
            csr_addr = csr_addr[(8-self.addr_width):] #Assuming csr address is always 6 bytes
            cmd_data = array('B', [0x01])
            cmd_data.extend(csr_addr)
            for word in word_array:
                logger.debug('word: {0}'.format(hex(word)))
                word = struct.pack('>Q', word)
                word = list(struct.unpack('BBBBBBBB', word))
                cmd_data.extend(word)
            logger.debug('poking bytes: {0}'.format([hex(x) for x in cmd_data]))
            sent_bytes = self.master.i2c_write(write_data = cmd_data, chip_inst=chip_inst)
            logger.debug('sent_bytes: {0}'.format(sent_bytes))
            if sent_bytes != len(cmd_data):
                logger.error(('Write Error! sent_bytes:{0}'
                       ' Expected: {1}').format(sent_bytes, len(cmd_data)))
                return False
            try:
                time.sleep(constants.I2C_CSR_SLEEP_SEC)
                status = array('B', [0x00])
                num_status_bytes = self.master.i2c_read(read_data = status, chip_inst=chip_inst)
                logger.debug('poke num_status_bytes:{0} status:{1}'.format(num_status_bytes, status))
                if num_status_bytes[0] != 1:
                    logger.error('Read Error!  status_bytes:{0} Expected:'
                                 '{1}'.format(num_status_bytes, 1))
                    return False
                if status[0] != 0x80:
                    logger.error('Write status returned Error!'
                                 ' {0}'.format(status[0]))
                    return False
            except Exception as e:
                logging.error(traceback.format_exc())
                return False
            return True
        else:
            ring_sel = csr_addr >> 35
            csr_addr = ((csr_addr & 0xffffffffff) |
                        ((0x3 << 60) |
                        ((csr_width_words & 0xf) << 54) |
                        (ring_sel << 49)))
            csr_addr = struct.pack('>Q', csr_addr)
            csr_addr = list(struct.unpack('BBBBBBBB', csr_addr))
            for i in range(csr_width_words):
                csr_data_addr = struct.pack('>Q', (i+1) * 8)
                csr_data_addr = list(struct.unpack('BBBBBBBB', csr_data_addr))
                csr_data_addr = csr_data_addr[(8-self.addr_width):]
                cmd_data = array('B', [0x01])
                cmd_data.extend(csr_data_addr)
                word = struct.pack('>Q', word_array[i])
                word = list(struct.unpack('BBBBBBBB', word))
                cmd_data.extend(word)
                logger.debug('poking bytes: {0}'.format([hex(x) for x in cmd_data]))
                sent_bytes = self.master.i2c_write(write_data = cmd_data, chip_inst=chip_inst)
                logger.debug('sent_bytes: {0}'.format(sent_bytes))
                if sent_bytes != len(cmd_data):
                    logger.error(('Write Error! sent_bytes:{0}'
                           ' Expected: {1}').format(sent_bytes, len(cmd_data)))
                    return False
                try:
                    time.sleep(constants.I2C_CSR_SLEEP_SEC)
                    status = array('B', [0x01])
                    status_bytes = self.master.i2c_read(read_data = status, chip_inst=chip_inst)
                    logger.debug('poke status_bytes:{0}'.format(status_bytes))
                    if status_bytes[0] != 1:
                        logger.debug('Read Error!  status_bytes:{0} Expected:'
                                     '{1}'.format(status_bytes, 1))
                        return False
                    if status[0] != 0x80:
                        logger.debug('Write status returned Error!'
                                     ' {0}'.format(status[0]))
                        return False
                except Exception as e:
                    logging.error(traceback.format_exc())
                    return False
            cmd_data = array('B', [0x01])
            csr_data_addr = struct.pack('>Q', 0)
            csr_data_addr = list(struct.unpack('BBBBBBBB', csr_data_addr))
            csr_data_addr = csr_data_addr[(8-self.addr_width):]
            cmd_data.extend(csr_data_addr)
            cmd_data.extend(csr_addr)
            logger.debug('poking bytes: {0}'.format([hex(x) for x in cmd_data]))
            sent_bytes = self.master.i2c_write(write_data = cmd_data, chip_inst=chip_inst)
            logger.debug('sent_bytes: {0}'.format(sent_bytes))
            if sent_bytes != len(cmd_data):
                logger.error(('Write Error! sent_bytes:{0}'
                       ' Expected: {1}').format(sent_bytes, len(cmd_data)))
                return False
            try:
                time.sleep(constants.I2C_CSR_SLEEP_SEC)
                status = array('B', [0x01])
                status_bytes = self.master.i2c_read(read_data = status, chip_inst=chip_inst)
                logger.debug('poke status_bytes:{0}'.format(status_bytes))
                if status_bytes[0] != 1:
                    logger.debug('Read Error!  status_bytes:{0} Expected:'
                                 '{1}'.format(status_bytes, 1))
                    return False
                if status[0] != 0x80:
                    logger.debug('Write status returned Error!'
                                 ' {0}'.format(status))
                    return False
            except Exception as e:
                logging.error(traceback.format_exc())
                return False
            return True

    def i2c_dbg_chal_cmd(self, cmd, data, chip_inst=None):
        self.__i2c_dbg_chal_fifo_flush(chip_inst)
        logger.debug('cmd: {0}'.format(hex(cmd)))
        byte_array = array('B', [0xC4])
        size = (0 if data is None else len(data)) + 4 + 4
        logger.debug('size: {0}'.format(size))
        s = struct.pack('<I', size)
        b = struct.unpack('BBBB',s)
        byte_array.extend(b)
        logger.debug('\nSend dbg chal cmd header: {0}'.format([hex(x) for x in byte_array]))
        sent_bytes = self.master.i2c_write(write_data = byte_array, chip_inst=chip_inst)
        if sent_bytes != len(byte_array):
            logger.error('Write dbg cmd/data Error! sent_bytes:{0}'.format(sent_bytes))
            return (False, 'i2c_write failed!')

        byte_array = array('B', [0x84])
        s = struct.pack('<I', cmd)
        b = struct.unpack('BBBB',s)
        byte_array.extend(b)
        logger.debug('\nSend dbg chal cmd {0}'.format([hex(x) for x in byte_array]))
        sent_bytes = self.master.i2c_write(write_data = byte_array, chip_inst=chip_inst)
        if sent_bytes != len(byte_array):
            logger.error('Write dbg cmd/data Error! sent_bytes:{0}'.format(sent_bytes))
            return (False, 'i2c_write failed!')

        num_bytes = 0 if data is None else len(data)
        i = 0
        flit_size = 48
        while i < num_bytes:
            if (num_bytes - i) >= flit_size:
                n = flit_size
            else:
                n = num_bytes - i
            tdata = array('B', [0x80 + (flit_size & 0x3f)])
            tdata.extend((data[i:i+n]))
            logger.debug(('i:{0} rem_bytes:{1} n:{2} tdata:{3}').format(i, num_bytes - i,
                                            n , list((tdata[1:1+flit_size]))))
            status = self.master.i2c_write(write_data = tdata, chip_inst=chip_inst)
            if status < 1:
                err_msg = ('i2c write Error!!! Expected sent_bytes: {0} return_status: {1}'
                        ' sent_total:{2}').format(len(tdata),
                            status, i)
                logger.error(err_msg)
                return (False, err_msg)
            if (status < len(tdata)):
                if status == 1:
                    retry += 1
                    if retry == 10:
                        err_msg = ('Error!!! i2c write stalled!!!! status: {0}'
                                ' sent_total:{1}').format(status, i)
                        logger.error(err_msg)
                        return (False, err_msg)
                else:
                    logger.info(('i2c write expected to send {0}'
                            ' bytes but sent: {1}').format(len(tdata), status))
                    i = i + (status - 1)
                    retry = 0
            else:
                retry = 0
                i = i + n
                logger.debug('successfully sent: {0} sent_total:{1}'.format(status, i))
            time.sleep(0.1)
        if num_bytes > 0:
            logger.info('Successfully transmitted {0} bytes!'.format(i))

        logger.debug('Sleeping to give time for hw(esp. emulation) to process the command!')
        time.sleep(constants.SBP_CMD_EXE_TIME_WAIT)
        (status, header) = self.__i2c_dbg_chal_cmd_header_read(chip_inst)
        if status is False:
            err_msg = 'Failed to read the header'
            logger.error(err_msg)
            return (False, err_msg)

        if len(header) != 4:
            err_msg = 'Invalid header length: {0} header:{1}'.format(len(header), header)
            logger.error(err_msg)
            return (False, err_msg)
        header = array('B', list(reversed(header[0:4])))
        length = int(binascii.hexlify(header), 16)
        length = length & 0xFFFF
        length -= 4
        rdata = None
        if (length  > 0):
            (status, rdata) = self.i2c_dbg_chal_nread(chip_inst, length)
        if status is True:
            if rdata is not None and len(rdata) != 0:
                header.extend(rdata)
            return (True, header)
        else:
            err_msg = rdata
            logger.error(err_msg)
            return (False, err_msg)

    def i2c_dbg_chal_nread(self, chip_inst, num_bytes):
        data = array('B', [])
        cur_cnt = 0
        iter_cnt = 0
        i = 0
        flit_size = 32
        while i< num_bytes:
            if (num_bytes - i) >= flit_size:
                n = flit_size
            else:
                n = num_bytes - i
            (status, rx_data) = self._i2c_dbg_chal_read(
                            chip_inst = chip_inst, length = n)
            if status == False:
                err_msg = rx_data
                logger.error(err_msg)
                return (False, err_msg)
            rx_cnt = len(rx_data) if rx_data else 0
            i += rx_cnt
            if rx_cnt > 0:
                    iter_cnt = 0
                    data.extend(rx_data[0:num_bytes])
            else:
                iter_cnt += 1
                if iter_cnt > 10:
                    if len(data) > 0:
                        logger.debug('Recived data: {0}'.format([hex(x) for x in data]))
                    err_msg = ('Timeout! insufficient number of bytes:{0}'
                              ' expected:{1}').format(i, num_bytes)
                    logger.error(err_msg)
                    return (False, err_msg)
            time.sleep(0.1)
        logger.debug('Recived data: {0}'.format([hex(x) for x in data]))
        logger.debug('Successfully Recived {0} bytes!'.format(i))
        return (True, data)

    def __i2c_dbg_chal_cmd_header_read(self, chip_inst):
        logger.debug('Reading the header cmd status header...!')
        data = array('B', [0x41])
        sent_bytes = self.master.i2c_write(write_data = data, chip_inst=chip_inst)
        if sent_bytes != len(data):
            logger.error('Get sbp cmd exec status write error! sent_bytes:{0}'.format(sent_bytes))
            return (False, 'i2c_write failed for get cmd status write!')

        time.sleep(constants.SBP_CMD_EXE_TIME_WAIT)
        rdata = array('B', [00])
        logger.debug('Reading the sbp cmd exec status byte!')
        self.master.i2c_read(read_data = rdata, chip_inst=chip_inst)
        logger.debug('Read data: {0}'.format(rdata))
        status_byte = rdata[0]
        status = status_byte >> 0x7
        if status:
            err_msg = 'CMD execution error({0})!'.format(status_byte)
            shim_action_state = status_byte >> 0x6
            if shim_action_state == 0x3:
                err_msg += ' *** Invalid shim action state ***'
            logger.error(err_msg)
            return (False, err_msg)

        length = status_byte & 0x7f
        if length < 4 or length > 64:
            err_msg = ('CMD execution error! Invalid number of bytes({0})!'
                    'Valid num bytes is 4-64').format(length)
            logger.error(err_msg)
            return (False, err_msg)

        (status, header) = self.i2c_dbg_chal_nread(chip_inst, 4)
        if status is True:
            return (True, header)
        else:
            err_msg = 'Falied to read the status bytes'
            logger.error(err_msg)
            return (False, err_msg)

    def __i2c_dbg_chal_fifo_flush(self, chip_inst):
        logger.debug('Flushing the FIFO...!')
        flushed = False
        while flushed == False:
            data = array('B', [0x41])
            sent_bytes = self.master.i2c_write(write_data = data, chip_inst=chip_inst)
            logger.debug('Write read status command. sent_bytes: {0}'.format(sent_bytes))
            if sent_bytes != len(data):
                logger.error('Get sbp cmd exec status write error! sent_bytes:{0}'.format(sent_bytes))
                return (False, 'i2c_write failed for get cmd status write!')

            time.sleep(0.1)
            rdata = array('B', [00])
            logger.debug('Reading the sbp cmd exec status byte!')
            self.master.i2c_read(read_data = rdata, chip_inst = chip_inst)
            logger.debug('Read data: {0}'.format(rdata))
            status_byte = rdata[0]
            status = status_byte >> 0x7
            length = status_byte & 0x7f
            if status != 0:
                logger.error('cmd error status:{0} is set! still proceeding with flush!'.format(status_byte))

            if (length  > 0):
                (status, data) = self.i2c_dbg_chal_nread(chip_inst, length)
                if status is True:
                    logger.debug('Flushed {0} bytes. data: {1}'.format(len(data), data))
                    flushed = False
                else:
                    logger.error('Failed to flush the data! Error: {0}'.format(data))
                    return False
            else:
                logger.debug('Flushed the FIFO!')
                flushed = True
        return True

    def _i2c_dbg_chal_read(self, chip_inst, length):
        logger.debug('read length: {0}'.format(length))
        if length > 64:
            err_msg = 'unsupported length: {0}'.format(length)
            logger.error(err_msg)
            return (False, err_msg)
        cmd_byte = 0x40 | (length+1)
        logger.debug('command_byte: {0}'.format(hex(cmd_byte)))
        data = array('B', [cmd_byte])
        sent_bytes = self.master.i2c_write(write_data = data, chip_inst=chip_inst)
        if sent_bytes != len(data):
            err_msg = 'write dbg read cmd error! sent_bytes:{0}'.format(sent_bytes)
            logger.error(err_msg)
            return (False, err_msg)

        time.sleep(0.1)
        rdata = array('B', [00] * (length+1))
        read_status_data = self.master.i2c_read(read_data = rdata, chip_inst=chip_inst)
        logger.debug('Read data: {0}'.format(rdata))
        logger.debug('rd read_status_data: {0}'.format(read_status_data))
        if read_status_data < 1:
            err_msg = 'i2c dbg read failed'
            logger.error(err_msg)
            return (False, err_msg)
        else:
            status = rdata[0] >> 7
            if status:
                err_msg = 'CMD execution error({0})!'.format(rdata[0])
                shim_action_state = rdata[0] >> 0x6
                if shim_action_state == 0x3:
                    err_msg += ' *** Invalid shim action state ***'
                logger.error(err_msg)
                return (False, err_msg)

            num_bytes = rdata[0] & 0x7f
            if status != 0:
                err_msg = 'Read dbg error: {0}!'.format(status)
                logger.error(err_msg)
                return (False, err_msg)
            elif num_bytes > 1:
                return (True, rdata[1:read_status_data[0]])
            else:
                return (True, None)

    def i2c_wedge_detect(self):
        if self.bmc_board is False:
            return self.master.i2c_wedge_detect()
        return False

    def i2c_unwedge(self):
        if self.bmc_board is False:
            return self.master.i2c_unwedge()
        return True

    def gpio_sck_trigger(self):
        if self.bmc_board is False:
            self.master.gpio_sck_trigger()
        return True


class csr2i2c(i2c):
    """
    i2c specialization for CSR2, because csr2 i2c access is different.

    TODO: remove duplication with version in isbp
    TODO: follow convention of not rethrowing exceptions, but returning error
          codes instead.
    """

    CSR2_ADDR_WIDTH_BYTES = 4

    def __init__(self, dev_id=None, slave_addr=None,
            bmc_ip_address=None, bitrate=None, chip_type='s1'):
        super(csr2i2c, self).__init__(dev_id=dev_id, slave_addr=slave_addr,
                bmc_ip_address=bmc_ip_address, bitrate=bitrate,
                chip_type=chip_type,
                addr_width=csr2i2c.CSR2_ADDR_WIDTH_BYTES)

    def _poke_qword(self, address, qword, chip_inst=None):
        """
        Internal method for poking a single qword.

        Returns True on success, False on failure.
        """
        logger.debug('csr2 qword_poke csr2_addr:{0} qword={1}, chip_inst:{2}'.format(hex(address), hex(qword), chip_inst))
        cmd_data = array('B', [0x01])

        csr_addr = struct.pack('>I', address)
        csr_addr = list(struct.unpack('BBBB', csr_addr))
        cmd_data.extend(csr_addr)

        qword = struct.pack('>Q', qword)
        qword = list(struct.unpack('BBBBBBBB', qword))
        cmd_data.extend(qword)

        logger.debug('csr2 poking bytes: {0}'.format(list(map(hex, cmd_data))))
        sent_bytes = self.master.i2c_write(write_data = cmd_data, chip_inst=chip_inst)
        logger.debug('csr2 sent_bytes: {0}'.format(sent_bytes))
        if sent_bytes != len(cmd_data):
            logger.error(('csr2 Write Error! sent_bytes:{0} Expected: {1}').format(sent_bytes, len(cmd_data)))
            return False
        try:
            time.sleep(constants.I2C_CSR_SLEEP_SEC)
            status = array('B', [0x00])
            num_status_bytes = self.master.i2c_read(read_data = status, chip_inst=chip_inst)
            logger.debug('csr2 poke num_status_bytes:{0} status:{1}'.format(num_status_bytes, hex(status[0])))
            if num_status_bytes[0] != 1:
                logger.error('csr2 Read Error!  status_bytes:{0} Expected: {1}'.format(num_status_bytes, 1))
                return False
            if status[0] != 0x80:
                logger.error('csr2 Write status returned Error! {0}'.format(status[0]))
                return False
        except Exception as e:
            logging.error(e)
            logging.error(traceback.format_exc())
            return False
        return True

    def _peek_qword(self, address, chip_inst=None):
        """
        Internal method for peeking at a single qword.

        Returns a tuple of (success, word) where success is a boolean.
        """
        logger.debug('csr2 qword_peek csr2_addr:{0} chip_inst:{1}'.format(hex(address), chip_inst))
        csr_addr = struct.pack('>I', address)
        csr_addr = list(struct.unpack('BBBB', csr_addr))
        cmd_data = array('B', [0x00])
        cmd_data.extend(csr_addr)
        logger.debug('csr2 cmd_data bytes: {0}'.format(list(map(hex, cmd_data))))
        sent_bytes = self.master.i2c_write(write_data = cmd_data, chip_inst=chip_inst)
        logger.debug('csr2 sent_bytes: {0}'.format(sent_bytes))
        if sent_bytes != len(cmd_data):
            logger.error(('csr2 Write Error! sent_bytes:{0} Expected: {1}').format(sent_bytes, len(cmd_data)))
            return (False, None)
        try:
            time.sleep(constants.I2C_CSR_SLEEP_SEC)
            read_data = array('B', [00]*(8 + 1))
            read_bytes = self.master.i2c_read(read_data = read_data, chip_inst=chip_inst)
            logger.debug(('csr2 read_bytes: {0} read_data: {1}').format(read_bytes, list(map(hex, read_data))))
            if read_bytes[0] != (8+1):
                logger.error(('csr2 Read Error! read_bytes:{0} Expected: {1}').format(read_bytes, (8 + 1)))
                return (False, None)
            if read_data[0] != 0x80:
                logger.error(('csr2 Read status returned Error! {0}').format(read_data[0]))
                return (False, read_data[0]&0xf)

            read_data = read_data[1:]
            qword = struct.unpack('>Q', struct.pack('B'*8, *read_data))[0]
            return (True, qword)
        except Exception as e:
            logging.error(traceback.format_exc())
            return (False, None)

    def _peek_wide_qword(self, address, wlen, chip_inst=None):
        """
        Internal method for peeking at a register that is > 1 qword in length.

        Returns a tuple of (success, word) where success is a boolean.
        """
        logger.debug('csr2 qword_wide_peek csr2_addr:{0} length:{1} chip_inst:{2}'.format(hex(address), hex(wlen),
                                                                                             chip_inst))
        ######### using native direct poke for wide reg csrctl ##################
        qword = (((0x3F & wlen) << 36) | ((0xF & 0x2) << 32) | address) & 0xFFFFFFFFFFFFFFFF
        CSRCTL_REGISTER = 0x00002158
        logger.debug(('poke at_csr_addr={0} qword={1}').format(hex(CSRCTL_REGISTER), hex(qword)))
        self._poke_qword(CSRCTL_REGISTER, qword, chip_inst)
        ######### using self direct peek for wide reg csrctl data ##############
        try:
            CSRCTL_DATA_ADDR = 0x00002100
            qwords = []
            for i in range(wlen):
                at_csr_addr = CSRCTL_DATA_ADDR + (i * 8)
                (status, qword) = self._peek_qword(at_csr_addr, chip_inst)
                if not status:
                    raise Exception('wide peek operation failed ...')
                qwords.append(qword)
            return True, qwords
        except Exception as e:
            logging.error(traceback.format_exc())
            return False, None

    def _poke_wide_qword(self, address, qwords, chip_inst=None):
        """
        Internal method for poking values into a register that is > 1 qword
        in length.
        """
        logger.debug('wide csr2 qword_poke csr2_addr:{0} qwords={1}, chip_inst:{2}'.format(hex(address),
                                                                                              qwords, chip_inst))
        ######### using self direct poke for wide reg csrctl data ##############
        CSRCTL_DATA_ADDR = 0x00002100
        for (i, qword) in enumerate(qwords):
            at_csr_addr = CSRCTL_DATA_ADDR + (i * 8)
            logger.debug(('poke at_csr_addr={0} qword={1}').format(hex(at_csr_addr), hex(qword)))
            self._poke_qword(at_csr_addr, qword, chip_inst)
        ######### using self direct poke for wide reg csrctl ##################
        qword = (((0x3F & len(qwords)) << 36) | ((0xF & 0x3) << 32) | address ) & 0xFFFFFFFFFFFFFFFF
        CSRCTL_REGISTER = 0x00002158
        logger.debug(('poke at_csr_addr={0} qword={1}').format(hex(CSRCTL_REGISTER), hex(qword)))
        self._poke_qword(CSRCTL_REGISTER, qword, chip_inst)
        return True

    def i2c_csr_peek(self, csr_addr, csr_width_words, chip_inst=None):
        """
        Overrides the method from the base i2c class to provide S1
        functionality.
        """
        qwords = []
        n_qwords = csr_width_words

        logger.debug('csr2 I2C peek! chip_inst: {0} csr_addr: {1} n_qwords:{2}'.format(chip_inst, hex(csr_addr), n_qwords))
        if not n_qwords or n_qwords == 0:
            logger.error(('csr2 peek n_qwords={0}').format(n_qwords))
            return None, -1
        elif n_qwords == 1:
            at_csr_addr = csr_addr
            try:
                (status, qword) = self._peek_qword(at_csr_addr, chip_inst)
                if not status:
                    raise Exception('peek operation failed ...')
                qwords.append(qword)
            except Exception as e:
                logger.error('csr2 peek failed for at_csr_addr={0}'.format(at_csr_addr))
                raise Exception('peek operation failed ...')
        else:
            try:
                (status, qwords) = self._peek_wide_qword(csr_addr, n_qwords, chip_inst)
                if not status:
                    raise Exception('wide peek operation failed ...')
            except Exception as e:
                logger.error('csr2 wide peek failed for at_csr_addr={0}'.format(csr_addr))
                logging.error(traceback.format_exc())
                raise Exception('wide peek api operation failed ...')

        return qwords, 0

    def i2c_csr_poke(self, csr_addr, word_array, chip_inst=None):
        """
        Overrides the method from the base i2c class to provide S1
        functionality.
        """
        logger.debug('csr2 I2C poke! chip_inst: {0} csr_addr: {1} poke_array:{2}'.format(chip_inst,
                                                                                           hex(csr_addr),
                                                                                           list(map(hex, word_array))))
        if not word_array:
            logger.error('csr2 poke array empty ...')
            return False
        elif len(word_array) == 1: # direct
            qword = word_array[0]
            at_csr_addr = csr_addr
            logger.debug('poke at_csr_addr={0} qword={1}'.format(hex(at_csr_addr), hex(qword)))
            status = self._poke_qword(at_csr_addr, qword, chip_inst)
            if not status:
                raise Exception('poke operation failed ...')
        else:
            try:
                (status) = self._poke_wide_qword(csr_addr, word_array, chip_inst)
                if not status:
                    raise Exception('wide poke operation failed ...')
            except Exception as e:
                logger.error(('csr2 wide poke failed for at_csr_addr={0}').format(csr_addr))
                logging.error(traceback.format_exc())
                raise Exception('wide poke api operation failed ...')
        return True
