import sys
sys.path.append("../software/devtools/firmware")
from dbgclient import *
import binascii
from array import array
import struct
#from named_bitfield import named_bitfield
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding

STATUS_NAMES = [ 
    "Status at last tamper",
    "Timestamp of last tamper",
    "Raw tamper status",
    "Current Time",
    "Boot Status",
    "eSecure Firmware Version",
    "Host Firmware Version",
    "Debug Grants"]

class CMD(object):
    GET_SERIAL_NUMBER = 0xFE000000
    GET_OTP = 0x08010000
    GET_STATUS = 0xFE010000
    INJECT_CERTIFICATE = 0xFE0A0000
    GET_CHALLANGE = 0xFD000000
    GRANT_DBG_ACCESS = 0xFD010000 

class CONST(object):
    DBG_GRANTS = 0x000C00F0
    IP_ADDR = '10.1.20.69'
    CONN_MODE = 'i2c'
    I2C_DEV_ID = 'TPCFbwoQ'
    PRIVATE_KEY_PASSWORD = 'fun123'

class DBG_CHAL_SDK(object):
    def __init__(self, mode=None, ip_addr=None, dev_id=None):
        self.mode = mode
        self.ip_addr = ip_addr
        self.dev_id = dev_id 
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
        status = dbgprobe.connect(self.mode, self.ip_addr, self.dev_id)
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
            if status_str_idx < len(STATUS_NAMES):
                print '\t{0}{1}'.format(STATUS_NAMES[status_str_idx], \
                        hex(int(binascii.hexlify(array('B', data[i:i+4])), 16))) 
                status_decoded[STATUS_NAMES[status_str_idx]] = \
                        hex(int(binascii.hexlify(array('B', data[i:i+4])), 16))

                i+=4
            else:
                print '\tExtra Bytes: {0}'.format([hex(x) for x in data[i:status_size]])
                status_decoded["Extra Bytes"] = data[i:status_size]
                i = status_size
        return status_decoded

    def int_to_bytes(self, val, num_bytes):
            return [(val & (0xff << pos*8)) >> pos*8 for pos in
                    range(num_bytes)]

    def get_serial_number(self):
        print('Getting serial number...!')
        (status, data)= self.dbgprobe.dbg_chal_cmd(CMD.GET_SERIAL_NUMBER)
        if status == True:
            print "Serial number: {0}".format([hex(x) for x in data])
            return (status, data)
        else:
            print "Dbg chal command error! {0}".format(data)
            return (False, None)

    def get_status(self):
        print "Getting status...!"
        (status, data)= self.dbgprobe.dbg_chal_cmd(CMD.GET_STATUS)
        if status == True:
            print "Status: {0}".format([hex(x) for x in data])
            return (True, self.decode_status_bytes(data))
        else:
            print "Dbg chal command error! {0}".format(data)
            return (False, None)

    def read_otp(self):
        print "Getting OTP...!"
        (status, data)= self.dbgprobe.dbg_chal_cmd(CMD.GET_OTP)
        if status == True:
            print "OTP: {0}".format([hex(x) for x in data] if data else "None")
            otpcm = utils.OTPCM()
            otpcm.set_bin(array('B', data))
            otp_decoded = otpcm.get_txt()
            return (True, otp_decoded)
        else:
            print "Dbg chal command error! {0}".format(data)
            return (False, None)

    def inject_cert(self, cert_file):
        print "Injecting Certificate...!"
        cert = array('B')
        cert_file_path = os.path.abspath(cert_file) 
        if not os.path.exists(cert_file_path):
            print('cert_file: {0} not found!'.format(cert_file_path))
            return (False, None)
        cert_length = os.path.getsize(cert_file_path)
        print('cert_length: {0}'.format(cert_length))
        with open(cert_file_path, 'rb') as f:
            cert.fromfile(f, cert_length)
        (status, data)= self.dbgprobe.dbg_chal_cmd(CMD.INJECT_CERTIFICATE, list(cert))
        if status == True:
            if data is not None and len(data) != 0:
                print "Succefully injected certificate. Response data:{0}".format([hex(x) for x in data])
            else:
                print 'Succefully injected certificate!'
            return True
        else:
            print "Dbg chal command error! {0}".format(data)
            return False

    def get_dbg_access(self, dev_cert, priv_key):
        print "Getting dbg access grant...!"
        dev_cert_path = os.path.abspath(dev_cert) 
        if not os.path.exists(dev_cert_path):
            print('Dev certificate file: {0} not found!'.format(dev_cert_path))
            return False
        priv_key_path = os.path.abspath(priv_key) 
        if not os.path.exists(priv_key_path):
            print('Private key file: {0} not found!'.format(priv_key_path))
            return False

        (status, rdata)= self.dbgprobe.dbg_chal_cmd(CMD.GET_CHALLANGE)
        if status == True:
            print "Challange: {0}".format([hex(x) for x in rdata])
        else:
            print "Dbg chal command error! {0}".format(rdata)
            return False

        if len(rdata) != 16:
            print('Invalid challange! length:{0} data: {1}'.format(len(rdata), data))
            return True

        challenge = [0,0,0,0,0,0]
        challenge[0] = CMD.GRANT_DBG_ACCESS
        challenge[1] = CONST.DBG_GRANTS
        challenge[2] = struct.unpack("I", array('B', rdata[0:4]))[0]
        challenge[3] = struct.unpack("I", array('B', rdata[4:8]))[0]
        challenge[4] = struct.unpack("I", array('B', rdata[8:12]))[0]
        challenge[5] = struct.unpack("I", array('B', rdata[12:16]))[0]

        challenge_bs = ""
        for word in challenge:
            print hex(word)
            challenge_bs += struct.pack('<I',word)
        print "data to sign (command + param + challenge): " +  binascii.hexlify(challenge_bs)

        s = struct.pack('<I', CONST.DBG_GRANTS)
        dbg_grant_bytes = struct.unpack('BBBB',s) 
        cert = array('B', dbg_grant_bytes)
        print 'dbg_grant_bytes: {0}'.format(cert)

        developer_cert_bs = array('B')
        dev_cert_size = os.path.getsize(dev_cert)
        print 'dev_cert_size: {0}'.format(dev_cert_size)
        with open(dev_cert_path, 'rb') as f:
            developer_cert_bs.fromfile(f, dev_cert_size)
        #print binascii.hexlify(developer_cert)
        cert.extend(developer_cert_bs)

        with open(priv_key_path, 'rb') as key_file:
            signing_key = serialization.load_pem_private_key(key_file.read(),
                    CONST.PRIVATE_KEY_PASSWORD, backend=default_backend())
        signed_challenge = signing_key.sign(challenge_bs, padding.PKCS1v15(),hashes.SHA512())
        #print binascii.hexlify(signed_challenge)
        signed_challenge_bs = array('B')
        signed_challenge_bs.fromstring(signed_challenge)

        signed_challenge_len = len(signed_challenge_bs)
        print "signed_challenge_len: {0}".format(signed_challenge_len)

        print 'signed_challenge_len: {0}'.format(list((self.int_to_bytes(signed_challenge_len, 4))))
        cert.extend(list((self.int_to_bytes(signed_challenge_len, 4))))
        cert.extend(signed_challenge_bs)

        print "cert length: {0}".format(len(cert))
        print "Unlocking..."
        # total length including header = 4 /length/ + 4 /command/ +
        #        4 /dbg_grant/ + developer_cert + 4 /size/ + signed_challenge
        msglen = 4 + dev_cert_size + 4 + signed_challenge_len
        print "msglen: {0}".format(msglen) 
        (status, rdata)= self.dbgprobe.dbg_chal_cmd(CMD.GRANT_DBG_ACCESS, list(cert))
        if status == True:
            print "Grant Access: {0}".format([hex(x) for x in rdata] if rdata else None)
            return True
        else:
            print "Dbg chal command error! {0}".format(rdata)
            return False

if __name__== "__main__":
    dbgprobe = DBG_CHAL_SDK(CONST.CONN_MODE, CONST.IP_ADDR, CONST.I2C_DEV_ID)
    dbgprobe.connect()
    #dbgprobe.get_serial_number()
    #dbgprobe.inject_cert('start_certificate.bin')
    dbgprobe.get_dbg_access('developer_cert.cert', 'developer_private_key.pem')
    dbgprobe.read_otp()
    dbgprobe.get_status()
    dbgprobe.disconnect()
