#!/usr/bin/env python
import os
import logging
from array import array
from i2cclient import *

logger = logging.getLogger("dbgclient")
logger.setLevel(logging.INFO)

class DBG_Client(object):
    def __init__(self):
        slef.connection_handle = None
        self.connection_mode = None
        self.ip_address = None
        self.dev_id = None
        self.connected = False

    def connect(mode, ip_addr, dev_id=None):
        if self.connected is True:
            try:
                self.disconnect()
            except Exception as e:
                logging.error(traceback.format_exc())
                logger.info('Still proceeding with connect..!')
            self.__init__()
        dbgclient = None
        if mode == 'i2c':
            dbgclient = I2C_Client(mode)
            status = dbgclient.connect(ip_addr, dev_id)
        elif mode == 'jtag':
            raise ValueError('Mode: "{0}" is not supported yet!'.format(mode))
            #dbgclient = JTAG_Client()
            #status = dbgclient.connect(ip_addr, dev_id)
        elif mode == 'dpc':
            raise ValueError('Mode: "{0}" is not supported yet!'.format(mode))
            #self.client = DPC_Client()
        else:
            raise ValueError('Invalid client connection mode: "{0}"'.format(mode))

        if status is True:
            print("Server connection Successful!")
            self.connection_mode = mode
            self.ip_address = ip_addr
            self.dev_id = dev_id
            self.connection_handle = dbgclient
            self.connected = True
            return True
        else:
            print("Server connection failed!")
            self.__init__()
            return False

    def disconnect():
        if self.connected is False:
	        print("Server is already disconnected!");
            return True
        if self.connected is True:
            try:
                status = self.connection_handle.disconnect()
            except Exception as e:
                logging.error(traceback.format_exc())
                logger.info('Still proceeding with connect..!')
            self.__init__()
            if status is not True:
                print("Server disconnect failed! error: {0}".format(status));
                return False
            print("Server is disconnected! status: {0}".format(status));
            return True

    # Sends peek request to server, get the response and returns the read data
    def csr_peek(self, csr_addr, csr_width_words):
        if self.connected is False:
            return (False, "Server is not connected!")
        return self.connection_handle.csr_peek(csr_addr, csr_width_words)

    # Sends poke request to server, get the response
    def csr_poke(self, csr_addr, csr_width_words, word_array):
        if self.connected is False:
            error_msg = "Server is not connected!"
	        print(error_msg);
            return (False, error_msg)
        return self.connection_handle.csr_poke(csr_addr,
                                        csr_width_words, word_array)

    # Disconnects remote connection and socket connection to remote server
    def disconnect(self):
        return self.connection_handle.disconnect()

