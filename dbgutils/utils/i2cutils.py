#!/usr/bin/env python

import sys, os
from aardvark_py import *
from array import array
import binascii
import time
import logging
import traceback
from i2c_usb_dev import *

logger = logging.getLogger("jsocket.tserver")
logger.setLevel(logging.INFO)

logger = logging.getLogger("i2cutils")
logger.setLevel(logging.INFO)

class constants(object):
    F1_I2C_SLAVE_ADDR = 0x70
    SERVER_TCP_PORT = 55668
    IC_DEVICE_FEATURE_MASK = 0x1B

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

        status = array('B', [00])
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

