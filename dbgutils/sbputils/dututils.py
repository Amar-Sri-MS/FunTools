#!/usr/bin/env python2.7

import sys
import json
import logging
import pkg_resources

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dut")
logger.setLevel(logging.ERROR)

class dut(object):
    def __init__(self):
        #dut_cfg_file = pkg_resources.resource_filename('.', 'dutdb.cfg')
        dut_cfg_file = 'dutdb.cfg'
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
        bmc_ip = dut_cfg.get('bmc_ip', None)
        if not bmc_ip:
            bmc = False
            i2c_proxy_ip = dut_cfg.get('i2c_proxy_ip', None)
            i2c_slave_addr = dut_cfg.get('i2c_slave_addr', None)
            i2c_slave_addr = int(i2c_slave_addr, 0)
            i2c_probe_serial = dut_cfg.get('i2c_probe_serial', None)
            if not i2c_probe_serial or not i2c_slave_addr or not i2c_proxy_ip:
                logger.error('Invalid dut db for dut: {}'.format(dut))
                return None

        if bmc is True and not bmc_ip:
            logger.error(('Invalid dut db for dut: {}.'
                         ' Specify bmc ip address!').format(dut))
            return None
        if bmc is True:
            return (True, bmc_ip)
        else:
            return (True, i2c_probe_serial, i2c_proxy_ip, i2c_slave_addr)

    def get_jtag_info(self, dut):
        if dut == None:
            logger.error('Invalid dut: None')
            return None
        dut_cfg = self.data.get(dut, None)
        if dut_cfg == None:
            logger.error('dut:{} does not exist in dut db!'.format(dut))
            logger.info('Valid duts: {}'.format(self.data))
            return None
        bmc = True
        bmc_ip = dut_cfg.get('bmc_ip', None)
        if not bmc_ip:
            bmc = False
        jtag_probe_id = dut_cfg.get('jtag_probe_id', None)
        jtag_probe_ip = dut_cfg.get('jtag_probe_ip', None)
        if not jtag_probe_id or not jtag_probe_ip:
            logger.error('Invalid dut db for dut: {}'.format(dut))
            return None
        if bmc is True:
            return (bmc, bmc_ip, jtag_probe_id, jtag_probe_ip)
        else:
            return (True, jtag_probe_id, jtag_probe_ip)

    def get_pcie_info(self, dut):
        if dut == None:
            logger.error('Invalid dut: None')
            return None
        dut_cfg = self.data.get(dut, None)
        if dut_cfg == None:
            logger.error('dut:{} does not exist in dut db!'.format(dut))
            logger.info('Valid duts: {}'.format(self.data))
            return None
        bmc = True
        bmc_ip = dut_cfg.get('bmc_ip', None)
        if not bmc_ip:
            bmc = False
        pcie_ccu_bar = dut_cfg.get('pcie_ccu_bar', None)
        pcie_probe_ip = dut_cfg.get('pcie_probe_ip', None)
        if not pcie_ccu_bar or not pcie_probe_ip:
            logger.error('Invalid dut db for dut: {}'.format(dut))
            return None
        if bmc is True:
            return (bmc, bmc_ip, pcie_ccu_bar, pcie_probe_ip)
        else:
            return (bmc, pcie_ccu_bar, pcie_probe_ip)

def dut_cfg_test():
    duts = dut()
    dut_cfg = duts.get_i2c_info('TPOD0')
    if dut_cfg is None:
        logger.error('Failed to get dut info!')
    else:
        logger.info('Found {0} dut info!'.format(dut_cfg))

if __name__== "__main__":
    dut_cfg_test()
