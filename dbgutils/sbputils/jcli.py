#!/usr/bin/env python3

# This file defines the user level JTAG call via otpions to initialize, read and
# write commands over JTAG transport.

# This actively used the code-scape8.6 python libraries.
# Hence the CodeScape-8.6 need to be installed on the probe server.
# This libraries, utilities and methods are imported via PYTHONPATH

import sys
import os

# CodeSpace8.6 is installed in ~/.local/opt/imgtec, which can be imported by setting PYTHONPATH
#
sys.path.append('/home/'+os.environ["USER"]+'/.local/opt/imgtec/Codescape-8.6/lib/python2.7/lib-dynload')
sys.path.append('/home/'+os.environ["USER"]+'/.local/opt/imgtec/Codescape-8.6/lib/python2.7/site-packages')
sys.path.append('/home/'+os.environ["USER"]+'/.local/opt/imgtec/Codescape-8.6/lib/python2.7/site-packages/sitepackages.zip')

# dutdb.cfg + dututils.py has probe-details
from dututils import dut
#from gpioutils import tap as gpiotap
from gpio3ptaputils import tap as gpiotap
import time

import sys
import argparse
import imgtec.console as con

import binascii
import struct
import os
import subprocess

from imgtec.console.support import command
from imgtec.lib.namedenum import namedenum
from imgtec.lib.namedbitfield import namedbitfield
from imgtec.console import *
from imgtec.console import CoreFamily

from imgtec.console import logging as cslogging
from imgtec.console import config as csconfig

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding

from jsbp import *

logger = logging.getLogger('jcli')
#import logging
#from logging.handlers import RotatingFileHandler
#import time
#logger = logging.getLogger(__name__)
#FORMAT = "[%(asctime)s %(filename)s->%(funcName)s():%(lineno)s]%(levelname)s: %(message)s"
#logging.basicConfig(format=FORMAT, level=logging.INFO)
#logging_filename = 'jcli_sbp.log'
#handler = RotatingFileHandler(logging_filename, maxBytes=1000000, backupCount=2) #10 files of 1MB each
#handler.setFormatter(logging.Formatter(FORMAT))
#logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

##############################################################################
# Error handling
##############################################################################

class RunError(Exception):
    pass

def run(main):
    try:
        main()
    except RunError as e:
        print("ERROR: %s" % e)
        exit(1)


##############################################################################
# File access
##############################################################################

def read(filename, nbytes=None):
    if filename==None:
        return ""
    print("Reading %s" % filename)
    try:
        txt = open(filename, "rb").read()
    except:
        raise RunError("Cannot open file '%s' for read" % filename)
    if nbytes and len(txt)!=nbytes:
        raise RunError("File '%s' has invalid length" % filename)
    return txt

def write(filename, content, overwrite=True, tohex=False, tobyte=False):
    if not filename:
        return
    print("Writing %s" % filename)
    # Overwrite
    if not overwrite and os.path.exists(filename):
        raise RunError("File '%s' already exists" % filename)
    # Open
    try:
        f = open(filename, "wb")
    except:
        raise RunError("Cannot open file '%s' for write" % filename)
    # Write
    if tohex:
        assert len(content)%4==0
        for pos in range(0, len(content), 4):
            f.write("%08X\n" % struct.unpack("<I", content[pos:pos+4]))
    elif tobyte:
        for pos in range(0, len(content)):
            f.write("%s\n" % binascii.hexlify(content[pos]))
    else:
        f.write(content)


##############################################################################
# Console commands
##############################################################################

IR_DEVICEADDR = 5
IR_APBACCESS = 6

ID_REGS = {
    "CIDR3"   : 0xFFC,
    "CIDR2"   : 0xFF8,
    "CIDR1"   : 0xFF4,
    "CIDR0"   : 0xFF0,
    "PIDR3"   : 0xFEC,
    "PIDR2"   : 0xFE8,
    "PIDR1"   : 0xFE4,
    "PIDR0"   : 0xFE0,
    "PIDR4"   : 0xFD0,
    "DEVTYPE" : 0xFCC,
    "DEVID"   : 0xFC8
}

DEVIDS = {
    "DEVID_MDH"             : 1,
    "DEVID_DBU"             : 2,
    "DEVID_APB2JTAG"        : 3,
    "DEVID_CORE"            : 4,
    "DEVID_MMBLOCK"         : 5,
    "DEVID_M7000_BRIDGE"    : 6,
    "DEVID_CM"              : 7,
    "DEVID_ESECURE"         : 8,
}

MfrCertType = namedenum('MfrCertType',
                        ChipMfr         = 0,
                        SystemMfr       = 1,
                        )

SlaveAddr = namedbitfield('SlaveAddr',
                          [('dest_id', 17, 12), ('core_id', 11, 6), ('vpe_id', 3, 0)])

BootInfo = namedbitfield('Bootinfo', [
    ('HostImage',20,20),
    ('eSecureImage',16,16),
    ('HostUpgradeFlag',12,12),
    ('eSecureUpgradeFlag',8,8),
    ('BootStep',7,0)])

