#!/usr/bin/env python

import sys, os
from aardvark_py import *
from array import array
import binascii
import time
import logging
import traceback
from i2cdev import *

logger = logging.getLogger("i2cutils")
logger.setLevel(logging.INFO)

class constants(object):
    F1_I2C_SLAVE_ADDR = 0x73
    SERVER_TCP_PORT = 55668
    IC_DEVICE_FEATURE_MASK = 0x1B
    F1_DBG_CHALLANGE_FIFO_SIZE = 64

# Converts byte array to big-endian 64-bit words
def byte_array_to_words_be(byte_array):
    logger.debug("byte_array: {0}".format(byte_array))
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
    logger.debug("word_array: {0}".format([hex(x) for x in words]))

    return words

# Check i2c device presence and open the device.
# Returns the device handle
def i2c_connect(dev_id):
    dev_idx = aardvark_i2c_spi_dev_index_from_serial(dev_id)
    if dev_idx is None:
        dev_list = aardvark_i2c_spi_dev_list()
        status_msg = (("Failed to detect i2c device: {0}!"
                       " dev_list: {1}").format(dev_id, dev_list))
        logger.error(status_msg)
        return (False, status_msg)
    n_devs, devs = aa_find_devices(dev_idx+1)
    logger.debug("n_devs:{0} devs:".format(n_devs))
    logger.debug(devs)
    if not devs or devs[dev_idx] is None:
        status_msg = "Failed to detect i2c device! dev_list: {0}".format(dev_list)
        logger.error(status_msg)
        return (False, status_msg)

    dev_handle =  devs[dev_idx]
    logger.debug("Dev handle: {0}".format(dev_handle))
    h = aa_open(dev_handle)
    if h == 0x8000:
        status_msg = "Error opening i2c device. Invalid dev Handle! {0}".format(h)
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

    status = aa_i2c_bitrate(h, 1)
    if status != 1:
        status_msg = ('Error Configuring the bitrate!'
                ' {0}({1})').format(aa_status_string(status), status)
        logger.error(status_msg)
        return (False, status_msg)

    logger.info("i2c dev is connected. handle: {0}".format(h))
    return (True, h)

# Free the i2c bus and close the device handle
def i2c_disconnect(h):
    logger.debug("Disconnect request")
    status = aa_i2c_free_bus(h)
    logger.debug("Free Bus: {0}".format(aa_status_string(status)))
    status = aa_close(h)
    logger.debug("Closed i2c handle")

# i2c csr read
def i2c_csr_peek(h, csr_addr, csr_width_words):
    logger.info(("I2C peek csr_addr:{0}"
           " csr_width_words:{1}").format(hex(csr_addr), csr_width_words))
    csr_addr = struct.pack('>Q', csr_addr)
    csr_addr = list(struct.unpack('BBBBBBBB', csr_addr))
    csr_addr = csr_addr[3:]
    cmd = array('B', [0x00])
    cmd.extend(csr_addr)
    logger.debug(cmd)
    sent_bytes = aa_i2c_write(h, constants.F1_I2C_SLAVE_ADDR, 0, cmd)
    logger.debug("sent_bytes: {0}".format(sent_bytes))
    if sent_bytes != len(cmd):
        logger.error(("Write Error! sent_bytes:{0}"
               " Expected: {1}").format(sent_bytes, len(cmd)))
        return None
    csr_width = csr_width_words * 8
    read_data = array('B', [00]*(csr_width+1))
    read_bytes = aa_i2c_read(h, constants.F1_I2C_SLAVE_ADDR, 0, read_data)
    logger.info(("read_data: {0}").format([hex(x) for x in read_data]))
    if read_bytes[0] != (csr_width + 1):
        logger.error(("Read Error!  read_bytes:{0}"
               " Expected: {1}").format(read_bytes, (csr_width + 1)))
        return None
    if read_data[0] != 0x80:
        logger.error(("Read status returned Error! {0}").format(
            aa_status_string(read_data[0])))
        return None

    read_data = read_data[1:]
    word_array = byte_array_to_words_be(read_data)
    logger.debug("Peeked word_array: {0}".format([hex(x) for x in word_array]))
    return word_array

