#!/usr/bin/env python
import json
import string, os
import socket
import jsocket
import time
import logging
from array import array

logger = logging.getLogger("i2cclient")
logger.setLevel(logging.INFO)

class constants(object):
    SERVER_TCP_PORT = 55668

# Opens tcp connection with remote server
def i2c_remote_connect(ip_address, dev_id):
    s = jsocket.JsonClient(address = ip_address,
			   port = constants.SERVER_TCP_PORT)
    if s is None:
        print("Failed to connect to i2c server {0}".format(ip_address))
        return None
    s.connect()
    connect_args = dict()
    connect_args["dev_id"] = dev_id
    time.sleep(0.5)
    s.send_obj({"cmd": "CONNECT",
                "args": connect_args})
    read_obj = s.read_obj()
    status = read_obj.get("STATUS", None)
    logger.info("Remote connect status: {0}".format(status))
    if status is not None and status[0] == True:
        return s
    else:
        s.close()
        return None

# Sends peek request to server, get the response and returns the read data
def i2c_remote_peek(s, csr_addr, csr_width_words):
    logger.debug(("s: {0} csr_addr:{1} csr_width_words:{2}").format(s, csr_addr,
                                                             csr_width_words))
    if s is None or csr_addr is None or csr_width_words is None \
            or csr_addr == 0 or csr_width_words < 1:
        print("Invalid peek arguments!")
        return None
    csr_peek_args = dict()
    csr_peek_args["csr_addr"] = csr_addr
    csr_peek_args["csr_width"] = csr_width_words
    s.send_obj({"cmd": "CSR_PEEK",
                "args": csr_peek_args})
    msg = s.read_obj()
    logger.debug(msg)
    status = msg.get("STATUS", None)
    if status[0] == True:
        word_array = msg.get("DATA", None)
        return word_array
    else:
        print("I2C peek over socket failed!")
        return None

# Sends poke request to server, get the response
def i2c_remote_poke(s, csr_addr, csr_width_words, word_array):
    logger.debug(("csr_addr:{0} csr_width_words:{1}"
        " word_array{2}").format(csr_addr,
            csr_width_words, word_array))
    if s is None:
        print 'i2c server is not connected!'
        return
    if csr_addr is None or csr_width_words is None \
            or word_array is None or csr_addr == 0 \
            or csr_width_words < 1:
        logger.info(("csr_addr:{0} csr_width_words:{1}"
           " word_array{2}").format(csr_addr,
               csr_width_words, word_array))
        print("Invalid poke arguments!")
        return False

    csr_poke_args = dict()
    csr_poke_args["csr_addr"] = csr_addr
    csr_poke_args["csr_width"] = csr_width_words
    csr_poke_args["csr_val"] = word_array
    s.send_obj({"cmd": "CSR_POKE",
                "args": csr_poke_args})
    msg = s.read_obj()
    status = msg.get("STATUS", None)
    if status[0] == True:
        logger.debug("poke success!")
        return True
    else:
        print("Error! poke failed!: {0}".format(status[1]))
        return False

# Disconnects remote i2c connection and socket connection to remote server
def i2c_remote_disconnect(s):
    if s is None:
        print("Not connected to server")
        return
    s.send_obj({"cmd": "DISCONNECT",
                "args": None })
    read_obj = s.read_obj()
    status = read_obj.get("STATUS", None)
    if status[0] == True:
        logger.info("Success! {0}".format(status[1]))
        s.close()
        return True
    else:
        logger.error("Error! {0}".format(status[1]))
        s.close()
        return False
