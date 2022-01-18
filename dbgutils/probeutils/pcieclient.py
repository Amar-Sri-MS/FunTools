#!/usr/bin/env python2.7
'''
pcieclient connects to pcieproxy on remote server which can issue register
access commands on our behalf using an mmap()'ed PCIe BAR Control/Status
Register (CSR) Control Unit (CCU) Remote Indirect CCU Interface.
'''
import json
import string, os
import socket
from array import array
import logging

logger = logging.getLogger('pcieclient')
logger.setLevel(logging.INFO)

class constants(object):
    CCU_SERVER_TCP_PORT = 44445

class PCIE_Client(object):
    def __init__(self, mode):
        self.con_handle = None


    def __del__(self):
        if self.con_handle is not None:
            self.disconnect()


    def connect(self, ip_address, pcie_ccu_bar, pcie_mem_offset):
        if pcie_ccu_bar is None:
            logger.error('pcie_ccu_bar must be specified!')
            return None

        try:
            con_handle = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            logger.error('Failed to get socket')
            return None

        try:
            con_handle.connect((ip_address, constants.CCU_SERVER_TCP_PORT))
        except socket.error:
            logger.error('Failed to connect to pcie server {0}'.format(ip_address))
            con_handle.close()
            return None

        con_handle.sendall('CONNECT {} {}\n'.format(pcie_ccu_bar, pcie_mem_offset))
        connect_rsp = str(con_handle.recv(1024))

        # Successful response: OKAY CONNECT
        connect_rsp_words = connect_rsp.split()
        if connect_rsp_words[0] == 'OKAY':
            self.con_handle = con_handle
            logger.info('PCIe Server connection Success!')
            return True

        logger.error('Connect failed ' + connect_rsp)
        con_handle.close()
        return False


    def disconnect(self):
        if self.con_handle is None:
            error_msg = 'Not connected to PCIe Server'
            logger.error(error_msg)
            return (False, error_msg)

        logger.info('Disconnecting from PICe Server')

        self.con_handle.sendall('DISCONNECT\n')
        disconnect_rsp = str(self.con_handle.recv(1024))

        # Successful response: OKAY DISCONNECT
        disconnect_rsp_words = disconnect_rsp.split()
        disconnect_success = disconnect_rsp_words[0] == 'OKAY'
        if disconnect_success:
            disconnect_msg = 'Disconnect successful'
            logger.info(disconnect_msg)
        else:
            disconnect_msg = 'Disconnect unsuccessful: ' + disconnect_rsp
            logger.error(disconnect_msg)

        self.con_handle.close()
        self.con_handle = None
        return (disconnect_success, disconnect_msg)


    def csr_peek(self, csr_addr, csr_width_words, chip_inst=None):
        logger.debug(('csr_addr: {0} csr_width_words: {1}').format(
                      csr_addr, csr_width_words))

        if self.con_handle is None:
            error_msg = 'PCIe Server is not connected!'
            logger.error(error_msg)
            return (False, error_msg)

        if csr_addr is None or csr_width_words is None \
                or csr_addr == 0 or csr_width_words < 1:
            error_msg = 'Invalid peek arguments!'
            logger.info('con_handle: {0} csr_addr: {1} csr_width_words: {2}'
                    ''.format(self.con_handle, csr_addr, csr_width_words))
            logger.error(error_msg)
            return (False, error_msg)

        self.con_handle.sendall('READ '
                                + str(csr_addr)
                                + ' '
                                + str(csr_width_words * 64)
                                + '\n')
        csr_peek_rsp = str(self.con_handle.recv(1024))

        # Successful response: OKAY READ <64-bit word> ...
        csr_peek_rsp_words = csr_peek_rsp.split()
        word_array = [int(w,0) for w in csr_peek_rsp_words[2:]]
        if csr_peek_rsp_words[0] == 'OKAY':
            return (True, word_array)

        return (False, 'PCIe peek failed: ' + csr_peek_rsp)


    def csr_poke(self, csr_addr, word_array, fast_poke=False, chip_inst=None):
        logger.debug(('csr_addr: {0} word_array: {1}').format(
            csr_addr, word_array))
        str_array = [str(w) for w in word_array]
        if self.con_handle is None:
            error_msg = 'PCIe Server is not connected!'
            logger.error(error_msg)
            return (False, error_msg)

        if csr_addr is None or word_array is None or csr_addr == 0:
            logger.info(('csr_addr: {0} word_array: {1}').format(
                csr_addr, word_array))
            error_msg = 'Invalid poke arguments!'
            logger.error(error_msg)
            return (False, error_msg)

        self.con_handle.sendall('WRITE '
                                + str(csr_addr)
                                + ' '
                                + str(len(word_array) * 64)
                                + ' '
                                + ' '.join(str_array)
                                + '\n')
        csr_poke_rsp = str(self.con_handle.recv(1024))

        # Successful response: OKAY WRITE
        csr_poke_rsp_words = csr_poke_rsp.split()

        if csr_poke_rsp_words[0] == 'OKAY':
            return (True, 'PCIe poke succeeded')

        return (False, 'PCIe poke failed: ' + csr_poke_rsp)
