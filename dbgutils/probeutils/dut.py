#!/usr/bin/env python3

import sys
import json
import logging
import socket
import pkg_resources

from .i2cutils import constants

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dut")
logger.setLevel(logging.INFO)


class dut(object):
    def __init__(self, cfg_path=None):
        if cfg_path:
            dut_cfg_file = cfg_path
        else:
            dut_cfg_file = pkg_resources.resource_filename('probeutils', 'dut.cfg')
        with open(dut_cfg_file) as f:
            self.data = json.load(f)

    def get_i2c_info(self, dut):
        if dut == None:
            logger.error('Invalid dut: None')
            return None
        dut_cfg = self.data.get(dut, None)
        if dut_cfg == None:
            logger.error('dut:{} does not exist in dut db!'.format(dut))
            logger.info('Valid duts: {}'.format(self.data))
            return None
        bmc = True
        chip_type = dut_cfg.get('chip_type', None)
        bmc_ip = dut_cfg.get('bmc_ip', None)
        if not bmc_ip:
            bmc = False
            i2c_proxy_ip = dut_cfg.get('i2c_proxy_ip', None)
            i2c_slave_addr = dut_cfg.get('i2c_slave_addr', None)
            i2c_slave_addr = int(i2c_slave_addr, 0)
            i2c_probe_serial = dut_cfg.get('i2c_probe_serial', None)
            i2c_bitrate = dut_cfg.get('i2c_bitrate', constants.DEFAULT_I2C_XFER_BIT_RATE)
            try:
                i2c_proxy_ip = socket.gethostbyname(i2c_proxy_ip)
            except socket.error:
                logger.error('Invalid i2c proxy: {}'.format(i2c_proxy_ip))
                i2c_proxy_ip = None
            if not i2c_probe_serial or not i2c_slave_addr or not i2c_proxy_ip:
                logger.error('Invalid dut db for dut: {}'.format(dut))
                return None

        if bmc is True and not bmc_ip:
            logger.error(('Invalid dut db for dut: {}.'
                         ' Specify bmc ip address!').format(dut))
            return None
        if bmc is True:
            try:
                bmc_ip = socket.gethostbyname(bmc_ip)
            except socket.error:
                return None
            return (True, bmc_ip, chip_type)
        else:
            return (False, i2c_probe_serial, i2c_proxy_ip,
                    i2c_slave_addr, i2c_bitrate, chip_type)

    def get_jtag_info(self, dut):
        if dut == None:
            logger.error('Invalid dut: None')
            return None
        dut_cfg = self.data.get(dut, None)
        if dut_cfg == None:
            logger.error('dut:{} does not exist in dut db!'.format(dut))
            logger.info('Valid duts: {}'.format(self.data))
            return None
        chip_type = dut_cfg.get('chip_type', None)
        jtag_probe_id = dut_cfg.get('jtag_probe_id', None)
        jtag_probe_ip = dut_cfg.get('jtag_probe_ip', None)
        jtag_bitrate = dut_cfg.get('jtag_bitrate', None)
        try:
            jtag_probe_ip = socket.gethostbyname(jtag_probe_ip)
        except socket.error:
            logger.error('Invalid jtag probe ip: {}'.format(jtag_probe_ip))
            jtag_probe_ip = None
        if not jtag_probe_id or not jtag_probe_ip or not jtag_bitrate:
            logger.error('Invalid dut db for dut: {}'.format(dut))
            return None

        return (False, jtag_probe_id, jtag_probe_ip, chip_type, jtag_bitrate)

    def get_pcie_info(self, dut):
        if dut == None:
            logger.error('Invalid dut: None')
            return None
        dut_cfg = self.data.get(dut, None)
        if dut_cfg == None:
            logger.error('dut:{} does not exist in dut db!'.format(dut))
            logger.info('Valid duts: {}'.format(self.data))
            return None
        chip_type = dut_cfg.get('chip_type', None)
        pcie_ccu_bar = dut_cfg.get('pcie_ccu_bar', None)
        pcie_probe_ip = dut_cfg.get('pcie_probe_ip', None)
        pcie_mem_offset = dut_cfg.get('pcie_mem_offset', 0)
        if not pcie_ccu_bar or not pcie_probe_ip:
            logger.error('Invalid dut db for dut: {}'.format(dut))
            return None
        return (pcie_ccu_bar, pcie_probe_ip, pcie_mem_offset, chip_type)

def dut_cfg_test():
    duts = dut()
    dut_cfg = duts.get_i2c_info('TPOD0')
    if dut_cfg is None:
        logger.error('Failed to get dut info!')
    else:
        logger.info('Found {0} dut info!'.format(dut_cfg))

if __name__== "__main__":
    dut_cfg_test()
