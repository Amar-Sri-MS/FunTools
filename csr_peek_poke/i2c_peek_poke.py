#!/usr/bin/env python

import sys, os
sys.path.append('aardvark')
from aardvark_py import *
from array import array
import binascii
import argparse
import threading
import time
import jsocket
import logging
import traceback
import signal
import socket
from socket import error as socket_error

class constants(object):
    F1_I2C_SLAVE_ADDR = 0x70


i2c_handle = None

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

def i2c_connect():
    n_devs, devs = aa_find_devices(1)
    print "n_devs:{0} devs:{1}".format(n_devs, devs)
    if not devs or devs[0] is None:
        status_msg = "Failed to detect i2c device!"
        self.send_obj({"STATUS":[False, status_msg]})
        print status_msg
        return None

    dev_handle =  devs[0]
    print "Dev handle: {0}".format(dev_handle)
    h = aa_open(dev_handle)
    if h == 0x8000:
        print "Invalid i2c Handle! {0}".format(h)
        return None

    features = aa_features(h)
    if features != 27:
        status_msg = "Invalid device features!: {0}".format(features)
        self.send_obj({"STATUS":[False, status_msg]})
        print status_msg
        return None

    status = aa_i2c_free_bus(h)
    print("Free Bus: {0}".format(aa_status_string(status)))
    status = aa_configure(h,2)
    if status != 2:
        status_msg = "Configure i2c mode! status:{0}".format(status)
        self.send_obj({"STATUS":[False, status_msg]})
        print status_msg
        return None

    status = aa_i2c_bitrate(h, 1)
    if status != 1:
        status_msg = "Configure bitrate! status:{0}".format(status)
        self.send_obj({"STATUS":[False, status_msg]})
        print status_msg
        return None

    print "i2c handle: {0}".format(h)
    return h

def i2c_disconnect(h):
    print "Disconnect request"
    status = aa_i2c_free_bus(h)
    print "Free Bus: {0}".format(aa_status_string(status))
    status = aa_close(h)
    print "Closed i2c handle"

def i2c_csr_peek(h, csr_addr, csr_width_words):
    print "I2C peek .... csr_addr:{0} csr_width_words:{1}".format(hex(csr_addr), csr_width_words)

    csr_addr = struct.pack('>Q', csr_addr)
    csr_addr = list(struct.unpack('BBBBBBBB', csr_addr))
    csr_addr = csr_addr[3:]
    cmd = array('B', [0x00])
    cmd.extend(csr_addr)
    print cmd
    sent_bytes = aa_i2c_write(h, constants.F1_I2C_SLAVE_ADDR, 0, cmd)
    print "sent_bytes: {0}".format(sent_bytes)
    if sent_bytes != len(cmd):
        print "Write Error! sent_bytes:{0} Expected: {1}".format(sent_bytes, len(cmd))
        return None
    csr_width = csr_width_words * 8
    read_data = array('B', [00]*(csr_width+1))
    read_bytes = aa_i2c_read(h, constants.F1_I2C_SLAVE_ADDR, 0, read_data)
    print ("read_data: {0} read_bytes: {1}").format(read_bytes, read_data)
    if read_bytes[0] != (csr_width + 1):
        print "Read Error!  read_bytes:{0} Expected: {1}".format(read_bytes, (csr_width + 1))
        return None
    if read_data[0] != 0x80:
        print "Read status returned Error! {0}".format(aa_status_string(read_data[0]))
        return None

    read_data = read_data[1:]
    word_array = byte_array_to_8byte_words_be(read_data)
    print "Peeked word_array: {0}".format(word_array)
    return word_array

