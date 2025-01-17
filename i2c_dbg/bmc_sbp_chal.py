#!/usr/bin/env python
#
# bmc_sbp_chal.py
#
# Copyright (c) 2017-2022 Fungible,Inc.
# All Rights Reserved
#
''' This module allows to execute commands, read images and update them
using the i2C challenge interface to SBP

Examples:

Get the status

$ python bmc_sbp_chal.py --chip 0 --status

Read the image of type 'eepr' and save it to the file eeprom.bin

$ python bmc_sbp_chal.py --chip 0 --read eepr --out eeprom.bin

Update the B copy of the pufr image with the content of the file signed_pufr_fpk4_v1.bin

$ python bmc_sbp_chal.py  --chip 0 --update signed_pufr_fpk4_v1.bin --BImage


***** IMPORTANT: this must be able to run on Python2.7 and Python 3 ********

'''

from __future__ import print_function
import os
import binascii
import datetime
import argparse
import struct
import logging
import platform   # Fungible
import hashlib
import sys
import collections

from subprocess import check_output as subprocess_check_output

# python2 then python3
try:
    from urllib import urlopen, urlretrieve
except ImportError:
    from urllib.request import urlopen, urlretrieve

from tempfile import NamedTemporaryFile
from gzip import open as gzip_open
from shutil import copyfileobj as shutil_copyfileobj, move as shutil_move
from traceback import print_exc as traceback_print_exc
from textwrap import wrap as textwrap_wrap

import ctypes
import ctypes.util  # find_library
from ctypes import (c_char_p, c_void_p,
                    c_ubyte, c_uint, c_int, c_ulong,
                    POINTER, byref)


logging.basicConfig()
logger = logging.getLogger('i2c')

def no_output(*_a,**_k):
    ''' alternative to print for print_fn argument '''
    pass

def hex_str(b_arr, indent_str=None):
    ''' byte array to hexadecimal codes '''
    s = ":".join(["%02x" % b for b in b_arr])
    ws = textwrap_wrap(s,48)
    if indent_str:
        return ("\n" + indent_str).join(ws)
    else:
        return "\n".join(ws)

def str2bytes(s):
    return bytes(str(s).encode('ascii'))

def bytes2str(b):
    return b.decode('ascii', 'backslashreplace')

def printable_str(b_arr):
    ''' convert an ascii byte array to a printable str
    Not really needed for Python2 where bytearray will be printed as C strings
    Python3 will print  "bytearray(b'<all bytes>')
    '''
    index_first_non_print = next((i for i,b in enumerate(b_arr)
                                  if b < 0x20 or b > 0x7E),
                                 len(b_arr))
    return bytes2str(b_arr[:index_first_non_print])


def raw_printable_str(b_arr):
    ''' convert a complete ascii byte array to a printable str
    Any non-printable characters are printed as '.'
    '''
    return ''.join([chr(c) if c >= 0x20 and c <= 0x7e else '.' for c in b_arr])


def le2int(b_arr):
    ''' interpret array of bytes of any length  as little endian integer
    since there is no int.from_bytes in Python2 '''
    ret = 0
    shift = 0
    for b in b_arr:
        ret |= (b << shift)
        shift += 8
    return ret

def get_fs1600_rev():
    ''' return the FS1600 system revision (1 or 2) '''
    result_txt = subprocess_check_output(['devmem', '0x1e780000'])
    result_int = int(result_txt, 0)
    return ((result_int & 0xF00) >> 8) + 1

def decompress_file(file_path):
    with gzip_open(file_path) as f_in:
        with NamedTemporaryFile(delete=False) as f_out:
            shutil_copyfileobj(f_in, f_out)
    shutil_move(f_out.name, file_path)


##############################################################################
# Remote resources
##############################################################################

def get_request(port, resource, data=None):
    url = "http://localhost:%s/%s" % (port, resource)
    f = urlopen(url, data)
    return f.read()

def get_remote_file(port, file_name, local_file_name=None):
    url = "http://localhost:%s/%s" % (port, file_name)
    local_file_name, _ = urlretrieve(url, local_file_name)
    return local_file_name


##############################################################################
# Structure
##############################################################################

