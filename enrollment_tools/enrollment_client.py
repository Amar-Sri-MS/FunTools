#!/usr/bin/env python3

##############################################################################
#  enrollment_client.py
#
#  Utility
#
#  Copyright (c) 2018-2019. Fungible, inc. All Rights Reserved.
#
##############################################################################

import array
import binascii
import argparse
import requests
import json
from os import path
from pathlib import Path

from probeutils.dut import *
from probeutils.dbgclient import *


###############################################################
#
# Constants
#
###############################################################
class CMD(object):
    ''' namespace for constants '''
    GET_SERIAL_NUMBER = 0xFE000000
    GET_STATUS = 0xFE010000
    GET_ENROLL_INFO = 0xFF050000
    SET_ENROLL_INFO = 0xFF060000

# Chip must report being in this boot step for enrollment
BOOT_STEP_PUF_INIT = (0x1A<<2)

#Default i2c clock speed
I2C_CLOCK_SPEED_DEFAULT = 500

###########################################################################
#
# Error checking and reporting
#
###########################################################################
def cmd_status(response_bytes):
    return  response_bytes[1] & 0xf

def cmd_status_ok(response_bytes):
    ''' second byte is status '''
    return cmd_status(response_bytes) == 0

def cmd_reply_length(response_bytes):
    ''' length is encoded in third and fourth byte '''
    return response_bytes[3] + response_bytes[2] * 255

def report_error(cmd, rdata):
    print("command %s failure = %d; command length = %d -- actual %d" %
          (cmd, cmd_status(rdata), cmd_reply_length(rdata), len(rdata)))

##########################################################################
#
# I2C routines as written return a list of integers: convert to byte string
#
# ref: https://www.python.org/doc/essays/list2str/
#
#########################################################################

def int_list_to_byte_str(l):
    return array('B', l).tostring()

def byte_str_to_int_list(s):
    a = array('B')
    a.fromstring(s)
    return list(a)


###########################################################################
#
# I2C connection and commands
#
###########################################################################

