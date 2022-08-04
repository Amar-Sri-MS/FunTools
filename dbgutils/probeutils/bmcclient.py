#!/usr/bin/env python3

import string, os
import logging
import subprocess
from .i2cutils import *

logger = logging.getLogger("bmcclient")
logger.setLevel(logging.INFO)

class BMC_Client(object):
    def __init__(self, bmc_ip_address, mode='i2c', chip_type='f1'):
        assert(bmc_ip_address)
        self.connected = False
        self.bmc_ip_address = bmc_ip_address
        self.mode = mode
        self.chip_type = chip_type
        if self.bmc_ip_address and self.mode == "i2c":
            if chip_type=='f1':
                self.probe = i2c(bmc_ip_address=bmc_ip_address, chip_type=chip_type)
            else:
                self.probe = csr2i2c(bmc_ip_address=bmc_ip_address, chip_type=chip_type)
        #elif self.bmc_ip_address and self.mode == "jtag":
        else:
            assert(0)

    def __del__(self):
        if self.connected is True:
            self.disconnect()

    def connect(self):
        (status, status_msg) = self.probe.i2c_connect()
        if status is True:
            self.connected = True
            logger.info("Connection Successful!")
            return True
        else:
            self.connected = False
            logger.error("Connection failed! {0}".format(status_msg))
            return False

    def disconnect(self):
        self.connected = False
        logger.info('disconnected!')
        return (True, 'Disconnected!')

    def csr_peek(self, chip_inst, csr_addr, csr_width_words):
        logger.info(("chip_inst: {0} csr_addr:{1} csr_width_words:{2}").format(
                chip_inst, hex(csr_addr), csr_width_words))
        if self.connected is False:
            error_msg = "bmc not connected!"
            logger.info('error_msg')
            return (False, error_msg)
        if csr_addr is None or csr_width_words is None \
                or csr_addr == 0 or csr_width_words < 1:
            error_msg = "Invalid peek arguments!"
            logger.info('connected: {0} csr_addr: {1} csr_width_words: {2}'
                    ''.format(self.connected, csr_addr, csr_width_words))
            logger.error(error_msg)
            return (False, error_msg)
        (data,status) = self.probe.i2c_csr_peek(csr_addr = csr_addr,
                                             csr_width_words = csr_width_words,
                                             chip_inst = chip_inst)
        if data:
            return (True, data)
        else:
            error_msg = "csr peek failed! Error:{0}".format(status)
            logger.error(error_msg)
            return (False, error_msg)

    # Sends poke request to Codescape probe
    def csr_poke(self, chip_inst, csr_addr, word_array, fast_poke=False):
        logger.debug(("chip_inst: {0} csr_addr:{1} word_array:{2}").format(
            chip_inst, hex(csr_addr), [hex(x) for x in word_array]))
        if self.connected is False:
            error_msg = "Probe not connected!"
            logger.info('error_msg')
            return (False, error_msg)
        if csr_addr is None or word_array is None or csr_addr == 0:
            logger.info(("csr_addr:{0} word_array: {1}").format(
                csr_addr, [hex(x) for x in word_array]))
            error_msg = "Invalid poke arguments!"
            logger.error(error_msg)
            return (False, error_msg)
        status = self.probe.i2c_csr_poke(csr_addr = csr_addr,
                                         word_array = word_array,
                                         chip_inst = chip_inst)
        if status is True:
            return (True, "poke success!")
        else:
            error_msg = "Error! poke failed!"
            logger.error(error_msg)
            return (False, error_msg)

    def dbg_chal_cmd(self, cmd, data=None, chip_inst=None):
        logger.debug(("dbg chal cmd:{0} data:{1}").format(cmd, data))
        if data is not None:
            logger.debug(("dbg chal data:{0}").format(
                    [hex(x) for x in data]))
        (status, return_data)  = self.probe.i2c_dbg_chal_cmd(cmd = cmd,
						data = data,
						chip_inst = chip_inst)
        if status is not True:
            error_msg = return_data
            logger.error(error_msg)
            return (False, error_msg)
        return (True, return_data)
