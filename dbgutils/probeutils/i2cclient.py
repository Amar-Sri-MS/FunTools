#!/usr/bin/env python
'''
i2cclient connects to i2cproxy on remote server
and can issue hw access commands using i2c interface
'''
import json
import string, os
import socket
import jsocket
import time
import logging
from array import array
import getpass

logger = logging.getLogger("i2cclient")
logger.setLevel(logging.INFO)

class constants(object):
    SERVER_TCP_PORT = 55668

class I2C_Client(object):
    def __init__(self, mode):
        self.con_handle = None

    def __del__(self):
        if self.con_handle is not None:
            self.disconnect()

    # Opens tcp connection with i2c proxy server and
    # opens remote i2c device connection
    def connect(self, ip_address, dev_id, slave_addr=None, force_connect=False):
        self.con_handle = jsocket.JsonClient(address = ip_address,
                               port = constants.SERVER_TCP_PORT)
        if self.con_handle is None:
            logger.error('Failed to connect to i2c server {0}'.format(ip_address))
            return None
        self.con_handle.connect()
        connect_args = dict()
        connect_args["dev_id"] = dev_id
        connect_args["slave_addr"] = slave_addr
        connect_args["user"] = getpass.getuser()
        connect_args["force_connect"] = force_connect
        time.sleep(0.5)
        self.con_handle.send_obj({"cmd": "CONNECT",
                    "args": connect_args})
        read_obj = self.con_handle.read_obj()
        status = read_obj.get("STATUS", None)
        if status is not None and status[0] == True:
            logger.info("Server connection Success!")
            return True
        else:
            logger.error("Connection Failed! Error:{0}".format(status[1]))
            self.con_handle.close()
            self.con_handle = None
            return False

    # Sends peek request to i2c proxy server, get the response and returns the read data
    def csr_peek(self, csr_addr, csr_width_words):
        logger.debug(('con_handle: {0} csr_addr:{1}'
                      ' csr_width_words:{2}').format(self.con_handle,
                      csr_addr, csr_width_words))
        if self.con_handle is None or csr_addr is None or csr_width_words is None \
                or csr_addr == 0 or csr_width_words < 1:
            error_msg = "Invalid peek arguments!"
            logger.info('con_handle: {0} csr_addr: {1} csr_width_words: {2}'
                    ''.format(self.con_handle, csr_addr, csr_width_words))
            logger.error(error_msg)
            return (False, error_msg)
        csr_peek_args = dict()
        csr_peek_args["csr_addr"] = csr_addr
        csr_peek_args["csr_width"] = csr_width_words
        self.con_handle.send_obj({"cmd": "CSR_PEEK",
                    "args": csr_peek_args})
        msg = self.con_handle.read_obj()
        logger.debug(msg)
        status = msg.get("STATUS", None)
        if status[0] == True:
            word_array = msg.get("DATA", None)
            return (True, word_array)
        else:
            error_msg = "i2c csr peek failed!"
            logger.error(error_msg)
            return (False, error_msg)

    # Sends dbg challange cmd request to i2c proxy server, get the response
    def dbg_chal_cmd(self, cmd, data=None):
        logger.debug(("dbg chal cmd:{0} data:{1}").format(cmd, data))
        if data is not None:
            logger.debug(("dbg chal data:{0}").format(
                    [hex(x) for x in data]))
        if self.con_handle is None:
            error_msg = "i2c server is not connected!"
            logger.error(error_msg)
            return (False, error_msg)
        dbg_chal_args = dict()
        dbg_chal_args["dbg_chal_cmd"] = cmd
        if data is not None and len(data) > 0:
            dbg_chal_args["data"] = data
        self.con_handle.send_obj({"cmd": "DBG_CHAL_CMD",
                    "args": dbg_chal_args})
        msg = self.con_handle.read_obj()
        (status, status_str) = msg.get("STATUS", None)
        data = msg.get("DATA", None)
        if status == True:
            return (True, data)
        else:
            error_msg = "Error! dbg challange command failed!: {0}".format(status_str)
            logger.error(error_msg)
            return (False, error_msg)

    # Sends poke request to i2c proxy server, get the response
    def csr_poke(self, csr_addr, word_array, fast_poke=False):
        logger.debug(("csr_addr:{0} word_array{1}").format(
            csr_addr, word_array))
        if self.con_handle is None:
            error_msg = "i2c server is not connected!"
            logger.error(error_msg)
            return (False, error_msg)
        if csr_addr is None or word_array is None or csr_addr == 0:
            logger.info(("csr_addr:{0} word_array{1}").format(
                csr_addr, word_array))
            error_msg = "Invalid poke arguments!"
            logger.error(error_msg)
            return (False, error_msg)

        csr_poke_args = dict()
        csr_poke_args["csr_addr"] = csr_addr
        csr_poke_args["csr_val"] = word_array
        if fast_poke:
            csr_poke_args["fast_poke"] = word_array
        self.con_handle.send_obj({"cmd": "CSR_POKE",
                    "args": csr_poke_args})
        if not fast_poke:
            msg = self.con_handle.read_obj()
            status = msg.get("STATUS", None)
            if status[0] == True:
                return (True, "poke success!")
            else:
                error_msg = "Error! poke failed!: {0}".format(status[1])
                logger.error(error_msg)
                return (False, error_msg)
        else:
            return (True, "poke success!")

    # Closes remote i2c devce connection and socket connection to i2c proxy server
    def disconnect(self):
        if self.con_handle is None:
            error_msg = "Not connected to server"
            logger.error(error_msg)
            return (False, error_msg)
        logger.info('Sending i2c disconnect!')
        disconnect_args = dict()
        disconnect_args['user'] = getpass.getuser()
        self.con_handle.send_obj({"cmd": "DISCONNECT",
                    "args": disconnect_args})
        read_obj = self.con_handle.read_obj()
        status = read_obj.get("STATUS", None)
        if status[0] == True:
            logger.info("Success! {0}".format(status[1]))
            self.con_handle.close()
            self.con_handle = None
            return (True, "i2c disconnect successful")
        else:
            error_msg = "{0}".format(status[1])
            logger.error(error_msg)
            self.con_handle.close()
            self.con_handle = None
            return (False, error_msg)

