#! /usr/bin/env python2

##############################################################################
#  enrollment_client.py
#
#  Utility
#
#  Copyright (c) 2018-2019. Fungible, inc. All Rights Reserved.
#
##############################################################################

import binascii
import argparse

import requests

from probeutils.dut import *
from probeutils.dbgclient import *

###############################################################
#
# Constants
#
###############################################################
class CMD(object):
    GET_SERIAL_NUMBER = 0xFE000000
    GET_STATUS = 0xFE010000
    GET_ENROLL_INFO = 0xFF050000
    SET_ENROLL_INFO = 0xFF060000

# Chip must report being in this boot step for enrollment
BOOT_STEP_PUF_INIT = (0x16<<2)

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


###########################################################################
#
# I2C connection and commands
#
###########################################################################

class DBG_Chal(object):
    def __init__(self, dut_name, chip_inst=None):
        logger.debug('dut: {0}'.format(dut_name))
        self.probe_ip_addr = None
        self.probe_id = None
        self.i2c_slave_addr = None
        self.connected = False
        self.dbgprobe = None
        self.chip_inst = None
        dut_i2c_info = dut().get_i2c_info(dut_name)
        if dut_i2c_info is None:
            print('Failed to get i2c connection details!')
            return None

        # if not board with bmc (emulation and socketed test boards do not have bmc)
        self.bmc_board = dut_i2c_info[0]
        if self.bmc_board is False:
            self.probe_id = dut_i2c_info[1]
            self.probe_ip_addr = dut_i2c_info[2]
            self.i2c_slave_addr = dut_i2c_info[3]
            if chip_inst is not None:
                print('****Ignoring the chip instance number****')
        else:
            self.bmc_ip_addr = dut_i2c_info[1]
            if chip_inst is None:
                print('Error: Chip instance number should be provided for board with BMC')
                sys.exit(1)
                self.chip_inst = int(chip_inst)
            if  self.chip_inst >= 2:
                print('Error: Chip instance number should be in range 0-1')
                sys.exit(1)
                print('chip_inst: {0}'.format(self.chip_inst))

    def __del__(self):
        print('Destroying the connection!')
        if self.connected is True:
            self.disconnect()

    def connect(self):
        if self.connected:
            print('Already connected!')
            return True

        dbgprobe = DBG_Client()
        if self.bmc_board is False:
            if self.probe_ip_addr is None:
                print('Invalid ip addr: {0}'.format(self.probe_ip_addr))
                return False
            if self.probe_id is None:
                print('Invalid probe_id: {0}'.format(self.probe_id))
                return False
            if not self.i2c_slave_addr:
                print('Invalid slave_addr: {0}'.format(self.i2c_slave_addr))
                return False
            status = dbgprobe.connect(mode='i2c', bmc_board=False,
                                      probe_ip_addr=self.probe_ip_addr,
                                      probe_id=self.probe_id,
                                      slave_addr=self.i2c_slave_addr)
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
            return rdata[4:]

        report_error("GetSerialNumber", rdata)
        return None

    def get_enroll_tbs(self):
        (status, rdata) = self.dbgprobe.dbg_chal_cmd(CMD.GET_ENROLL_INFO,
                                                     chip_inst=self.chip_inst)
        if status is True and cmd_status_ok(rdata):
            return rdata[4:]

        report_error("Enrollment", rdata)
        return None

    def save_enroll_cert(self, cert):
        (status, rdata) = self.dbgprobe.dbg_chal_cmd(CMD.SET_ENROLL_INFO,
                                                     data=list(cert),
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
    print "Enrollment Information: " + binascii.b2a_hex(tbs_cert)

    tbs_cert_64 = binascii.b2a_base64(tbs_cert)

    if verbose:
        print "TBS: ", tbs_cert_64

    response = requests.put("https://f1reg.fungible.com/cgi-bin/enrollment_server.cgi",
                            data=tbs_cert_64, verify='./f1registration.ca.pem')

    if response.status_code != requests.codes.ok:
        print "Server response: %d %s" % (response.status_code, response.reason)
        return None

    cert_64 = response.text

    if verbose:
        print "CERT: ", cert_64

    return binascii.a2b_base64(cert_64)


def get_cert_of_serial_number(sn, verbose=False):

    sn_64 = binascii.b2a_base64(sn)

    url = "https://f1reg.fungible.com/cgi-bin/enrollment_server.cgi?cmd=cert&sn=%s" % sn_64
    response = requests.get(url, verify='./f1registration.ca.pem')

    if response.status_code != requests.codes.ok:
        print "Server response: %d %s" % (response.status_code, response.reason)
        return None

    cert_64 = response.text

    if verbose:
        print "CERT: ", cert_64

    return binascii.a2b_base64(cert_64)


#########################################################################
#
# Main
#
#########################################################################

def main():

    parser = argparse.ArgumentParser(
        description="Perform enrollment via I2C",
        epilog="Challenge Interface must be accessible via debug probe "\
        "prior to running this script, check the device documentation on how to do this")
    parser.add_argument("--dut", help="Dut name")
    parser.add_argument("--tbs", type=argparse.FileType('r'),
                        help="Test: Read the enrollment tbs from the file")
    parser.add_argument("--sn", type=argparse.FileType('r'),
                        help="Test: Read the serial number from the file")

    args = parser.parse_args()

    if args.tbs:
        # read the tbs from file
        tbs_cert = args.tbs.read()
        # get enrollment certificate from enrollment server
        cert = generate_enrollment_cert(tbs_cert, True)
        return True
    elif args.sn:
        # read the sn from file
        sn = args.sn.read()
        # get enrollment certificate from enrollment server
        cert = get_cert_of_serial_number(sn, True)
        return True

    # get enrollment info
    # check for connection
    dbgprobe = DBG_Chal(args.dut)
    status = dbgprobe.connect()
    if status is False:
        print('Connection failed!')
        return False

    print('Connected to probe')
    # verify we are in the correct step
    if not dbgprobe.check_boot_step(BOOT_STEP_PUF_INIT):
        print("Chip is not at the correct boot step for enrollment")
        return False

    # Get serial number
    sn = dbgprobe.get_serial_number()
    if sn is None:
        print("Error getting the chip serial number")
        return False

    cert = get_cert_of_serial_number(sn)

    #if the cert is there, write it
    if cert:
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

main()
