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

import httplib
import ssl

from probeutils.dut import *
from probeutils.dbgclient import *

verbose = False

###############################################################
#
# Dbg infrastructure -- modified from secure_debug_i2c.py
#
###############################################################
class CMD(object):
    GET_STATUS = 0xFE010000
    GET_ENROLL_INFO = 0xFF050000
    SET_ENROLL_INFO = 0xFF060000

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

SBP_STATUS_STR = [
    "Status at last tamper",
    "Timestamp of last tamper",
    "Raw tamper status",
    "Current Time",
    "Boot Status",
    "eSecure Firmware Version",
    "Host Firmware Version",
    "Debug Grants"]

# Chip must report being in this boot step for enrollment
BOOT_STEP_PUF_INIT = (0x16<<2)


def cmd_status_ok(response_bytes):
    ''' first 4 bytes are the response header in little-endian format
    where bits 0-15 = size, 16-19 = status so just check byte 2'''
    return (response_bytes[2] & 0xf) == 0

def cmd_reply_length(response_bytes):
    ''' first 4 bytes are the response header in little-endian format
    where bits 0-15 = size, 16-19 = status so just combine bytes 0 and 1'''
    return response_bytes[0] + response_bytes[1] * 255


class DBG_Chal(object):
    def __init__(self, dut_name):
        print('dut: %s' % str(dut_name))
        self.probe_ip_addr = None
        self.probe_id = None
        self.i2c_slave_addr = None
        self.connected = False
        self.dbgprobe = None
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
        else:
            self.bmc_ip_addr = dut_i2c_info[1]
            status = dbgprobe.connect(mode='i2c', bmc_board=True,
                                        bmc_ip_address=self.bmc_ip_addr)

    def __del__(self):
        print('Destroying the connection!')
        if self.connected is True:
            self.disconnect()

    def connect(self):
        if self.probe_ip_addr is None:
            print('Invalid ip addr: {0}'.format(self.probe_ip_addr))
            return False
        if self.probe_id is None:
            print('Invalid probe_id: {0}'.format(self.probe_id))
            return False
        if not self.i2c_slave_addr:
            print('Invalid slave_addr: {0}'.format(self.i2c_slave_addr))
            return False
        if self.connected is True:
            print('Already connected!')
            return True
        dbgprobe = DBG_Client()
        if self.bmc_board is False:
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
        (status, rdata) = self.dbgprobe.dbg_chal_cmd(CMD.GET_STATUS)
        if status is True and cmd_status_ok(rdata) and cmd_reply_length(rdata) > 20:
            boot_step = rdata[20]
            if boot_step == desired_boot_step:
                return True
            else:
                print "Device is not in the proper state: {:02x}".format(boot_step)

        return False

    def enroll(self):
        (status, rdata) = self.dbgprobe.dbg_chal_cmd(CMD.GET_ENROLL_INFO)
        if status is True and cmd_status_ok(rdata):
            return rdata[4:]
        return None

    def get_enroll_tbs(self):
        ''' return the TBS enroll info or None if error '''
        if not self.check_boot_step(BOOT_STEP_PUF_INIT):
            return None

        return self.enroll()

    def save_enroll_cert(self, cert):
        (status, rdata) = self.dbgprobe.dbg_chal_cmd(CMD.SET_ENROLL_INFO, list(cert))
        return status is True and cmd_status_ok(rdata)


def get_enrollment_cert(tbs_cert):

    tbs_cert_64 = binascii.b2a_base64(tbs_cert)

    if verbose:
        print "TBS: ", tbs_cert_64

    # no security for testing
    conn = httplib.HTTPSConnection("localhost", context=ssl._create_unverified_context())

    conn.request("PUT", "/cgi-bin/enrollment_server.py", tbs_cert_64)

    http_response = conn.getresponse()

    if http_response.status != 200:
        print "Server response: %d %s" % (http_response.status, http_response.reason)
        return None

    cert_64 = http_response.read()

    if verbose:
        print "CERT: ", cert_64

    conn.close()

    return binascii.a2b_base64(cert_64)



def main():

    global verbose

    parser = argparse.ArgumentParser(
        description="Perform enrollment via I2C",
        epilog="Challenge Interface must be accessible via debug probe prior to running this script,\
        check the device documentation on how to do this")
    parser.add_argument("--dut", required=True, help="Dut name")
    parser.add_argument("--verbose", action='store_true', help="Print more information")
    parser.add_argument("--tbs", type=argparse.FileType('r'),
                        help="Read the enrollment tbs from the file")

    args = parser.parse_args()

    verbose = args.verbose # set the global

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

        tbs_cert = dbgprobe.get_enroll_tbs()

        # disconnect
        dbgprobe.disconnect()

        # power cycle

    # get enrollment certificate from enrollment server
    cert = get_enrollment_cert(tbs_cert)

    if cert is not None:
        # (re)connect
        status = dbgprobe.connect()
        if status is False:
            print 'Reconnection failed!'
            return False

        if dbgprobe.save_enroll_cert(cert):
            print "Chip enrolled!"
        else:
            print "Error enrolling chip"

        dbgprobe.disconnect()


main()
