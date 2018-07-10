#!/usr/bin/env python

import sys, os
sys.path.append('aardvark')
from aardvark_py import *
from array import array
import binascii
import argparse
import threading

class constants(object):
    F1_I2C_SLAVE_ADDR = 0x70
    F1_DBG_CHALLANGE_FIFO_SIZE = 64

def byte_array_to_8byte_words_be(byte_array):
    print byte_array
    words = list()
    byte_attay_size = len(byte_array)
    word_array_size = byte_attay_size / 8
    print "byte_array_to_8byte_words_b1"
    for i in range(word_array_size):
        print "byte_array_to_8byte_words_b2 i"
        val = int(binascii.hexlify(byte_array[i:i+8]), 16)
        print "byte_array_to_8byte_words_b2 2"
        words.extend([val])
        i += 8

    print "byte_array_to_8byte_words_b2"
    remaining_bytes = len(byte_array)%8
    if remaining_bytes != 0:
        last_word = byte_array[-remaining_bytes:]
        last_word.extend(array('B', [0x00]*(8 - remaining_bytes)))
        val = int(binascii.hexlify(byte_array[i, i+8]), 16)
        words.extend(val)

    print "byte_array_to_8byte_words_b3"
    print [hex(x) for x in words]
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
    read_data = array('B')
    #print "peek*****{0}".format(csr_width_words * 8)
    #print csr_width_words * 8
    print csr_width_words
    print "Peeking *******"
    if data is None:
        print "peek*****{0}".format(csr_width_words*8)
        for i in range(csr_width_words*8):
            read_data.append(i)
        print "peek*****21"
        #read_data = array('B', [00] * csr_width_words * 8)
    else:
        read_data = data
    print "peek*****3"
    print read_data
    print "peek*****4"
    word_array = byte_array_to_8byte_words_be(read_data)
    print "peek*****5"
    print word_array
    print "peek*****6"
    return word_array

def i2c_csr_poke(csr_addr, csr_width_words, word_array):
    print("Starting I2C poke ....!")
    print csr_width_words
    print word_array
    if csr_width_words != len(word_array):
        print "Insufficient data! Expected: {} data length: {}".format(csr_width_words, len(word_array))
        return False

    print "poke"
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

    print "poke0"
    print word_array
    print "poke1"
    csr_addr = struct.pack('>Q', csr_addr)
    print "poke2"
    csr_addr = list(struct.unpack('BBBBBBBB', csr_addr))
    print "poke3"
    csr_addr = csr_addr[3:]
    print "poke4"
    cmd_data = array('B', [0x01])
    print "poke5"
    cmd_data.extend(csr_addr)
    print "poke6"

    for word in word_array:
        print "poke7 word: {0}".format(word)
        word = struct.pack('>Q', word)
        print "poke8 word: {0}".format(word)
        word = list(struct.unpack('BBBBBBBB', word))
        print "poke9 word: {0}".format(word)
        cmd_data.extend(word)
        print "poke10 word: {0}".format(word)

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



import jsocket
import logging

logger = logging.getLogger("jsocket.I2CServer")

class I2CServer(jsocket.ThreadedServer):
    def __init__(self):
        super(I2CServer, self).__init__()
        self.timeout = 2.0
        logger.warning("I2CServer init!")

    def _process_message(self, obj):
        """ virtual method """
        if obj != '':
            if obj['message'] == "new connection":
                logger.info("new connection.")