def i2c_csr_poke(h, csr_addr, csr_width_words, word_array):
    print("Starting I2C poke. csr_addr: {0} csr_width_words: {1} word_array:{2}").format(hex(csr_addr), csr_width_words, word_array)
    if csr_width_words != len(word_array):
        print "Insufficient data! Expected: {0} data length: {0}".format(csr_width_words, len(word_array))
        return False

    csr_addr = struct.pack('>Q', csr_addr)
    csr_addr = list(struct.unpack('BBBBBBBB', csr_addr))
    csr_addr = csr_addr[3:]
    cmd_data = array('B', [0x01])
    cmd_data.extend(csr_addr)
    for word in word_array:
        word = struct.pack('>Q', word)
        word = list(struct.unpack('BBBBBBBB', word))
        cmd_data.extend(word)

    print "poking bytes: {0}".format([hex(x) for x in cmd_data])
    sent_bytes = aa_i2c_write(h, constants.F1_I2C_SLAVE_ADDR, 0, cmd_data)
    print "sent_bytes: {0}".format(sent_bytes)

    try:
        if sent_bytes != len(cmd_data):
            print "Write Error! sent_bytes:{0} Expected: {1}".format(sent_bytes, len(cmd_data))
            return False

        status = array('B', [00])
        status_bytes = aa_i2c_read(h, constants.F1_I2C_SLAVE_ADDR, 0, status)
        print "poke status_bytes:{0}".format(status_bytes)
        if status_bytes[0] != 1:
            print "Read Error!  status_bytes:{0} Expected: {1}".format(status_bytes, 1)
            return False
        if status[0] != 0x80:
            print "Write status returned Error! {0}".format(aa_status_string(status[0]))
            return False
    except Exception as e:
        logging.error(traceback.format_exc())
        return False
    return True

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

    def _process_message(self, obj):
        global i2c_handle
        """ virtual method - Implementer must define protocol """
        print "process message!!!! pid: {0} {1}".format(os.getpid(), threading.current_thread())
        if obj != '':
            logger.info(obj)
            if obj.get("CONNECT", None):
                logger.info("Connection Request.")
                if i2c_handle is not None:
                    logger.info("Already connected! closing it!")
                    i2c_disconnect(i2c_handle)
                    i2c_handle = None
                try:
                    i2c_handle = i2c_connect()
                except Exception as e:
                    logging.error(traceback.format_exc())
                    self.send_obj({"STATUS":[False, "Exception!"]})
                    return
                if i2c_handle is None:
                    self.send_obj({"STATUS":[False, "i2c device open failed!"]})
                else:
                    self.send_obj({"STATUS":[True, "i2c device is ready!"]})
            elif obj.get("CSR_PEEK", None):
                print "Peeking ..."
                if i2c_handle is None:
                    self.send_obj({"STATUS":[False, "I2c dev is not connected!"]})
                    return
                try:
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
                    try:
                        word_array = i2c_csr_peek(i2c_handle, csr_addr, csr_width_words)
                    except Exception as e:
                        logging.error(traceback.format_exc())
                        self.send_obj({"STATUS":[False, "Exception!"]})
                        return
                    print "Peek returning words: {0}".format(word_array)
                    self.send_obj({"STATUS":[True, "peek success!"],
                            "DATA":word_array})
                except Exception as e:
                    logging.error(traceback.format_exc())
                    self.send_obj({"STATUS":[False, "Exception!"]})
                    return
            elif obj.get("CSR_POKE", None):
                csr_poke_args = obj.get("CSR_POKE", None)
                if not csr_poke_args:
                    self.send_obj({"STATUS":[False, "Invalid poke args!"]})
                    return
                if i2c_handle is None:
                    self.send_obj({"STATUS":[False, "I2c dev is not connected!"]})
                    return
                csr_addr = csr_poke_args.get("csr_addr", None)
                csr_width_words = csr_poke_args.get("csr_width", None)
                word_array = csr_poke_args.get("csr_val", None)
                if not csr_addr or not csr_width_words or not word_array:
                    self.send_obj({"STATUS":[False, "Invalid peek args!"]})
                    return
                print "csr_addr: {0} csr_width_words:{1} word_array:{2}".format(csr_addr, csr_width_words, word_array)
                status = i2c_csr_poke(i2c_handle, csr_addr, csr_width_words, word_array)
                self.send_obj({"STATUS":[status, ""]})
            elif obj.get("DISCONNECT", None):
                if i2c_handle is not None:
                    i2c_disconnect(i2c_handle)
                    self.send_obj({"STATUS":[True, "I2c is disconnected"]})
                else:
                    self.send_obj({"STATUS":[True, "I2c is already disconnected"]})
                i2c_handle = None
            else:
                print "Invalid msg!"
                self.send_obj({"STATUS":[False, "Invalid message!"]})


if __name__ == "__main__":
    server = None

    def signal_handler(signal, frame):
        # close the socket here
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
    except socket_error:
        print "Invalid ip address! {0}".format(socket_error)
        sys.exit(1)

    server = jsocket.ServerFactory(I2CFactoryThread, address=ip_addr, port=55667)
    server.timeout = 2.0
    #server.daemon = True
    server.start()

    while True:
        print "Running server!!!! pid: {0} {1}".format(os.getpid(),
                threading.current_thread())
        server.join(600)
        if not server.isAlive():
            break

