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
# Dbg infrastructure -- modified from secure_debug_i2c.py
#
###############################################################
class CMD(object):
    GET_SERIAL_NUMBER = 0xFE000000
    GET_STATUS = 0xFE010000
    GET_ENROLL_INFO = 0xFF050000
    SET_ENROLL_INFO = 0xFF060000

# Chip must report being in this boot step for enrollment
BOOT_STEP_PUF_INIT = (0x16<<2)

CMD_STATUS_CODE_STR = [
    "OK",
    "Invalid Command",
    "Authorization Error",
    "Invalid Signature",
    "Bus Error",
    "Reserved",
    "Crypto Error",
    "Invalid Parameter"
]


def cmd_status_ok(response_bytes):
    ''' second byte is status '''
    return (response_bytes[1] & 0xf) == 0

def cmd_reply_length(response_bytes):
    ''' length is encoded in third and fourth byte '''
    return response_bytes[3] + response_bytes[2] * 255

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
            if (self.chip_inst >= 2):
                print('Error: Chip instance number should be in range 0-1')
                sys.exit(1)
            print('chip_inst: {0}'.format(self.chip_inst))

    def __del__(self):
        print('Destroying the connection!')
        if self.connected is True:
            self.disconnect()

    def connect(self):
        if self.connected == True:
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
        else:
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
        else:
            print('Disconnect failed!')
            return False

    def check_boot_step(self, desired_boot_step):
        ''' check that the chip is in the right boot step
        status returns header (4), tamper_status (4), tamper_timestamp (4)
        status (4), RTC time (4), boot step (1), upgrade(1), etc... '''
        (status, rdata) = self.dbgprobe.dbg_chal_cmd(CMD.GET_STATUS,
                                                     chip_inst=self.chip_inst)
        print(status)
        print(rdata)

        print("command success = %s" % cmd_status_ok(rdata),
              "command length = %d -- actual %d" % (cmd_reply_length(rdata), len(rdata)))

        if status is True and cmd_status_ok(rdata) and cmd_reply_length(rdata) > 20:
            if rdata[20] == desired_boot_step:
                print("Chip in correct boot step")
                return True
            else:
                print "Device is not in the proper state: {:02x}".format(boot_step)


        return False

    def enroll(self):
        (status, rdata) = self.dbgprobe.dbg_chal_cmd(CMD.GET_ENROLL_INFO,
                                                     chip_inst=self.chip_inst)
        if status is True and cmd_status_ok(rdata):
            print("Got enrollment data:")
            print(rdata[4:])
            return rdata[4:]

        print("Error getting enrollment data")
        return None

    def get_enroll_tbs(self):
        ''' return the TBS enroll info or None if error '''
        if not self.check_boot_step(BOOT_STEP_PUF_INIT):
            return None
        return self.enroll()

    def save_enroll_cert(self, cert):
        (status, rdata) = self.dbgprobe.dbg_chal_cmd(CMD.SET_ENROLL_INFO,
                                                     data=list(cert),
                                                     chip_inst=self.chip_inst)
        return status is True and cmd_status_ok(rdata)


##############################################################################################
#
# Get Enrollment Certificate from f1registration.fungible.com
#
##############################################################################################

def get_enrollment_cert(tbs_cert):

    tbs_cert_64 = binascii.b2a_base64(tbs_cert)

    if verbose:
        print "TBS: ", tbs_cert_64

    # no security for testing
    response = requests.put("https://f1registration.fungible.com/cgi-bin/enrollment_server.cgi",
                            data=tbs_cert_64, verify='./f1registration.ca.pem')

    if response.status_code != requests.code.ok:
        print "Server response: %d %s" % (response.status_code, response.reason)
        return None

    cert_64 = response.text

    if verbose:
        print "CERT: ", cert_64

    return binascii.a2b_base64(cert_64)



def main():

    global verbose

    parser = argparse.ArgumentParser(
        description="Perform enrollment via I2C",
        epilog="Challenge Interface must be accessible via debug probe prior to running this script,\
        check the device documentation on how to do this")
    parser.add_argument("--dut", required=True, help="Dut name")
    parser.add_argument("--tbs", type=argparse.FileType('r'),
                        help="Read the enrollment tbs from the file")

    args = parser.parse_args()

    dbgprobe = DBG_Chal(args.dut)

    if args.tbs:
        # read the tbs from file
        tbs_cert = args.tbs.read()

    else:
        # get enrollment info
        # check for connection
        status = dbgprobe.connect()
        if status is False:
            print 'Connection failed!'
            return False

        print("Connected to probe")
        tbs_cert = dbgprobe.get_enroll_tbs()

        # disconnect
        dbgprobe.disconnect()

        # power cycle

    # get enrollment certificate from enrollment server
    cert = get_enrollment_cert(tbs_cert)

    # if cert is not None:
    #     # (re)connect
    #     status = dbgprobe.connect()
    #     if status is False:
    #         print 'Reconnection failed!'
    #         return False

    #     if dbgprobe.save_enroll_cert(cert):
    #         print "Chip enrolled!"
    #     else:
    #         print "Error enrolling chip"

    #     dbgprobe.disconnect()


main()
