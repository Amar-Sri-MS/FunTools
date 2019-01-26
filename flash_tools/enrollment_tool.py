##############################################################################
#  enrollment_tool.py
#
#  Utility
#
#  Copyright (c) 2018. Fungible, inc. All Rights Reserved.
#
#  1. Start Python
#  2. >>> import enrollment_tool as et
#  3. >>> et.probe('sp491', '10.1.23.131')
#  4. [autodetected-target_offline] >>> et.esecure_enroll()
#
#
#  3 connects to the Codescape probe (note the prompt change after)
#  4 prints the status
#  5 start enrollment process: this commands need to be run twice:
# the first time, it will generate the TBS, sign it and then store it in
# the database; the second time, it will retrieve the cert from the database
# and install it on the chip.
#
##############################################################################

import binascii
import struct
import os
import subprocess

import psycopg2

from imgtec.console.support import command
from imgtec.lib.namedenum import namedenum
from imgtec.lib.namedbitfield import namedbitfield
from imgtec.console import *
from imgtec.console import CoreFamily

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding



##############################################################################
# Error handling
##############################################################################

class RunError(Exception):
    pass

def run(main):
    try:
        main()
    except RunError as e:
        print "ERROR: %s" % e
        exit(1)


##############################################################################
# File access
##############################################################################

def read(filename, nbytes=None):
    if filename==None:
        return ""
    print "Reading %s" % filename
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
    print "Writing %s" % filename
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

TIMEOUT = 1000
DEBUG = 0

def prepare_target():
    if probe().mode not in ('autodetected', 'table'):
        autodetect()
    check_use_fast_read()


#@command()
def mdh_read_new(byte_address):
    """ the inbuilt mdh read is broken on some console versions """
    try:
        return probe().tiny.ReadMemory(byte_address)
    except:
        raise RuntimeError("APB read failed try a lower TCK clock") #TODO retry abit if valid = 0

def mdh_read_old(byte_address):
    tapscan("5 %d" % IR_DEVICEADDR, "32 %d" % (byte_address & 0xf80) )
    tapscan("5 %d" % IR_APBACCESS, "39 %d" % ((byte_address & 0x7c) | 0x3) )
    result = tapd("39 %d" % ((byte_address & 0x7c) | 0x2) )

    if (result[0] & 0x3) == 0x3:
        return result[0] >> 7

    raise RuntimeError("APB read failed try a lower TCK clock") #TODO retry abit if valid = 0


#@command()
def mdh_write_new(byte_address,word):
    """ the inbuilt mdh read is broken on some console versions """
    try:
        probe().tiny.WriteMemory(byte_address, word)
    except:
        raise RuntimeError("APB read failed try a lower TCK clock") #TODO retry abit if valid = 0

def mdh_write_old(byte_address,word):
    tapscan("5 %d" % IR_DEVICEADDR, "32 %d" % (byte_address & 0xf80) )
    result = tapscan("5 %d" % IR_APBACCESS, "39 %d" % (word << 7 | (byte_address & 0x7c) | 0x1) )

    if (result[0] & 0x3) == 0x3:
        return

    raise RuntimeError("APB read failed try a lower TCK clock") #TODO retry abit if valid = 0

mdh_read_ = mdh_read_old
mdh_write_ = mdh_write_old

def check_use_fast_read():
    global  mdh_read_
    global  mdh_write_
    try:
        if listdevices()[0].family == CoreFamily.MIPSecure:
            mdh_read_ = mdh_read_new
            mdh_write_ = mdh_write_new
        else:
            mdh_read_ = mdh_read_old
            mdh_write_ = mdh_write_old
    except:
        mdh_read_ = mdh_read_old
        mdh_write_ = mdh_write_old

#@command()
def esecure_read():
    """ internal only """
    mdh_write_(CONTROL,RD_REQ)
    timeout = 0
    while (mdh_read_(CONTROL) & RD_REQ) == 0: #wait for RD_REQ=1
        timeout+=1
        if timeout == TIMEOUT:
            raise RuntimeError("esecure_read: timeout waiting for RD_REQUEST to go high")
    data = mdh_read_(RDATA)
    mdh_write_(CONTROL,RD_ACK)
    timeout = 0
    while (mdh_read_(CONTROL) & RD_REQ) != 0: #wait for RD_REQ=0
        timeout+=1
        if timeout == TIMEOUT:
            raise RuntimeError("esecure_read: timeout waiting for RD_REQUEST to go low")
    mdh_write_(CONTROL,0)
    return data