WDATA = 0x8
RDATA = 0x4
CONTROL = 0x0
WR_REQ = 1<<3 #8
RD_REQ = 1<<2 #4
WR_ACK = 1<<1 #2
RD_ACK = 1<<0 #1

TIMEOUT = 8000
DEBUG = 0

def prepare_target(do_ad=None):
    if probe().mode not in ('autodetected', 'table'):
        if do_ad:
            for attempt in range(do_ad):
                logger.info("attempt: %s ... calling autodetect ... with a reset(probe)" % attempt)
                mips_debugger_init()
                autodetect()
        else:
            logger.info("skipping autodetect ...")
    check_use_fast_read()


#@command()
def mdh_read_new(byte_address):
    """ the inbuilt mdh read is broken on some console versions """
    try:
        #logger.info("mdh_read_new: byte_address={} ...".format(hex(byte_address)))
        return probe().tiny.ReadMemory(byte_address)
    except:
        raise RuntimeError("mdh_read_new: APB read failed try a lower TCK clock") #TODO retry abit if valid = 0

#@command()
def mdh_write_new(byte_address,word):
    """ the inbuilt mdh read is broken on some console versions """
    try:
        #logger.info("mdh_write_new: byte_address={} word={} ...".format(hex(byte_address), hex(word)))
        probe().tiny.WriteMemory(byte_address, word)
    except:
        raise RuntimeError("mdh_write_new: APB read failed try a lower TCK clock") #TODO retry abit if valid = 0

def my_tapscan(ir, dr, verbose=False):
    if verbose:
        ia, ib = list(map(hex, list(map(int, ir.split()))))
        da, db = list(map(hex, list(map(int, dr.split()))))
        logger.info("ir={} {} | dr={} {}".format(ia, ib, da, db))
    return tapscan(ir, dr)

def my_tapd(dr, verbose=False):
    if verbose:
        da, db = list(map(hex, list(map(int, dr.split()))))
        logger.info("dr={} {}".format(da, db))
    return tapd(dr)

def my_tapi(ir, verbose=False):
    if verbose:
        ia, ib = list(map(hex, list(map(int, ir.split()))))
        logger.info("ir={} {}".format(ia, ib))
    return tapi(ir)

def mdh_read_old(byte_address):
    #logger.info("mdh_read_old - address={}".format(hex(byte_address)))
    result = tapscan("5 %d" % IR_DEVICEADDR, "32 %d" % (byte_address & 0xf80) )
    #print("tapscan 5", hex(IR_DEVICEADDR), "32", hex(byte_address & 0xf80), "result=", result )
    time.sleep(0.1) #sleep during 100ms
    result = tapscan("5 %d" % IR_APBACCESS, "39 %d" % ((byte_address & 0x7c) | 0x3) )
    #print("tapscan 5", hex(IR_APBACCESS), "39", hex((byte_address & 0x7c) | 0x3), "result=", result )
    time.sleep(0.1) #sleep during 100ms
    result = tapd("39 %d" % ((byte_address & 0x7c) | 0x2) )
    #print ("tapd 39", hex((byte_address & 0x7c) | 0x2), "result=", result)

    if (result[0] & 0x3) == 0x3:
        return result[0] >> 7

    raise RuntimeError("mdh_read_old: APB read failed try a lower TCK clock") #TODO retry abit if valid = 0

def mdh_write_old(byte_address,word):
    #logger.info("mdh_write_old - address={}, word={}".format(hex(byte_address), hex(word)))
    result = tapscan("5 %d" % IR_DEVICEADDR, "32 %d" % (byte_address & 0xf80) )
    #print("tapscan 5", hex(IR_DEVICEADDR), "32", hex(byte_address & 0xf80), "result=", result )
    time.sleep(0.1)
    result = tapscan("5 %d" % IR_APBACCESS, "39 %d" % (word << 7 | (byte_address & 0x7c) | 0x1) )
    #print("tapscan 5", hex(IR_APBACCESS), "39", hex(word << 7 | (byte_address & 0x7c) | 0x1), "result=", result )
    if (result[0] & 0x3) == 0x3:
        return

    raise RuntimeError("mdh_write_old: APB read failed try a lower TCK clock") #TODO retry abit if valid = 0

mdh_read_ = mdh_read_old
mdh_write_ = mdh_write_old

def check_use_fast_read():
    global  mdh_read_
    global  mdh_write_
    try:
        if listdevices()[0].family == CoreFamily.MIPSecure:
            logger.info("CoreFamily.MIPSecure ... selecting mdh_new_routines...")
            mdh_read_ = mdh_read_new
            mdh_write_ = mdh_write_new
        else:
            logger.info("Family not CoreFamily.MIPSecure: selecting mdh_old_routinues ...")
            mdh_read_ = mdh_read_old
            mdh_write_ = mdh_write_old
    except:
        logger.info("check_use_fast_read_exception: selecting mdh_old_routinues ...")
        mdh_read_ = mdh_read_old
        mdh_write_ = mdh_write_old