class I2CFactoryThread(jsocket.ServerFactoryThread):
    def __init__(self):
        super(I2CFactoryThread, self).__init__()
        self.timeout = 2.0
	self.i2c_handle = None

    def _process_message(self, obj):
        """ virtual method - Implementer must define protocol """
        print "process message!!!! pid: {0} {1}".format(os.getpid(), threading.current_thread())
        print obj
        if obj != '':
            logger.info(obj)
            if obj.get("CONNECT", None):
                """
                if self.i2c_handle:
                    self.i2c_handle.close()
                    aa_i2c_free_bus(self.i2c_handle)

                logger.info("Connection Request.")
                n_devs, devs = aa_find_devices(1)
                print "n_devs:{0} devs:{1}".format(n_devs, devs)
                if not devs or devs[0] is None:
                    status_msg = "Failed to detect i2c device!"
                    self.send_obj({"STATUS":[False, status_msg]})
                    print status_msg
                    return
                dev_handle =  devs[0]
                print "Dev handle: {0}".format(dev_handle)
                self.i2c_handle = aa_open(dev_handle)
                features = aa_features(self.i2c_handle)
                if features != 27:
                    status_msg = "Invalid device features!: {0}".format(features)
                    self.send_obj({"STATUS":[False, status_msg]})
                    print status_msg
                    return
                status = aa_i2c_free_bus(self.i2c_handle)
                print("Free Bus: {0}".format(aa_status_string(status)))
                status = aa_configure(self.i2c_handle,2)
                if status != 2:
                    status_msg = "Configure i2c mode! status:{0}".format(status)
                    self.send_obj({"STATUS":[False, status_msg]})
                    print status_msg
                    return
                status = aa_i2c_bitrate(self.i2c_handle, 1)
                if status != 1:
                    status_msg = "Configure bitrate! status:{0}".format(status)
                    self.send_obj({"STATUS":[False, status_msg]})
                    print status_msg
                    return
                """
                self.send_obj({"STATUS":[True, "i2c device is ready!"]})
            elif obj.get("CSR_PEEK", None):
                print "Peeking ..."
                csr_peek_args = obj.get("CSR_PEEK", None)
                if not csr_peek_args:
                    self.send_obj({"STATUS":[False, "Invalid peek args!"]})
                    return
                csr_addr = csr_peek_args.get("csr_addr", None)
                csr_width_words = csr_peek_args.get("csr_width", None)
                if not csr_addr or not csr_width_words:
                    self.send_obj({"STATUS":[False, "Invalid peek args!"]})
                    return
                print "csr_addr: {0} csr_width_words:{1}".format(csr_addr, csr_width_words)
                word_array = i2c_csr_peek(csr_addr, csr_width_words)
                #word_array = [00]
                print word_array
                print "Peeking ..."
                self.send_obj({"STATUS":[True, "NAG"],
                            "DATA":word_array})
                #print "csr_addr: {0} csr_width_words:{1} word_array:{2}".format(csr_addr, csr_width_words, word_array)
                #self.send_obj({"DATA":word_array})
                #return
            elif obj.get("CSR_POKE", None):
                csr_poke_args = obj.get("CSR_POKE", None)
                if not csr_poke_args:
                    self.send_obj({"STATUS":[False, "Invalid poke args!"]})
                    return
                csr_addr = csr_poke_args.get("csr_addr", None)
                csr_width_words = csr_poke_args.get("csr_width", None)
                word_array = csr_poke_args.get("csr_val", None)
                if not csr_addr or not csr_width_words or not word_array:
                    self.send_obj({"STATUS":[False, "Invalid peek args!"]})
                    return
                print "csr_addr: {0} csr_width_words:{1} word_array:{2}".format(csr_addr, csr_width_words, word_array)
                status = i2c_csr_poke(csr_addr, csr_width_words, word_array)
                self.send_obj({"STATUS":[status, ""]})
            elif obj.get("DISCONNECT", None):
                """
                #self.send_obj({"STATUS": [True, "Disconnected"]})
                print "Disconnect request"
                status = aa_i2c_free_bus(self.i2c_handle)
                print "Freed I2C bus"
                #print "Free Bus: {0}".format(aa_status_string(status))
                status = aa_close(self.i2c_handle)
                print "Closed i2c handle"
                status_msg = "Close: {0}".format(aa_status_string(status))
                #print status_msg
                print "Disconneced ***********"
                """

                self.send_obj({"STATUS":[True, "I2c is disconnected"]})
            else:
                print "Invalid msg!"
                self.send_obj({"STATUS":[False, "Invalid message!"]})

import signal
import sys

if __name__ == "__main__":
    import time
    import jsocket
    #from socket import *
    import socket
    from socket import error as socket_error
    server = None

    def signal_handler(signal, frame):
        # close the socket here
        print server
        if server is not None:
            print "Stopping the server!!!! pid: {0} {1}".format(os.getpid(), threading.current_thread())
    	    server.stop()
            server.close()
    	    server.join()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    parser = argparse.ArgumentParser()
    parser.add_argument('ip_addr', nargs=1, type=str, help="ip address of server")
    args = parser.parse_args()
    ip_addr = args.ip_addr[0]
    print ip_addr
    try:
        socket.inet_aton(ip_addr)
        # legal
    #except socket.error:
    except socket_error:
        print "Invalid ip address! {0}".format(socket_error)
        sys.exit(1)

    server = jsocket.ServerFactory(I2CFactoryThread, address=ip_addr, port=55667)
    server.timeout = 2.0
    #server.daemon = True
    server.start()

    while True:
        print "Running server!!!! pid: {0} {1}".format(os.getpid(), threading.current_thread())
        server.join(600)
        if not server.isAlive():
            break

