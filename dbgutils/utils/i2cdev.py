#!/usr/bin/python

import sys
import usb.core

def aardvark_i2c_spi_dev_list():
    # find USB devices
    dev = usb.core.find(find_all=True)
    # loop through devices
    aardvark_i2c_spi_dev_list = list()
    for cfg in dev:
        if cfg.idVendor == 0x403 and cfg.idProduct == 0xe0d0:
            dev_info = str(cfg)
            matched_lines = [line for line in dev_info.split('\n') if "iSerialNumber" in line]
            if len(matched_lines) != 1:
                print("Invalid usb device metadata parsing! {}".format(matched_lines))
                sys.exit(1)
            usb_i2c_spi = matched_lines[0]
            tokens = usb_i2c_spi.split()
            if len(tokens) != 4:
                print("Invalid usb device serial number parsing! {}".format(tokens))
                sys.exit(1)
            aardvark_i2c_spi_dev_list.append(usb_i2c_spi.split()[3])

    return aardvark_i2c_spi_dev_list

def aardvark_i2c_spi_dev_index_from_serial(serial):
    dev_list = aardvark_i2c_spi_dev_list()
    if len(dev_list) == 0:
        print "No aardvark i2c spi devices found!"
        return None
    if serial in dev_list:
        return dev_list.index(serial)
    print('Device with serial num: {0} not found!'.format(serial))
    if len(dev_list) != 0:
        print('dev_list:{0}'.format(dev_list))
    return None

if __name__== "__main__":
    dev_list = aardvark_i2c_spi_dev_list()
    if len(dev_list) == 0:
        print "No aardvark i2c spi devices found!"
    else:
        print('Found {0} Aardvark i2c spi device(s)!'.format(len(dev_list)))
        for idx, serial in enumerate(dev_list):
            print 'Dev:{0} Serial Number: {1}'.format(idx, serial)
