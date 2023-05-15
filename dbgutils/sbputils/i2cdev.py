#!/usr/bin/env python3

import sys
import usb.core
import logging
from array import array
from aardvark_py import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("i2cdev")
logger.setLevel(logging.DEBUG)

def aardvark_i2c_spi_dev_list_ext():
    unique_ids = array('I', [0x0]*16)
    devices = 16
    (n_devs, dev_ids, serial_nums) = aa_find_devices_ext(devices, unique_ids)
    logger.info('Found {0} devices with dev_ids: {1}'
                ' Serial numbers: {2}'.format(n_devs,
                     [hex(x) for x in dev_ids[:n_devs]] if dev_ids else None,
                     [x for x in serial_nums[:n_devs]] if serial_nums else None))
    if not n_devs or not dev_ids or not serial_nums:
        logger.error('No aardvark i2c spi devices found!')
        return (None, None)
    return (dev_ids[:n_devs], serial_nums[:n_devs])

def aardvark_i2c_spi_dev_list():
    (dev_ids, serial_nums) = aardvark_i2c_spi_dev_list_ext()
    if not dev_ids or not serial_nums:
        return None
    return serial_nums

def aardvark_usb_devices():
    # find USB devices
    dev = usb.core.find(find_all=True)
    # loop through devices
    aardvark_i2c_spi_dev_list = list()
    for cfg in dev:
        if cfg.idVendor == 0x403 and cfg.idProduct == 0xe0d0:
            dev_info = str(cfg)
            matched_lines = [line for line in dev_info.split('\n') if "iSerialNumber" in line]
            if len(matched_lines) != 1:
                logger.error("Invalid usb device metadata"
			     " parsing! {}".format(matched_lines))
                sys.exit(1)
            usb_i2c_spi = matched_lines[0]
            tokens = usb_i2c_spi.split()
            if len(tokens) != 4:
                logger.error(('Invalid usb device serial number parsing!'
			' {}').format(tokens))
                sys.exit(1)
            aardvark_i2c_spi_dev_list.append(usb_i2c_spi.split()[3])

    return aardvark_i2c_spi_dev_list

def aardvark_i2c_spi_dev_index_from_serial(serial):
    (dev_ids, serial_nums) = aardvark_i2c_spi_dev_list_ext()
    if not dev_ids or not serial_nums:
        return None
    if serial in serial_nums:
        index = serial_nums.index(serial)
        return dev_ids[index]
    logger.error('Device with serial num: {0} not found!'.format(serial))
    if len(serial_nums) != 0:
        logger.info('Found serial numbers:{0}'.format(serial_nums))
    return None

def aardvark_i2c_find_slaves(dev_id, serial):
    n_devs, devs = aa_find_devices(10)
    dev_handle =  devs[dev_id]
    h = aa_open(dev_handle)
    features = aa_features(h)
    if features != 27:
        logger.error("Invalid device features!: {0}".format(features))
        sys.exit(1)
    status = aa_i2c_free_bus(h)
    logger.info("Free Bus: {0}".format(aa_status_string(status)))
    status = aa_configure(h,2)
    logger.info("Configure i2c mode! status:{0}".format(status))
    logger.info("Pull up status: {0}".format(status))
    data = array('B', [])
    for s in [1, 10, 100, 400]:
        status = aa_i2c_bitrate(h, s)
        logger.info("Configure bitrate! status:{0}".format(status))
        for address in range(0x0, 0x7f):
            for addr_mode in [0x0, 0x1]:
                (status, sent_bytes) = aa_i2c_write_ext(h, address, addr_mode, data)
                if status == AA_I2C_STATUS_OK:
                    logger.info((" ********* FOUND DEVICE AT ADDRESS: {0} ADDR_MODE:{1} SPEED: {2}"
                        " ********").format(hex(address), addr_mode, s));

if __name__== "__main__":
    dev_list = aardvark_i2c_spi_dev_list()
    if len(dev_list) == 0:
        logger.error('No aardvark i2c spi devices found!')
    else:
        logger.info('Found {0} Aardvark i2c spi device(s)!'.format(len(dev_list)))
        for idx, serial in enumerate(dev_list):
            logger.info('Dev:{0} Serial Number: {1} ... slaves are ...'.format(idx, serial))
            aardvark_i2c_find_slaves(idx, serial)
