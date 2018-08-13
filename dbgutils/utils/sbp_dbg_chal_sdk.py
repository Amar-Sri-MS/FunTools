from dbgclient import *
import binascii
import sys
from array import array
import struct
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding


STATUS_STRS = [ 
    "Status at last tamper    : ",
    "Timestamp of last tamper : ",
    "Raw tamper status        : ",
    "Current Time             : ",
    "Boot Status              : ",
    "eSecure Firmware Version : ",
    "Host Firmware Version    : ",
    "Debug Grants             : "]

def dump_status_data(data):
    print 'Status:\n'
    i = 0 
    status_size = len(data)
    while i < status_size:
        status_str_idx = i/4
        if status_str_idx < len(STATUS_STRS):

            print '\t{0}{1}'.format(STATUS_STRS[status_str_idx],
                    hex(int(binascii.hexlify(array('B', data[i:i+4])), 16))) 
            i+=4
        else:
            print '\tExtra Bytes: {0}'.format([hex(x) for x in data[i:status_size]])
            i = status_size

def int_to_bytes(val, num_bytes):
        return [(val & (0xff << pos*8)) >> pos*8 for pos in
                range(num_bytes)]

def dbg_chal_get_serial_number():
    dbgprobe = DBG_Client()
    status = dbgprobe.connect('i2c', '10.1.20.69', 'TPCFbwoQ')
    if status is True:
        print 'dbgprobe connection successful'
    else:
        print 'Error in dbgprobe connection!'
        sys.exit(1)
    print "Dbg challange command for serial number"
    cmd = 0xFE000000
    (status, data)= dbgprobe.dbg_chal_cmd(cmd)
    if status == True:
        print "Serial number: {0}".format([hex(x) for x in data])
    else:
        print "Dbg chal command error! {0}".format(data)

    status = dbgprobe.disconnect()
def dbg_chal_get_status():
    dbgprobe = DBG_Client()
    status = dbgprobe.connect('i2c', '10.1.20.69', 'TPCFbwoQ')
    if status is True:
        print 'dbgprobe connection successful'
    else:
        print 'Error in dbgprobe connection!'
        sys.exit(1)
    print "Dbg challange command for status"
    cmd = 0xFE010000
    (status, data)= dbgprobe.dbg_chal_cmd(cmd)
    if status == True:
        print "sbp status: {0}".format([hex(x) for x in data])
        dump_status_data(data)
    else:
        print "Dbg chal command error! {0}".format(data)
    status = dbgprobe.disconnect()

def dbg_chal_read_otp():
    dbgprobe = DBG_Client()
    status = dbgprobe.connect('i2c', '10.1.20.69', 'TPCFbwoQ')
    if status is True:
        print 'dbgprobe connection successful'
    else:
        print 'Error in dbgprobe connection!'
        sys.exit(1)
    print "Dbg challange command for status"
    cmd = 0x08010000
    (status, data)= dbgprobe.dbg_chal_cmd(cmd)
    if status == True:
        print "OTP: {0}".format([hex(x) for x in data] if data else "None")
    else:
        print "Dbg chal command error! {0}".format(data)
    status = dbgprobe.disconnect()

def dbg_chal_inject_cert():
    dbgprobe = DBG_Client()
    status = dbgprobe.connect('i2c', '10.1.20.69', 'TPCFbwoQ')
    if status is True:
        print 'dbgprobe connection successful'
    else:
        print 'Error in dbgprobe connection!'
        sys.exit(1)
    print "Dbg challange command for status"
    cmd = 0xFE0A0000
    cert = array('B')
    with open('start_certificate.bin', 'rb') as f:
        cert.fromfile(f, 1096)

    (status, data)= dbgprobe.dbg_chal_cmd(cmd, list(cert))
    if status == True:
        print data
        if data is not None and len(data) != 0:
            print "Succefully injected certificate. Response data:{0}".format([hex(x) for x in data])
        else:
            print 'Succefully injected certificate!'
    else:
        print "Dbg chal command error! {0}".format(data)
    status = dbgprobe.disconnect()

