#!/usr/bin/env python

'''
SBP debug challange api using i2c
'''

import os, sys
workspace = os.environ["WORKSPACE"]
sbp_tools_path = workspace + 'SBPFirmware/software/devtools/firmware'
print 'sbp_tools_path: {0}'.format(sbp_tools_path)
sys.path.append(sbp_tools_path)
import utils
from probeutils.dbgclient import *
import binascii
from array import array
import struct
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
#from named_bitfield import named_bitfield

class CMD(object):
    GET_SERIAL_NUMBER = 0xFE000000
    GET_OTP = 0xFE0B0000
    GET_STATUS = 0xFE010000
    INJECT_CERTIFICATE = 0xFE0A0000
    GET_CHALLANGE = 0xFD000000
    GRANT_DBG_ACCESS = 0xFD010000
    READ = 0xFC020000
    BUFFER_DATA = 0x00002000
    BUFFER_CLEAR = 0x00003000
    BUFFER_END = 0x00004000
    PROGRAM = 0xFC010000
    ERASE_SECTOR = 0xFC000000


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

class const(object):
    # DBG_GRANTS = 0x000C00F0
    # DBG_GRANTS = 0x00000200
    DBG_GRANTS = 0x00030200
    IP_ADDR = '10.1.20.69'
    CONN_MODE = 'i2c'
    I2C_DEV_ID = 2238701524
    PRIVATE_KEY_PASSWORD = 'fun123'
    I2C_SLAVE_ADDR = 0x73
    CERT_KEY_DIR = workspace