#@command()
def esecure_read():
    """ internal only """
    mdh_write_(CONTROL,RD_REQ)
    timeout = 0
    while (mdh_read_(CONTROL) & RD_REQ) == 0: #wait for RD_REQ=1
        time.sleep(0.5)
        logger.info("esecure_read: waiting for RD_REQ to go high ...")
        timeout+=1
        if timeout == TIMEOUT:
            raise RuntimeError("esecure_read: timeout waiting for RD_REQUEST to go high")
    data = mdh_read_(RDATA)
    mdh_write_(CONTROL,RD_ACK)
    timeout = 0
    while (mdh_read_(CONTROL) & RD_REQ) != 0: #wait for RD_REQ=0
        time.sleep(0.5)
        logger.info("esecure_read: waiting for RD_REQ to go low ...")
        timeout+=1
        if timeout == TIMEOUT:
            raise RuntimeError("esecure_read: timeout waiting for RD_REQUEST to go low")
    mdh_write_(CONTROL,0)
    return data

#@command()
def esecure_write(data):
    """ internal only """
    #logger.info("esecure_write: data={}".format(hex(data)))
    mdh_write_(WDATA,data)
    mdh_write_(CONTROL,WR_REQ)
    timeout = 0
    while (mdh_read_(CONTROL) & WR_ACK) == 0:
        time.sleep(0.5)
        timeout+=1
        logger.info("esecure_write: waiting for WR_ACK to go high ...")
        if timeout == TIMEOUT:
            raise RuntimeError("esecure_write: timeout waiting for WR_ACK to go high")
    mdh_write_(CONTROL,0)
    timeout = 0
    while (mdh_read_(CONTROL) & WR_ACK) != 0:
        time.sleep(0.5)
        logger.info("esecure_write: waiting for WR_ACK to go low ...")
        timeout+=1
        if timeout == TIMEOUT:
            raise RuntimeError("esecure_read: timeout waiting for WR_ACK to go low")

def dump_id_regs():
    for k,v in list(ID_REGS.items()):
        print(k + " " + hex(mdh_read_(v)))


def char_repr(le_word):
    t = ""
    for i in range(4):
        t += chr(le_word & 0xFF)
        le_word >>= 8

    return t

#@command()
def dump_return_data(status=None):
    """internal"""
    if not status:
        status = esecure_read()
    if status >> 16 == 0:
        while (mdh_read_(CONTROL) & RD_REQ) != 0:
            print(hex(esecure_read()))
    else:
        print(decode_cmd_status(status))

STATUS_STRS = [
    "Status at last tamper    : ",
    "Timestamp of last tamper : ",
    "Raw tamper status        : ",
    "Current Time             : ",
    "Boot Status              : ",
    "eSecure Firmware Version : ",
    "Host Firmware Version    : ",
    "Debug Grants             : "]

def dump_status_data():
    status = esecure_read() #dont print status and size field but wait for it
    i = 0
    bs = None # bs is the word with boot step
    while (mdh_read_(CONTROL) & RD_REQ) != 0:
        if i < len(STATUS_STRS):
            if i == 4:
                bs = esecure_read()
                print(STATUS_STRS[i]  + hex(bs) + " : ")
                print(repr(BootInfo(bs)))
            else:
                print(STATUS_STRS[i] + hex(esecure_read()))
        else:
            word = esecure_read()
            print("Extra data: " + hex(word) + " " + char_repr(word))
        i+=1
    return bs

STATUS_CODE_STR = [
    "OK",
    "Invalid Command",
    "Authorization Error",
    "Invalid Signature",
    "Bus Error",
    "Reserved",
    "Crypto Error",
    "Invalid Parameter"
]

def decode_cmd_status(status):
    sts = (status >> 16) & 0xf
    if sts >=0 and sts < len(STATUS_CODE_STR):
        return STATUS_CODE_STR[sts]

    return "reserved"

def cmd_status_ok(status):
    sts = (status >> 16) & 0xf
    return sts == 0

def cmd_reply_length(status):
    return status & 0xFFFF

# interisting commands
CMD_GET_CHALLENGE=0xFD000000
CMD_SET_DEBUG_ACCESS=0xFD010000

CMD_GET_SERIAL_NUMBER=0xFE000000
CMD_GET_STATUS=0xFE010000
CMD_GET_PUBKEY=0xFE020000
CMD_DIAG_SET_UPGRADE_FLAG=0xFE030000

CMD_READ_OTP=0xFE0B0000

CMD_SET_START_CERT=0xFE0A0000

CMD_GENERATE_PUF=0xFF050000
CMD_SET_PUF_CERT=0xFF060000

CMD_OPTION_CUSTOMER=1

def diag_set_upgrade_flag(imagetype):
    print("\nRequest to set (imagetype=%s) UPGRADE flag ..." % imagetype)
    esecure_write(0xC)
    esecure_write(CMD_DIAG_SET_UPGRADE_FLAG)
    esecure_write(struct.unpack('>I', imagetype)[0])
    print ("\nResponse:")
    dump_return_data()

def read_otp():
    esecure_write(0x8)
    esecure_write(CMD_READ_OTP)
    print ("\nOTP contents:")
    dump_return_data()

def get_serial():
    esecure_write(0x8)
    esecure_write(CMD_GET_SERIAL_NUMBER)
    print ("\nSerial Number:")
    dump_return_data()