class DBG_Chal(object):
    ''' i2c connection object '''
    def __init__(self, dut, chip_inst=0):
        self.i2c_proxy_ip = dut.get("i2c_proxy_ip", None)
        self.i2c_probe_serial = dut.get("i2c_probe_serial", None)
        self.i2c_slave_addr = dut.get("i2c_slave_addr",None)
        self.bmc_ip_addr = dut.get("bmc_ip_addr", None)
        self.i2c_bitrate = dut.get('i2c_bitrate', I2C_CLOCK_SPEED_DEFAULT)

        self.connected = False
        self.dbgprobe = None
        self.chip_inst = chip_inst

    def __del__(self):
        print('Destroying the connection!')
        if self.connected is True:
            self.disconnect()

    def connect(self):
        if self.connected:
            print('Already connected!')
            return True

        dbgprobe = DBG_Client()
        if self.bmc_ip_addr is None:
            if self.i2c_proxy_ip is None:
                print('Invalid proxy ip addr(None)!')
                return False
            if self.i2c_probe_serial is None:
                print('Invalid i2c probe serial(None)!')
                return False
            if not self.i2c_slave_addr:
                print('Invalid slave_addr(None)!')
                return False
            if (self.i2c_bitrate  < 1) or (self.i2c_bitrate > I2C_CLOCK_SPEED_DEFAULT):
                print('Invalid bus clock speed: {}'.format(self.i2c_bitrate))
                return False

            status = dbgprobe.connect(mode='i2c', bmc_board=False,
                                      probe_ip_addr=self.i2c_proxy_ip,
                                      probe_id=self.i2c_probe_serial,
                                      slave_addr=int(self.i2c_slave_addr, 0),
                                      i2c_bitrate=self.i2c_bitrate,
                                      force=True)
        else:
            status = dbgprobe.connect(mode='i2c', bmc_board=True,
                                      bmc_ip_address=self.bmc_ip_addr)
        if status is True:
            self.dbgprobe = dbgprobe
            self.connected = True
            print('Successfully connected to debug probe!')
            return True

        print('Failed to connect to debug probe!')
        self.dbgprobe = None
        self.connected = False
        return False

    def disconnect(self):
        self.connected = False
        status = self.dbgprobe.disconnect()
        if status is True:
            print('Successfully disconnected!')
            self.dbgprobe = None
            return True

        print('Disconnect failed!')
        return status

    def check_boot_step(self, desired_boot_step):
        ''' check that the chip is in the right boot step
        status returns header (4), tamper_status (4), tamper_timestamp (4)
        status (4), RTC time (4), boot step (1), upgrade(1), etc... '''
        (status, rdata) = self.dbgprobe.dbg_chal_cmd(CMD.GET_STATUS,
                                                     chip_inst=self.chip_inst)

        if status is True and cmd_status_ok(rdata) and cmd_reply_length(rdata) > 20:
            return rdata[20] == desired_boot_step

        report_error("GetStatus", rdata)
        return False

    def get_serial_number(self):
        ''' get the chip's serial number '''
        (status, rdata) = self.dbgprobe.dbg_chal_cmd(CMD.GET_SERIAL_NUMBER,
                                                     chip_inst=self.chip_inst)
        if status is True and cmd_status_ok(rdata):
            return int_list_to_byte_str(rdata[4:])

        report_error("GetSerialNumber", rdata)
        return None

    def get_enroll_tbs(self):
        (status, rdata) = self.dbgprobe.dbg_chal_cmd(CMD.GET_ENROLL_INFO,
                                                     chip_inst=self.chip_inst)
        if status is True and cmd_status_ok(rdata):
            return int_list_to_byte_str(rdata[4:])

        report_error("Enrollment", rdata)
        return None

    def save_enroll_cert(self, cert):

        (status, rdata) = self.dbgprobe.dbg_chal_cmd(CMD.SET_ENROLL_INFO,
                                                     data=byte_str_to_int_list(cert),
                                                     chip_inst=self.chip_inst)
        if status is True and cmd_status_ok(rdata):
            return True

        report_error("WriteEnrollmentCertificate", rdata)
        return False


#########################################################################
#
# Get Enrollment Certificate from f1registration.fungible.com
#
#########################################################################

def generate_enrollment_cert(tbs_cert, verbose=False):

    # always print the TBS since it is precious
    print("Enrollment Information: " + binascii.b2a_hex(tbs_cert))

    tbs_cert_64 = binascii.b2a_base64(tbs_cert)

    if verbose:
        print("TBS: ", tbs_cert_64)

    response = requests.put("https://f1reg.fungible.com/cgi-bin/enrollment_server.cgi",
                            data=tbs_cert_64)

    if response.status_code != requests.codes.ok:
        print("Server response: %d %s" % (response.status_code, response.reason))
        return None

    cert_64 = response.text

    if verbose:
        print("CERT: ", cert_64)

    return binascii.a2b_base64(cert_64)


def get_cert_of_serial_number(sn, verbose=False):

    sn_64 = binascii.b2a_base64(sn).rstrip()

    url = "https://f1reg.fungible.com/cgi-bin/enrollment_server.cgi?cmd=cert&sn=%s" % sn_64
    response = requests.get(url)

    if response.status_code != requests.codes.ok:
        print("Server response: %d %s" % (response.status_code, response.reason))
        return None

    cert_64 = response.text

    if verbose:
        print("CERT: ", cert_64)

    return binascii.a2b_base64(cert_64)


#########################################################################
#
# Main
#
#########################################################################