class DBG_Chal(object):
    def __init__(self, mode, ip_addr, dev_id, i2c_slave_addr):
        self.mode = mode
        self.ip_addr = ip_addr
        self.dev_id = dev_id
        self.i2c_slave_addr = i2c_slave_addr
        self.connected = False
        self.dbgprobe = None

    def __del__(self):
        print('Destroying the connection!')
        self.disconnect()

    def connect(self):
        if self.mode is None:
            print('Invalid mode: {0}'.format(self.mode))
            return False
        if self.ip_addr is None:
            print('Invalid ip addr: {0}'.format(self.ip_addr))
            return False
        if self.dev_id is None:
            print('Invalid dev_id: {0}'.format(self.dev_id))
            return False

        if self.connected == True:
            print('Already connected!')
            return True

        dbgprobe = DBG_Client()
        status = dbgprobe.connect(self.mode, self.ip_addr, self.dev_id,
                                  self.i2c_slave_addr)
        if status is True:
            self.dbgprobe = dbgprobe
            self.connected = True
            print('Successfully connect to debug probe!')
            return True
        else:
            print('Failed to connect to debug probe!')
            self.dbgprobe = None
            self.connected = False
            return False

    def disconnect(self):
        if self.connected:
            status = self.dbgprobe.disconnect()
            if status is True:
                print('Successfully disconnected!')
                return True
            else:
                print('Disconnect failed!')
                return False

    def decode_status_bytes(self, data):
        print 'Status:\n'
        i = 0
        status_size = len(data)
        status_decoded = dict()
        while i < status_size:
            status_str_idx = i/4
            if status_str_idx < len(SBP_STATUS_STR):
                print '\t{0}{1}'.format(SBP_STATUS_STR[status_str_idx], \
                        hex(int(binascii.hexlify(array('B', data[i:i+4])), 16)))
                status_decoded[SBP_STATUS_STR[status_str_idx]] = \
                        hex(int(binascii.hexlify(array('B', data[i:i+4])), 16))

                i+=4
            else:
                print '\tExtra Bytes: {0}'.format([hex(x) for x in data[i:status_size]])
                status_decoded["Extra Bytes"] = data[i:status_size]
                i = status_size
        return status_decoded

    def int_to_bytes(self, val, num_bytes):
            print "int_to_bytes"
            print list(struct.unpack('BBBB', struct.pack('<I', val)))
            byte_array = [(val & (0xff << pos*8)) >> pos*8 for pos in range(num_bytes)]
            print byte_array
            return byte_array

    def cmd_status_code_str(self, header_bytes):
        header = array('B', list(reversed(header_bytes[0:4])))
        status = int(binascii.hexlify(header), 16)
        sts = (status >> 16) & 0xf
        if sts >=0 and sts < len(CMD_STATUS_CODE_STR):
            return CMD_STATUS_CODE_STR[sts]
        return "reserved"

    def cmd_status_ok(self, header_bytes):
        header = array('B', list(reversed(header_bytes[0:4])))
        status = int(binascii.hexlify(header), 16)
        sts = (status >> 16) & 0xf
        return sts == 0

    def cmd_reply_length(self, header_bytes):
        header = array('B', list(reversed(header_bytes[0:4])))
        status = int(binascii.hexlify(header), 16)
        return status & 0xFFFF

    def get_serial_number(self):
        print('Getting serial number...!')
        (status, rdata)= self.dbgprobe.dbg_chal_cmd(CMD.GET_SERIAL_NUMBER)
        if status == True:
            #print "Serial number: {0}".format([hex(x) for x in rdata] if rdata else None)
            if not self.cmd_status_ok(rdata[0:4]):
                return (False, cmd_status_code_str(rdata))
            else:
                return (status, rdata[4:])
        else:
            err_msg = "Dbg chal command error! {0}".format(rdata)
            print err_msg
            return (False, err_msg)

    def get_buffer_sizes(self):
        print "Getting buffer sizes"
        self.get_status()
        (status, rdata)= self.dbgprobe.dbg_chal_cmd(0xFC020000|0x00001000)
        print status, rdata
        (status, rdata)= self.dbgprobe.dbg_chal_cmd(0xFC010000|0x00001000)
        print status, rdata
        (status, rdata)= self.dbgprobe.dbg_chal_cmd(0xFE080000)
        print status, rdata

    def write_flash(self):
        print "Write flash"
        cmd = CMD.PROGRAM | CMD.BUFFER_CLEAR
        (status, rdata)= self.dbgprobe.dbg_chal_cmd(cmd)
        print status, [x for x in rdata]
        cmd = CMD.PROGRAM | CMD.BUFFER_DATA
        l = [0, 0, 0, 0]
        l.extend([0xff, 0x0, 0, 0])
        # create page worth
        data = []
        for i in range(256):
            data.append(0x56)
        l.extend(data)
        (status, rdata)= self.dbgprobe.dbg_chal_cmd(cmd, l)
        print status, [x for x in rdata]
        cmd = CMD.PROGRAM | CMD.BUFFER_END
        (status, rdata)= self.dbgprobe.dbg_chal_cmd(cmd, [0, 0, 0, 0])
        print status, [x for x in rdata]

    def erase_flash(self):
        print "Erase flash"
        cmd = CMD.ERASE_SECTOR
        (status, rdata)= self.dbgprobe.dbg_chal_cmd(cmd, [0, 0, 0, 0])
        print status, [x for x in rdata]

    def read_flash(self):
        print "Read flash"
        cmd = CMD.READ | CMD.BUFFER_DATA
        (status, rdata)= self.dbgprobe.dbg_chal_cmd(cmd, [0, 0, 0, 0, 16, 0, 0, 0])
        print status, [hex(x) for x in rdata]


    def set_watchdog_timeout(self):
        print ("Setting watchdog")
        (status, rdata)= self.dbgprobe.dbg_chal_cmd(0x54220000, [0xA, 0, 0, 0])
        if status == True:
            print "Set watchdog successful"
            #print "Serial number: {0}".format([hex(x) for x in rdata] if rdata else None)
            if not self.cmd_status_ok(rdata[0:4]):
                return (False, cmd_status_code_str(rdata))
            else:
                return (status, rdata[4:])
        else:
            err_msg = "Dbg chal command error! {0}".format(rdata)
            print err_msg
            return (False, err_msg)

    def block_main_loop(self):
        print ("Block main loop")
        (status, rdata)= self.dbgprobe.dbg_chal_cmd(0x54230000)
        if status == True:
            print "Block main successful"
            #print "Serial number: {0}".format([hex(x) for x in rdata] if rdata else None)
            if not self.cmd_status_ok(rdata[0:4]):
                return (False, cmd_status_code_str(rdata))
            else:
                return (status, rdata[4:])
        else:
            err_msg = "Dbg chal command error! {0}".format(rdata)
            print err_msg
            return (False, err_msg)

    def get_status(self):
        print "Getting status...!"
        (status, rdata)= self.dbgprobe.dbg_chal_cmd(CMD.GET_STATUS)
        if status == True:
            print "Status: {0}".format([hex(x) for x in rdata] if rdata else None)
            if not self.cmd_status_ok(rdata):
                return (False, cmd_status_code_str(rdata))
            else:
                return (status, self.decode_status_bytes(rdata[4:]))
        else:
            err_msg = "Dbg chal command error! {0}".format(rdata)
            print err_msg
            return (False, err_msg)

    def read_otp(self):
        print "Getting OTP...!"
        (status, rdata)= self.dbgprobe.dbg_chal_cmd(CMD.GET_OTP)
        if status == True:
            print "OTP: {0}".format([hex(x) for x in rdata] if rdata else "None")
            if self.cmd_status_ok(rdata) is True:
                if len(rdata[4:]) > 0:
                    otpcm = utils.OTPCM()
                    otpcm.set_bin(array('B', rdata[4:]))
                    otp_decoded = otpcm.get_txt()
                    return (True, otp_decoded)
                else:
                    err_msg = 'OTP is empty!'
                    print err_msg
                    return (False, err_msg)
            else:
                return (status, self.cmd_status_code_str(rdata))
        else:
            err_msg = "Dbg chal command error! {0}".format(rdata)
            print err_msg
            return (False, err_msg)

    def inject_cert(self, cert_file):
        print "Injecting Certificate...!"
        cert = array('B')
        cert_file_path = os.path.abspath(cert_file)
        if not os.path.exists(cert_file_path):
            err_msg = 'cert_file: {0} not found!'.format(cert_file_path)
            print err_msg
            return (False, err_msg)
        cert_length = os.path.getsize(cert_file_path)
        print('cert_length: {0}'.format(cert_length))
        with open(cert_file_path, 'rb') as f:
            cert.fromfile(f, cert_length)
        (status, rdata)= self.dbgprobe.dbg_chal_cmd(CMD.INJECT_CERTIFICATE, list(cert))
        if status == True:
            print('Injected certificate. Response rdata:'
                  ' {0}'.format([hex(x) for x in rdata] if rdata is not None else None))
            if not self.cmd_status_ok(rdata):
                return (False, cmd_status_code_str(rdata))
            if len(rdata) > 4:
                err_msg = "No response rdata is expected!"
                print err_msg
                return (False, err_msg)
            print 'Succefully injected certificate!'
            return (True, None)
        else:
            err_msg = "Dbg chal command error! {0}".format(rdata)
            print err_msg
            return (False, err_msg)

    def get_dbg_access(self, dev_cert, priv_key, grants=const.DBG_GRANTS):
        print "Getting dbg access grant...!"
        dev_cert_path = os.path.abspath(dev_cert)
        if not os.path.exists(dev_cert_path):
            err_msg = 'Dev certificate file: {0} not found!'.format(dev_cert_path)
            print err_msg
            return (False, err_msg)
        priv_key_path = os.path.abspath(priv_key)
        if not os.path.exists(priv_key_path):
            err_msg = 'Private key file: {0} not found!'.format(priv_key_path)
            print err_msg
            return (False, err_msg)

        (status, rdata)= self.dbgprobe.dbg_chal_cmd(CMD.GET_CHALLANGE)
        if status == True:
            print "Challange: {0}".format([hex(x) for x in rdata] if rdata is not None else None)
            header = rdata[0:4]
            if self.cmd_status_ok(header) is False:
                err_msg = ('Error in getting dbg challange:'
                      '{0}'.format(self.cmd_status_code_str(header)))
                print err_msg
                return (False, err_msg)
        else:
            err_msg = 'Dbg chal command error! {0}'.format(rdata)
            print err_msg
            return (False, err_msg)
        if not len(rdata) == self.cmd_reply_length(rdata) and \
                self.cmd_reply_length(rdata) == 20:
            err_msg = 'Invalid challange! length:{0} data: {1}'.format(len(rdata), data)
            print err_msg
            return (False, err_msg)

        rdata = rdata[4:]

        challenge = [0,0,0,0,0,0]
        challenge[0] = CMD.GRANT_DBG_ACCESS
        challenge[1] = grants
        challenge[2] = struct.unpack("I", array('B', rdata[0:4]))[0]
        challenge[3] = struct.unpack("I", array('B', rdata[4:8]))[0]
        challenge[4] = struct.unpack("I", array('B', rdata[8:12]))[0]
        challenge[5] = struct.unpack("I", array('B', rdata[12:16]))[0]

        challenge_bs = ""
        for word in challenge:
            challenge_bs += struct.pack('<I',word)
        print "data to sign (command + param + challenge): " +  binascii.hexlify(challenge_bs)

        s = struct.pack('<I', const.DBG_GRANTS)
        dbg_grant_bytes = struct.unpack('BBBB',s)
        cert = array('B', dbg_grant_bytes)

        developer_cert_bs = array('B')
        dev_cert_size = os.path.getsize(dev_cert)
        print 'dev_cert_size: {0}'.format(dev_cert_size)
        with open(dev_cert_path, 'rb') as f:
            developer_cert_bs.fromfile(f, dev_cert_size)
        cert.extend(developer_cert_bs)

        with open(priv_key_path, 'rb') as key_file:
            signing_key = serialization.load_pem_private_key(key_file.read(),
                    const.PRIVATE_KEY_PASSWORD, backend=default_backend())
        signed_challenge = signing_key.sign(challenge_bs, padding.PKCS1v15(),hashes.SHA512())
        signed_challenge_bs = array('B')
        signed_challenge_bs.fromstring(signed_challenge)

        signed_challenge_len = len(signed_challenge_bs)
        print "signed_challenge_len: {0}".format(signed_challenge_len)
        cert.extend(list(struct.unpack('BBBB', struct.pack('<I', signed_challenge_len))))
        cert.extend(signed_challenge_bs)
        print "cert length: {0}".format(len(cert))
        # total length including header = 4 /length/ + 4 /command/ +
        #        4 /dbg_grant/ + developer_cert + 4 /size/ + signed_challenge
        msglen = 4 + dev_cert_size + 4 + signed_challenge_len
        print "msglen: {0}".format(msglen)
        (status, rdata) = self.dbgprobe.dbg_chal_cmd(CMD.GRANT_DBG_ACCESS, list(cert))
        print "Grant Access: {0}".format([hex(x) for x in rdata] if rdata else None)
        if status == True:
            if not self.cmd_status_ok(rdata):
                return (False, cmd_status_code_str(rdata))
            if len(rdata) > 4:
                err_msg = "No response data is expected!"
                print err_msg
                return (False, err_msg)
            return (True, None)
        else:
            err_msg = "Dbg chal command error! {0}".format(rdata)
            print err_msg
            return (False, err_msg)


