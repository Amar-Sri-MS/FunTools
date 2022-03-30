import sys
import os
sys.path.append("../software/devtools/firmware")
#import utils
from .sbp_structs import *

from .dututils import dut
from .isbp import s1i2c
import binascii
import json
from array import array
import argparse
import struct
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding

import socket

class CMD(object):
    GET_SERIAL_NUMBER = 0xFE000000
    GET_OTP = 0xFE0B0000
    GET_STATUS = 0xFE010000
    INJECT_CERTIFICATE = 0xFE0A0000

    GET_CHALLANGE = 0xFD000000
    GRANT_DBG_ACCESS = 0xFD010000

    FLASH_ERASE_SECTION = 0xFC000000
    FLASH_WRITE_BUFF_SIZE =  0xFC010000 | 0x00001000
    FLASH_WRITE_ADD_DATA =   0xFC010000 | 0x00002000
    FLASH_WRITE_CLEAR_DATA = 0xFC010000 | 0x00003000
    FLASH_WRITE_FLUSH_DATA = 0xFC010000 | 0x00004000

    FLASH_READ_BUFF_SIZE =   0xFC020000 | 0x00001000
    FLASH_READ_DATA =        0xFC020000 | 0x00002000  # FLASH_READ | CMD_BUFFER_DATA

    QSPI_PAGE_SIZE = 0x100
    QSPI_SECTOR_SIZE = 0x10000

CMD_STATUS_CODE_STR = {
    0 : 'Okay',
    1 : 'Invalid command',
    2 : 'Authorization error',
    3 : 'Invalid signature (if command is signature verification)',
    4 : 'Bus error (if DMA is used)',
    5 : 'Reserved',
    6 : 'Crypto error',
    7 : 'Invalid parameter',
}

SBP_STATUS_STR = [
    "Status at last tamper",
    "Timestamp of last tamper",
    "Raw tamper status",
    "Current Time",
    "Boot Status",
    "eSecure Firmware Version",
    "Host Firmware Version",
    "Debug Grants"]

class CONST(object):
    DBG_GRANTS = 0x000F00F0
    IP_ADDR = '10.1.20.69'
    CONN_MODE = 'i2c'
    I2C_DEV_ID = 2238646800
    PRIVATE_KEY_PASSWORD = None