def dump_status():
    def get_key(id, index, name):
        print("get_key: id={}, index={}, name={} ...".format(id, index, name))
        esecure_write(0xC)
        esecure_write(CMD_GET_PUBKEY + id)
        esecure_write(index)
        status = esecure_read();
        if cmd_status_ok(status):
            print("\nPublic Key - %s [%d]:" % (name, index))
            dump_return_data(status)

    # PUF-ROM keys
    get_key(0, 2, "Debugging key")
    get_key(0, 3, "Fungible key")
    get_key(0, 4, "Fungible Enrollment key")
    get_key(1, 0, "Customer key0")
    get_key(1, 1, "Customer key1")

    esecure_write(0x8)
    esecure_write(CMD_GET_STATUS)
    print ("\ndump_status-Status:")
    dump_status_data()

    esecure_write(0x8)
    esecure_write(CMD_GET_SERIAL_NUMBER)
    print ("\nSerial Number:")
    dump_return_data()

def check_for_esecure(do_ad=None):
    prepare_target(do_ad=do_ad)
    #logger.info ("calling jtagchain ...")
    #jtagchain()
    cidr1 = mdh_read_(ID_REGS["CIDR1"])

    if ((cidr1 >> 4) & 0xf) == 0xe:
        devid = mdh_read_(ID_REGS["DEVID"])
        if devid == 8:
            print ("Found eSecure challenge interface")
            return

    print ("Failed to find eSecure Challenge Interface")
    dump_id_regs()


def esecure_write_bytes(bytestr):
    if len(bytestr) % 4 != 0:
        raise RuntimeError("bytestr must always be a multiple of 4 bytes")

    words = []
    for pos in range(0, len(bytestr), 4):
        words.append(struct.unpack('<I',bytestr[pos:pos+4])[0])

    for word in words:
        if DEBUG: print("writing: "+ hex(word))
        esecure_write(word)

def esecure_read_bytes():
    str = ''
    while (mdh_read_(CONTROL) & RD_REQ) != 0:
        str += struct.pack('<I',esecure_read())
    return str


@command()
def esecure_print_status():
    """ Print the status from the esecure hardware """
    prepare_target()
    check_for_esecure()
    dump_status()

CERTIFICATE_LENGTH = 1096
@command()
def esecure_inject_certificate(certificate, customer=False):
    ''' Inject a start certificate into SBP for debugging
    Necessary only in secure mode when the PUF-ROM cannot be loaded from the ROM
    '''
    prepare_target()
    check_for_esecure()
    start_cert = read(certificate)
    if len( start_cert) != 1096:
        print ("This script is not able to use certificate with invalid length")
        return 7 # Invalid Param

    cmd = CMD_SET_START_CERT
    if customer:
        cmd += CMD_OPTION_CUSTOMER

    # total length = 4 /length/ + 4 /command/ + start_cert
    msglen = 4 + 4 + CERTIFICATE_LENGTH

    if DEBUG: print("writing: " + hex(msglen))
    esecure_write(msglen)
    if DEBUG: print("writing: " + hex(cmd))
    esecure_write(cmd)
    esecure_write_bytes(start_cert)

    status = esecure_read()

    print("esecure_inject_certificate-Status: " + decode_cmd_status(status))

    return status


@command()
def esecure_enable_debug(developer_key,developer_certificate,dbg_grant,
                         key_password=None,customer=False,verbose=False):
    ''' Enable debug access to the requested devices
        developer_key - name (+ path) of the file containing the developers private (secret) key
        developer_certificate - name (+ path) of the file containing the developer certificate (signed by the manufacturer for the given developer key and allowed permissions).
        dbg_grant - 16bit bitmask, 1 bit for each dbg_grant[] in the cpu within the eSecure block,
        Note, that the request bitmask must not exceed the mask set in the certificate, as in such case eSecure will reject the request
    '''
    prepare_target()
    check_for_esecure()

    #Send Get Challenge Command
    esecure_write(0x8)
    esecure_write(CMD_GET_CHALLENGE)

    #Read Challenge
    status = esecure_read()
    if status != 0x14:
        print("Unexpected status from get challenge: " + hex(status))
        dump_return_data()
        raise RuntimeError()

    print ("challenge_data:")
    challenge = [0,0,0,0]
    for i in range(len(challenge)):
        challenge[i] = esecure_read()
        print(hex(challenge[i]))

    if (mdh_read_(CONTROL) & RD_REQ) != 0:
        print ("Warning Extra Read data still pending:")
        dump_return_data()
        #todo raise exception ??

    cmd = CMD_SET_DEBUG_ACCESS
    if customer:
        cmd += CMD_OPTION_CUSTOMER

    challenge.insert(0,dbg_grant)
    challenge.insert(0,cmd)

    challenge_bs = ""
    for word in challenge:
        challenge_bs += struct.pack('<I',word)

    if DEBUG: print("data to sign (command + param + challenge): " +  binascii.hexlify(challenge_bs))

    #sign challenge
    developer_cert = read(developer_certificate)
    if verbose: print ("developer cert:")
    if verbose: print(binascii.hexlify(developer_cert))
    with open(developer_key, 'rb') as key_file:
        signing_key = serialization.load_pem_private_key(key_file.read(),
                                                         password=key_password,
                                                         backend=default_backend())

    signed_challenge = signing_key.sign(challenge_bs,
                                        padding.PKCS1v15(),
                                        hashes.SHA512())
    if DEBUG: print ("signed challenge:")
    if DEBUG: print(binascii.hexlify(signed_challenge))
    signed_challenge_len = len(signed_challenge)

    #Send Debug Access Request Command
    print ("Unlocking...")

    # total length = 4 /length/ + 4 /command/ + 4 /dbg_grant/ + developer_cert + 4 /size/ + signed_challenge
    msglen = 4 + 4 + 4 + len(developer_cert) + 4 + signed_challenge_len

    if DEBUG: print("writing: " + hex(msglen))
    esecure_write(msglen)
    if DEBUG: print("writing: " + hex(cmd))
    esecure_write(cmd)
    if DEBUG: print("writing: " + hex(dbg_grant))
    esecure_write(dbg_grant)
    esecure_write_bytes(developer_cert)
    if DEBUG: print("writing: " + hex(signed_challenge_len))
    esecure_write(signed_challenge_len)
    esecure_write_bytes(signed_challenge)

    status = esecure_read()
    print("esecure_enable_debug-Status (customer=%s): " % customer + decode_cmd_status(status))
    return status