#@command()
def esecure_write(data):
    """ internal only """
    mdh_write_(WDATA,data)
    mdh_write_(CONTROL,WR_REQ)
    timeout = 0
    while (mdh_read_(CONTROL) & WR_ACK) == 0:
        timeout+=1
        if timeout == TIMEOUT:
            raise RuntimeError("esecure_write: timeout waiting for WR_ACK to go high")
    mdh_write_(CONTROL,0)
    timeout = 0
    while (mdh_read_(CONTROL) & WR_ACK) != 0:
        timeout+=1
        if timeout == TIMEOUT:
            raise RuntimeError("esecure_read: timeout waiting for WR_ACK to go low")

def dump_id_regs():
    for k,v in ID_REGS.items():
        print k + " " + hex(mdh_read_(v))


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
            print hex(esecure_read())
    else:
        print decode_cmd_status(status)

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
                print STATUS_STRS[i]  + hex(bs) + " : "
                print repr(BootInfo(bs))
            else:
                print STATUS_STRS[i] + hex(esecure_read())
        else:
            word = esecure_read()
            print "Extra data: " + hex(word) + " " + char_repr(word)
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


CMD_SET_START_CERT=0xFE0A0000

CMD_GENERATE_PUF=0xFF050000
CMD_SET_PUF_CERT=0xFF060000

CMD_OPTION_CUSTOMER=1

def dump_status():
    def get_key(id, index, name):
        esecure_write(0xC)
        esecure_write(CMD_GET_PUBKEY + id)
        esecure_write(index)
        status = esecure_read();
        if cmd_status_ok(status):
            print "\nPublic Key - %s [%d]:" % (name, index)
            dump_return_data(status)

    # PUF-ROM keys
    get_key(0, 2, "Debugging key")
    get_key(0, 3, "Fungible key")
    get_key(0, 4, "Fungible Enrollment key")
    get_key(1, 0, "Customer key")

    esecure_write(0x8)
    esecure_write(CMD_GET_STATUS)
    print "\nStatus:"
    dump_status_data()

    esecure_write(0x8)
    esecure_write(CMD_GET_SERIAL_NUMBER)
    print "\nSerial Number:"
    dump_return_data()

def check_for_esecure():
    prepare_target()
    jtagchain()

    cidr1 = mdh_read_(ID_REGS["CIDR1"])

    if ((cidr1 >> 4) & 0xf) == 0xe:
        devid = mdh_read_(ID_REGS["DEVID"])
        if devid == 8:
            print "Found eSecure challenge interface"
            return

    print "Failed to find eSecure Challenge Interface"
    dump_id_regs()


