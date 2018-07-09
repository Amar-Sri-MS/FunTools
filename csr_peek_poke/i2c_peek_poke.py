#!/usr/bin/env python

import sys, os
sys.path.append('aardvark')
from aardvark_py import *
from array import array
import binascii

class constants(object):
	F1_I2C_SLAVE_ADDR = 0x70
	F1_DBG_CHALLANGE_FIFO_SIZE = 64

def byte_array_to_8byte_words_be(byte_array):
    print byte_array
    words = list()
    byte_attay_size = len(byte_array)
    word_array_size = byte_attay_size / 8
    for i in range(word_array_size):
        val = int(binascii.hexlify(byte_array[i:i+8]), 16)
        words.extend([val])
        i += 8

    remaining_bytes = len(byte_array)%8
    if remaining_bytes != 0:
        last_word = byte_array[-remaining_bytes:]
        last_word.extend(array('B', [0x00]*(8 - remaining_bytes)))
        val = int(binascii.hexlify(byte_array[i, i+8]), 16)
        words.extend(val)

    #print [hex(x) for x in words]
    return words

data = None

def i2c_csr_peek(csr_addr, csr_width_words):
    print("Starting I2C peek ....!")
    """
    n_devs, devs = aa_find_devices(1)
    #print n_devs
    #print devs

    #print "n_devs:{0} devs:{1}".format(n_devs, devs)
    if not devs or not devs[0]:
        print "Failed to detect device!"
        return None
    dev_handle =  devs[0]
    #print "Dev handle: {0}".format(dev_handle)
    h = aa_open(dev_handle)
    features = aa_features(h)
    if features != 27:
        print("Invalid device features!: {0}".format(features))
        sys.exit(1)
    status = aa_i2c_free_bus(h)
    #print("Free Bus: {0}".format(aa_status_string(status)))
    status = aa_configure(h,2)
    #print "Configure i2c mode! status:{0}".format(status)
    status = aa_i2c_bitrate(h, 1)
    #print "Configure bitrate! status:{0}".format(status)

    csr_addr = struct.pack('>Q', csr_addr)
    csr_addr = list(struct.unpack('BBBBBBBB', csr_addr))
    csr_addr = csr_addr[3:]
    cmd = array('B', [0x00])
    cmd.extend(csr_addr)
    sent_bytes = aa_i2c_write(h, constants.F1_I2C_SLAVE_ADDR, 0, cmd)
    print "sent_bytes: {0}".format(sent_bytes)

    if sent_bytes != len(cmd):
        print "Write Error! sent_bytes:{0} Expected: {1}".format(sent_bytes, len(data))
        status = aa_i2c_free_bus(h)
        print("Free Bus: {0}".format(aa_status_string(status)))
        status = aa_close(h)
        print("Close: {0}".format(aa_status_string(status)))
        return None

    #print csr_width_words
    csr_width = csr_width_words * 8
    read_data = array('B', [00]*(csr_width+1))
    read_bytes = aa_i2c_read(h, constants.F1_I2C_SLAVE_ADDR, 0, read_data)
    if read_bytes != (csr_width + 1):
        print "Read Error!  read_bytes:{0} Expected: {1}".format(read_bytes, (csr_width + 1))
        return None
    if read_data[0] != 0x80:
        print "Read status returned Error! {}".format(aa_status_string(read_data[0]))
        return None

    status = aa_i2c_free_bus(h)
    print("Free Bus: {0}".format(aa_status_string(status)))
    status = aa_close(h)
    print("Close: {0}".format(aa_status_string(status)))

    read_data = read_data[1:]
    word_array = byte_array_to_8byte_words_be(read_data)
    print word_array
    return word_array
    """
    global data
    read_data = data
    word_array = byte_array_to_8byte_words_be(read_data)
    print word_array
    return word_array

def i2c_csr_poke(csr_addr, csr_width_words, word_array):
    print("Starting I2C poke ....!")
    if csr_width_words != len(word_array):
        print "Insufficient data! Expected: {} data length: {}".format(csr_width_words, len(word_array))
        return False

    """
    n_devs, devs = aa_find_devices(1)
    print "n_devs:{0} devs:{1}".format(n_devs, devs)
    dev_handle =  devs[0]
    print "Dev handle: {0}".format(dev_handle)
    h = aa_open(dev_handle)
    features = aa_features(h)
    if features != 27:
        print("Invalid device features!: {0}".format(features))
        sys.exit(1)
    status = aa_i2c_free_bus(h)
    print("Free Bus: {0}".format(aa_status_string(status)))
    status = aa_configure(h,2)
    print "Configure i2c mode! status:{0}".format(status)
    status = aa_i2c_bitrate(h, 1)
    print "Configure bitrate! status:{0}".format(status)
    """

    csr_addr = struct.pack('>Q', csr_addr)
    csr_addr = list(struct.unpack('BBBBBBBB', csr_addr))
    csr_addr = csr_addr[3:]
    cmd_data = array('B', [0x01])
    cmd_data.extend(csr_addr)

    for word in word_array:
        word = struct.pack('>Q', word)
        word = list(struct.unpack('BBBBBBBB', word))
        cmd_data.extend(word)

    print "poking bytes: {}".format([hex(x) for x in cmd_data])
    global data
    data = cmd_data[6:] #remove this
    """
    sent_bytes = aa_i2c_write(h, constants.F1_I2C_SLAVE_ADDR, 0, cmd_data)
    print "sent_bytes: {0}".format(sent_bytes)

    if sent_bytes != len(cmd):
        print "Write Error! sent_bytes:{0} Expected: {1}".format(sent_bytes, len(data))
        status = aa_i2c_free_bus(h)
        print("Free Bus: {0}".format(aa_status_string(status)))
        status = aa_close(h)
        print("Close: {0}".format(aa_status_string(status)))
        return False

    status = array('B', [00])
    status_bytes = aa_i2c_read(h, constants.F1_I2C_SLAVE_ADDR, 0, status)
    if status_bytes != (csr_width + 1):
        print "Read Error!  status_bytes:{0} Expected: {1}".format(status_bytes, 1)
        return False
    if status[0] != 0x80:
        print "Write status returned Error! {}".format(aa_status_string(status[0]))
        return False
    """
    return True