def dut_info_get(dut_name, dut_file):
    if not dut_file:
        dut_file = dut_cfg_file = pkg_resources.resource_filename('probeutils', 'dut.cfg')
        #print('Using pre-installed dut config file: {}'.format(dut_file))
    else:
        dut_file = str(Path(dut_file).resolve())

    print('Using dut config file: {}'.format(dut_file))
    dut_json = json.load(open(dut_file))
    dut_info = dut_json.get(dut_name, None)
    if not dut_info:
        return None

    bmc_ip = dut_info.get('bmc_ip', None)
    if bmc_ip:
        print('bmc info is not expected in non-bmc mode for dut {}. Ignoring...'.format(dut_name))
    i2c_proxy_ip = dut_info.get('i2c_proxy_ip', None)
    i2c_slave_addr = dut_info.get('i2c_slave_addr', None)
    i2c_probe_serial = dut_info.get('i2c_probe_serial', None)
    try:
        i2c_proxy_ip = socket.gethostbyname(i2c_proxy_ip)
    except socket.error:
        logger.error('Invalid i2c proxy: {}'.format(i2c_proxy_ip))
        i2c_proxy_ip = None
    if not i2c_probe_serial or not i2c_slave_addr or not i2c_proxy_ip:
        logger.error('Invalid dut config for dut: {}'.format(dut_name))
        return None
    return dut_info

def main():
    parser = argparse.ArgumentParser(
        description="Perform enrollment via I2C",
        epilog="Challenge Interface must be accessible via debug probe "\
        "prior to running this script, check the device documentation on how to do this")

    # can either do enrollment using a dut-file or a bmc-ip_addr

    #parser.add_argument("--dut-file", help="Dut file (JSON)")
    parser.add_argument('--dut-file', help='JSON dut config input file', type=Path)
    parser.add_argument("--dut-name", help="Dut name")
    parser.add_argument("--bmc-ip-addr", help="BMC IP Address")

    parser.add_argument("--chip", type=int, required=True, choices=range(0, 2),
            help='chip instance number. For boards with signle dpu, it should be \"0\"')

    args = parser.parse_args()

    #print args
    if args.bmc_ip_addr and (args.dut_name or args.dut_file):
        print('bmc_ip_addr and dut arguments are mutually exclusive!')
        sys.exit(1)

    dut = None
    if not args.bmc_ip_addr:
        if not args.dut_name:
            print('dut name is required!')
            sys.exit(1)
        dut = dut_info_get(args.dut_name, args.dut_file)
    else:
        dut = { 'bmc_ip_addr' : args.bmc_ip_addr }

    if not dut:
        print('Failed to get the dut info for {}'.format(args.dut_name))
        sys.exit(1)

    #print(dut)

    # get enrollment info
    # check for connection
    dbgprobe = DBG_Chal(dut, args.chip)
    status = dbgprobe.connect()
    if status is False:
        print('Connection failed!')
        return False

    print('Connected to probe')
    # verify we are in the correct step
    if not dbgprobe.check_boot_step(BOOT_STEP_PUF_INIT):
        print("Chip is not at the correct boot step for enrollment")
        return False

    print("Chip at the correct boot step; retrieving serial number")
    # Get serial number
    sn = dbgprobe.get_serial_number()
    if sn is None:
        print("Error getting the chip serial number")
        return False

    cert = get_cert_of_serial_number(sn)

    #if the cert is there, write it
    if cert:
        print("Found certificate for this serial number")
        if dbgprobe.save_enroll_cert(cert):
            print("Enrollment certificate installed on chip")
            return True

        print("Enrollment certificate could not be installed")
        return False


    # cert was not in database: enroll and get tbs information
    tbs_cert = dbgprobe.get_enroll_tbs()
    if not tbs_cert:
        print("Error getting the enrollment information")
        return False

    # get enrollment certificate from enrollment server
    # do not write it, it will be when running this script
    # again on the same chip
    cert = generate_enrollment_cert(tbs_cert)
    if cert:
        print("Enrollment certificate generated")
        return True

    print("Error getting the enrollment certificate")
    return False



if __name__ == '__main__':
    main()