def block_tests():
    dbgprobe = DBG_Chal(const.CONN_MODE, const.IP_ADDR, const.I2C_DEV_ID,
                        const.I2C_SLAVE_ADDR)
    status = dbgprobe.connect()
    if status is False:
        print 'Connection failed!'
        return False
    (status, data) = dbgprobe.get_status()
    dbgprobe.set_watchdog_timeout()
    dbgprobe.block_main_loop()

def just_unlock():
    dbgprobe = DBG_Chal(const.CONN_MODE, const.IP_ADDR, const.I2C_DEV_ID,
                        const.I2C_SLAVE_ADDR)
    status = dbgprobe.connect()
    if status is False:
        print 'Connection failed!'
        return False

    (status, data) = dbgprobe.get_serial_number()
    if status is False:
        print 'Failed to get serial number! Error: {0}'.format(data)
        return False
    print('Serial Number: {0}'.format([hex(x) for x in data]))
    (status, data) = dbgprobe.get_status()

    (status, data) = dbgprobe.inject_cert('start_certificate.bin')
    if status is False:
        print 'Failed to inject certificate! Error: {0}'.format(data)
        return False
    print('Injected certificate!')

    (status, data) = dbgprobe.get_dbg_access(os.path.join(const.CERT_KEY_DIR , 'developer_cert.cert'),
                                             os.path.join(const.CERT_KEY_DIR + 'developer_private_key.pem'))
    if status is False:
        print 'Failed to grant debug access! Error: {0}'.format(data)
        return False
    print('Debug access granted!')