class Structure(object):

    vocabulary = None

    def __init__(self):
        self.content = 0
        self.nextpos = 0
        self.fields = {}
        self.listfields = []

    def add_field(self, name, size, bigend):
        assert size > 0
        if size%8==0:
            assert self.nextpos%8==0
        if name:
            self.fields[name] = (self.nextpos, size, bigend)
            self.listfields.append(name)
        self.nextpos += size

    def get_pos(self, key):
        try:
            pos, nbits, bigend = self.fields[key]
        except:
            raise ValueError("invalid field '%s'" % key)
        lsb = pos
        msb = lsb+nbits
        mask = 2**msb-2**lsb
        return nbits, mask, lsb, bigend

    def set_bits(self, key, value):
        nbits, mask, shift, bigend = self.get_pos(key)
        # Convert to integer
        try:
            value = int(value, 0)
        except:
            raise ValueError("invalid %s value: '%s'" % (key, value))
        # Check range
        if value<0 or value>=2**nbits:
            raise ValueError("%s value out of range: %#x" % (key, value))
        # Swap bytes
        if bigend:
            assert nbits%8==0
            value = "{0:0{1}x}".format(value, nbits//4)   # To hexadecimal string
            value = binascii.unhexlify(value)             # To bytes
            value = value[::-1]                           # Swap bytes
            value = binascii.hexlify(value)               # To hexadecimal string
            value = int(value, 16)                        # To integer
        self.content &= ~mask
        self.content |= value<<shift

    def get_bits(self, key):
        # Extract value
        nbits, mask, shift, bigend = self.get_pos(key)
        value = (self.content&mask)>>shift
        # Convert to hexadecimal string
        value = "{0:0{1}x}".format(value, nbits//4)
        # Swap bytes
        if bigend:
            assert nbits%8==0
            value = binascii.unhexlify(value)                 # To bytes
            value = value[::-1]                               # Swap bytes
            value = binascii.hexlify(value).decode('ascii')   # To hexadecimal string
        return value

    def set_txt(self, txt):
        for l in txt.splitlines():
            l = l.strip()
            if not l.startswith('#'):
                try:
                    key, value = tuple(l.split(None, 1))
                    if self.vocabulary:
                        value = self.vocabulary.get(value, value)
                except:
                    raise ValueError("value with invalid format (%s)" % l)
                self.set_bits(key, value)

    def set_bin(self, abin):
        self.set_bits("all", "0x" + binascii.hexlify(abin).decode('ascii'))

    def get_size(self):
        return (self.nextpos+7)/8

    def get_txt(self):
        txt = ""
        for key in self.listfields:
            txt += "  %s 0x%s\n" % (key, self.get_bits(key))
        return txt.rstrip()

    def get_bin(self, field_name='all'):
        return binascii.unhexlify(self.get_bits(field_name))



##############################################################################
# OTP
##############################################################################

class OTPCM(Structure):

    def __init__(self):
        super(OTPCM, self).__init__()          #nbits, bigend
        self.add_field("HW_LOCK_BIT",             1, False)
        self.add_field("ESEC_SECUREBOOT",         1, False)
        self.add_field("WATCHDOG",                1, False)
        self.add_field(None,                      5, False)
        self.add_field("CUSTOMER_KEY_BIT",        1, False)
        self.add_field("I2C_CHAL_BIT",            1, False)
        self.add_field("CC_DBU_MASTER",           1, False)
        self.add_field("PC_DBU_MASTER",           1, False)
        self.add_field(None,                      4, False)
        self.add_field("TAMPERFILTERPERIOD",      8, False)
        self.add_field("TAMPERFILTERTHRESHOLD",   8, False)
        self.add_field("DEBUGLOCK",              32, False)
        self.add_field("SERIAL_INFO",            64, True)
        self.add_field("SERIALNO",              128, True)
        for i in range(32):
            self.add_field("TAMP%02d_CM"%i,        4, False)
        self.fields["all"] = (0, self.nextpos, True)

class OTPSM(Structure):

    def __init__(self):
        super(OTPSM, self).__init__()          #nbits, bigend
        self.add_field("CUSTOMER_SEC_CTRL",       8, False)
        self.add_field("CUSTOMER_KEY_VALID",      8, False)
        self.add_field("CUSTOMER_KEY_REVOKED",    8, False)
        self.add_field("CUSTOMER_KEY_TYPE",       8, False)
        self.add_field("DEBUGLOCK",              32, False)
        self.add_field("NR_ZEROES_KEY_HASH1",     8, False)
        self.add_field("NR_ZEROES_KEY_HASH2",     8, False)
        self.add_field(None,                  6 * 8, False)
        self.add_field(None,                 16 * 8, True)
        self.add_field("KEY_HASH1",          32 * 8, True)
        self.add_field("KEY_HASH2",          32 * 8, True)
        self.fields["all"] = (0, self.nextpos, True)

################################################################################
# Exceptions classes
################################################################################

class SigningError(Exception):
    ''' Exception raised when error signing '''
    pass

# derive ChallengeError from Environment error to capture error code
class ChallengeError(EnvironmentError):
    ''' Exception raised with error with challenge protocol '''
    pass

class NorImageError(Exception):
    ''' Exception related to content of the Nor Image '''
    pass

################################################################################
# Crypto
################################################################################
class CryptoUtils(object):

    MAX_RSA_KEY_SIZE = 512

    def __init__(self):
        if 'ami' in platform.release():
            # use the special location on this Fungible BMC platform
            self.libcrypto = ctypes.cdll.LoadLibrary('/usr/lib/arm-linux-gnueabi/libcrypto.so')
            self.libc = ctypes.cdll.LoadLibrary('/lib/arm-linux-gnueabi/libc.so.6')
        else:
            libcrypto = ctypes.util.find_library('crypto')
            if libcrypto is None:
                libcrypto = '/usr/lib/libcrypto.so'
            self.libcrypto = ctypes.cdll.LoadLibrary(libcrypto)

            libc = ctypes.util.find_library('c')
            if libc is None:
                libc = '/lib/libc.so.6'
            self.libc = ctypes.cdll.LoadLibrary(libc)

        self.fopen = self.libc.fopen
        self.fopen.argtypes = [c_char_p, c_char_p]
        self.fopen.restype = c_void_p

        self.fclose = self.libc.fclose
        self.fclose.argtypes = [c_void_p]

        self.PEM_read_RSAPrivateKey = self.libcrypto.PEM_read_RSAPrivateKey
        self.PEM_read_RSAPrivateKey.argtypes = [c_void_p, POINTER(c_void_p),
                                                c_void_p, c_void_p]

        self.RSA_sign = self.libcrypto.RSA_sign
        self.RSA_sign.argtypes = [c_int, c_char_p, c_uint, c_char_p,
                                  POINTER(c_uint), c_void_p]

        self.RSA_free = self.libcrypto.RSA_free
        self.RSA_free.argtypes = [c_void_p]

        self.ERR_get_error = self.libcrypto.ERR_get_error
        self.ERR_get_error.restype = c_ulong

        self.ERR_lib_error_string = self.libcrypto.ERR_lib_error_string
        self.ERR_lib_error_string.argtypes = [c_ulong]
        self.ERR_lib_error_string.restype = c_char_p

        self.ERR_func_error_string = self.libcrypto.ERR_func_error_string
        self.ERR_func_error_string.argtypes = [c_ulong]
        self.ERR_func_error_string.restype = c_char_p

        self.ERR_reason_error_string = self.libcrypto.ERR_reason_error_string
        self.ERR_reason_error_string.argtypes = [c_ulong]
        self.ERR_reason_error_string.restype = c_char_p

    def get_ossl_errs(self):
        errs = ""
        ossl_err = self.ERR_get_error()
        while ossl_err:
            errs += "OpenSSL error %s:%s:%s\n" % (
                bytes2str(self.ERR_lib_error_string(ossl_err)),
                bytes2str(self.ERR_func_error_string(ossl_err)),
                bytes2str(self.ERR_reason_error_string(ossl_err)))
            ossl_err = self.ERR_get_error()
        return errs

    def rsa_pkcs_sign(self, key_file_name, hash_name, data):
        # read the key from the PEM file
        key = c_void_p()
        fp = self.fopen(str2bytes(key_file_name), b'rb')
        if not fp:
            raise SigningError("Unable to open key file %s for reading" %
                               key_file_name)

        res = self.PEM_read_RSAPrivateKey(fp, byref(key), None, None)
        self.fclose(fp)

        if not res:
            raise SigningError("Error reading key from %s:\n%s" %
                               (key_file_name, self.get_ossl_errs()))

        digest = hashlib.new(hash_name, data).digest()
        hash_nid = self.libcrypto.OBJ_txt2nid(str2bytes(hash_name))
        signature = ctypes.create_string_buffer(CryptoUtils.MAX_RSA_KEY_SIZE)
        siglen = c_uint()
        res = self.RSA_sign(hash_nid, digest, len(digest),
                            signature, byref(siglen), key)
        # done with the key
        self.RSA_free(key)

        if not res:
            raise SigningError("Error  signing with key from %s: %s" %
                               (key_file_name, self.get_ossl_errs()))

        return signature.raw[:siglen.value]


CERT_SIZE = 1096

class DebuggingResources(object):
    ''' abstract base class for debugging resources '''
    def start_certificate(self, _req_dbg_grants, _serial_nr):
        raise RuntimeError("Abstract class called")

    def debugging_certificate(self, _req_dbg_grants, _serial_nr):
        raise RuntimeError("Abstract class called")

    def sign(self, _tbs):
        raise RuntimeError("Abstract class called")


class LocalDebuggingResources(DebuggingResources):
    ''' local files: deprecated -- local should use a certificate db '''

    def __init__(self, cert_file, key_file, start_cert_file):
        self.crypto_utils = None   # lazy instantiation
        self.cert_file = cert_file
        self.key_file = key_file
        self.start_cert_file = start_cert_file

    def start_certificate(self, _req_dbg_grants, _serial_nr):
        if self.start_cert_file is None:
            raise RuntimeError("Unable to unlock: no start certificate provided")

        with open(self.start_cert_file, 'rb') as f:
            cert = bytearray(f.read())
        # should we check that this cert can unlock the required grants?
        return cert

    def debugging_certificate(self, _req_dbg_grants, _serial_nr):
        if self.cert_file is None:
            raise RuntimeError("Unable to unlock: no debugging certificate provided")

        with open(self.cert_file, 'rb') as f:
            cert = bytearray(f.read())
        # should we check that this cert can unlock the required grants?
        return cert

    def sign(self, tbs):

        if self.key_file is None:
            raise RuntimeError("unable to unlock: no key provided")

        if not self.crypto_utils:
            self.crypto_utils = CryptoUtils()

        return self.crypto_utils.rsa_pkcs_sign(self.key_file, 'sha512', tbs)


class RemoteDebuggingResources(DebuggingResources):

    CTX_ID_LEN = 8
    CERT_GRANT_OFFSET = 4

    def __init__(self, http_port):
        self.http_port = http_port
        self.ctx_id = None
        self.certs = None


    def _get_certs(self, req_dbg_grants, serial_nr):
        data = b'\x00' + struct.pack('<I', req_dbg_grants) + serial_nr
        response = get_request(self.http_port,
                               "debugging_certificates",
                               data=data)
        # in our simple protocol, reply is version (0), 8 bytes group_id, followed by
        # debugging certificate and then start certificate
        if not response:
            raise RuntimeError("Remote server did not find any suitable certificate")
        if response[0:1] != b'\x00':
            raise RuntimeError("Version mismatch from remote debug server: %s" %
                               response[0:1])
        self.ctx_id = response[1:1+self.CTX_ID_LEN]
        self.certs = response[1+self.CTX_ID_LEN:]

    def start_certificate(self, req_dbg_grants, serial_nr):
        # get the certs if not there
        if self.certs is None:
            self._get_certs(req_dbg_grants, serial_nr)

        start_cert = self.certs[CERT_SIZE:]
        return start_cert


    def debugging_certificate(self, req_dbg_grants, serial_nr):
        # get the certs if not there or do not match req_dbg_grants
        if self.certs is None:
            self._get_certs(req_dbg_grants, serial_nr)
        else:
            # dbg grants are the 4 bytes after MAGIC
            dbg_auth = self.certs[self.CERT_GRANT_OFFSET:self.CERT_GRANT_OFFSET+4]
            cert_dbg_grants = struct.unpack('<I', dbg_auth)[0]
            if (cert_dbg_grants & req_dbg_grants) != req_dbg_grants:
                self._get_certs(req_dbg_grants, serial_nr)

        dbg_cert = self.certs[:CERT_SIZE]
        return dbg_cert


    def sign(self, tbs):

        # verify there is a current context id
        if self.ctx_id is None:
            raise RuntimeError("Signature before retrieving certificate")

        data = b'\x00' + self.ctx_id + tbs
        response = get_request(self.http_port, "signature", data=data)
        if not response:
            raise RuntimeError("Empty signature from remote debug server")
        if response[0:1] != b'\x00':
            raise RuntimeError("Version mismatch from remote debug server")

        return response[1:]


##############################################################################
# I2C
##############################################################################

class i2c_dbg(object):
    ''' class used to call the functions of i2c_dbg.so '''
    def __init__(self):
        this_script_dir = os.path.dirname(os.path.realpath(__file__))
        libi2c_dbg = ctypes.cdll.LoadLibrary(this_script_dir + '/i2c_dbg.so')

        # all purpose challenge command
        self.i2c_dbg_chal_cmd = libi2c_dbg.i2c_dbg_chal_cmd
        self.i2c_dbg_chal_cmd.restype = POINTER(c_ubyte)
        self.i2c_dbg_chal_cmd.argtypes = [c_uint, c_int,
                                          c_char_p, c_int,
                                          c_int, POINTER(c_int)]
        # specialized write flash
        self.i2c_dbg_write_flash = libi2c_dbg.i2c_dbg_write_flash
        self.i2c_dbg_write_flash.restype = c_int
        self.i2c_dbg_write_flash.argtypes = [c_int, c_int,
                         c_char_p, c_int]

        # specialized read flash
        self.i2c_dbg_read_flash_ex = libi2c_dbg.i2c_dbg_read_flash_ex
        self.i2c_dbg_read_flash_ex.restype = POINTER(c_ubyte)
        self.i2c_dbg_read_flash_ex.argtypes = [c_int, c_int,
                                               c_int, POINTER(c_int)]

        # config -- debug
        self.i2c_dbg_debugging_on = libi2c_dbg.debugging_on
        self.i2c_dbg_debugging_on.argtypes = [c_int]

        # config -- i2c devices
        self.i2c_dbg_set_chip_device = libi2c_dbg.set_device
        self.i2c_dbg_set_chip_device.argtypes = [c_int, c_char_p]

        self.i2c_dbg_get_chip_device = libi2c_dbg.get_device
        self.i2c_dbg_get_chip_device.restype = c_char_p
        self.i2c_dbg_get_chip_device.argtypes = [c_int]


    def chal_cmd(self, cmd, chip_inst, data=None,
         reply_delay_sec=0):
        reslen = c_int()
        res = self.i2c_dbg_chal_cmd(cmd, chip_inst,
                    bytes(data) if data else None,
                    len(data) if data else 0,
                    int(reply_delay_sec * 1000000),
                    byref(reslen))
        return bytearray(ctypes.string_at(res, reslen.value))

    def write_flash(self, chip_inst, nor_addr, input_data):
        if input_data:
            err = self.i2c_dbg_write_flash(chip_inst, nor_addr,
                        bytes(input_data), len(input_data))
            if err:
                raise ChallengeError(err, "Error writing flash: %d" % err)


    def read_flash(self, chip_inst, nor_addr, length):
        err = c_int()
        res = self.i2c_dbg_read_flash_ex(chip_inst, nor_addr,
                                         length, byref(err))
        if err:
            raise ChallengeError(err, "Error reading flash: %d" % err.value)

        return bytearray(ctypes.string_at(res, length))

    def debugging_on(self, turnon):
        self.i2c_dbg_debugging_on(1 if turnon else 0)

    def get_chip_device(self, chip_inst):
        return self.i2c_dbg_get_chip_device(chip_inst)

    def set_chip_device(self, chip_inst, device_str):
        return self.i2c_dbg_set_chip_device(chip_inst, str2bytes(device_str))


##############################################################################
# Challenge Command
##############################################################################

GET_SERIAL_NUMBER = 0xFE000000
GET_OTP = 0xFE0B0000
GET_STATUS = 0xFE010000
GET_PUBKEY = 0xFE020000
GET_ENROLL_INFO = 0xFF050000
SET_ENROLL_INFO = 0xFF060000

# OTP READ Options:
OTP_CM = 0
OTP_SM = 1
OTP_FULL = 2

# Chip must report being in this boot step for enrollment
BOOT_STEP_PUF_INIT = 0x68

INJECT_CERTIFICATE = 0xFE0A0000

GET_CHALLENGE = 0xFD000000
GRANT_DBG_ACCESS = 0xFD010000
CHALLENGE_LENGTH = 16

FLASH_ERASE_SECTION = 0xFC000000

PREPARE_QSPI = 0xFE080000

QSPI_PAGE_SIZE = 0x100
QSPI_SECTOR_SIZE = 0x10000
FLASH_SIZE = 0x1000000     # 16 MB

ERR_OK = 0
ERR_INVALID_CMD = 1
ERR_AUTH_ERR = 2
ERR_INVALID_SIGN = 3
ERR_BUS_ERROR = 4
ERR_RESERVED = 5
ERR_CRYPTO_ERR = 6
ERR_INVALID_PARAM = 7

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

EXTRA_DATA_PARSE_V1 = (
    ("Version",      1),
    ("Magic",        3),
    ("Flash Size",   4),
    ("Flags",        4),
    ("Init",         1),
    ("RD Cmd",       1),
    ("Dummy Cycles", 1),
    ("Mode Bits",    1))

EXTRA_DATA_PARSE_V2 = EXTRA_DATA_PARSE_V1 + (
    ("Puf current version", 4),
    ("eSecure Firmware Current Version", 4))

EXTRA_BYTES_KEY = "Extra Bytes"
VERSION_BYTES_KEY = "Version string"

class DBG_FlashOp(object):
    ''' base class for flash operations '''

    def read_flash(self, _offset, _num_bytes):
        raise RuntimeError("Abstact class called")

    def erase_flash_sector(self, _offset):
        raise RuntimeError("Abstact class called")

    def write_flash(self, _nor_addr, _input_data):
        return (False, "This class does nothing")



class DBG_File(DBG_FlashOp):
    ''' Similar to DBG_Chal but use a file: used for NOR_Image with a file '''

    def __init__(self, file_name):
        self.file_name = file_name
        self.f = open(file_name, 'rb+')


    def read_flash(self, offset, num_bytes):
        self.f.seek(offset)
        data = self.f.read(num_bytes)
        return bytearray(data)

    def erase_flash_sector(self, offset):
        ''' simulate erase flash sector at offset '''
        print("Erasing flash at offset %d (0x%08x)" % (offset,offset))
        if (offset & (QSPI_SECTOR_SIZE - 1)) != 0:
            raise ValueError("Invalid offset %d: must be a multiple of %d" %
                             (offset, QSPI_SECTOR_SIZE))

        self.f.seek(offset)
        self.f.write(b'\xFF' * QSPI_SECTOR_SIZE)


    def write_flash(self, nor_addr, input_data):
        ''' simuulate NOR flash writing '''
        self.f.seek(nor_addr)
        data_len = len(input_data)
        curr_data = bytearray(self.f.read(data_len))
        to_write = bytearray([(c & i) for c,i in zip(curr_data, input_data)])
        self.f.seek(nor_addr)
        self.f.write(to_write)


class DBG_Chal(DBG_FlashOp):

    def __init__(self, chip_inst, port, cert_file, key_file, start_cert_file, i2c_dev):
        self.i2c_dbg = i2c_dbg()
        self.chip_inst = chip_inst
        if i2c_dev:
            # i2c_dev can be a dev port (/dev/i2c-17) or a number (17):
            # Linux's i2ctools and enrollment_client.py uses the number
            # so as a convenience for the user,  detect that case and
            # generate the devport for the user if a number is provided
            if i2c_dev.isdigit():
                i2c_dev = "/dev/i2c-%d" % i2c_dev

            self.i2c_dbg.set_chip_device(chip_inst, i2c_dev)

        if logger.getEffectiveLevel() <= logging.DEBUG:
            print('Using device "%s" for chip %d\n' %
              (bytes2str(self.i2c_dbg.get_chip_device(chip_inst)),chip_inst))
            self.i2c_dbg.debugging_on(True)

        self.serial_nr = None # cache serial number

        # prefer remote
        if port:
            self.dbg_info = RemoteDebuggingResources(port)
        else:
            self.dbg_info = LocalDebuggingResources(cert_file,
                                                    key_file,
                                                    start_cert_file)

    def challenge_cmd(self, cmd, data=None, reply_delay_sec=0):
        logger.info("Executing command 0x%08x", cmd)

        rdata = self.i2c_dbg.chal_cmd(cmd, self.chip_inst, data,
                                      reply_delay_sec)
        err_info = self.cmd_status_code(rdata, cmd)
        if err_info[0] != 0:
            raise ChallengeError(*err_info)

        return rdata[4:]  # strip the header


    # header in LE format
    def cmd_status_code(self, header_bytes, cmd):
        ''' look at header and return (errno, strerror) '''
        sts = header_bytes[2]
        sts_str = ""
        if sts >= 0:
            if sts < len(CMD_STATUS_CODE_STR):
                sts_str = "Cmd: 0x%08x: %s" % (cmd, CMD_STATUS_CODE_STR[sts])
            else:
                sts_str = "Cmd: 0x%08x: %d" % (cmd, sts)
        return sts, sts_str

    # header in LE format
    def cmd_reply_length(self, header_bytes):
        return header_bytes[0] + 0x0100 * header_bytes[1]

    def write_flash(self, nor_addr, input_data):
        return self.i2c_dbg.write_flash(self.chip_inst, nor_addr, input_data)

    def read_flash(self, offset, num_bytes):
        if offset > FLASH_SIZE:
            raise RuntimeError("Attempt to read past FLASH SIZE @ %x" % offset)
        return self.i2c_dbg.read_flash(self.chip_inst, offset, num_bytes)

    def decode_extra_data(self, extra_bytes, version):
        ret = []
        start = end = 0
        extra_data = {
            1: EXTRA_DATA_PARSE_V1,
            2: EXTRA_DATA_PARSE_V2
        }
        if version not in extra_data:
            return [("Unknown", 0)], extra_bytes

        for instr in extra_data[version]:
            end = start + instr[1]
            ret.append( (instr[0], le2int(extra_bytes[start:end])) )
            start = end

        return ret, extra_bytes[end:]


    def decode_status_bytes(self, data):
        logger.info('STATUS:\traw_bytes:\n%s', hex_str(data))
        status_size = len(data)
        status_decoded = collections.OrderedDict()
        i = 0
        while i < status_size:
            status_str_idx = i//4
            if status_str_idx < len(SBP_STATUS_STR):
                status_value = struct.unpack('<I', data[i:i+4])[0]
                status_decoded[SBP_STATUS_STR[status_str_idx]] = status_value
                i+=4
            else:
                # extract version string: search for anything that looks like
                # a stream of printable ascii characters
                extra = data[i:status_size]
                status_decoded[VERSION_BYTES_KEY] = printable_str(extra)
                # extend by 1 to include a terminating null and
                # round up to the next 4-byte word
                version_len = 4 * ((len(status_decoded[VERSION_BYTES_KEY]) + 1 + 3) // 4)
                extra = extra[version_len:]
                if bytes(extra[1:4]) == b'\xd0\xde\xad':
                    version = struct.unpack('B', extra[0:1])[0]
                    extra_data, extra = self.decode_extra_data(extra, version)
                    for k,v in extra_data:
                        assert (k not in status_decoded)
                        status_decoded[k] = v

                status_decoded[EXTRA_BYTES_KEY] = extra
                i = status_size # all done
        return status_decoded

    def print_decoded_status(self, status_dict):
        print("Status:")
        for key, value in status_dict.items():
            if key == EXTRA_BYTES_KEY:
                continue

            if isinstance(value, str if sys.version_info[0] >= 3 else basestring):
                print("\t%s: %s" % (key, value))
            else:
                print("\t%s: 0x%08x" % (key, value))

            if key == 'Boot Status':
                print('\t\t%s: 0x%02x' % ('BootStep', value & 0xFF))
                print('\t\t%s: 0x%x' % ('eSecureUpgradeFlag', (value >> 8) & 0x1))
                print('\t\t%s: 0x%x' % ('HostUpgradeFlag', (value >> 12) & 0x1))
                print('\t\t%s: 0x%x' % ('eSecureImage',(value >> 14) & 0x1))
                print('\t\t%s: 0x%x' % ('HostImage',(value >> 20) & 0x1))

        extra_bytes = status_dict[EXTRA_BYTES_KEY]
        print('\t%s: %s\n\t\traw: %s' %
              (EXTRA_BYTES_KEY,
               raw_printable_str(extra_bytes),
               hex_str(extra_bytes, indent_str="\t\t     ")))


    def get_serial_number(self):
        '''
        return the serial number.
        Cached since this is small and often required
        '''
        if self.serial_nr is None:
            self.serial_nr = self.challenge_cmd(GET_SERIAL_NUMBER)
        return self.serial_nr

    def get_status(self):
        rdata = self.challenge_cmd(GET_STATUS)
        return self.decode_status_bytes(rdata)

    def read_otp(self, option):
        rdata = self.challenge_cmd(GET_OTP | option)
        if option == OTP_CM:
            otpcm = OTPCM()
            otpcm.set_bin(rdata)
            otp_decoded = otpcm.get_txt()
            return otp_decoded

        #otherwise return hex dump
        return hex_str(rdata)

    def get_key(self, index, customer=False):

        cmd = GET_PUBKEY
        # for customer, key is always 1
        if customer:
            index = 1
            cmd += 1  # cmd modification

        key_index = bytearray(struct.pack('<I', index))
        return self.challenge_cmd(cmd, key_index)

    def prepare_qspi(self):
        return self.challenge_cmd(PREPARE_QSPI)

    def save_enroll_cert(self, cert):
        try:
            self.challenge_cmd(SET_ENROLL_INFO, cert,
                               reply_delay_sec = 1)
        except ChallengeError as ce:
            # this challenge command returns its own err codes
            ce.strerror = ""
            raise ce

    def get_enroll_tbs(self):
        try:
            return self.challenge_cmd(GET_ENROLL_INFO)
        except ChallengeError as ce:
            ce.strerror = ""
            raise ce

    def erase_flash_sector(self, offset):
        ''' erase flash sector at offset '''
        print("Erasing flash at offset 0x%08x" % offset)
        if (offset & (QSPI_SECTOR_SIZE - 1)) != 0:
            raise ValueError("Invalid offset %d: must be a multiple of %d" %
                             (offset, QSPI_SECTOR_SIZE))

        params = bytearray(struct.pack('<I', offset))
        return self.challenge_cmd(FLASH_ERASE_SECTION, params, reply_delay_sec=0.5)

    def get_start_cert(self):
        return self.dbg_info.start_certificate(0, self.get_serial_number())

    def inject_cert(self, dbg_grants):

        start_cert = self.dbg_info.start_certificate(dbg_grants, self.get_serial_number())
        self.challenge_cmd(INJECT_CERTIFICATE, start_cert, 5)
        print('Injected certificate')


    def get_dbg_access(self, dbg_grants):

        challenge = self.challenge_cmd(GET_CHALLENGE)

        logger.info("Challenge = %s", ' '.join([hex(x) for x in challenge]))

        if len(challenge) != CHALLENGE_LENGTH:
            raise ValueError("Invalid challenge length: %d" % len(challenge))

        # challenge command: parameter: requested debug grants
        # input data = debugging certificate + signature( command + parameter + challenge)

        # certificate
        cert = self.dbg_info.debugging_certificate(dbg_grants, self.get_serial_number())

        # mask the dbg grants with one on the certs to make sure they are correct
        # if not, the grant dbg access will fail
        cert_dbg_grants = struct.unpack('<I', cert[4:8])[0]
        dbg_grants = cert_dbg_grants & dbg_grants

        # again, signature is over command + debug_grants + challenge
        to_be_signed = struct.pack('<2I', GRANT_DBG_ACCESS, dbg_grants)
        to_be_signed += challenge

        logger.info("data to sign (command + param + challenge): %s",
                    binascii.hexlify(to_be_signed))

        signature = self.dbg_info.sign(to_be_signed)

        input_data = bytearray(struct.pack('<I', dbg_grants))
        input_data.extend(cert)
        input_data.extend(struct.pack('<I', len(signature)))
        input_data.extend(signature)

        self.challenge_cmd(GRANT_DBG_ACCESS, input_data, 0.1)

        # return the obtained dbg_grants in natural order
        current_dbg_grants = self.get_status()[SBP_STATUS_STR[-1]]
        return current_dbg_grants



WORD_SIZE = 4
SIGNING_INFO_SIZE = 2048
AUTH_HEADER_SIZE = 76
IMG_HEADER_SIZE = 2 * SIGNING_INFO_SIZE + AUTH_HEADER_SIZE
DIR_OF_DIR_SIZE = 3 * WORD_SIZE
DIR_OF_DIR_ADDRS = [0, 0x200]

ENROLLMENT_CERT_MAGIC = 0xB1005C1E
ENROLLMENT_CERT_SIZE = 1548

SERIAL_NR_SIZE = 24
CERT_SERIAL_NR_OFFSET = 16



# impossible name for local directory used as indicator for remote source
INVALID_DIRECTORY = b'\x00'

# special image types that have no real header
HEADERLESS_4CC = [b'nrol', b'hdat', b'sdat']

class NOR_IMAGE(object):
    '''
    Class to encapsulate Read/Write Flash operation on images
    and read on image files '''


    @staticmethod
    def size_version_from_auth_header(header):
        ''' parse header '''
        return struct.unpack('<2I', header[:2 * WORD_SIZE])

    @staticmethod
    def parse_auth_header(header):
        ''' parse header '''
        size, version = NOR_IMAGE.size_version_from_auth_header(header)
        img_type = bytes(header[2*WORD_SIZE:3*WORD_SIZE])
        description = printable_str(header[3*WORD_SIZE + 32:])
        return { 'size': size,
                 'version': version,
                 '4cc' : img_type,
                 'description' : description }

    @staticmethod
    def size_from_img_header(img_header):
        ''' parse image header '''
        return NOR_IMAGE.size_version_from_auth_header(
            img_header[2 * SIGNING_INFO_SIZE:])[0]


    def __init__(self, dbg_chal):
        self.dbg_chal = dbg_chal

    def get_challenge_interface(self):
        return self.dbg_chal

    def directory_addresses(self):
        data = self.dbg_chal.read_flash(DIR_OF_DIR_ADDRS[0],
                                        DIR_OF_DIR_SIZE)
        # address of directories is second and third word
        dirs = struct.unpack('<2I', data[WORD_SIZE:])
        return dirs

    def read_dir_of_dir(self):
        # return the address of the first directory
        return self.directory_addresses()[0]

    def read_dir_ex(self):
        dir_of_dir = self.read_dir_of_dir()

        # empty flash case
        if dir_of_dir > FLASH_SIZE:
            return None, None

        # 256 bytes enough to read the whole directory
        data = self.dbg_chal.read_flash(dir_of_dir,
                                        QSPI_PAGE_SIZE)

        # first word is CRC, 2 and 3rd word are pufr, ignore 4th
        # and then addrA, addrB, fourcc
        nor_dir = {b'pufr': struct.unpack('<2I', data[4:12])}

        start = 16
        while start + 12 < len(data):
            addrs = struct.unpack('<2I', data[start:start+8])
            fourcc = bytes(data[start+8:start+12])
            if fourcc == b'\xFF\xFF\xFF\xFF':
                logger.info("End of directory found!")
                break
            nor_dir[fourcc] = addrs
            start = start + 12
        # return the parse dict and the binary data
        return nor_dir, data[:start+8]


    def read_dir(self):
        return self.read_dir_ex()[0]

    def read_flash(self, addr, size):
        return self.dbg_chal.read_flash(addr, size)

    def write_flash(self, nor_addr, what):
        return self.dbg_chal.write_flash(nor_addr, what)

    def get_auth_header_of_image_at_addr(self, image_addr):
        header_addr = image_addr + 2 * SIGNING_INFO_SIZE
        auth_header = self.read_flash(header_addr, AUTH_HEADER_SIZE)
        return NOR_IMAGE.parse_auth_header(auth_header)

    def get_version_of_image_at_addr(self, image_addr):
        header_info = self.get_auth_header_of_image_at_addr(image_addr)
        if header_info['version'] == 0xffffffff:
            return 0 # convert missing image data to version 0 for easier processing
        return header_info['version']

    def get_address_of_highest_version(self, addresses):
        all_raw_versions = { a : self.get_version_of_image_at_addr(a) for a in addresses}
        # filter out all missing images
        all_versions = { a : v for a, v in all_raw_versions.items() if v != 0 }

        if not all_versions:
            return None, None

        addr_of_max_version = max(all_versions, key=all_versions.get)
        return all_raw_versions, addr_of_max_version


    def read_image(self, addr):
        # read the header
        start_time = datetime.datetime.now()
        img_header = self.read_flash(addr, IMG_HEADER_SIZE)

        # extract size
        image_size = NOR_IMAGE.size_from_img_header(img_header)

        if image_size == 0xFFFFFFFF:
            return None # "No Image at that location"

        print("****** Image size is %d" % image_size)
        image = self.read_flash(addr + IMG_HEADER_SIZE, image_size)

        duration = (datetime.datetime.now() - start_time).total_seconds()
        total_len = len(img_header)+len(image)
        if duration > 0:
            logger.info("Read %d bytes in %g seconds (%g bytes/second)",
                        total_len, duration, total_len/duration)
        else:
            logger.info("Read %d bytes", total_len)

        return img_header+image


    # special image: nrol
    def read_enrollment_cert(self, nor_dir):
        ''' read the enrollment certificate, returns None if not found '''
        if 'nrol' not in nor_dir:
            return None # no data

        packed_magic = struct.pack('<I', ENROLLMENT_CERT_MAGIC)

        enroll_cert_addresses = nor_dir[b'nrol']

        enroll_cert_addr = enroll_cert_addresses[0]
        magic = self.read_flash(enroll_cert_addr, WORD_SIZE)

        if magic != packed_magic:
            enroll_cert_addr = enroll_cert_addresses[1]
            magic = self.read_flash(enroll_cert_addr, WORD_SIZE)

        if magic != packed_magic:
            return None # no data

        rest = self.read_flash(enroll_cert_addr + WORD_SIZE,
                               ENROLLMENT_CERT_SIZE - WORD_SIZE)
        return magic+rest


    # special image: hdat
    def read_host_data(self, nor_dir):
        ''' read the host data, return None if not found '''
        # try directory first
        if 'hdat' in nor_dir:
            addr = nor_dir[b'hdat'][0]
        else:
            # use the last sector
            logger.info("No entry for hdat in directory: reading last sector")
            addr = FLASH_SIZE - QSPI_SECTOR_SIZE

        # the host data is 4 bytes and a list of nul terminated strings
        # the last string has length 0
        host_data = bytearray()
        search_start = WORD_SIZE # do not check the CRC
        end_addr = addr + QSPI_SECTOR_SIZE
        while addr < end_addr:
            page = self.read_flash(addr, QSPI_PAGE_SIZE)

            # check for empty flash (i.e. all are 0xFF)
            if search_start > 0:
                unique = set(page)
                if len(unique) == 1 and min(unique) == 0xFF:
                    return None

            # search for end of data
            found = page.find(b'\x00\x00', search_start)
            if found >= 0:
                host_data.extend(page[:found+2])
                return host_data

            # did not find the end: iterate
            host_data.extend(page)
            search_start = 0 # no longer need omit the CRC in our search
            addr += QSPI_PAGE_SIZE

        # read a whole SECTOR without finding the end...GIGO
        return None


    def erase_sector_at_addr(self, addr):
        return self.dbg_chal.erase_flash_sector(addr)


    def erase_at_addr_for_size(self, addr, size):
        ''' erase as many sectors as necessary to write size at addr '''
        erase_addr = addr
        while erase_addr < addr + size:
            self.erase_sector_at_addr(erase_addr)
            erase_addr += QSPI_SECTOR_SIZE

    def check_img_header(self, img):
        # verify that the start certificate on this image is valid for this chip
        # if not replace it -- ASSUMES THAT SAME KEYS ARE USED FOR BOTH START CERT
        serial_nr = self.dbg_chal.get_serial_number()

        sn_offset = SIGNING_INFO_SIZE + CERT_SERIAL_NR_OFFSET
        cert_serial_nr = img[sn_offset:
                             sn_offset+SERIAL_NR_SIZE]
        cert_serial_mask = img[sn_offset+SERIAL_NR_SIZE:
                               sn_offset+2*SERIAL_NR_SIZE]
        # use the mask on both serial numbers and they must be equal
        match = True
        for cs, scs, scm in zip(serial_nr, cert_serial_nr, cert_serial_mask):
            if (cs & scm) != (scs & scm):
                match = False
                break
        if match:
            return img

        new_start_cert = self.dbg_chal.get_start_cert()
        new_img = img[:SIGNING_INFO_SIZE]
        new_img.extend(new_start_cert)
        new_img.extend(img[SIGNING_INFO_SIZE + CERT_SIZE:])
        return new_img

    def prepare_src_image(self, img_type, src_image, src_image_info):
        ''' returns img '''
        src_file = src_image_info.get('override')
        if src_file:
            img = bytearray(open(src_file, 'rb').read())
        else:
            img = src_image.read_image(src_image_info['addr'])
        if img_type != b'pufr':
            return img

        return self.check_img_header(img)


    def update_image(self, nor_addr, img, sorted_addresses, resume_at=0):

        # some size checks: internal consistency
        logical_size = NOR_IMAGE.size_from_img_header(img)
        image_size = logical_size + IMG_HEADER_SIZE

        print("Size of image: %d: %d bytes needed" %  (logical_size, image_size))
        # enough room on directory?
        max_size = max_available_size(nor_addr, sorted_addresses)
        if image_size > max_size:
            raise NorImageError("Not enough space %d required, %d available" %
                                (image_size, max_size))

        # if writing from beginning, erase all sectors;
        # otherwise assume this was done before
        if resume_at == 0:
            # erase all the sectors before writing; USE image_size not nor_size
            # which would erase the whole flash after nor_addr if 0xFFFF_FFFF
            self.erase_at_addr_for_size(nor_addr, image_size)

        self.write_flash(nor_addr+resume_at, img[resume_at:])


def unlock_chip(challenge_interface, req_dbg_grants):
    ''' unlocks the chip: figure out if the start certificate needs to get in
    and call the appropriate functions '''

    # see if key 2 is known, then no need to inject the start certificate
    inject = False
    try:
        challenge_interface.get_key(2)
    except ChallengeError as e:
        if e.errno == ERR_INVALID_PARAM:
            logger.info("Key 2 unknown: start certificate needed")
            inject = True
        else:
            raise e

    if inject:
        try:
            challenge_interface.inject_cert(req_dbg_grants)
        except ChallengeError as e:
            logger.info("Start certificate injection failed: continuing anyway")


    dbg_grants = challenge_interface.get_dbg_access(req_dbg_grants)
    print("Chip unlocked: Debug Grants: 0x%08x" % dbg_grants)


def get_addr_of_image(directory, image_type, b_image):
    addrs = directory.get(image_type, None)
    if addrs is None:
        return None

    if b_image:
        return addrs[1]

    return addrs[0]


def write_directory_to_flash(nor_image, directory, nor_addr):
    nor_image.erase_sector_at_addr(nor_addr)
    nor_image.write_flash(nor_addr, directory)


def show_flash_dir(nor_image):
    nor_dir = nor_image.read_dir()
    print("Directory on flash:")
    for img_type, addresses in sorted(nor_dir.items(),
                                      key=lambda x: min(x[1])):
        print("%s: (%10d (0x%08x), %10d (0x%08x))" %
              (bytes2str(img_type), addresses[0], addresses[0],
               addresses[1], addresses[1]))
    return nor_dir

def show_flash_images(nor_image):
    nor_dir = nor_image.read_dir()

    for img_type, addresses in sorted(nor_dir.items(),
                                      key=lambda x: min(x[1])):
        for addr in addresses:
            logger.info("Retrieving header of image %s at 0x%08x",
                        img_type, addr)
            img_info = nor_image.get_auth_header_of_image_at_addr(addr)
            print("%s: %8d (0x%08x)" % (bytes2str(img_type), addr, addr),
                  end='')
            if img_info['size'] == 0xFFFFFFFF:
                print("")
            else:
                print(" size = %6d version = %6d (%s)" %
                      (img_info['size'],
                       img_info['version'],
                       img_info['description']))


def get_image_data(nor_image, img_type, b_image, nor_dir):

    if nor_dir is None:
        nor_dir = nor_image.read_dir()

    if img_type == b'nrol':
        data = nor_image.read_enrollment_cert(nor_dir)
    elif img_type == b'hdat':
        data = nor_image.read_host_data(nor_dir)
    else:
        nor_addr = get_addr_of_image(nor_dir, img_type, b_image)
        if nor_addr is None:
            print("No such image type '%s' on Flash" % bytes2str(img_type))
            return None
        data = nor_image.read_image(nor_addr)
    return data


def do_image_read(nor_image, img_type, b_image, output_f, nor_dir):

    data = get_image_data(nor_image, img_type, b_image, nor_dir)

    if not data:
        return None

    if output_f is None:
        output_f = "".join([bytes2str(img_type),
                            "B" if b_image else "A",
                            ".bin"])
        script_dir = os.path.dirname(os.path.realpath(__file__))
        output_f = os.path.join(script_dir, output_f)

    open(output_f, 'wb').write(data)
    return output_f


def max_available_size(target_addr, sorted_addresses):

    addr_index = sorted_addresses.index(target_addr)
    # while this is not the last address
    while addr_index < len(sorted_addresses) - 1:
        addr_index += 1
        next_addr = sorted_addresses[addr_index]
        # check for no duplicate
        if next_addr != target_addr:
            return next_addr - target_addr

    # this was the last address. Return all remaining space except the last
    # sector which may have been used for hdat on all systems.
    return FLASH_SIZE - (QSPI_SECTOR_SIZE + target_addr)


def get_src_images(src_image, override_file_names):
    '''
    return a dictionary with the address and version of the image with
    the highest version. images without version (nrol, hdat) are not in
    the dictionary
    '''

    # images on source NOR_IMAGE
    src_dir = src_image.read_dir()

    # remove the special image types: nrol and hdat, added at runtime
    for img_type in HEADERLESS_4CC:
        src_dir.pop(img_type, None)

    src_images = {}
    for img_type, addresses in src_dir.items():
        versions, addr_of_max_version = src_image.get_address_of_highest_version(addresses)
        if addr_of_max_version:
            versions_str = ''.join(["0x%08x: %d " %
                                    (a, v) for a, v in versions.items()])
            print("%s : 0x%08x  (versions: %s)" %
                  (bytes2str(img_type), addr_of_max_version, versions_str))
            src_images[img_type] = { 'addr' : addr_of_max_version,
                                     'version' : versions[addr_of_max_version],
                                     'override': None }

    # return if no overrides
    if not override_file_names:
        return src_images

    # sort all addresses to figure out the available space for an override
    sorted_addresses = sorted([addr for addresses in src_dir.values()
                               for addr in addresses])

    # now the overrides
    for override_file_name in override_file_names:
        # read the authenticated header
        with open(override_file_name, 'rb') as f:
            f.seek(2 * SIGNING_INFO_SIZE)
            auth_header = f.read(AUTH_HEADER_SIZE)
            header_info = NOR_IMAGE.parse_auth_header(auth_header)
            img_type = header_info['4cc']

            # if img_type present on NOR image, override version and source
            # keep the addr since this is used for the full rewrite
            src_info = src_images.get(img_type, None)
            if src_info:
                # first, some size checks
                # advertized size is correct
                f.seek(0, os.SEEK_END)
                real_size = f.tell()
                if real_size != header_info['size'] + IMG_HEADER_SIZE:
                    raise NorImageError(
                        "%s: Inconsistent file size %d in header but %d extent" %
                        (override_file_name,
                         header_info['size'] + IMG_HEADER_SIZE,
                         real_size))

                # check it fits on the directory
                max_size = max_available_size(src_info['addr'], sorted_addresses)
                if max_size < real_size:
                    raise NorImageError(
                        "%s: image is too big (%d) for the available space (%d)" %
                        (override_file_name, real_size, max_size))

                src_info['override'] = override_file_name
                src_info['version'] = header_info['version']

    return src_images


def do_image_update(nor_image, src_image, sorted_addresses,
                    img_type, target_address, target_version,
                    src_info, dry_run):

    if src_info['version'] <= target_version:
        print("%s : source (%d) is same as or older than target (%d)" %
              (bytes2str(img_type), src_info['version'], target_version))
        return

    src_file = src_info['override']
    if src_file:
        print_source = src_file
    else:
        print_source = "0x%08x" % src_info['addr']

    print("%s : Updating at 0x%08x (version = %d) with %s (version = %d)" %
          (bytes2str(img_type), target_address, target_version,
           print_source, src_info['version']) )

    if not dry_run:
        # read the newer image on source
        img = nor_image.prepare_src_image(img_type, src_image, src_info)
        nor_image.update_image(target_address, img, sorted_addresses)

        print("%s : image at %d was updated to version %d!" %
              (bytes2str(img_type), target_address, src_info['version']))



def do_full_update(nor_image, src_image, override_files, dry_run, install_missing):
    st = datetime.datetime.now()

    # figure out the address on file of the newer source imag
    print("Sources images:")
    src_images = get_src_images(src_image, override_files)

    print("Target images:")
    nor_dir = nor_image.read_dir()
    sorted_addresses = sorted([addr for addresses in nor_dir.values()
                               for addr in addresses])
    for img_type, src_info in src_images.items():
        img_type_str = bytes2str(img_type)
        dest_addresses = nor_dir.get(img_type)
        if dest_addresses:
            versions, target_address = nor_image.get_address_of_highest_version(dest_addresses)
            if target_address is None:
                print("%s: no current image found for this type on Flash "\
                      "=> no safe update possible" %
                      img_type_str)
            else:
                versions_str = ''.join(["0x%08x: %s " %
                                        (a, v if v else 'None')
                                        for a,v in versions.items()])
                print("%s : 0x%08x  (versions: %s)" %
                      (img_type_str, target_address, versions_str))
                do_image_update(nor_image, src_image, sorted_addresses,
                                img_type, target_address,
                                versions[target_address],
                                src_info, dry_run)
            if versions and install_missing:
                for address, version in versions.items():
                    if version == 0:
                        print("Install %s missing at location 0x%08x" %
                              (img_type_str, address))
                        do_image_update(nor_image, src_image, sorted_addresses,
                                img_type, address, version,
                                src_info, dry_run)

        else:
            print("%s: image not found on Flash => cannot update" % img_type_str)
            print("Consider using the full-rewrite option")

    duration = (datetime.datetime.now() - st).total_seconds()
    print("Completed in %dmn %ds" % (duration / 60, duration % 60))


def same_image_addresses(img_type, dir1, dir2):
    return dir1.get(img_type, [0,0]) == dir2.get(img_type, [0,0])


def do_full_rewrite(nor_image, src_image, override_files, nor_dir):
    ''' rewrite the nor flash: preserves only the enrollment certificate and host data '''

    st = datetime.datetime.now()

    #### gather all the pieces from the source image
    # read dir of dirs (at address 0)
    dir_of_dirs = src_image.read_flash(DIR_OF_DIR_ADDRS[0], DIR_OF_DIR_SIZE)
    dir_addresses = struct.unpack('<2I', dir_of_dirs[WORD_SIZE:])

    # read directory from source
    src_dir, src_dir_bin = src_image.read_dir_ex()

    ##
    # nrol and hdat need to be preserved.
    # if their current locations match the new ones do not do anything: safer and faster
    # otherwise save them.
    #
    if nor_dir is None:
        nor_dir = nor_image.read_dir()

    need_to_move = {}
    if nor_dir:
        for img_type in HEADERLESS_4CC:
            need_to_move[img_type] = not same_image_addresses(img_type,
                                                              nor_dir,
                                                              src_dir)
    # read the enrollment certificate from flash
    if need_to_move.get(b'nrol'):
        enrollment_cert = nor_image.read_enrollment_cert(nor_dir)

    # read the host data from flash
    if need_to_move.get(b'hdat'):
        host_data = nor_image.read_host_data(nor_dir)

    # identify sources: get_srcs_images() will give a set of good images
    # with their addresses
    src_images = get_src_images(src_image, override_files)

    for img_type, src_info in src_images.items():

        print("writing %s image (version = %d) at 0x%08x" %
              (bytes2str(img_type), src_info['version'], src_info['addr']))
        # read the source image
        img = nor_image.prepare_src_image(img_type, src_image, src_info)
        new_image_size = NOR_IMAGE.size_from_img_header(img)

        # erase the sectors at both addresses -- use set in case addresses are the same
        for addr in set(src_dir[img_type]):
            nor_image.erase_at_addr_for_size(addr,
                                             new_image_size + IMG_HEADER_SIZE)
        # write the image at trgt_addr on NOR
        nor_image.write_flash(src_info['addr'], img)

    # erase/write enrollment certificate
    if need_to_move.get(b'nrol'):
        for addr in set(src_dir[b'nrol']):
            nor_image.erase_at_addr_for_size(addr, ENROLLMENT_CERT_SIZE)
            if enrollment_cert:
                nor_image.write_flash(addr, enrollment_cert)

    # erase/write host data: hdat should be in recent image but be prepared...
    if need_to_move.get(b'hdat'):
        addresses = src_dir.get(b'hdat', [FLASH_SIZE - QSPI_SECTOR_SIZE])
        addr = addresses[0] # use only one location
        nor_image.erase_at_addr_for_size(addr, 1) # erase only one sector
        if host_data:
            nor_image.write_flash(addr, host_data)

    # finally write the directories
    for addr in dir_addresses:
        nor_image.erase_at_addr_for_size(addr, len(src_dir_bin))
        nor_image.write_flash(addr, src_dir_bin)

    # and the directory of directories (hard coded)
    nor_image.erase_at_addr_for_size(0, max(DIR_OF_DIR_ADDRS) + len(dir_of_dirs))
    for addr in DIR_OF_DIR_ADDRS:
        nor_image.write_flash(addr, dir_of_dirs)

    duration = (datetime.datetime.now() - st).total_seconds()
    print("Completed in %dmn %ds" % (duration / 60, duration % 60))


def prepare_recovery(challenge_interface):
    ''' prepare for recovery operation:
    1.make sure current grants allow read/write to flash
    2.call prepare_qspi if in ROM that needs it
    '''

    # get status
    decoded_status = challenge_interface.get_status()

    # debug grants check
    debug_grants = decoded_status[SBP_STATUS_STR[-1]]
    READ_WRITE_GRANTS = (1 << 16) | (1 << 17)
    need_debug_access = ((debug_grants & READ_WRITE_GRANTS) != READ_WRITE_GRANTS)

    if need_debug_access:
        print("Debugging access required")
        unlock_chip(challenge_interface, READ_WRITE_GRANTS)

    # call prepare_qspi if needed -- rom_6843 (prepare_qspi not needed on bld_3098)
    in_rom = decoded_status[VERSION_BYTES_KEY].startswith('rom_')
    if in_rom:
        print("In %s: prepare QSPI" % decoded_status[VERSION_BYTES_KEY])
        challenge_interface.prepare_qspi()



def do_recovery(nor_image, args, local_dir=None):
    ''' recover the system from a set of images that can be remote or
    local; if debug grants are needed, can also use remote to get
    the necessary files '''

    NOR_IMAGE_SRC = 'qspi_image_hw.bin'
    NOR_IMAGE_SRC_GZ = 'qspi_image_hw.bin.gz'
    CACHED_NOR_IMAGE_SRC = 'last_qspi_image_hw.bin'

    # select the proper eeproms
    # (FS1600 only for the moment)
    try:
        fs1600_rev = get_fs1600_rev()
        eeprom_file = 'eeprom_f1_fs1600_rev%d_%d.bin' % (fs1600_rev, args.chip)
    except:
        eeprom_file = None

    # get full path to the 2 sources files: Nor Image and eeprom
    if local_dir:
        eeprom_path = os.path.join(local_dir,
                                   eeprom_file) if eeprom_file else None
        src_image_path = os.path.join(local_dir, NOR_IMAGE_SRC)
    else:
        eeprom_path = get_remote_file(args.port,
                                      eeprom_file) if eeprom_file else None
        # if we can use the cache, and the file is there,
        # use it instead of downloading
        script_dir = os.path.dirname(os.path.realpath(__file__))
        cached_file = os.path.join(script_dir, CACHED_NOR_IMAGE_SRC)

        if args.use_cache and os.path.isfile(cached_file):
            print("Using cached file %s" % cached_file)
            src_image_path = cached_file
        else:
            # otherwise just download to canonical_path
            print("Downloading file to %s" % cached_file)
            src_image_path = get_remote_file(args.port,
                                             NOR_IMAGE_SRC_GZ,
                                             cached_file)
            decompress_file(src_image_path)

    try:
        challenge_interface = nor_image.get_challenge_interface()
        prepare_recovery(challenge_interface)

        src_image = NOR_IMAGE(DBG_File(src_image_path))
        # now just have to do the full rewrite

        nor_dir = None
        # try installing the current one if no replacement eepr
        if eeprom_path is None:
            nor_dir = nor_image.read_dir()
            eeprom_path = do_image_read(nor_image, b'eepr', False,
                                        None, nor_dir)
            if eeprom_path is None:
                eeprom_path = do_image_read(nor_image, b'eepr', True,
                                            None, nor_dir)

        override_files = [eeprom_path] if eeprom_path else []
        do_full_rewrite(nor_image, src_image, override_files, nor_dir)

    finally:

        # clean up the tmp files if remotely retrieved
        if local_dir is None and eeprom_file and eeprom_path:
            os.remove(eeprom_path)



def execute_challenge_command(challenge_interface, args):

    # Simple challenge interface commands
    if args.status:
        status_dict = challenge_interface.get_status()
        challenge_interface.print_decoded_status(status_dict)
        return

    if args.otp:
        data = challenge_interface.read_otp(OTP_CM)
        print("OTP:\n%s" % data)
        return

    if args.otp_full:
        data = challenge_interface.read_otp(OTP_FULL)
        print("OTP:\n%s" % data)
        return

    if args.serial_number:
        data = challenge_interface.get_serial_number()
        print("Serial Number:")
        print(hex_str(data))
        return

    if args.fungible_key:
        try:
            data = challenge_interface.get_key(int(args.fungible_key))
        except ChallengeError as e:
            if e.errno == ERR_INVALID_PARAM:
                print("No Fungible key %s found" % args.fungible_key)
                return
            raise e

        print("Fungible Key %s:" % args.fungible_key)
        print(hex_str(data))
        return

    if args.customer_key:
        try:
            data = challenge_interface.get_key(0, customer=True)
        except ChallengeError as e:
            if e.errno == ERR_INVALID_PARAM:
                print("No Fungible key %s found" % args.fungible_key)
                return
            raise e
        print("Customer Key:")
        print(hex_str(data))
        return

    if args.unlock:
        unlock_chip(challenge_interface, int(args.unlock,0))
        return

    if args.prepare_qspi:
        challenge_interface.prepare_qspi()
        return

    # Next options are manipulating the Image on Flash:

    nor_image = NOR_IMAGE(challenge_interface)

    if args.recovery is not None:
        # this option has an optional argument: local directory to use
        if args.recovery == INVALID_DIRECTORY:
            if args.port is None:
                print("No local directory specified for recovery: port required")
                return
            do_recovery(nor_image, args, None)
        else:
            do_recovery(nor_image, args, args.recovery)
        return

    if args.full_rewrite is not None:
        src_image = NOR_IMAGE(DBG_File(args.full_rewrite))
        do_full_rewrite(nor_image, src_image, args.override, None)
        return

    if args.full_update is not None:
        src_image = NOR_IMAGE(DBG_File(args.full_update))
        do_full_update(nor_image, src_image, args.override, dry_run=False,
                        install_missing=args.install_missing)
        return

    if args.explain_full_update is not None:
        src_image = NOR_IMAGE(DBG_File(args.explain_full_update))
        do_full_update(nor_image, src_image, args.override, dry_run=True,
                       install_missing=args.install_missing)
        return

    if args.images:
        show_flash_images(nor_image)
        return

    if args.read_directory:
        show_flash_dir(nor_image)
        return

    if args.update is not None:
        if args.update[4] == ":":
            # extract the file from this NOR Image file
            src_image = NOR_IMAGE(DBG_File(args.update[5:]))
            new_image = get_image_data(src_image,
                                       str2bytes(args.update[:4]),
                                       False,
                                       None)
        else:
            new_image = bytearray(open(args.update, 'rb').read())

        if args.address:
            # unconditional write
            nor_addr = int(args.address,0)
            nor_image.write_flash(nor_addr, new_image)
            return

        fourcc_offset = 2 * SIGNING_INFO_SIZE + 8
        fourcc = bytes(new_image[fourcc_offset:fourcc_offset+WORD_SIZE])
        print("Image type %s" % bytes2str(fourcc))
        nor_dir = show_flash_dir(nor_image)
        nor_addr = get_addr_of_image(nor_dir, fourcc, args.BImage)
        if nor_addr is None:
            print("No such image type '%s' on Flash" % bytes2str(fourcc))
            return

        sorted_addresses = sorted([addr for addresses in nor_dir.values()
                                   for addr in addresses])
        nor_image.update_image(nor_addr, new_image, sorted_addresses,
                               resume_at=int(args.resume,0))
        return

    if args.read_header is not None:
        if args.read_header in HEADERLESS_4CC:
            print("Images of type %s do not have any header" %
                  bytes2str(args.read_header))
            return

        nor_dir = show_flash_dir(nor_image)
        nor_addr = get_addr_of_image(nor_dir, args.read_header, args.BImage)
        if nor_addr is None:
            print("No such image type '%s' on Flash" %
                  bytes2str(args.read_header))
            return

        header_info = nor_image.get_auth_header_of_image_at_addr(nor_addr)
        print("%s version = %d size = %d (%s)" % (
            header_info['4cc'],
            header_info['version'],
            header_info['size'],
            header_info['description']))

        return

    if args.read is not None:
        out_file = do_image_read(nor_image, args.read, args.BImage,
                                 args.output, None)
        if out_file:
            print("Image written to %s" % out_file)
        else:
            print("No image %s at %s location" %
                 (bytes2str(args.read), "B" if args.BImage else "A"))
        return

    if args.erase_sector is not None:
        nor_image.erase_sector_at_addr(int(args.erase_sector, 0))
        return

    if args.raw_read is not None:
        nor_addr = int(args.raw_read, 0)
        num_bytes = int(args.read_size, 0)
        bytes_read = 0
        if args.output is None:
            args.output = "raw_read_%d@0x%08x.bin" % (num_bytes, nor_addr)
        with open(args.output, 'wb') as f:
            while bytes_read < num_bytes:
                cnt = min(64*1024, num_bytes - bytes_read)
                print("read %d bytes from 0x%08x" % (cnt, nor_addr + bytes_read))
                data = nor_image.read_flash(nor_addr + bytes_read, cnt)
                f.write(data)
                bytes_read += cnt
        return


def main():

    log_levels = { logging.getLevelName(a) : a for a in
                   [logging.DEBUG, logging.INFO, logging.WARN, logging.ERROR] }

    parser = argparse.ArgumentParser(
        description="Execute commands using the Challenge Interface via I2C")

    spec_grp = parser.add_argument_group("General",
                                         "Can be used with all the options")
    spec_grp.add_argument("--chip", type=int, default=0, choices=[0,1],
                          help="chip instance number (default = 0)")

    spec_grp.add_argument("--i2c-dev", type=str,
                          help="number or path to i2c device")
    spec_grp.add_argument("--log", choices=log_levels.keys(),
                          default="ERROR",
                          help="set log level")

    # Simple commands
    diag_grp = parser.add_argument_group("Simple Diagnostics",
                                         "Simple diagnostics commands")
    diag_grp.add_argument("--status", action="store_true",
                          help="Display esecure device status")
    diag_grp.add_argument("--otp", action="store_true",
                          help="Display OTP content (might require unlocking in ROM)depending on the chip)")
    diag_grp.add_argument("--otp-full", action="store_true",
                          help="Display Full OTP content (might require unlocking in ROM)depending on the chip)")
    diag_grp.add_argument("--serial-number", action="store_true",
                          help="Display Serial Number Information")
    diag_grp.add_argument("--fungible-key", metavar="KEY_INDEX",
                          help="Display the Fungible public key")
    diag_grp.add_argument("--customer-key", action="store_true",
                          help="Display the customer public key if present")


    # Debug grants
    unlock_grp = parser.add_argument_group("Unlock Chip",
                                           "Unlock the chip for modifications")
    unlock_grp.add_argument("--unlock", nargs='?', const="0x030000",
                            action="store", metavar="OPTIONAL_DEBUG_GRANTS",
                            help="unlock the chip on secure systems")
    unlock_grp.add_argument("--cert",
                            metavar="DEVELOPER_CERTIFICATE",
                            help="developer certificate (required to unlock)")
    unlock_grp.add_argument("--key",
                            metavar="DEVELOPER_KEY_PEM_FILE",
                            help="developer key (required for unlocking)")
    unlock_grp.add_argument("--start-cert",
                            metavar="START_CERTIFICATE",
                            help="start certificate "\
                            "(required for unlocking when in the ROM) or "\
                            "when serial number of chip does not match "\
                            "the start certificate in the source image")
    unlock_grp.add_argument("--port",
                            help="HTTP localhost port to use for unlock "\
                            "and remote recovery operations")

    # Flash manipulation
    flash_grp = parser.add_argument_group("Flash Read/Write",
                                          "Read/Write the flash")
    flash_grp.add_argument("--prepare-qspi", action="store_true",
                           help="configure flash for QSPI")
    flash_grp.add_argument("--read-directory", action="store_true",
                           help="read and print the directory on the Flash")
    flash_grp.add_argument("--images", action="store_true",
                           help="print information about all images on the Flash")
    flash_grp.add_argument("--read", metavar="FOUR_CC", type=str2bytes,
                           help="read the image "\
                           "with the fourcc type specified from the Flash")
    flash_grp.add_argument("--read-header", metavar="FOUR_CC", type=str2bytes,
                           help="read the header of the image "\
                           "with the fourcc type specified from the Flash")
    flash_grp.add_argument("--raw-read", metavar="ADDRESS",
                           help="read 256 bytes at the adress specified")
    flash_grp.add_argument("--read-size", metavar="NUM_BYTES", default="256",
                           help="specify the number of bytes to raw-read")
    flash_grp.add_argument("--output", metavar="FILE",
                           help="output file for read operations "\
                           "(default [<4cc>[A|B]|raw_read_<size>@<address>].bin)")
    flash_grp.add_argument("--erase-sector", metavar="ADDRESS",
                           help="erase the sector starting at address")
    flash_grp.add_argument("--update", metavar="IMAGE_FILE|FOUR_CC:NOR_IMAGE_FILE",
                           help="update the image on flash with the file specified (IMAGE_FILE) "\
                           "or the subimage from the NOR file image (FOUR_CC:NOR_IMAGE_FILE)")
    flash_grp.add_argument("--BImage", action="store_true",
                           help="perform the operation on the B copy "\
                           "(read commands, update command)")
    flash_grp.add_argument("--resume", default="0",
                           help="resume writing at the offset specified "\
                           "(update command)")
    flash_grp.add_argument("--address",
                           help="address to use for unconditional update")
    flash_grp.add_argument("--nor-file", metavar="NOR_IMAGE_FILE",
                           help="do not use the flash, "\
                           "use this file instead for the operation (testing)")
    flash_grp.add_argument("--explain-full-update", metavar="NOR_IMAGE_FILE",
                           help="explain how to use specified NOR image to replace "\
                           "most recent/add images on the Flash")
    flash_grp.add_argument("--full-update", metavar="NOR_IMAGE_FILE",
                           help="use specified NOR image to replace "\
                           "most recent/add images on the Flash")
    flash_grp.add_argument("--full-rewrite", metavar="NOR_IMAGE_FILE",
                           help="use specified NOR image to completely rewrite "\
                           "a set of images on the Flash. Only a single copy of the "\
                           "images will be updated, the other will be erased")
    flash_grp.add_argument("--override", metavar="IMAGE_FILE", action="append",
                           help="use specified Image Files as source "
                           "instead of the ones on the NOR IMAGE FILE "\
                           "(full-rewrite,full-update)")
    flash_grp.add_argument("--recovery", nargs='?', const=INVALID_DIRECTORY,
                           metavar='LOCAL_DIRECTORY',
                           help="recover the system automatically")
    flash_grp.add_argument("--use-cache", action="store_true",
                           help="Use the last downloaded NOR Image file "\
                           "for remote recovery")
    flash_grp.add_argument("--no-install-missing", dest='install_missing',
                           action="store_false",
                           help="Do not fill in missing firmware locations"\
                           " during full update")

    args = parser.parse_args()

    logger.setLevel(log_levels[args.log])

    if args.nor_file:
        challenge_interface = DBG_File(args.nor_file)
    else:
        challenge_interface = DBG_Chal(chip_inst=int(args.chip),
                                       port=args.port,
                                       cert_file=args.cert,
                                       key_file=args.key,
                                       start_cert_file=args.start_cert,
                                       i2c_dev=args.i2c_dev)

    # catch the exception here so the custom ones look better
    try:
        execute_challenge_command( challenge_interface, args)
    except:
        traceback_print_exc()

if __name__ == "__main__":
    main()