def send_info_cmd(cmd):
    ''' send a simple command with no input, capture its reply in a string '''
    # send the command
    esecure_write(0x8)
    esecure_write(cmd)

    #capture the return data
    status = esecure_read()
    if not cmd_status_ok(status):
        print("Error " + decode_cmd_status(status) + " for command " + hex(cmd))
        return None

    # len = cmd_reply_length(status)
    return esecure_read_bytes()

def check_boot_step(desired_boot_step):
    ''' check that the chip is in the right boot step '''
    esecure_write(0x8)
    esecure_write(CMD_GET_STATUS)
    bs = dump_status_data()

    boot_step = BootInfo(bs).BootStep

    if boot_step == desired_boot_step:
        print("Device is not in the proper state: {:02x}".format(boot_step))
        return False

    return True

def mips_debugger_init(myprobe=None):
    print("Reset the probe state ...")
    reset(type='probe')
    print("Enable mips sysprobe logging=on...")
    #csconfig("Log Debug Instructions", 1)
    #csconfig("Verbose Logging", 1)
    #con.logging(type='comms', enable=True)
    #con.logging(type='jtag', enable=True)
    #con.logging(type='probe', enable=True)
    #myprobe.logging(type='console', enable=True)

# Connect to JTAG MIPS probe device using name, ip of CodeScape SysProbe
# The probe is connected with different CLK speed when execution is in ROM (i.e 5K) and 250K in PUFR/HOST.
def probe_connect(name, ip, in_rom=None, flag=None):
    try:
        print("connecting to JTAG probe ip=%s force_disconnect=%s ..." % (ip, flag) )
        status = con.probe(name, ip, force_disconnect=flag)
        status = str(status)
        if (("SysProbe" not in status) or ("Firmware" not in status) or
            ("ECONNREFUSED" in status) or ("InvalidArgError" in status)):
            return (False, status)
        mips_debugger_init(con)
        #JTAG_TCKRATE = 5000 if in_rom else 100000
        # RTL1008 at different speeds, hence reducing JTAG to 5000
        JTAG_TCKRATE = 5000 if in_rom else 5000
        print("connecting to JTAG probe with TCKRATE(%s)..." % JTAG_TCKRATE )
        con.tckrate(JTAG_TCKRATE)
        con.scanonly()
    except Exception as e:
        print("Error connecting to probe: %s" % e)
        raise Exception("Error connecting to probe")

# unlock secure device with native CHIP MFG firmwares
def device_unlock_CM(cm_sk, cm_cert, dbg_grant, password):
    esecure_enable_debug(cm_sk, cm_cert, dbg_grant, password, customer=False)

# unlock secure device with external customer SYS MFG firmwares
def device_unlock_SM(sm_sk, sm_cert, dbg_grant, password):
    esecure_enable_debug(sm_sk, sm_cert, dbg_grant, password, customer=True)