def secure_debug_tests():
    dbgprobe = DBG_Chal(const.CONN_MODE, const.IP_ADDR, const.I2C_DEV_ID,
                        const.I2C_SLAVE_ADDR)
    status = dbgprobe.connect()
    if status is False:
        print 'Connection failed!'
        return False

    (status, data) = dbgprobe.get_serial_number()
    if status is False:
        print 'Failed to get serial number! Error: {0}'.format(data)
        return False
    print('Serial Number: {0}'.format([hex(x) for x in data]))
    (status, data) = dbgprobe.get_status()

    (status, data) = dbgprobe.inject_cert('start_certificate.bin')
    if status is False:
        print 'Failed to inject certificate! Error: {0}'.format(data)
        return False
    print('Injected certificate!')

    (status, data) = dbgprobe.get_dbg_access(os.path.join(const.CERT_KEY_DIR , 'developer_cert.cert'),
                                             os.path.join(const.CERT_KEY_DIR + 'developer_private_key.pem'))
    if status is False:
        print 'Failed to grant debug access! Error: {0}'.format(data)
        return False
    print('Debug access granted!')

    (status, data) = dbgprobe.read_otp()
    if status is False:
        print 'Failed to get OTP! Error: {0}'.format(data)
        return False
    print('OTP: {0}'.format(data))

    (status, data) = dbgprobe.get_status()
    if status is False:
        print 'Failed to get OTP! Error: {0}'.format(data)
        return False
    print('SBP status: {0}'.format(data))

    dbgprobe.disconnect()

    return True