class dbgi2c(s1i2c):
    page_size = None
    wr_buf_size = None

    def cmd_status_code_str(self, frame):
        status, length_in_header, pktlen = frame[1], frame[3], len(frame)
        #print status, hex(status), length_in_header, hex(length_in_header), pktlen, hex(pktlen)
        if pktlen < 4:
            return "Insufficient bytes:{} in return header".format(pktlen)
        if length_in_header != pktlen:
            return "length_in_header:{} mismatch with frame length:{}".format(length_in_header, pktlen)
        if status not in list(CMD_STATUS_CODE_STR.keys()):
            return "return code: status={} Undefined !!".format(status)
        else:
            return "dbg status: {}".format(CMD_STATUS_CODE_STR[status])

    def challenge_disconnect(self):
        (status) = self.csr_challenge_disconnect()
        if status == True:
            status, msg = True, "Dbg disconnect command success!"
        else:
            status, msg = False, "Dbg disconnect command error!"
        return (status, msg)

    def cmd_status_ok(self, header_bytes):
        return ((header_bytes >= 4) and (header_bytes[1] == 0))

    def decode_response_data(self, cmd, data):
        RDATA = arraypack(data)
        print("#", "+"*80)
        print("# Response for command : %s (%s)" % (hex(cmd), commandEnum[cmd]))
        #hexdump(RDATA)
        print("#", "="*80)
        if cmd in list(DBG_CMDRESP.keys()):
            DBG_CMDRESP[cmd](RDATA).show2()
        else:
            HEADER(RDATA).show2() 
        print('#', "-"*80)
        return True #data

    def challenge_cmd(self, cmd, data=None):
        (status, rdata) = self.i2c_dbg_chal_cmd_safe(cmd, data)
        if status == True:
            if self.cmd_status_ok(rdata):
                self.decode_response_data(cmd, rdata)
                return (True, rdata[4:])  # strip the header
            else:
                HEADER(arraypack(rdata)).show2()
                return (False, self.cmd_status_code_str(rdata))
        else:
            err_msg = "Dbg chal command 0x{0} error! {1}".format(hex(cmd), rdata)
            print (err_msg)
            return (False, err_msg)

    def decode_status_bytes(self, data):
        print ('STATUS:')
        print ('\tRaw bytes:')
        byte_str = ''
        for i in range(len(data)):
            byte_str += ' 0x%02x' % (data[i])
            if (i+1) % 8 == 0 or (i+1) == len(data):
                print('\t  %04d: %s' % (i & ~0x7, byte_str))
                byte_str = ''
        i = 0
        status_size = len(data)
        status_decoded = dict()
        while i < status_size:
            status_str_idx = i/4
            if status_str_idx < len(SBP_STATUS_STR):
                status_value = socket.htonl(int(binascii.hexlify(array('B', data[i:i+4])), 16))
                print('\t{0}: {1}'.format(SBP_STATUS_STR[status_str_idx], \
                        hex(status_value).rstrip("L")))
                if SBP_STATUS_STR[status_str_idx] == 'Boot Status':
                    print('\t\t{0}: {1}'.format('BootStep',
                                                hex(status_value & 0xff).rstrip("L")))
                    print('\t\t{0}: {1}'.format('eSecureUpgradeFlag',
                                                hex((status_value >> 8) & 0x1).rstrip("L")))
                    print('\t\t{0}: {1}'.format('HostUpgradeFlag',
                                                hex((status_value >> 12) & 0x1).rstrip("L")))
                    print('\t\t{0}: {1}'.format('eSecureImage',
                                                hex((status_value >> 16) & 0x1).rstrip("L")))
                    print('\t\t{0}: {1}'.format('HostImage',
                                                hex((status_value >> 20) & 0x1).rstrip("L")))

                status_decoded[SBP_STATUS_STR[status_str_idx]] = hex(status_value).rstrip("L")
                i+=4
            else:
                extra_bytes = data[i-4:status_size]
                r, a = repr(''.join(map(chr, extra_bytes))), list(map(hex, extra_bytes))
                print('\tExtra Bytes:{}  raw:{}'.format(r, a))
                #''.join([str(chr(x)) for x in extra_bytes]),
                #status_decoded["Extra Bytes"] = [str(chr(x)) for x in data[i:status_size]]
                #status_decoded["Extra Bytes"] = [str(x) for x in data[i:status_size]]
                i = status_size
        return status_decoded

    def int_to_bytes(self, val, num_bytes):
            print ("int_to_bytes")
            print(list(struct.unpack('BBBB', struct.pack('<I', val))))
            byte_array = [(val & (0xff << pos*8)) >> pos*8 for pos in range(num_bytes)]
            print (byte_array)
            return byte_array



    def cmd_reply_length(self, header_bytes):
        header = array('B', list(reversed(header_bytes[0:4])))
        status = int(binascii.hexlify(header), 16)
        return status & 0xFFFF

    def get_serial_number(self):
        print('Getting serial number...!')
        (status, rdata)= self.challenge_cmd(cmd=CMD.GET_SERIAL_NUMBER)
        if status == True:
            return (status, rdata)
        else:
            err_msg = "Dbg chal command error! {0}".format(rdata)
            print (err_msg)
            return (False, err_msg)

    def get_status(self):
        print ("Getting status...!")
        (status, rdata)= self.challenge_cmd(cmd=CMD.GET_STATUS)
        if status == True:
            return (status, rdata)
        else:
            err_msg = "Dbg chal command error! {0}".format(rdata)
            print (err_msg)
            return (False, err_msg)

    def read_otp(self):
        print ("Getting OTP...!")
        (status, rdata)= self.challenge_cmd(CMD.GET_OTP)
        if status == True:
            return (status, rdata)
        else:
            err_msg = "Dbg chal command error! {0}".format(rdata)
            print (err_msg)
            return (False, err_msg)

    def read_flash(self, num_bytes, offset):
        print("Reading flash: {0} bytes at offset {1}".format(num_bytes, offset))
        params = array('B', struct.pack('<2I', int(offset), int(num_bytes)))
        return self.challenge_cmd(CMD.FLASH_READ_DATA, list(params))


    def erase_flash_sector(self, offset):
        ''' erase flash sector at offset '''
        print("Erasing flash at offset {0}".format(offset))
        if (offset & (CMD.QSPI_SECTOR_SIZE - 1)) != 0:
            return (False,"Invalid offset passed as argument: must be a multiple of SECTOR_SIZE : %s" % hex(CMD.QSPI_SECTOR_SIZE))

        params = array('B', struct.pack('<I', int(offset)))
        return self.challenge_cmd(CMD.FLASH_ERASE_SECTION, list(params))

    def get_write_buffer_sizes(self):
        (status,rdata) = self.challenge_cmd(CMD.FLASH_WRITE_BUFF_SIZE)
        if status == True:
            # set the member variables
            self.page_size, self.wr_buf_size = struct.unpack('<2I', struct.pack('8B', *rdata))

        return (status,rdata)

    def clear_write_buffer(self):
        ''' clear the write buffer -- filled with 0xFF '''
        return self.challenge_cmd(CMD.FLASH_WRITE_CLEAR_DATA)

    def write_flash(self, input_data, offset):
        if self.page_size is None or self.wr_buf_size is None:
            (status,rdata) = self.get_write_buffer_sizes()
            print(status,rdata)
            if status is False:
                return (status,rdata)

        # clear the write buffer only at the beginning
        # since it's done automatically after a write
        (status, rdata) = self.clear_write_buffer()
        if status is False:
            return (status, rdata)

        input_data_size = len(input_data)
        print("Writing {0} bytes".format(input_data_size))
        start = 0
        buffer_load_size = min(self.page_size, self.wr_buf_size)
        while start < input_data_size:
            # write the minimum of page size and remaining data
            page_data_size = min(self.page_size, input_data_size - start)
            offset_in_page = 0

            # loop to load the write buffer -- (if wr_buf_size < page_data_size)
            while page_data_size > 0:
                load_size = min(buffer_load_size, page_data_size)
                params = array('B', struct.pack('<2I', offset_in_page, load_size))
                # add the data to the byte array
                print("Sending bytes {0} to {1}".format(start+offset_in_page, start+offset_in_page+load_size))
                data_to_send = input_data[start+offset_in_page:start+offset_in_page+load_size]
                params.extend(data_to_send)

                (status, rdata) = self.challenge_cmd(CMD.FLASH_WRITE_ADD_DATA, list(params))
                if status is False:
                    return (status,rdata)
                offset_in_page += load_size
                page_data_size -= load_size

            # write buffer data is loaded -- write it (a self.page_size) to flash
            params = array('B', struct.pack('<I', offset))
            (status, rdata) = self.challenge_cmd(CMD.FLASH_WRITE_FLUSH_DATA, list(params))
            if status is False:
                return (status,rdata)

            start += self.page_size
            offset += self.page_size

        return (True,b'')

    def inject_cert(self, cert_file, customer=False):
        print("Injecting Certificate...! customer:{}".format(customer))
        cert = array('B')
        cert_file_path = os.path.abspath(cert_file)
        if not os.path.exists(cert_file_path):
            err_msg = 'cert_file: {0} not found!'.format(cert_file_path)
            print (err_msg)
            return (False, err_msg)
        cert_length = os.path.getsize(cert_file_path)
        print('cert_length: {0}'.format(cert_length))
        with open(cert_file_path, 'rb') as f:
            cert.fromfile(f, cert_length)

        CMD.INJECT_CERTIFICATE += 1 if customer else 0

        (status, rdata)= self.challenge_cmd(CMD.INJECT_CERTIFICATE, list(cert))
        if status == True:
            #print('Injected certificate. Response rdata:{0}'.format([hex(x) for x in rdata] if rdata is not None else None))
            print ('Succefully injected certificate!')
            return (True, None)
        else:
            err_msg = "Dbg chal command error! {0}".format(rdata)
            print (err_msg)
            return (False, err_msg)

    def get_dbg_access(self, priv_key, dev_cert, grants=CONST.DBG_GRANTS, password=CONST.PRIVATE_KEY_PASSWORD, customer=False, quicktest=None):
        print("Getting dbg access grant...! customer:{}".format(customer))
        dev_cert_path = os.path.abspath(dev_cert)
        if not os.path.exists(dev_cert_path):
            err_msg = 'Dev certificate file: {0} not found!'.format(dev_cert_path)
            print (err_msg)
            return (False, err_msg)
        priv_key_path = os.path.abspath(priv_key)
        if not os.path.exists(priv_key_path):
            err_msg = 'Private key file: {0} not found!'.format(priv_key_path)
            print (err_msg)
            return (False, err_msg)

        (status, rdata)= self.challenge_cmd(CMD.GET_CHALLANGE)
        if status == True:
            #print "Challange: {0}".format([hex(x) for x in rdata] if rdata is not None else None)
            if not len(rdata) == 16 :
                err_msg = 'Invalid challange! length:{0} data: {1}'.format(len(rdata), data)
                print (err_msg)
                return (False, err_msg)
            print ('Succefully got Challenge bytes!')
        else:
            err_msg = 'Dbg chal command error! {0}'.format(rdata)
            print (err_msg)
            return (False, err_msg)

        challenge = [0,0,0,0,0,0]
        CMD.GRANT_DBG_ACCESS += 1 if customer else 0
        challenge[0] = CMD.GRANT_DBG_ACCESS
        challenge[1] = grants
        challenge[2] = struct.unpack("I", array('B', rdata[0:4]))[0]
        if 'nonceflip' in quicktest :
            print ("quicktest to corrupt nonce returned ...")
            challenge[3] = struct.unpack("I", array('B', rdata[0:4]))[0]
        else:
            challenge[3] = struct.unpack("I", array('B', rdata[4:8]))[0]
        challenge[4] = struct.unpack("I", array('B', rdata[8:12]))[0]
        challenge[5] = struct.unpack("I", array('B', rdata[12:16]))[0]

        challenge_bs = ""
        for word in challenge:
            challenge_bs += struct.pack('<I',word)
        print("data to sign (command + param + challenge): " +  binascii.hexlify(challenge_bs))

        s = struct.pack('<I', grants)
        dbg_grant_bytes = struct.unpack('BBBB',s)
        cert = array('B', dbg_grant_bytes)

        developer_cert_bs = array('B')
        dev_cert_size = os.path.getsize(dev_cert)
        print('dev_cert_size: {0}'.format(dev_cert_size))
        with open(dev_cert_path, 'rb') as f:
            developer_cert_bs.fromfile(f, dev_cert_size)
        cert.extend(developer_cert_bs)

        with open(priv_key_path, 'rb') as key_file:
            signing_key = serialization.load_pem_private_key(key_file.read(),
                    password, backend=default_backend())
        signed_challenge = signing_key.sign(challenge_bs, padding.PKCS1v15(),hashes.SHA512())
        signed_challenge_bs = array('B')
        signed_challenge_bs.fromstring(signed_challenge)

        signed_challenge_len = len(signed_challenge_bs)
        print("signed_challenge_len: {0}".format(signed_challenge_len))
        cert.extend(list(struct.unpack('BBBB', struct.pack('<I', signed_challenge_len))))
        cert.extend(signed_challenge_bs)
        print("cert length: {0}".format(len(cert)))
        # total length including header = 4 /length/ + 4 /command/ +
        #        4 /dbg_grant/ + developer_cert + 4 /size/ + signed_challenge
        msglen = 4 + dev_cert_size + 4 + signed_challenge_len
        print("msglen: {0}".format(msglen))
        (status, rdata) = self.challenge_cmd(CMD.GRANT_DBG_ACCESS, list(cert))
        #print "Grant Access: {0}".format([hex(x) for x in rdata] if rdata else None)
        if status == True:
            #print "Status: {0}".format([hex(x) for x in rdata] if rdata else None)
            return (status, rdata)
        else:
            err_msg = "Dbg chal command error! {0}".format(rdata)
            print (err_msg)
            return (False, err_msg)

