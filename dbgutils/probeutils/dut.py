#!/usr/bin/python

import sys
import json
import logging
import pkg_resources

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dut")
logger.setLevel(logging.INFO)

class dut(object):
    def __init__(self):
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
        i2c_probe_serial = dut_cfg.get('i2c_probe_serial', None)
        i2c_proxy_ip = dut_cfg.get('i2c_proxy_ip', None)
        i2c_slave_addr = dut_cfg.get('i2c_slave_addr', None)
        i2c_slave_addr = int(i2c_slave_addr, 0)
        if not i2c_probe_serial or not i2c_proxy_ip or not i2c_slave_addr:
            logger.error('Invalid dut db for dut: {}'.format(dut))
            return None
        return (i2c_probe_serial, i2c_proxy_ip, i2c_slave_addr)

    def get_jtag_info(self, dut):
        if dut == None:
            logger.error('Invalid dut: None')
            return None
        dut_cfg = self.data.get(dut, None)
        if dut_cfg == None:
            logger.error('dut:{} does not exist in dut db!'.format(dut))
            logger.info('Valid duts: {}'.format(self.data))
            return None
        jtag_probe_id = dut_cfg.get('jtag_probe_id', None)
        jtag_probe_ip = dut_cfg.get('jtag_probe_ip', None)
        if not jtag_probe_id or not jtag_probe_ip:
            logger.error('Invalid dut db for dut: {}'.format(dut))
            return None
        return (jtag_probe_id, jtag_probe_ip)

def dut_cfg_test():
    duts = dut()
    dut_cfg = duts.get_i2c_info('TPOD0')
    if dut_cfg is None:
        logger.error('Failed to get dut info!')
    else:
        logger.info('Found {0} dut info!'.format(dut_cfg))

if __name__== "__main__":
    dut_cfg_test()