# i2c csr write
def i2c_csr_poke(h, csr_addr, csr_width_words, word_array):
    logger.info(("Starting I2C poke. csr_addr: {0} csr_width_words: {1}"
          " word_array:{2}").format(hex(csr_addr), csr_width_words,
                                    [hex(x) for x in word_array]))
    if csr_width_words != len(word_array):
        logger.error(("Insufficient data! Expected: {0}"
               " data length: {0}").format(csr_width_words, len(word_array)))
        return False

    csr_addr = struct.pack('>Q', csr_addr)
    csr_addr = list(struct.unpack('BBBBBBBB', csr_addr))
    csr_addr = csr_addr[3:] #Assuming csr address is always 6 bytes
    cmd_data = array('B', [0x01])
    cmd_data.extend(csr_addr)
    for word in word_array:
        word = struct.pack('>Q', word)
        word = list(struct.unpack('BBBBBBBB', word))
        cmd_data.extend(word)
    logger.debug("poking bytes: {0}".format([hex(x) for x in cmd_data]))
    sent_bytes = aa_i2c_write(h, constants.F1_I2C_SLAVE_ADDR, 0, cmd_data)
    logger.debug("sent_bytes: {0}".format(sent_bytes))

    try:
        if sent_bytes != len(cmd_data):
            logger.error(("Write Error! sent_bytes:{0}"
                   " Expected: {1}").format(sent_bytes, len(cmd_data)))
            return False

        status = array('B', [01])
        status_bytes = aa_i2c_read(h, constants.F1_I2C_SLAVE_ADDR, 0, status)
        logger.debug("poke status_bytes:{0}".format(status_bytes))
        if status_bytes[0] != 1:
            logger.debug("Read Error!  status_bytes:{0} Expected:"
                         "{1}".format(status_bytes, 1))
            return False
        if status[0] != 0x80:
            logger.debug("Write status returned Error!"
                         " {0}".format(aa_status_string(status[0])))
            return False
    except Exception as e:
        logging.error(traceback.format_exc())
        return False
    return True

def gpio_sck_trigger(h):
    print("Starting GPIO test ....!")

    status = aa_configure(h, 0)
    print status
    print "Configure GPIO mode! status:" + aa_status_string(status)

    status = aa_gpio_direction(h, 0x8)
    print "3.Configuring direction. status: " + aa_status_string(status)

    status = aa_gpio_set(h, 0x8)
    print "gpio set. status: " + aa_status_string(status)

    sleep(0.00001)
    status = aa_gpio_set(h, 0x00)
    print "gpio set. status: " + aa_status_string(status)

    sleep(0.00001)
    status = aa_gpio_set(h, 0x8)
    print "gpio set. status: " + aa_status_string(status)

    print "Done!"

def i2c_dbg_chal_cmd(h, cmd, data):
    __i2c_dbg_chal_fifo_flush(h)
    print "cmd: {0}".format(cmd)
    byte_array = array('B', [0xC4])
    size = (0 if data is None else len(data)) + 4 + 4
    print 'size: {0}'.format(size)
    s = struct.pack('<I', size)
    b = struct.unpack('BBBB',s)
    byte_array.extend(b)
    print "\nSending command0: {0}".format([hex(x) for x in byte_array])
    sent_bytes = aa_i2c_write(h, constants.F1_I2C_SLAVE_ADDR, 0, byte_array)
    print "sent_bytes: {0}".format(sent_bytes)
    if sent_bytes != len(byte_array):
        print "Write dbg cmd/data Error! sent_bytes:{0}".format(sent_bytes)
        return (False, "aa_i2c_write failed!")

    byte_array = array('B', [0x84])
    s = struct.pack('<I', cmd)
    b = struct.unpack('BBBB',s)
    byte_array.extend(b)
    print "\nSending command1: {0}".format([hex(x) for x in byte_array])
    sent_bytes = aa_i2c_write(h, constants.F1_I2C_SLAVE_ADDR, 0, byte_array)
    print "sent_bytes: {0}".format(sent_bytes)
    if sent_bytes != len(byte_array):
        print "Write dbg cmd/data Error! sent_bytes:{0}".format(sent_bytes)
        return (False, "aa_i2c_write failed!")

    num_bytes = 0 if data is None else len(data)
    i = 0
    flit_size = 32
    while i < num_bytes:
        if (num_bytes - i) >= flit_size:
            n = flit_size
        else:
            n = num_bytes - i
        tdata = array('B', [0x80 + (flit_size & 0x3f)])
        tdata.extend((data[i:i+n]))
        print(('i:{0} rem_bytes:{1} n:{2} tdata:{3}').format(i, num_bytes - i,
                                        n , list((tdata[1:1+flit_size]))))
        status = aa_i2c_write(h, constants.F1_I2C_SLAVE_ADDR,
                                  0, tdata)
        if status < 1:
            err_msg = ('i2c write Error!!! Expected sent_bytes: {0} return_status: {1}'
                    ' error_code: {2} sent_total:{3}').format(len(tdata),
                        status, aa_status_string(status), i)
            print err_msg
            gpio_sck_trigger(h)
            sys.exit(1)
            #return (False, err_msg)
        if (status < len(tdata)):
            if status == 1:
                retry += 1
                if retry == 10:
                    err_msg = ('Error!!! i2c write stalled!!!! status: {0}'
                            ' error_code: {1} sent_total:{2}').format(status, aa_status_string(status), i)
                    print err_msg
                    return (False, err_msg)
            else:
                print('i2c write expected to send {0} bytes but sent: {1}').format(len(tdata), status) 
                i = i + (status - 1)
                retry = 0
        else:
            retry = 0
            i = i + n
            print "successfully sent: {0} sent_total:{1}".format(status, i)
        time.sleep(0.1)
    if num_bytes > 0:
        print "Successfully transmitted {0} bytes!".format(i)

    (status, header) = __i2c_dbg_chal_cmd_header_read(h)
    if status is False:
        err_msg = 'Failed to read the status'
        print err_msg 
        return (False, err_msg)

    if len(header) != 4:
        err_msg = 'Invalid header length: {0} header:{1}'.format(len(header), header)
        print err_msg 
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
        return (False, None)