class DeviceFlash:
    # Commands
    ERASE_SECTOR = 0xFC000000
    PROGRAM = 0xFC010000
    READ = 0xFC020000

    # Command flags
    BUFFER_GET_SIZE = 0x00001000
    BUFFER_DATA = 0x00002000
    BUFFER_CLEAR = 0x00003000
    BUFFER_END = 0x00004000

    def __init__(self, dry=False):
        self.dry = dry

        if self.dry:
            self.page_size = 256
            self.rd_buf_size = 100
            self.wr_buf_size = 100
            print("Flash device page: %d, read buffer size: %d" % (self.page_size, self.rd_buf_size))
            print("Flash device page: %d, write buffer size: %d" % (self.page_size, self.wr_buf_size))
        else:
            cmd = [ self.READ | self.BUFFER_GET_SIZE ]
            self.__esec_write(cmd)
            status = self.__esec_read_status("Unable to access flash for reading")

            self.page_size = self.__esec_read()
            self.rd_buf_size = self.__esec_read()
            print("Flash device page: %d, read buffer size: %d" % (self.page_size, self.rd_buf_size))

            cmd = [ self.PROGRAM | self.BUFFER_GET_SIZE ]
            self.__esec_write(cmd)
            status = self.__esec_read_status("Unable to access flash for writing")

            # Note: overwrite previous value of page_size, but it should be the same anyway
            # and it's more important for write operations than for reads, so if they differ,
            # only the one reported here is useful
            self.page_size = self.__esec_read()
            self.wr_buf_size = self.__esec_read()
            print("Flash device page: %d, write buffer size: %d" % (self.page_size, self.wr_buf_size))

    def __esec_write(self, cmd):
        if self.dry:
            return
        esecure_write(4 + 4 * len(cmd))
        list(map(esecure_write, cmd))

    def __esec_read(self,val=None):
        if self.dry:
            return val or 0
        return esecure_read()

    def __esec_read_status(self, err, val=None):
        status = self.__esec_read(val)
        if not cmd_status_ok(status):
            print("{}: {}" % (err, decode_cmd_status(status)))
            raise Exception(decode_cmd_status(status))
        return status

    def read(self, offset, size):
        res = []
        while size:
            s = min(size, self.rd_buf_size)
            cmd = [ self.READ | self.BUFFER_DATA, offset, s ]
            print("Flash device read command: %s" % list(map(hex, cmd)))
            self.__esec_write(cmd)
            status = self.__esec_read_status("Unable to access flash for reading", val=s)

            cnt = status - 4
            while cnt:
                data = self.__esec_read()
                cnt -= 4
                res.append(data)

            offset += s
            size -= s
        return res;

    def erase_sector(self, offset):
        cmd = [ self.ERASE_SECTOR, offset ]
        self.__esec_write(cmd);
        print("Flash device erase command: %s" % list(map(hex, cmd)))
        status = self.__esec_read_status("Unable to access flash for reading")

    def write(self, offset, data):
        size = len(data) * 4
        start = 0
        write_size = min(self.page_size, self.wr_buf_size)
        while start < size:
            page_offset = 0
            page_data = min(self.page_size, size - start)
            cmd = [ self.PROGRAM | self.BUFFER_CLEAR ]
            print("Flash device write command: %s" % list(map(hex, cmd)))
            self.__esec_write(cmd)
            status = self.__esec_read_status("Unable to clear write buffer")

            while page_data:
                this_write_size = min(write_size, page_data)
                cmd = [ self.PROGRAM | self.BUFFER_DATA, page_offset, this_write_size ]
                cmd.extend(data[(start + page_offset)/4 : (start + page_offset + this_write_size)/4])

                print("Flash device page-data write command: %s" % list(map(hex, cmd)))
                self.__esec_write(cmd)
                status = self.__esec_read_status("Unable to write data buffer")

                page_offset += this_write_size
                page_data -= this_write_size

            cmd = [ self.PROGRAM | self.BUFFER_END, offset ]
            print("cmd=%s Program buffer at 0x%08X" % (list(map(hex, cmd)), offset))
            self.__esec_write(cmd)
            status = self.__esec_read_status("Unable to clear write buffer")

            offset += self.page_size
            start += self.page_size

def change_back_to_default_mode(tapmode=None, T=None):
    if tapmode:
        T.set_none()
        T.close()

def change_back_to_dbg_mode(tapmode=None, T=None):
    if tapmode:
        T.set_none()
        T.close()

def change_to_mdh_mode(tapmode=None, T=None):
    if tapmode:
        T.set_mdh()

def change_to_csr_mode(tapmode=None, T=None):
    if tapmode:
        T.set_avago()
    else:
        print ("Did you UNLOCK the chip and change the TAP to CSR ??? Now press character to access CSR probe ...")
        #mydata = input('Prompt :')
        #print (mydata)
    #csr_probe_init()

def auto_int(x):
    return int(x, 0)