def auto_int(x):
    return int(x, 0)

def main():
    parser = argparse.ArgumentParser(
        description="Run basic tests over Challenge Interface via I2C",
        epilog="Challenge Interface must be accessible via debug probe prior to running this script,\
        check the device documentation on how to do this")
    parser.add_argument("--dut", required=True, help="Dut name defined in dutdb.cfg")
    parser.add_argument("--in-rom", default=None, help="Rom Certificate to be injected for unlock")
    #parser.add_argument("--chip", type=int, default=0, choices=xrange(0, 2), help="chip instance number")

    #parser_cmds = parser.add_mutually_exclusive_group(required=False)
    parser.add_argument("--status", action='store_true', help="Display esecure device status")
    parser.add_argument("--otp", action='store_true', help="Display fused otp contents")
    parser.add_argument("--serial", action='store_true', help="Display serial number")
    parser.add_argument("--cm-unlock", action='store_true', help="Attempt to unlock debug interface in native chip mfg environments")
    cm_args = parser.add_argument_group("Chip Certificates", "Debug certificates, keys and credentials to unlock native chip mfg environments")
    cm_args.add_argument("--cm-grant", type=auto_int, help="Debug grant bits to unlock with --cm-unlock command")
    cm_args.add_argument("--cm-key", help="chipMfg developer's private key")
    cm_args.add_argument("--cm-cert", help="chipMfg developer's certificate signed with key for cm-key")
    cm_args.add_argument("--cm-pass", default=None, help="chipMfg developer's password for cm-key")

    parser.add_argument("--sm-unlock", action='store_true', help="Attempt to unlock debug interface in native chip mfg environments")
    sm_args = parser.add_argument_group("Customer Certificates", "Debug certificates, keys and credentials to unlock native customer/system environments")
    sm_args.add_argument("--sm-grant", type=auto_int, help="Debug grant bits to unlock with --sm-unlock command")
    sm_args.add_argument("--sm-key", help="sysMfg developer's private key")
    sm_args.add_argument("--sm-cert", help="sysMfg developer's certificate signed with key for sm-key")
    sm_args.add_argument("--sm-pass", default=None, help="sysMfg developer's password for sm-key")

    parser.add_argument("--flash", default=None, type=auto_int, help="perform flash test of erase, write, read at offset")
    parser.add_argument("--flash-read", default=None, type=auto_int, help="Perform flash read at offset provided")
    parser.add_argument("--flash-erase", default=None, type=auto_int, help="Perform flash erase at offset provided")
    parser.add_argument("--flash-write", default=None, type=auto_int, help="Perform flash write at offset provided")
    parser.add_argument("--csr", action='store_true', help="CSR peek poke test of a well defined scratch pad register")
    parser.add_argument("--mioval", default=None, type=auto_int, help="CSR poke value to MIO scratch pad register")
    parser.add_argument("--disconnect", action='store_true', help="CSR challenege disconnect")

    parser.add_argument("--csr-peek", action='store_true', help="CSR peek of a register with nqwords")
    parser.add_argument("--csr-poke", action='store_true', help="CSR poke at register with given array of qwords")
    parser.add_argument("--csr-verify", action='store_true', help="CSR poke and peek at register with given array of qwords")
    parser.add_argument("--regadr", default=0x1d00e170, type=auto_int, help="CSR address or or flash offset")
    parser.add_argument("--reglen", default=1, type=auto_int, help="CSR qwords to peek/poke or flash words")
    parser.add_argument("--regval", action='store', dest='regval', type=auto_int, nargs='+', default=[0xaabbccdd11223344], help="CSR qwords to poke or flash words")

    parser.add_argument("--reboot", action='store_true', help="Attempt to perform reboot via CSR operation")

    parser.add_argument('--quicktest', action='store', dest='quicktest', type=str, nargs='*', default=[], help="Examples: --quicktest nonceflip nopass xyz")


    args = parser.parse_args()
    ################### do some options integrity checking ################################
    if args.cm_unlock and not all([args.cm_key, args.cm_cert, args.cm_grant]):
        parser.error("--unlock requires all CM keys and certificates to be specified")

    if args.sm_unlock and not all([args.sm_key, args.sm_cert, args.sm_grant]):
        parser.error("--unlock requires all SM keys and certificates to be specified")


    print(dut().get_i2c_info(args.dut))
    status, serial, ip, addr = dut().get_i2c_info(args.dut)
    if not status:
        raise Exception("name={} not in database ...".format(args.dut))

    print ('instantiating s1 dbg probe ...')
    dbgprobe = dbgi2c(serial, addr)
    (status, status_msg) = dbgprobe.i2c_connect()
    if not status:
        raise Exception("s1-i2c-probe connect failed: status_msg={} ...".format(status_msg))

    #(status, status_msg) = dbgprobe.i2c_disconnect()
    #sys.exit(1)

    if args.status:
        (status, data) = dbgprobe.get_status()
        if status is False:
            print('Failed to get status! Error: {0}'.format(data))
            return False

    if args.cm_unlock:
        if args.in_rom:
            (status, data) = dbgprobe.inject_cert(args.in_rom, customer=False)
            if status is False:
                print('Failed to cm inject certificate! Error: {0}'.format(data))
                return False
            print('Injected cm certificate!')

        (status, data) = dbgprobe.get_dbg_access(args.cm_key, args.cm_cert, grants=args.cm_grant, password=args.cm_pass, customer=False, quicktest=args.quicktest)
        if status is False:
            print('Failed to cm-grant debug access! Error: {0}'.format(data))
            return False
        print('Debug access cm-granted!')

    if args.sm_unlock:
        if args.in_rom:
            (status, data) = dbgprobe.inject_cert(args.in_rom, customer=True)
            if status is False:
                print('Failed to sm inject certificate! Error: {0}'.format(data))
                return False
            print('Injected sm certificate!')

        password = None if 'nopass' in args.quicktest else args.sm_pass
        (status, data) = dbgprobe.get_dbg_access(args.sm_key, args.sm_cert, grants=args.sm_grant, password=password, customer=True, quicktest=args.quicktest)
        if status is False:
            print('Failed to sm-grant debug access! Error: {0}'.format(data))
            return False
        print('Debug access sm-granted!')


    if args.otp:
        (status, data) = dbgprobe.read_otp()
        if status is False:
            print('Failed to get OTP! Error: {0}'.format(data))
            return False

    if args.serial:
        (status, data) = dbgprobe.get_serial_number()
        if status is False:
            print('Failed to get serial number! Error: {0}'.format(data))
            return False

    if args.flash_read is not None:
        (status, data) = dbgprobe.read_flash(256, args.flash_read)
        if status is False:
            print('Failed to read the flash! Error: {0}'.format(data))
            return False

    if args.flash_erase is not None:
        (status, data) = dbgprobe.erase_flash_sector(args.flash_erase)
        if status is False:
            print('Failed to erase the flash! Error: {0}'.format(data))
            return False

    if args.flash_write is not None:
        (status, data) = dbgprobe.write_flash([0xA5]*256, args.flash_write)
        if status is False:
            print('Failed to write the flash! Error: {0}'.format(data))
            return False

    if args.flash is not None:
        (status, data) = dbgprobe.erase_flash_sector(args.flash)
        if status is False:
            print('Failed to erase the flash! Error: {0}'.format(data))
            return False

        (status, data) = dbgprobe.write_flash([0xB7]*256, args.flash)
        if status is False:
            print('Failed to write the flash! Error: {0}'.format(data))
            return False

        (status, data) = dbgprobe.read_flash(256, args.flash)
        if status is False:
            print('Failed to read the flash! Error: {0}'.format(data))
            return False

    if args.csr:
        print('\n************POKE MIO SCRATCHPAD ***************')
        if args.mioval:
            print(dbgprobe.local_csr_poke(0x1d00e170, [args.mioval]))
        else:
            print(dbgprobe.local_csr_poke(0x1d00e170, [0xabcd112299885566]))
        print('\n************PEEK MIO SCRATCHPAD ***************')
        status, word_array = dbgprobe.local_csr_peek(0x1d00e170, 1)
        print("word_array: {}".format(list(map(hex, word_array)) if word_array else None))
        #word_array = local_csr_peek(0x1d00e160, 1)
        #word_array = local_csr_peek(0x1d00e0a0, 1)
        #word_array = local_csr_peek(0x1d00e2c8, 1)

    if args.csr_peek:
        print('\n************PEEK CSR2 ***************')
        print('\nregadr={} reglen={}'.format(hex(args.regadr), hex(args.reglen)))
        status, word_array = dbgprobe.local_csr_peek(args.regadr, args.reglen)
        print("word_array: {}".format(list(map(hex, word_array)) if word_array else None))

    if args.csr_poke:
        print('\n************POKE CSR2 ***************')
        print('\nregadr={} regval={}'.format(hex(args.regadr), list(map(hex, args.regval))))
        status = dbgprobe.local_csr_poke(args.regadr, args.regval)
        print("status: {}".format(status))

    if args.csr_verify:
        print('\n************POKE PEEK and VERIFY CSR2 ***************')
        print('\nregadr={} regval={}'.format(hex(args.regadr), list(map(hex, args.regval))))
        pokestatus = dbgprobe.local_csr_poke(args.regadr, args.regval)
        print("pokestatus: {}".format(pokestatus))
        if pokestatus:
            print('\nregadr={} reglen={}'.format(hex(args.regadr), hex(args.reglen)))
            peekstatus, word_array = dbgprobe.local_csr_peek(args.regadr, args.reglen)
            print("peekstatus={}, word_array: {}".format(peekstatus, list(map(hex, word_array)) if word_array else None))
            if peekstatus:
                if (args.regval == word_array):
                    print("Success")
                    return True
                else:
                    print("Fail: word_array={} regval={}".format(list(map(hex, word_array)) if word_array else None, list(map(hex, args.regval))))
                    return False
            else:
                print("peek failed with status: {}".format(peekstatus))
                return False
        else:
            print("poke failed with status: {}".format(pokestatus))
            return False

    if args.disconnect:
        print('\n************debug disconnect command ***************')
        print(dbgprobe.challenge_disconnect())

    if args.reboot:
        print('\n************POKE RESET REGISTER ***************')
        print(dbgprobe.local_csr_poke(0x1d00e0a0, [0x0000000000000010]))

    #else:
    #    print('Invalid option: {0}'.format(args))


    dbgprobe.i2c_disconnect()

if __name__== "__main__":
    main()