def i2c_dbg_chal_nread(dev, num_bytes):
    data = array('B', [])
    cur_cnt = 0
    iter_cnt = 0
    i = 0
    flit_size = 4 
    while i< num_bytes:
        if (num_bytes - i) >= flit_size:
            n = flit_size
        else:
            n = num_bytes - i
        (status, rx_data) = _i2c_dbg_chal_read(dev, n)
        if status == False:
            sys.exit(1)
            #return (False, None)
        rx_cnt = len(rx_data) if rx_data else 0
        i += rx_cnt
        if rx_cnt > 0:
                iter_cnt = 0
                data.extend(rx_data[0:num_bytes])
        else:
            iter_cnt += 1
            if iter_cnt > 10:
                if len(data) > 0:
                    print "Recived data: {0}".format([hex(x) for x in data])
                print "Timeout! insufficient number of bytes:{0} expected:{1}".format(i, num_bytes)
                return (False, None)
        time.sleep(0.1)
    print "Recived data: {0}".format([hex(x) for x in data])
    print "Successfully Recived {0} bytes!".format(i)
    return (True, data)

def __i2c_dbg_chal_cmd_header_read(dev):
    print("Reading the header cmd status header...!")
    data = array('B', [0x41])
    sent_bytes = aa_i2c_write(dev, constants.F1_I2C_SLAVE_ADDR, 0, data)
    print "Write read status command sent_bytes: {0}".format(sent_bytes)
    if sent_bytes != len(data):
        print "Get sbp cmd exec status write error! sent_bytes:{0}".format(sent_bytes)
        return (False, "aa_i2c_write failed for get cmd status write!")

    time.sleep(0.1)
    rdata = array('B', [00])
    print('Reading the sbp cmd exec status byte!')
    aa_i2c_read(dev, constants.F1_I2C_SLAVE_ADDR, 0, rdata)
    print "Read data: {0}".format(rdata)
    status_byte = rdata[0]
    status = status_byte >> 0x6
    length = status_byte & 0x3f
    if status != 0:
        print "CMD execution error!"
        return (False, ["CMD execution error!"])

    if length < 4:
        return (False, ["CMD execution error! Insufficient num bytes header!"])

    if (length  >= 4):
        (status, header) = i2c_dbg_chal_nread(dev, 4)
        if status is True:
            return (True, header)
        else:
            return (False, "Falied to read the status bytes")
  
def __i2c_dbg_chal_fifo_flush(dev):
    print("Flushing the FIFO...!")
    flushed = False
    while flushed == False: 
        data = array('B', [0x41])
        sent_bytes = aa_i2c_write(dev, constants.F1_I2C_SLAVE_ADDR, 0, data)
        print 'Write read status command. sent_bytes: {0}'.format(sent_bytes)
        if sent_bytes != len(data):
            print 'Get sbp cmd exec status write error! sent_bytes:{0}'.format(sent_bytes)
            return (False, 'aa_i2c_write failed for get cmd status write!')

        time.sleep(0.1)
        rdata = array('B', [00])
        print('Reading the sbp cmd exec status byte!')
        aa_i2c_read(dev, constants.F1_I2C_SLAVE_ADDR, 0, rdata)
        print "Read data: {0}".format(rdata)
        status_byte = rdata[0]
        status = status_byte >> 0x6
        length = status_byte & 0x3f
        if status != 0:
            print "cmd error status:{0} is set! still proceeding with flush!".format(status)

        if (length  > 0):
            (status, data) = i2c_dbg_chal_nread(dev, length)
            if status is True:
                print 'Flushed {0} bytes. data: {1}'.format(len(data), data)
                flushed = False
            else:
                print 'Failed to flush the data! Error: {0}'.format(data)
                return False 
        else:
            print 'Finished flushing all data'
            flushed = True
    return True
      
def _i2c_dbg_chal_read(dev, length):
    print "read length: {0}".format(length)
    if length > 64:
        print 'unsupported length: {0}'.format(length)
        return (False, None)
    cmd_byte = 0x40 | (length+1)
    print "command_byte: {0}".format(hex(cmd_byte))
    data = array('B', [cmd_byte])
    sent_bytes = aa_i2c_write(dev, 0x73, 0, data)
    print "sent_bytes: {0}".format(sent_bytes)
    if sent_bytes != len(data):
        print "write dbg read cmd error! sent_bytes:{0}".format(sent_bytes)
        return (False, None)

    time.sleep(0.1)
    rdata = array('B', [00] * (length+1))
    read_status_data = aa_i2c_read(dev, 0x73, 0, rdata)
    print "Read data: {0}".format(rdata)
    print "rd read_status_data: {0}".format(read_status_data)
    if read_status_data < 1:
        print "i2c dbg read failed"
        return (False, None) 
    else:
        status = rdata[0] >> 6
        num_bytes = rdata[0] & 0x3f
        if status != 0:
            print "Read dbg error: {0}!".format(status)
            return (False, None) 
        elif num_bytes > 1:
            return (True, rdata[1:read_status_data[0]])
        else:
            return (True, None) 