def main():
    parser = argparse.ArgumentParser(
                 description="Run basic tests over Challenge Interface via different bus",
                 epilog="Challenge Interface must be accessible via debug probe prior to running this script,\
                         check the device documentation on how to do this")
    parser.add_argument("--dut", required=True, help="Dut name")
    parser.add_argument("--in-rom-cm", default=None, help="CM Rom Certificate to be injected for unlock")
    parser.add_argument("--in-rom-sm", default=None, help="SM Rom Certificate to be injected for unlock")
    parser.add_argument("--do_ad", dest='do_ad', type=auto_int, default=None, help="perform autodetect n times")
    parser.add_argument("--status", action='store_true', help="Display esecure device status")
    parser.add_argument("--otp", action='store_true', help="Read OTP from esecure device (verify unlock)")
    parser.add_argument("--set-upgrade", default=None, choices=['pufr', 'frwm', 'host', 'eepr' ], help="WIP : Toggle Upgrade flags to boot from next image (verify unlock)")
    parser.add_argument("--serial", action='store_true', help="get Serial number for the device")

    parser.add_argument("--cm-unlock", action='store_true', help="Attempt to unlock CM debug interface")
    cm_args = parser.add_argument_group("Chip Certificates", "Debug certificates and user keys paths")
    cm_args.add_argument("--cm-grant", type=auto_int, help="Debug grant bits to unlock with --unlock command")
    cm_args.add_argument("--cm-key", help="Developer's private key")
    cm_args.add_argument("--cm-cert", help="Certificate signed with chip manufacturer's key for cm-key")
    cm_args.add_argument("--cm-pass", help="Certificate password with chip manufacturer's key for sm-key")

    parser.add_argument("--sm-unlock", action='store_true', help="Attempt to unlock SM debug interface")
    sm_args = parser.add_argument_group("Customer Certificates", "Debug certificates and user keys paths")
    sm_args.add_argument("--sm-grant", type=auto_int, help="Debug grant bits to unlock with --unlock command")
    sm_args.add_argument("--sm-key", help="Developer's private key")
    sm_args.add_argument("--sm-cert", help="Certificate signed with system manufacturer's key for sm-key")
    sm_args.add_argument("--sm-pass", help="Certificate password with system manufacturer's key for sm-key")

    parser.add_argument("--flash", action='store_true', help="Perform flash read/erase/write tests")
    parser.add_argument("--disconnect", default=False, action='store_true', help="Perform a probe disconnect prior to CSR read")
    #fl_args = parser.add_argument_group("Flash APIs", "Options for erase/read/program")
    #fl_args.add_argument("--erase", help="Flash erase at <offset> <nwords>")
    #fl_args.add_argument("--at", type=auto_int, help="Perform operation at this offset")
    #fl_args.add_argument("--nwords", type=int, help="Perform operation of nwords")
    #fl_args.add_argument("--read", type=auto_int, help="Flash read at <offset> <nwords> and write to <outfile>")
    #fl_args.add_argument("--ofile", type=argparse.FileType('w'), nargs="?", help="read from flash and write into filename")
    #fl_args.add_argument("--write", help="Flash write at <offset> <infile>")
    #fl_args.add_argument("--ifile", type=argparse.FileType('r'), nargs="?", help="read from filename and write into flash")

    parser.add_argument("--tap", action='store_true', help="Dynamically select CSR TAP and Attempt to perform CSR operation")
    parser.add_argument("--csr", action='store_true', help="Attempt to perform CSR operation")

    parser.add_argument("--csr-peek", action='store_true', help="CSR peek of a register with nqwords")
    parser.add_argument("--csr-poke", action='store_true', help="CSR poke at register with given array of qwords")
    parser.add_argument("--csr-verify", action='store_true', help="CSR poke and peek at register with given array of qwords")
    parser.add_argument("--regadr", default=0x440080a0, type=auto_int, help="CSR address or or flash offset")
    parser.add_argument("--reglen", default=1, type=auto_int, help="CSR qwords to peek/poke or flash words")
    parser.add_argument("--regval", action='store', dest='regval', type=auto_int, nargs='+', default=[0xaabbccdd11223344], help="CSR qwords to poke or flash words")

    parser.add_argument("--reboot", action='store_true', help="Attempt to perform reboot via CSR operation")

    parser.add_argument('--quicktest', action='store', dest='quicktest', type=str, nargs='*', default=[], help="Examples: --quicktest nopass")

    args = parser.parse_args()
    ################### do some options integrity checking ################################

    #import pprint
    #pprint.pprint(args)

    if args.cm_unlock and not all([args.cm_key, args.cm_cert, args.cm_grant, args.cm_pass]):
        parser.error("--unlock requires all CM keys and certificates to be specified")

    if args.sm_unlock and not all([args.sm_key, args.sm_cert, args.sm_grant, args.sm_pass]):
        parser.error("--unlock requires all SM keys and certificates to be specified")

    # connect to probe configuration provided by user
    try:
        status, probe_id, probe_addr = dut().get_jtag_info(args.dut)
    except:
        raise RunError("name={} not in database ...".format(args.dut))

    if args.tap:
        t = gpiotap(args.dut, pullups=0xFF)
        probe_connect(probe_id, probe_addr, args.in_rom_cm, flag=True)
        if (args.csr or args.csr_peek or args.csr_poke or args.csr_verify):
            change_to_csr_mode(args.tap, t)
            csr_probe_init()
            #probe_connect(probe_id, probe_addr, args.in_rom, flag=args.disconnect)
            #local_csr_probe(probe_id, probe_addr, args.in_rom, flag=True)
            #probe_connect(probe_id, probe_addr, args.in_rom, flag=True)
        if (args.cm_unlock or args.sm_unlock or args.status or args.otp or args.serial or args.flash):
            change_to_mdh_mode(args.tap, t)
            check_for_esecure(do_ad=args.do_ad)
        time.sleep(3)
    else:
        probe_connect(probe_id, probe_addr, args.in_rom_cm, flag=True)
        if (args.csr or args.csr_peek or args.csr_poke or args.csr_verify):
            csr_probe_init()
        if (args.cm_unlock or args.sm_unlock or args.status or args.otp or args.serial or args.flash):
            check_for_esecure(do_ad=args.do_ad)
        t = None

    constants.GLOBAL_EMULATION_ROM_MODE = True if args.in_rom_cm else False

    if args.cm_unlock:
        if args.in_rom_cm:
            # in_rom mode provide, so feed the inject_certificate with cert file provided by user.
            esecure_inject_certificate(args.in_rom_cm, customer=False)
            time.sleep(5)
        device_unlock_CM(args.cm_key, args.cm_cert, args.cm_grant, args.cm_pass)

    if args.sm_unlock:
        if args.in_rom_sm:
            # in_rom mode provide, so feed the inject_certificate with cert file provided by user.
            esecure_inject_certificate(args.in_rom_sm, customer=True)
            time.sleep(5)
        password = None if 'nopass' in args.quicktest else args.sm_pass
        device_unlock_SM(args.sm_key, args.sm_cert, args.sm_grant, password)

    # Once unlocked proceed with dump_status to verify if the grant are enabled as required.
    if args.status:
        print("Reading dump_status...")
        dump_status()

    #if args.status:
    #    print("2nd attempt Reading dump_status...")
    #    dump_status()

    # Once unlocked proceed with get otp (a secure access command).
    # Intentionally didn't handle the unlock failure above
    # to test if read_otp is denied if unlock fails above.
    if args.otp:
        read_otp()

    # Once unlocked proceed with set upgrade flag (a secure access command).
    #Intentionally didn't handle the unlock failure above
    # to test if set upgrade flag is denied if unlock fails above.
    if args.set_upgrade:
        diag_set_upgrade_flag(args.set_upgrade)

    # Intentionally didn't handle the unlock failure above
    if args.serial:
        get_serial()

    # Once unlocked proceed with flash API (a secure access) command.
    # Intentionally didn't handle the unlock failure above
    # to test if read_otp is denied if unlock fails above.
    if args.flash:
        d = DeviceFlash(dry=False)
        NUM_PTRS = 6

        flash_ptrs = d.read(0, 4 * NUM_PTRS)

        print("Flash data pointers: " + ' '.join(hex(x) for x in flash_ptrs))
        if any(p < 0x10000 and p != 0xffffffff for p in flash_ptrs):
            print ("This test expects no pointers to data in first flash sector ...")

        print ("Attempting to erase first sector ...")
        d.erase_sector(0)

        flash_data = d.read(0, d.page_size)
        print("Reading flash pointers again: " + ' '.join(hex(x) for x in flash_data[0:NUM_PTRS]))

        if any(p != 0xffffffff for p in flash_data):
            print ("The data was not erased properly")

        flash_data = flash_ptrs
        flash_data.extend([(x << 16) + x for x in range(500)])

        d.write(0, flash_data)

        flash_data_new = d.read(0, len(flash_data) * 4)
        print("Flash data verified correctly: %s" % ("True" if flash_data_new == flash_data else "FALSE"))

    # Once unlocked proceed with CSR poke and peek as a !!!! SEPERATE !!!! command.
    # Remember to run this command seperately without disconnecting the probe as we need t oconnnect probe to set CSR ring
    if args.csr or args.csr_peek or args.csr_poke or args.csr_verify :
        change_to_csr_mode(args.tap, t)
        if args.csr:
            print('\n************POKE MIO SCRATCHPAD ***************')
            print(local_csr_poke(0x440080a0, [0xabcd112299885566]))
            print('\n************PEEK MIO SCRATCHPAD ***************')
            word_array = local_csr_peek(0x440080a0, 1)
            print("word_array: {}".format([hex(x) for x in word_array] if word_array else None))

        if args.csr_peek:
            print('\n************PEEK CSR2 ***************')
            print('\nregadr={} reglen={}'.format(hex(args.regadr), hex(args.reglen)))
            word_array = local_csr_peek(args.regadr, args.reglen)
            print("word_array: {}".format(list(map(hex, word_array)) if word_array else None))

        if args.csr_poke:
            print('\n************POKE CSR2 ***************')
            print('\nregadr={} regval={}'.format(hex(args.regadr), list(map(hex, args.regval))))
            status = local_csr_poke(args.regadr, args.regval)
            print("status: {}".format(status))

        if args.csr_verify:
            print('\n************POKE PEEK and VERIFY CSR2 ***************')
            print('\nregadr={} regval={}'.format(hex(args.regadr), list(map(hex, args.regval))))
            pokestatus = local_csr_poke(args.regadr, args.regval)
            print("pokestatus: {}".format(pokestatus))
            if pokestatus:
                print('\nregadr={} reglen={}'.format(hex(args.regadr), hex(args.reglen)))
                word_array = local_csr_peek(args.regadr, args.reglen)
                if (args.regval == word_array):
                    print("Success")
                    #return True
                else:
                    print("Fail: word_array={} regval={}".format(list(map(hex, word_array)) if word_array else None, list(map(hex, args.regval))))
                    #return False
            else:
                print("poke failed with status: {}".format(pokestatus))
                #return False

    if args.reboot:
        change_to_csr_mode(args.tap, t)
        print('\n************POKE RESET REGISTER ***************')
        print(local_csr_poke(0x440080e8, [0x0000000000000010]))
        #change_back_to_default_mode(args.tap, t)

    change_back_to_default_mode(args.tap, t)
if __name__ == "__main__":
    main()
