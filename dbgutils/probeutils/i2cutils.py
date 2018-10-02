#!/usr/bin/env python

import sys, os
from aardvark_py import *
from array import array
import binascii
import time
import logging
import traceback
from i2cdev import *

logger = logging.getLogger('i2cutils')
logger.setLevel(logging.INFO)

class constants(object):
    F1_I2C_SLAVE_ADDR = 0x73
    IC_DEVICE_FEATURE_MASK = 0x1B
    F1_DBG_CHALLANGE_FIFO_SIZE = 64
    IC_DEVICE_MODE_I2C = 0x2
    IC_DEVICE_MODE_GPIO = 0x0
    I2C_XFER_BIT_RATE = 1
    SBP_CMD_EXE_TIME_WAIT = 0.5
    I2C_CSR_SLEEP_SEC    = 0.001

# Converts byte array to big-endian 64-bit words
def byte_array_to_words_be(byte_array):
    logger.debug('byte_array: {0}'.format(byte_array))
    words = list()
    byte_attay_size = len(byte_array)
    word_array_size = byte_attay_size / 8
    for i in range(word_array_size):
        val = int(binascii.hexlify(byte_array[i:i+8]), 16)
        words.extend([val])
        i += 8

    remaining_bytes = len(byte_array) % 8
    if remaining_bytes != 0:
        last_word = byte_array[-remaining_bytes:]
        last_word.extend(array('B', [0x00] * (8 - remaining_bytes)))
        val = int(binascii.hexlify(byte_array[i, i + 8]), 16)
        words.extend(val)
    logger.debug('word_array: {0}'.format([hex(x) for x in words]))

    return words