def flash_tests():
    dbgprobe = DBG_Chal(const.CONN_MODE, const.IP_ADDR, const.I2C_DEV_ID,
                        const.I2C_SLAVE_ADDR)
    status = dbgprobe.connect()
    if status is False:
        print 'Connection failed!'
        return False

    (status, data) = dbgprobe.inject_cert('start_certificate.bin')
    if status is False:
        print 'Failed to inject certificate! Error: {0}'.format(data)
        return False
    print('Injected certificate!')

    (status, data) = dbgprobe.get_dbg_access(os.path.join(const.CERT_KEY_DIR, 'developer_cert.cert'),
                                             os.path.join(const.CERT_KEY_DIR + 'developer_private_key.pem'))
    if status is False:
        print 'Failed to grant debug access! Error: {0}'.format(data)
        return False
    print('Debug access granted!')


    dbgprobe.get_buffer_sizes()
    dbgprobe.read_flash()
    dbgprobe.erase_flash()
    dbgprobe.write_flash()
    dbgprobe.read_flash()

def status_test():
    dbgprobe = DBG_Chal(const.CONN_MODE, const.IP_ADDR, const.I2C_DEV_ID,
                        const.I2C_SLAVE_ADDR)
    status = dbgprobe.connect()
    if status is False:
        print 'Connection failed!'
        return False
    (status, data) = dbgprobe.get_status()

if __name__== "__main__":
    for i in range(1):
        print('****** TEST ITERATION:{0} ********'.format(i))
        status = just_unlock()
        '''
        if status == False:
            print('Secure debug tests failed!')
            sys.exit(1)
        '''
        # status = secure_debug_tests()
        # status = block_tests()
        # flash_tests()
        status_test()