def esecure_write_bytes(bytestr):
    if len(bytestr) % 4 != 0:
        raise RuntimeError("bytestr must always be a multiple of 4 bytes")

    words = []
    for pos in range(0, len(bytestr), 4):
        words.append(struct.unpack('<I',bytestr[pos:pos+4])[0])

    for word in words:
        if DEBUG: print "writing: "+ hex(word)
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
        print "This script is not able to use certificate with invalid length"
        return 7 # Invalid Param

    cmd = CMD_SET_START_CERT
    if customer:
        cmd += CMD_OPTION_CUSTOMER

    # total length = 4 /length/ + 4 /command/ + start_cert
    msglen = 4 + 4 + CERTIFICATE_LENGTH

    if DEBUG: print "writing: " + hex(msglen)
    esecure_write(msglen)
    if DEBUG: print "writing: " + hex(cmd)
    esecure_write(cmd)
    esecure_write_bytes(start_cert)

    status = esecure_read()

    print "Status: " + decode_cmd_status(status)

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
        print "Unexpected status from get challenge: " + hex(status)
        dump_return_data()
        raise RuntimeError()

    print "challenge_data:"
    challenge = [0,0,0,0]
    for i in range(len(challenge)):
        challenge[i] = esecure_read()
        print hex(challenge[i])

    if (mdh_read_(CONTROL) & RD_REQ) != 0:
        print "Warning Extra Read data still pending:"
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

    if DEBUG: print "data to sign (command + param + challenge): " +  binascii.hexlify(challenge_bs)

    #sign challenge
    developer_cert = read(developer_certificate)
    if verbose: print "developer cert:"
    if verbose: print binascii.hexlify(developer_cert)
    with open(developer_key, 'rb') as key_file:
        signing_key = serialization.load_pem_private_key(key_file.read(),
                                                         password=key_password,
                                                         backend=default_backend())

    signed_challenge = signing_key.sign(challenge_bs,
                                        padding.PKCS1v15(),
                                        hashes.SHA512())
    if DEBUG: print "signed challenge:"
    if DEBUG: print binascii.hexlify(signed_challenge)
    signed_challenge_len = len(signed_challenge)

    #Send Debug Access Request Command
    print "Unlocking..."

    # total length = 4 /length/ + 4 /command/ + 4 /dbg_grant/ + developer_cert + 4 /size/ + signed_challenge
    msglen = 4 + 4 + 4 + len(developer_cert) + 4 + signed_challenge_len

    if DEBUG: print "writing: " + hex(msglen)
    esecure_write(msglen)
    if DEBUG: print "writing: " + hex(cmd)
    esecure_write(cmd)
    if DEBUG: print "writing: " + hex(dbg_grant)
    esecure_write(dbg_grant)
    esecure_write_bytes(developer_cert)
    if DEBUG: print "writing: " + hex(signed_challenge_len)
    esecure_write(signed_challenge_len)
    esecure_write_bytes(signed_challenge)

    status = esecure_read()
    print "Status: " + decode_cmd_status(status)
    return status


def send_info_cmd(cmd):
    ''' send a simple command with no input, capture its reply in a string '''
    # send the command
    esecure_write(0x8)
    esecure_write(cmd)

    #capture the return data
    status = esecure_read()
    if not cmd_status_ok(status):
        print "Error " + decode_cmd_status(status) + " for command " + hex(cmd)
        return None

    # len = cmd_reply_length(status)
    return esecure_read_bytes()

def check_boot_step(desired_boot_step):
    ''' check that the chip is in the right boot step '''
    esecure_write(0x8)
    esecure_write(CMD_GET_STATUS)
    bs = dump_status_data()

    boot_step = BootInfo(bs).BootStep

    if boot_step <> desired_boot_step:
        print "Device is not in the proper state: {:02x}".format(boot_step)
        return False

    return True


########################################################################################
#
# Database routines
#
########################################################################################


def make_slicer_of(b):
    ''' return an object that will slice a string into multiple buffers '''
    offset = [0]

    def make_buff(size):
        ''' create a buffer at the current offset of the specified size '''
        ret = buffer(b, offset[0], size)
        offset[0] += size
        return ret

    return make_buff


DATA_DESC = (
    ('magic', 4),
    ('flags', 4),
    ('serial_info', 8),
    ('serial_nr', 16),
    ('puf_key', 64),
    ('nonce', 48),
    ('activation_code', 888),
    ('rsa_signature', 516))

FIELDS = [desc[0] for desc in DATA_DESC]
FIELDS_LIST = ",".join(FIELDS)
FIELDS_CONCAT = " || ".join(FIELDS)
ARGS_LIST = ",".join(["%({0})s".format(fld) for fld in FIELDS])

INSERT_STMT = "INSERT INTO enrollment (" + \
    FIELDS_LIST + ") VALUES (" + ARGS_LIST + ")"
RETRIEVE_STMT = "SELECT " + FIELDS_CONCAT + """ FROM enrollment WHERE serial_nr = %(serial_nr)s
                                               AND serial_info = %(serial_info)s """


def db_store_cert(conn, cert):
    ''' store the full certificate in the database '''

    # slice the cert into constituent buffers
    slicer = make_slicer_of(cert)
    values = {desc[0]: slicer(desc[1]) for desc in DATA_DESC}

    with conn.cursor() as cur:
        cur.execute(INSERT_STMT, values)

    conn.commit()

