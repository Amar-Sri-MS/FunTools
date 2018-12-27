#!/usr/bin/env python
import os
import logging
import traceback
from array import array
from i2cclient import *
from sys import platform as _platform
if _platform == "linux" or _platform == "linux2":
    from jtagclient import *

logger = logging.getLogger("dbgclient")
logger.setLevel(logging.INFO)

class DBG_Client(object):
    def __init__(self):
        self.connection_handle = None
        self.connection_mode = None
        self.ip_address = None
        self.dev_id = None
        self.connected = False

    def connect(self, mode, ip_addr, dev_id=None, slave_addr = None, force = False):
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
            status = dbgclient.connect(ip_addr, dev_id, slave_addr, force)
        elif mode == 'jtag':
            if (_platform == "linux" or _platform == "linux2"):
                dbgclient = JTAG_Client()
                status = dbgclient.connect(ip_addr, dev_id)
            else:
                raise ValueError('Mode: "{0}" is supported on this platform!'.format(mode))
        elif mode == 'dpc':
            raise ValueError('Mode: "{0}" is not supported yet!'.format(mode))
            #self.client = DPC_Client()
        else:
            raise ValueError('Invalid client connection mode: "{0}"'.format(mode))

        if status is True:
            logger.debug("Connection to probe successful!")
            self.connection_mode = mode
            self.ip_address = ip_addr
            self.dev_id = dev_id
            self.connection_handle = dbgclient
            self.connected = True
            return True
        else:
            logger.debug("Connection to probe failed!")
            self.__init__()
            return False

    # Disconnects dbgprobe connection to remote server
    def disconnect(self):
        status = False
        if self.connected is False:
            logger.info("Probe is already disconnected!");
            return True
        if self.connected is True:
            try:
                (status, msg_str) = self.connection_handle.disconnect()
            except Exception as e:
                logging.error(traceback.format_exc())
                logger.info('Still proceeding with connect..!')
            self.__init__()
            if status is not True:
                print("Disconnect to probe failed! error: {0}".format(status));
                return False
            logger.debug("Disconnect to probe failed! status: {0}".format(status));
            return True

    # Sends peek request to server, get the response and returns the read data
    def csr_peek(self, csr_addr, csr_width_words):
        if self.connected is False:
            return (False, "dbg probe is not connected!")
        return self.connection_handle.csr_peek(csr_addr, csr_width_words)

    # Sends poke request to server, get the response
    def csr_poke(self, csr_addr, word_array):
        if self.connected is False:
            error_msg = "dbg probe is not connected!"
            print(error_msg);
            return (False, error_msg)
        return self.connection_handle.csr_poke(csr_addr,
                      word_array, False)

    def csr_fast_poke(self, csr_addr, word_array):
        if self.connected is False:
            error_msg = "Probe is not connected!"
            print(error_msg);
            return (False, error_msg)
        return self.connection_handle.csr_poke(csr_addr,
                              word_array, True)
    def dbg_chal_cmd(self, cmd, data=None):
        if self.connected is False:
            error_msg = "Probe is not connected!"
            print(error_msg);
            return (False, error_msg)
        return self.connection_handle.dbg_chal_cmd(cmd, data)
