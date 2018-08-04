#!/usr/bin/env python

import sys, os
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
from i2c_usb_dev_scan import *

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

class I2CServer(jsocket.ThreadedServer):
    def __init__(self):
        super(I2CServer, self).__init__()
        self.timeout = 2.0
        logger.warning("I2CServer init!")

    def _process_message(self, obj):
        """ virtual method """
        if obj != '': #Dummy implementation
            if obj['message'] == "new connection":
                logger.info("new connection.")

# class for i2c server thread
class I2CFactoryThread(jsocket.ServerFactoryThread):
    def __init__(self):
        super(I2CFactoryThread, self).__init__()
        self.timeout = 2.0
        self.i2c_handle = None
    def __del__(self):
        if self.i2c_handle is not None:
            logger.info("Closing i2c Connection!")
            i2c_disconnect(self.i2c_handle)
            self.i2c_handle = None
        logger.info("Destroyed i2c factory thread!");

    def _process_message(self, obj):
        """ virtual method - Implementer must define protocol """
        logger.debug(("New thread process message!!!! pid: {0}"
               " thread: {1}").format(os.getpid(), threading.current_thread()))
        if obj != '':
            logger.info(obj)
            cmd = obj.get("cmd", None)
            if cmd == "CONNECT":
		connect_args = obj.get("args", None)
		if not connect_args:
		    self.send_obj({"STATUS":[False, "Invalid connect args!"]})
		    return
		dev_id = connect_args.get("dev_id", None)
		if not dev_id:
		    self.send_obj({"STATUS":[False, ("Invalid connect args."
			" dev_id is missing!")]})
		    return
                logger.info("Connection Request to dev_id: {0}".format(dev_id))
                if self.i2c_handle is not None:
                    logger.info("Already connected! closing it!")
                    i2c_disconnect(self.i2c_handle)
                    self.i2c_handle = None
                try:
                    (status, value) = i2c_connect(dev_id)
                    if status is True:
                        self.i2c_handle = value
                        self.send_obj({"STATUS":[True, "i2c device is ready!"]})
                        logger.info(('i2c device connection is ready!'
                                    ' i2c_handle:{0}').format(self.i2c_handle))
                    else:
                        self.i2c_handle = None
                        error_str = value
                        self.send_obj({"STATUS":[False, error_str]})
                        return
                except Exception as e:
                    logging.error(traceback.format_exc())
                    self.send_obj({"STATUS":[False, "Exception!"]})
                    return
            elif cmd == "CSR_PEEK":
                if self.i2c_handle is None:
                    self.send_obj({"STATUS":[False, "I2c dev is not connected!"]})
                    return
                try:
                    csr_peek_args = obj.get("args", None)
                    if not csr_peek_args:
                        self.send_obj({"STATUS":[False, "Invalid peek args!"]})
                        return
                    csr_addr = csr_peek_args.get("csr_addr", None)
                    csr_width_words = csr_peek_args.get("csr_width", None)
                    if not csr_addr or not csr_width_words:
                        self.send_obj({"STATUS":[False, "Invalid peek args!"]})
                        return
                    logger.debug("csr_addr: {0} csr_width_words:{1}".format(csr_addr,
                                 csr_width_words))
                    try:
                        word_array = i2c_csr_peek(self.i2c_handle, csr_addr, csr_width_words)
                    except Exception as e:
                        logging.error(traceback.format_exc())
                        self.send_obj({"STATUS":[False, "Exception!"]})
                        return
                    logger.debug("Peeked words: {0}".format(word_array))
                    if word_array is not None:
                        self.send_obj({"STATUS":[True, "peek success!"],
                                "DATA":word_array})
                    else:
                        self.send_obj({"STATUS":[False, "peek fail!"],
                                "DATA":word_array})
                except Exception as e:
                    logging.error(traceback.format_exc())
                    self.send_obj({"STATUS":[False, "Exception!"]})
                    return
            elif cmd == "CSR_POKE":
                csr_poke_args = obj.get("args", None)
                if not csr_poke_args:
                    self.send_obj({"STATUS":[False, "Invalid poke args!"]})
                    return
                if self.i2c_handle is None:
                    self.send_obj({"STATUS":[False, "I2c dev is not connected!"]})
                    return
                csr_addr = csr_poke_args.get("csr_addr", None)
                csr_width_words = csr_poke_args.get("csr_width", None)
                word_array = csr_poke_args.get("csr_val", None)
                if not csr_addr or not csr_width_words or not word_array:
                    self.send_obj({"STATUS":[False, "Invalid peek args!"]})
                    return
                logger.debug(("csr_addr: {0} csr_width_words:{1}"
                       " word_array:{2}").format(csr_addr, csr_width_words,
                                                 word_array))
                status = i2c_csr_poke(self.i2c_handle, csr_addr, csr_width_words, word_array)
                self.send_obj({"STATUS":[status, "OK!" if status else "i2c csr error!"]})
            elif cmd == "DISCONNECT":
                if self.i2c_handle is not None:
                    i2c_disconnect(self.i2c_handle)
                    self.send_obj({"STATUS":[True, "I2c is disconnected"]})
                else:
                    self.send_obj({"STATUS":[True, "I2c is already disconnected"]})
                self.i2c_handle = None
            else:
                logger.debug("Invalid msg!")
                self.send_obj({"STATUS":[False, "Invalid message!"]})

if __name__ == "__main__":
    server = None
    def signal_handler(signal, frame):
        # close the socket here
        if server is not None:
            logger.info(("Stopping the server!!!! pid: {0}"
                   " thread: {1}").format(os.getpid(),
                   threading.current_thread()))
            server.stop()
            server.close()
            server.join()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler) #Terminate cleanly on ctrl+c

    parser = argparse.ArgumentParser()
    parser.add_argument('ip_addr', nargs='?', type=str,
                        help="ip address of server")
    args = parser.parse_args()
    if args.ip_addr is None:
        ip_addr = socket.gethostbyname(socket.gethostname())
    else:
        ip_addr = args.ip_addr[0]

    try:
        socket.inet_aton(ip_addr) #Validates the ip address
    except socket_error:
        logger.debug("Invalid ip address! {0}".format(socket_error))
        sys.exit(1)

    server = jsocket.ServerFactory(I2CFactoryThread, address=ip_addr,
                                   port = constants.SERVER_TCP_PORT)
    server.timeout = 2.0
    logger.info("Starting the server IP:{0} PORT:{1}".format(ip_addr,
                                            constants.SERVER_TCP_PORT))
    server.start()

    # Let the main thread stay alive and recieve contl+c
    while True:
        logger.debug(("Running server!!!! pid:{0} thread:{1}").format(os.getpid(),
                threading.current_thread()))
        server.join(600)
        if not server.isAlive():
            break