def dbg_chal_get_access():
    dbgprobe = DBG_Client()
    status = dbgprobe.connect('i2c', '10.1.20.69', 'TPCFbwoQ')
    if status is True:
        print 'dbgprobe connection successful'
    else:
        print 'Error in dbgprobe connection!'
        sys.exit(1)
    print "Dbg challange command for serial number"
    cmd = 0xFD000000
    (status, rdata)= dbgprobe.dbg_chal_cmd(cmd)
    if status == True:
        print "Challange: {0}".format([hex(x) for x in rdata])
    else:
        print "Dbg chal command error! {0}".format(rdata)

    dev_cert = "/home/nponugoti/funtools/dbgutils/developer_cert.cert"
    priv_key = "/home/nponugoti/funtools/dbgutils/developer_private_key.pem"

    command = 0xFD010000
    dbg_grant_bytes = [0x00, 0x0C, 0x00, 0xF0]
    dbg_grant = binascii.hexlify(array('B', dbg_grant_bytes))
    print 'dbg_grant: {0}'.format(dbg_grant) 
    challenge = [0,0,0,0,0,0]
    challenge[0] = 0xFD010000; 
    challenge[1] = 0x000C00F0; 
    challenge[2] = struct.unpack("I", array('B', rdata[0:4]))[0]
    challenge[3] = struct.unpack("I", array('B', rdata[4:8]))[0]
    challenge[4] = struct.unpack("I", array('B', rdata[8:12]))[0]
    challenge[5] = struct.unpack("I", array('B', rdata[12:16]))[0]

    challenge_bs = ""
    for word in challenge:
        print hex(word)
        challenge_bs += struct.pack('<I',word)
    print "data to sign (command + param + challenge): " +  binascii.hexlify(challenge_bs)

    cert = array('B', [0xF0, 0x00, 0x0C, 0x00])

    developer_cert_bs = array('B')
    dev_cert_size = os.path.getsize(dev_cert)
    print 'dev_cert_size: {0}'.format(dev_cert_size)
    with open(dev_cert, 'rb') as f:
        developer_cert_bs.fromfile(f, 1096)
    #print binascii.hexlify(developer_cert)

    cert.extend(developer_cert_bs)

    with open(priv_key, 'rb') as key_file:
        signing_key = serialization.load_pem_private_key(key_file.read(), password="fun123", backend=default_backend())
    signed_challenge = signing_key.sign(challenge_bs, padding.PKCS1v15(),hashes.SHA512())
    #print binascii.hexlify(signed_challenge)
    signed_challenge_bs = array('B')
    signed_challenge_bs.fromstring(signed_challenge)

    signed_challenge_len = len(signed_challenge_bs)
    print "signed_challenge_len: {0}".format(signed_challenge_len)

    cert.extend(list((int_to_bytes(signed_challenge_len, 4))))
    cert.extend(signed_challenge_bs)

    print "cert length: {0}".format(len(cert))

    print "Unlocking..."
     # total length = 4 /length/ + 4 /command/ + 4 /dbg_grant/ + developer_cert + 4 /size/ + signed_challenge
    msglen = 4 + 1096 + 4 + signed_challenge_len
    print "msglen: {0}".format(msglen) 

    (status, rdata)= dbgprobe.dbg_chal_cmd(command, list(cert))
    if status == True:
        print "Grant Access: {0}".format([hex(x) for x in rdata])
    else:
        print "Dbg chal command error! {0}".format(rdata)

    status = dbgprobe.disconnect()


if __name__== "__main__":
    #dbg_chal_get_serial_number()
    #dbg_chal_inject_cert()
    #dbg_chal_get_access()
    dbg_chal_read_otp()
    #dbg_chal_get_status()



