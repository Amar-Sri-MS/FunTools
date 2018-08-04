#!/usr/bin/env python
import os
import logging
from array import array
from i2cclient import *

logger = logging.getLogger("dbgclient")
logger.setLevel(logging.INFO)

class DBG_Client(object):
    def __init__(self, mode):
        if mode == 'i2c':
            self.con_mode = mode
            self.client = I2C_Client(mode)
        elif mode == 'jtag':
            self.con_mode = mode
            raise ValueError('Mode: "{0}" is not supported yet!'.format(mode))
            #self.client = JTAG_Client()
        elif mode == 'dpc':
            self.con_mode = mode
            raise ValueError('Mode: "{0}" is not supported yet!'.format(mode))
            #self.client = DPC_Client()
        else:
            raise ValueError('Invalid client connection mode: "{0}"'.format(mode))

    def __del__(self):
        self.client.__del__()

    # Opens tcp connection with remote server
    def connect(self, ip_address, dev_id):
        self.client.connect(ip_address, dev_id)

    # Sends peek request to server, get the response and returns the read data
    def csr_peek(self, csr_addr, csr_width_words):
        return self.client.csr_peek(csr_addr, csr_width_words)

    # Sends poke request to server, get the response
    def csr_poke(self, csr_addr, csr_width_words, word_array):
        return self.client.csr_poke(csr_addr, csr_width_words, word_array)

    # Disconnects remote connection and socket connection to remote server
    def disconnect(self):
        return self.client.disconnect()