class i2c:
    def __init__(self, dev_id, slave_addr):
        self.dev_id = dev_id
        self.slave_addr = slave_addr
        self.handle = None

    # Check i2c device presence and open the device.
    # Returns the device handle
    def i2c_connect(self):
        dev_idx = aardvark_i2c_spi_dev_index_from_serial(self.dev_id)
        if dev_idx is None:
            dev_list = aardvark_i2c_spi_dev_list()
            status_msg = (('Failed to detect i2c device: {0}!'
                           ' dev_list: {1}').format(self.dev_id, dev_list))
            logger.error(status_msg)
            return (False, status_msg)
        n_devs, devs = aa_find_devices(dev_idx+1)
        logger.debug('n_devs:{0} devs:'.format(n_devs))
        logger.debug(devs)
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

        status = aa_i2c_bitrate(h, constants.I2C_XFER_BIT_RATE)
        if status != constants.I2C_XFER_BIT_RATE:
            status_msg = ('Error Configuring the bitrate!'
                    ' {0}({1})').format(aa_status_string(status), status)
            logger.error(status_msg)
            return (False, status_msg)

        logger.info('i2c dev is connected. handle: {0}'.format(h))
        self.handle = h
        return (True, h)

    # Free the i2c bus and close the device handle
    def i2c_disconnect(self):
        logger.debug('Disconnect request')
        h = self.handle
        status = aa_i2c_free_bus(h)
        logger.debug('Free Bus: {0}'.format(aa_status_string(status)))
        status = aa_close(h)
        self.handle = None 
        logger.debug('Closed i2c handle')

    # i2c csr read
    def i2c_csr_peek(self, csr_addr, csr_width_words):
        h = self.handle
        logger.info(('I2C peek csr_addr:{0}'
               ' csr_width_words:{1}').format(hex(csr_addr), csr_width_words))
        if csr_width_words == 0:
            logger.error('csr width expected should be non-zero positive number')
            return None
        elif csr_width_words == 1: #Fast mode for single wide csr access
            csr_addr = struct.pack('>Q', csr_addr)
            csr_addr = list(struct.unpack('BBBBBBBB', csr_addr))
            csr_addr = csr_addr[3:]
            cmd = array('B', [0x00])
            cmd.extend(csr_addr)
            logger.debug(cmd)
            logger.info('i2c slave addr: {0}'.format(self.slave_addr))
            sent_bytes = aa_i2c_write(h, self.slave_addr, 0, cmd)
            logger.debug('sent_bytes: {0}'.format(sent_bytes))
            if sent_bytes != len(cmd):
                logger.error(('Write Error! sent_bytes:{0}'
                       ' Expected: {1}').format(sent_bytes, len(cmd)))
                return None
            time.sleep(constants.I2C_CSR_SLEEP_SEC)
            csr_width = csr_width_words * 8
            read_data = array('B', [00]*(csr_width+1))
            read_bytes = aa_i2c_read(h, self.slave_addr, 0, read_data)
            logger.info(('read_data: {0}').format([hex(x) for x in read_data]))
            if read_bytes[0] != (csr_width + 1):
                logger.error(('Read Error!  read_bytes:{0}'
                       ' Expected: {1}').format(read_bytes, (csr_width + 1)))
                return None
            if read_data[0] != 0x80:
                logger.error(('Read status returned Error! {0}').format(
                    aa_status_string(read_data[0])))
                return None

            read_data = read_data[1:]
            word_array = byte_array_to_words_be(read_data)
            logger.debug('Peeked word_array: {0}'.format([hex(x) for x in word_array]))
            return word_array
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
            csr_data_addr = csr_data_addr[3:]
            cmd_data.extend(csr_data_addr)
            cmd_data.extend(csr_addr)
            logger.debug('poking bytes: {0}'.format([hex(x) for x in cmd_data]))
            sent_bytes = aa_i2c_write(h, self.slave_addr, 0, cmd_data)
            logger.debug('sent_bytes: {0}'.format(sent_bytes))
            try:
                if sent_bytes != len(cmd_data):
                    logger.error(('Write Error! sent_bytes:{0}'
                           ' Expected: {1}').format(sent_bytes, len(cmd_data)))
                    return False
                time.sleep(constants.I2C_CSR_SLEEP_SEC)
                status = array('B', [0x01])
                status_bytes = aa_i2c_read(h, self.slave_addr, 0, status)
                logger.debug('poke status_bytes:{0}'.format(status_bytes))
                if status_bytes[0] != 1:
                    logger.debug('Read Error!  status_bytes:{0} Expected:'
                                 '{1}'.format(status_bytes, 1))
                    return False
                if status[0] != 0x80:
                    logger.debug('Write status returned Error!'
                                 ' {0}'.format(aa_status_string(status[0])))
                    return False
            except Exception as e:
                logging.error(traceback.format_exc())
                return False
            word_array = list() 
            for i in range(csr_width_words):
                csr_data_addr = struct.pack('>Q', (i+1) * 8)
                csr_data_addr = list(struct.unpack('BBBBBBBB', csr_data_addr))
                csr_data_addr = csr_data_addr[3:]
                cmd_data = array('B', [0x00])
                cmd_data.extend(csr_data_addr)
                sent_bytes = aa_i2c_write(h, self.slave_addr, 0, cmd_data)
                logger.debug('sent_bytes: {0}'.format(sent_bytes))
                if sent_bytes != len(cmd_data):
                    logger.error(('Write Error! sent_bytes:{0}'
                       ' Expected: {1}').format(sent_bytes, len(cmd_data)))
                    return None
                time.sleep(constants.I2C_CSR_SLEEP_SEC)
                csr_width = 8
                read_data = array('B', [00]*(csr_width+1))
                read_bytes = aa_i2c_read(h, self.slave_addr, 0, read_data)
                logger.info(('read_data: {0}').format([hex(x) for x in read_data]))
                if read_bytes[0] != (csr_width + 1):
                    logger.error(('Read Error!  read_bytes:{0}'
                           ' Expected: {1}').format(read_bytes, (csr_width + 1)))
                    return None
                if read_data[0] != 0x80:
                    logger.error(('Read status returned Error! {0}').format(
                        aa_status_string(read_data[0])))
                    return None
                read_data = read_data[1:]
                word_array.extend(byte_array_to_words_be(read_data))
            logger.info('Peeked word_array: {0}'.format([hex(x) for x in word_array]))
            return word_array

    # i2c csr write
    def i2c_csr_poke(self, csr_addr, csr_width_words, word_array):
        h = self.handle
        logger.info(('Starting I2C poke. csr_addr: {0} csr_width_words: {1}'
              ' word_array:{2}').format(hex(csr_addr), csr_width_words,
                                        [hex(x) for x in word_array]))
        if csr_width_words != len(word_array):
            logger.error(('Insufficient data! Expected: {0}'
                   ' data length: {0}').format(csr_width_words, len(word_array)))
            return False

        if csr_width_words == 0:
            logger.error('csr width expected should be non-zero positive number')
            return None
        elif csr_width_words == 1: #Fast mode for single wide csr access
            csr_addr = struct.pack('>Q', csr_addr)
            csr_addr = list(struct.unpack('BBBBBBBB', csr_addr))
            csr_addr = csr_addr[3:] #Assuming csr address is always 6 bytes
            cmd_data = array('B', [0x01])
            cmd_data.extend(csr_addr)
            for word in word_array:
                word = struct.pack('>Q', word)
                word = list(struct.unpack('BBBBBBBB', word))
                cmd_data.extend(word)
            logger.debug('poking bytes: {0}'.format([hex(x) for x in cmd_data]))
            sent_bytes = aa_i2c_write(h, self.slave_addr, 0, cmd_data)
            logger.debug('sent_bytes: {0}'.format(sent_bytes))

            try:
                if sent_bytes != len(cmd_data):
                    logger.error(('Write Error! sent_bytes:{0}'
                           ' Expected: {1}').format(sent_bytes, len(cmd_data)))
                    return False
                time.sleep(constants.I2C_CSR_SLEEP_SEC)
                status = array('B', [0x01])
                status_bytes = aa_i2c_read(h, self.slave_addr, 0, status)
                logger.debug('poke status_bytes:{0}'.format(status_bytes))
                if status_bytes[0] != 1:
                    logger.debug('Read Error!  status_bytes:{0} Expected:'
                                 '{1}'.format(status_bytes, 1))
                    return False
                if status[0] != 0x80:
                    logger.debug('Write status returned Error!'
                                 ' {0}'.format(aa_status_string(status[0])))
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
                csr_data_addr = csr_data_addr[3:]
                cmd_data = array('B', [0x01])
                cmd_data.extend(csr_data_addr)
                word = struct.pack('>Q', word_array[i])
                word = list(struct.unpack('BBBBBBBB', word))
                cmd_data.extend(word)
                logger.debug('poking bytes: {0}'.format([hex(x) for x in cmd_data]))
                sent_bytes = aa_i2c_write(h, self.slave_addr, 0, cmd_data)
                logger.debug('sent_bytes: {0}'.format(sent_bytes))
                try:
                    if sent_bytes != len(cmd_data):
                        logger.error(('Write Error! sent_bytes:{0}'
                               ' Expected: {1}').format(sent_bytes, len(cmd_data)))
                        return False
                    time.sleep(constants.I2C_CSR_SLEEP_SEC)
                    status = array('B', [0x01])
                    status_bytes = aa_i2c_read(h, self.slave_addr, 0, status)
                    logger.debug('poke status_bytes:{0}'.format(status_bytes))
                    if status_bytes[0] != 1:
                        logger.debug('Read Error!  status_bytes:{0} Expected:'
                                     '{1}'.format(status_bytes, 1))
                        return False
                    if status[0] != 0x80:
                        logger.debug('Write status returned Error!'
                                     ' {0}'.format(aa_status_string(status[0])))
                        return False
                except Exception as e:
                    logging.error(traceback.format_exc())
                    return False
            cmd_data = array('B', [0x01])
            csr_data_addr = struct.pack('>Q', 0)
            csr_data_addr = list(struct.unpack('BBBBBBBB', csr_data_addr))
            csr_data_addr = csr_data_addr[3:]
            cmd_data.extend(csr_data_addr)
            cmd_data.extend(csr_addr)
            logger.debug('poking bytes: {0}'.format([hex(x) for x in cmd_data]))
            sent_bytes = aa_i2c_write(h, self.slave_addr, 0, cmd_data)
            logger.debug('sent_bytes: {0}'.format(sent_bytes))
            try:
                if sent_bytes != len(cmd_data):
                    logger.error(('Write Error! sent_bytes:{0}'
                           ' Expected: {1}').format(sent_bytes, len(cmd_data)))
                    return False
                time.sleep(constants.I2C_CSR_SLEEP_SEC)
                status = array('B', [0x01])
                status_bytes = aa_i2c_read(h, self.slave_addr, 0, status)
                logger.debug('poke status_bytes:{0}'.format(status_bytes))
                if status_bytes[0] != 1:
                    logger.debug('Read Error!  status_bytes:{0} Expected:'
                                 '{1}'.format(status_bytes, 1))
                    return False
                if status[0] != 0x80:
                    logger.debug('Write status returned Error!'
                                 ' {0}'.format(aa_status_string(status[0])))
                    return False
            except Exception as e:
                logging.error(traceback.format_exc())
                return False
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

    def i2c_dbg_chal_cmd(self, cmd, data):
        h = self.handle
        __i2c_dbg_chal_fifo_flush(h)
        logger.debug('cmd: {0}'.format(hex(cmd)))
        byte_array = array('B', [0xC4])
        size = (0 if data is None else len(data)) + 4 + 4
        logger.debug('size: {0}'.format(size))
        s = struct.pack('<I', size)
        b = struct.unpack('BBBB',s)
        byte_array.extend(b)
        logger.debug('\nSend dbg chal cmd header: {0}'.format([hex(x) for x in byte_array]))
        sent_bytes = aa_i2c_write(h, self.slave_addr, 0, byte_array)
        if sent_bytes != len(byte_array):
            logger.error('Write dbg cmd/data Error! sent_bytes:{0}'.format(sent_bytes))
            return (False, 'aa_i2c_write failed!')

        byte_array = array('B', [0x84])
        s = struct.pack('<I', cmd)
        b = struct.unpack('BBBB',s)
        byte_array.extend(b)
        logger.debug('\nSend dbg chal cmd {0}'.format([hex(x) for x in byte_array]))
        sent_bytes = aa_i2c_write(h, self.slave_addr, 0, byte_array)
        if sent_bytes != len(byte_array):
            logger.error('Write dbg cmd/data Error! sent_bytes:{0}'.format(sent_bytes))
            return (False, 'aa_i2c_write failed!')

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
            status = aa_i2c_write(h, self.slave_addr,
                                      0, tdata)
            if status < 1:
                err_msg = ('i2c write Error!!! Expected sent_bytes: {0} return_status: {1}'
                        ' error_code: {2} sent_total:{3}').format(len(tdata),
                            status, aa_status_string(status), i)
                logger.error(err_msg)
                return (False, err_msg)
            if (status < len(tdata)):
                if status == 1:
                    retry += 1
                    if retry == 10:
                        err_msg = ('Error!!! i2c write stalled!!!! status: {0}'
                                ' error_code: {1} sent_total:{2}').format(status, aa_status_string(status), i)
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
        (status, header) = __i2c_dbg_chal_cmd_header_read(h)
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
            (status, rdata) = i2c_dbg_chal_nread(h, length)
        if status is True:
            if rdata is not None and len(rdata) != 0:
                header.extend(rdata)
            return (True, header)
        else:
            err_msg = rdata
            logger.error(err_msg)
            return (False, err_msg)

    def i2c_dbg_chal_nread(self, num_bytes):
        h = self.handle
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
            (status, rx_data) = self._i2c_dbg_chal_read(n)
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
        logger.info('Successfully Recived {0} bytes!'.format(i))
        return (True, data)

    def __i2c_dbg_chal_cmd_header_read(self):
        logger.debug('Reading the header cmd status header...!')
        h = self.handle
        data = array('B', [0x41])
        sent_bytes = aa_i2c_write(h, self.slave_addr, 0, data)
        if sent_bytes != len(data):
            logger.error('Get sbp cmd exec status write error! sent_bytes:{0}'.format(sent_bytes))
            return (False, 'aa_i2c_write failed for get cmd status write!')

        time.sleep(constants.SBP_CMD_EXE_TIME_WAIT)
        rdata = array('B', [00])
        logger.debug('Reading the sbp cmd exec status byte!')
        aa_i2c_read(h, self.slave_addr, 0, rdata)
        logger.debug('Read data: {0}'.format(rdata))
        status_byte = rdata[0]
        status = status_byte >> 0x6
        length = status_byte & 0x3f
        if status != 0:
            err_msg = 'CMD execution error!'
            logger.error(err_msg)
            return (False, err_msg)

        if length < 4:
            err_msg = 'CMD execution error! Insufficient num header bytes!'
            logger.error(err_msg)
            return (False, err_msg)

        if (length  >= 4):
            (status, header) = self.i2c_dbg_chal_nread(4)
            if status is True:
                return (True, header)
            else:
                err_msg = 'Falied to read the status bytes'
                logger.error(err_msg)
                return (False, err_msg)
      
    def __i2c_dbg_chal_fifo_flush(self):
        logger.debug('Flushing the FIFO...!')
        h = self.handle
        flushed = False
        while flushed == False: 
            data = array('B', [0x41])
            sent_bytes = aa_i2c_write(h, self.slave_addr, 0, data)
            logger.debug('Write read status command. sent_bytes: {0}'.format(sent_bytes))
            if sent_bytes != len(data):
                logger.error('Get sbp cmd exec status write error! sent_bytes:{0}'.format(sent_bytes))
                return (False, 'aa_i2c_write failed for get cmd status write!')

            time.sleep(0.1)
            rdata = array('B', [00])
            logger.debug('Reading the sbp cmd exec status byte!')
            aa_i2c_read(h, self.slave_addr, 0, rdata)
            logger.debug('Read data: {0}'.format(rdata))
            status_byte = rdata[0]
            status = status_byte >> 0x6
            length = status_byte & 0x3f
            if status != 0:
                logger.error('cmd error status:{0} is set! still proceeding with flush!'.format(status))

            if (length  > 0):
                (status, data) = self.i2c_dbg_chal_nread(length)
                if status is True:
                    logger.debug('Flushed {0} bytes. data: {1}'.format(len(data), data))
                    flushed = False
                else:
                    logger.error('Failed to flush the data! Error: {0}'.format(data))
                    return False 
            else:
                logger.info('Flushed the FIFO!')
                flushed = True
        return True
          
    def _i2c_dbg_chal_read(self, length):
        logger.debug('read length: {0}'.format(length))
        h = self.handle
        if length > 64:
            err_msg = 'unsupported length: {0}'.format(length)
            logger.error(err_msg)
            return (False, err_msg)
        cmd_byte = 0x40 | (length+1)
        logger.debug('command_byte: {0}'.format(hex(cmd_byte)))
        data = array('B', [cmd_byte])
        sent_bytes = aa_i2c_write(h, self.slave_addr, 0, data)
        if sent_bytes != len(data):
            err_msg = 'write dbg read cmd error! sent_bytes:{0}'.format(sent_bytes)
            logger.error(err_msg)
            return (False, err_msg)

        time.sleep(0.1)
        rdata = array('B', [00] * (length+1))
        read_status_data = aa_i2c_read(h, self.slave_addr, 0, rdata)
        logger.debug('Read data: {0}'.format(rdata))
        logger.debug('rd read_status_data: {0}'.format(read_status_data))
        if read_status_data < 1:
            err_msg = 'i2c dbg read failed'
            logger.error(err_msg)
            return (False, err_msg)
        else:
            status = rdata[0] >> 6
            num_bytes = rdata[0] & 0x3f
            if status != 0:
                err_msg = 'Read dbg error: {0}!'.format(status)
                logger.error(err_msg)
                return (False, err_msg)
            elif num_bytes > 1:
                return (True, rdata[1:read_status_data[0]])
            else:
                return (True, None) 

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