def db_retrieve_cert_aux( conn, query_data, descs):
    ''' retrieve a certificate matching the query data '''
    slicer = make_slicer_of(query_data)
    values = {desc[0]: slicer(desc[1]) for desc in descs}

    with conn.cursor() as cur:
        cur.execute(RETRIEVE_STMT, values)
        if cur.rowcount > 0:
            return str(cur.fetchone()[0])
    return None

def db_retrieve_cert(conn, tbs):
    ''' retrieve a possible certificate for tbs from the database '''
    return db_retrieve_cert_aux( conn, tbs, DATA_DESC)

def db_retrieve_cert_for_serial_nr(conn, serial_nr):
    ''' retrieve a possible certificate for tbs from the database '''
    return db_retrieve_cert_aux( conn, serial_nr, (
        ('serial_info', 8),
        ('serial_nr', 16)
    ))


####################################################################################################
#
#  Connection to HSM
#
####################################################################################################

def sign(tbs_cert):
    ''' contact the HSM to sign that TBS '''

    # The HSM is controlled via a Python3 script so we need to start a new process
    cmd = "python3 generate_firmware_image.py sign -f - -o - -k fpk4"
    # FIXME: devtools/firmware
    script_dir = "/home/fferino/Projects/SBPFirmware/software/devtools/firmware"
    sign_p = subprocess.Popen(cmd, shell=True,
                              stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              cwd=script_dir)

    stdout, stderr = sign_p.communicate(tbs_cert)
    print "Signing result: %s" % sign_p.returncode
    if sign_p.returncode != 0:
        print stderr
        return None

    return stdout


####################################################################################################
#
# Enrollment command -- only one PUF activation is possible per Boot
#
# Case 1: chip has never been seen : get the enrollment tbs, generate certificate
#         and store in the database
# Case 2: chip was seen before: send the certificate from the database
#
####################################################################################################


def save_enroll_cert(cert):
    ''' install the enrollment certificate on the device '''
    # send the command:    # total length = 4 /length/ + 4 /command/ +_cert
    msglen = 4 + 4 + len(cert)

    esecure_write(msglen)
    esecure_write(CMD_SET_PUF_CERT)
    esecure_write_bytes(cert)

    status = esecure_read()
    success = cmd_status_ok(status)
    if not success:
        print "Error saving the enrollment certificate: " + decode_cmd_status(status)

    return success


BOOT_STEP_PUF_INIT=(0x13<<2)

def enroll(conn):

    prepare_target()
    check_for_esecure()

    # always verify the chip is in the PUF-ROM handler
    # check bootstep
    if not check_boot_step( BOOT_STEP_PUF_INIT):
        return False, "Chip is not in the correct state"

    # Get serial number to see if this chip went through PUF-Activation
    # in an earlier boot sequence
    serial_nr = send_info_cmd(CMD_GET_SERIAL_NUMBER)
    print "Serial Number: " + binascii.hexlify(serial_nr)

    # is a corresponding certificate in the database
    cert = db_retrieve_cert_for_serial_nr( conn, serial_nr)
    if cert is None:
        print "No certificate for this chip in the database"
        tbs = send_info_cmd(CMD_GENERATE_PUF);
        print "Enrollment information :" + binascii.hexlify(tbs)
        # sign the TBS with the HSM
        cert = sign(tbs)
        if cert is None:
            return False, "Error signing the certificate"

        print "Storing new certificate in database"
        db_store_cert(conn, cert)
        return True, """Certificate in the database.
        Reboot the chip and rerun the esecure_enroll command"""

    if not save_enroll_cert(cert):
        return False, "Unable to save the enrollment certificate on the chip"

    return True, "Chip enrolled"


def esecure_enroll():
    '''
    enroll the chip trying to do the right thing depending on the db content
    '''
    # with .. as conn: does not close the connection automatically so...
    conn = psycopg2.connect("dbname=enrollment_db")
    result, summary = enroll(conn)
    conn.close()

    print summary
    return result
