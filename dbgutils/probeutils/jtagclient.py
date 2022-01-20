#!/usr/bin/env python2.7

import string, os
import logging
from jtagutils import jtagutils

logger = logging.getLogger("jtagclient")
logger.setLevel(logging.ERROR)

class JTAG_Client(object):
    def __init__(self, chip_type):
        """
        chip_type is one of ['f1', 's1']
        """
        self.chip = chip_type
        self.connected = False

    def __del__(self):
        if self.connected is True:
            self.disconnect()

    # Connects to Codescape probe
    def connect(self, ip_address, dev_type, jtag_bitrate):
        (status, status_msg) = jtagutils.csr_probe(dev_type, ip_address, jtag_bitrate)
        if status is True:
            self.connected = True
            logger.info("Connection Successful!")
            return True
        else:
            self.connected = False
            logger.error("Connection failed! {0}".format(status_msg))
            return False

    def csr_peek(self, csr_addr, csr_width_words, chip_inst):
        logger.debug(("csr_addr:{0} csr_width_words:{1}").format(
                csr_addr, csr_width_words))
        if self.connected is False:
            error_msg = "Probe not connected!"
            logger.info('error_msg')
            return (False, error_msg)
        if csr_addr is None or csr_width_words is None \
                or csr_addr == 0 or csr_width_words < 1:
            error_msg = "Invalid peek arguments!"
            logger.info('connected: {0} csr_addr: {1} csr_width_words: {2}'
                    ''.format(self.connected, csr_addr, csr_width_words))
            logger.error(error_msg)
            return (False, error_msg)
        word_array = jtagutils.csr_peek(csr_addr, csr_width_words, self.chip)
        if word_array:
            return (True, word_array)
        else:
            error_msg = "jtag csr peek failed!"
            logger.error(error_msg)
            return (False, error_msg)

    # Sends poke request to Codescape probe
    def csr_poke(self, csr_addr, word_array, fast_poke=False, chip_inst=None):
        logger.debug(("csr_addr:{0} word_array:{1}").format(
            csr_addr, [hex(x) for x in word_array]))
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
        status = jtagutils.csr_poke(csr_addr, word_array, self.chip)
        if status is True:
            return (True, "poke success!")
        else:
            error_msg = "Error! poke failed!"
            logger.error(error_msg)
            return (False, error_msg)

    # Closes remote i2c devce connection and socket connection to i2c proxy server
    def disconnect(self):
        if self.connected is True:
            jtagutils.disconnect()
            logger.debug('jtag probe is disconnected!')
        else:
            logger.info('Probe is already disconnected!')
            self.connected = False
        return (True, 'Disconnected!')
