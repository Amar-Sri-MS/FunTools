#!/usr/bin/env python3

##############################################################################
#  enrollment_client.py
#
#  Utility -- Used for production enrollment
#
#  Stand alone script using i2c CLI tools on the BMC or other
#
#  Copyright (c) 2018-2022. Fungible, inc. All Rights Reserved.
#  Copyright (c) 2023. Microsoft Corporation. All Rights Reserved.
#
##############################################################################

# pylint: disable=missing-function-docstring, missing-class-docstring
# pylint: disable=consider-using-f-string

'''
 This script is used for enrollment using the I2C/DBG/Challenge Interface.
 A general rule is that all binary data is manipulated using python bytearray
'''


import sys
import time
import binascii
import struct
import subprocess
import argparse
import logging
import traceback

#conditional imports to allow running on simple local BMC python installations
REQUESTS_WARN = r'''
Python module "requests" could not be imported.
This module is necessary to contact the enrollment server.
You can still use this script for simple tests.
'''

PARAMIKO_WARN = r'''
Python module "paramiko" could not be imported.
This module is necessary to connect via SSH to the BMC or other with i2c interface.
'''


try:
    import requests
except:
    print(REQUESTS_WARN)


try:
    import paramiko
except:
    print(PARAMIKO_WARN)



###############################################################
#
# Constants
#
###############################################################
class CMD:              # pylint: disable=too-few-public-methods
    ''' namespace for challenge commands constants '''
    GET_SERIAL_NUMBER = 0xFE000000
    GET_STATUS = 0xFE010000
    PREPARE_QSPI = 0xFE080000
    GET_ENROLL_INFO = 0xFF050000
    SET_ENROLL_INFO = 0xFF060000

#maximal i2c FLIT_SIZE
MAX_FLIT_SIZE = 64
CHAL_HEADER_SIZE = 4


# success messages
ENROLL_CERT_GENERATED = r'''
Enrollment certificate successfully generated by the registration server.
Please
1-power cycle the chip %d on %s -- this is very important.
2-rerun this script with the same arguments to install the enrollment certificate'''

ENROLL_CERT_INSTALLED = r'''
An enrollment certificate was found for this chip on the registration server.
It was successfully installed on chip %d on %s.
The machine is now enrolled.'''


########################################################################
#
# I2C command line interface executer or commander
#
########################################################################

class I2CCliCmdr:

    def close(self):
        pass

    def get_cmd_output(self, _cmd):
        return None


class I2CCliLocalCmdr(I2CCliCmdr):

    def get_cmd_output(self, cmd):
        try:
            logging.info("Executing cmd locally: %s", cmd)
            p = subprocess.Popen(cmd, shell=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)

            err = p.stderr.read()
            if len(err):
                logging.error("Error: %s\n%s",
                             err, traceback.format_exc())
                return None

            return p.stdout.read()

        except Exception:
            status_msg = traceback.format_exc()
            logging.error(status_msg)
            return None


class I2CCliSSHCmdr(I2CCliCmdr):

    def __init__(self, ssh_client):
        self.ssh_client = ssh_client

    def close(self):
        self.ssh_client.close()
        self.ssh_client = None

    def get_cmd_output(self, cmd):
        assert self.ssh_client
        logging.info("Executing cmd via SSH: %s", cmd)

        _, stdout, stderr = self.ssh_client.exec_command(cmd)

        err = stderr.read()
        if len(err):
            logging.error("Error: %s\n%s",
                          err, traceback.format_exc())
            return None

        return stdout.read()

########################################################################
#
# I2C command line interface command
#
########################################################################

class I2CCliCmd():

    def prepare_cmd(self, _bus_num, read_len=0, write_bytes=None):
        # num_read or write_bytes must be specified ...
        assert(read_len > 0 or write_bytes is not None)
        # but not both at once ...
        assert(read_len == 0 or write_bytes is None)
        return ""

    def process_read_output(self, _cmd, read_cmd_output):
        return read_cmd_output

    def process_write_output(self, _cmd, _write_cmd_output, _write_data_length):
        return False

SLAVE_ADDR = 0x70

class I2CTransferCli(I2CCliCmd):
    ''' CLI with i2ctransfer '''

    def __init__(self, i2ct_path):
        self.i2ct_path = i2ct_path

    def prepare_cmd(self, bus_num, read_len=0, write_bytes=None):
        super().prepare_cmd(bus_num, read_len, write_bytes)

        cmd = '%s -y -f %d %s%d@0x%02x ' % (
            self.i2ct_path,
            bus_num,
            'r' if read_len else 'w',
            read_len if read_len else len(write_bytes),
            SLAVE_ADDR)

        if write_bytes:
            for b in write_bytes:
                cmd += ' 0x%02x' % b

        return cmd

    def process_read_output(self, _cmd, read_cmd_output):
        output_lines = read_cmd_output.splitlines()
        logging.debug(output_lines)
        # i2ctransfer output: 1 line: 0x78 0xbc ... 0xda
        return bytearray([int(x,16) for x in output_lines[0].split()])


    def process_write_output(self, cmd, write_cmd_output, _write_data_length):
        if len(write_cmd_output) != 0:
            logging.error('No output is expected for the cmd: %s',cmd)
            return False
        return True


class I2CTestCli(I2CCliCmd):
    ''' CLI with i2cclient-test '''

    def prepare_cmd(self, bus_num, read_len=0, write_bytes=None):
        super().prepare_cmd(bus_num, read_len, write_bytes)

        cmd = 'i2c-test -b %02d -s 0x%02x ' % (bus_num, SLAVE_ADDR)
        if read_len:
            cmd += ' -rc %d -r' % read_len
        else:
            cmd += ' -w -d'

        if write_bytes:
            for b in write_bytes:
                cmd += ' 0x%02x' % b

        return cmd


    def process_read_output(self, _cmd, read_cmd_output):
        output_lines = read_cmd_output.splitlines()
        logging.debug(output_lines)
        # i2c-test output:
        num_bytes_read = int(output_lines[0].split(b':')[1].strip())
        logging.debug('num_bytes_read:%d', num_bytes_read)
        bytes_read = bytearray()
        for line in output_lines[1:]:
            bytes_read += bytearray([int(x,16) for x in line.strip().split()])
        assert num_bytes_read == len(bytes_read)
        logging.debug('num_bytes_read: %d data: %s',
                      num_bytes_read,
                      [hex(x) for x in bytes_read])
        return bytes_read


    def process_write_output(self, cmd, write_cmd_output, write_data_length):
        if len(write_cmd_output) == 0:
            logging.error('No output for the cmd: %s',cmd)
            return False
        output_lines = write_cmd_output.splitlines()
        logging.debug(output_lines)

        status_line_flds = output_lines[1].split(b':')
        logging.debug(status_line_flds)

        num_bytes_wrote = int(status_line_flds[1].strip())

        if num_bytes_wrote != write_data_length:
            logging.error('Wrote %d bytes instead of %d',
                          num_bytes_wrote, write_data_length)
            return False
        return True


############################################################################
#
# I2CInterface
#
############################################################################

class I2CInterface:
    ''' abstract I2C interface class '''
    def connect(self):
        return False

    def disconnect(self):
        pass

    def read(self, _bus_num, _len_data):
        ''' return bytes read as a bytearray() '''
        return bytearray()

    def write(self, _bus_num, _write_data):
        ''' return bool for success '''
        return False


########################################################################
#
# I2CCli: I2C command line interface
#
########################################################################

class I2CCli(I2CInterface):
    ''' Implements I2C interface using helper CLI objects '''

    def __init__(self, cmd_prep, cmd_exec):
        self.cmd_prep = cmd_prep
        self.cmd_exec = cmd_exec

    def disconnect(self):
        self.cmd_exec.close()
        self.cmd_exec = None

    def read(self, bus_num, len_data):
        assert self.cmd_prep
        assert self.cmd_exec

        cmd = self.cmd_prep.prepare_cmd(bus_num, len_data)
        logging.debug('i2c_read cmd: %s', cmd)

        cmd_output = self.cmd_exec.get_cmd_output(cmd)

        logging.debug(cmd_output)
        if len(cmd_output) == 0:
            logging.error('No output for the cmd: %s\n%s',
                          cmd, traceback.format_exc())
            return None

        bytes_read = self.cmd_prep.process_read_output(cmd, cmd_output)
        logging.debug('i2c_read read_data: %s', bytes_read)

        if len(bytes_read) == 0:
            logging.error('No output for the cmd: %s\n%s',
                          cmd, traceback.format_exc())
            return None

        return bytes_read


    def write(self, bus_num, write_data):
        ''' return True if Successful, False otherwise '''
        assert self.cmd_prep
        assert self.cmd_exec

        cmd = self.cmd_prep.prepare_cmd(bus_num, 0, write_bytes=write_data)
        logging.debug('i2c_write cmd: %s', cmd)

        cmd_output = self.cmd_exec.get_cmd_output(cmd)

        return self.cmd_prep.process_write_output(cmd,
                                                  cmd_output,
                                                  len(write_data))


############################################################################
#
# BMC: implementation of the I2CInterface using an I2CCli
#
############################################################################

SSH_CREDENTIALS = (
    ("root", "root"),
    ("sysadmin", "superuser"),
    ("localadmin", None)       # must use ssh-copy-id for this case
)

class BMC(I2CInterface):
    ''' implement the i2c interface: connect, disconnect, read, write '''

    def __init__(self, bmc_ip_address):
        self.bmc_ip_address = bmc_ip_address
        self.i2c_cli = None


    def _try_bmc_connect(self, username, password):
        logging.info('bmc trying to connect as  %s@%s',
                     username, self.bmc_ip_address)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(self.bmc_ip_address, username = username,
                           password=password)
        except Exception:
            logging.debug('Failed to connect to BMC: %s using "%s"\n%s',
                          self.bmc_ip_address,
                          username,
                          traceback.format_exc())
            client.close()
            return None

        return client

    def _get_i2ctransfer_path(self, cmdr):
        try:
            # some distros (Debian 11)  do not add /usr/sbin to the path
            cmd = "PATH=/usr/sbin:$PATH command -v i2ctransfer"
            cmd_output = cmdr.get_cmd_output(cmd)
            logging.debug(cmd_output)
            return cmd_output.rstrip().decode('ascii')

        except Exception:
            status_msg = traceback.format_exc()
            logging.error(status_msg)
        return ""


    # Check i2c device presence and open the device.
    # Returns Connected

    def connect(self):
        logging.info('bmc connect')

        cmdr = None

        if self.bmc_ip_address is None or \
           self.bmc_ip_address == 'localhost' or \
           self.bmc_ip_address == '127.0.0.1' :
            cmdr = I2CCliLocalCmdr()
            logging.info("Executing command locally")
        else:

            for ssh_credential in SSH_CREDENTIALS:
                ssh_client = self._try_bmc_connect(*ssh_credential)
                if ssh_client:
                    cmdr = I2CCliSSHCmdr(ssh_client)
                    logging.info("Executing command via SSH")
                    break
            if cmdr is None:
                print("Unable to connect to %s with known credentials" %
                      self.bmc_ip_address)
                return False


        i2ctransfer_path = self._get_i2ctransfer_path(cmdr)
        if len(i2ctransfer_path):
            logging.info("Using i2ctransfer %s", i2ctransfer_path)
            self.i2c_cli = I2CCli(I2CTransferCli(i2ctransfer_path),
                                 cmdr)
        else:
            logging.info("Using i2c-test")
            self.i2c_cli = I2CCli(I2CTestCli(), cmdr)

        return True


    # Free the i2c bus and close the device handle
    def disconnect(self):
        if self.i2c_cli:
            self.i2c_cli.disconnect()
        logging.info('Disconnected!')


    # i2c read
    def read(self, bus_num, len_data):
        ''' return bytes read as a bytearray() '''
        assert self.i2c_cli
        return self.i2c_cli.read(bus_num, len_data)


    # i2c write
    def write(self, bus_num, write_data):
        ''' return True if Successful, False otherwise '''
        assert self.i2c_cli
        return self.i2c_cli.write(bus_num, write_data)


###############################################################################
#
# dbg challenge protocol using an i2c interface
#
###############################################################################
class I2CDbgChallenge:
    ''' Implement the DBG Fungible protocol on top of an I2C interface '''
    def __init__(self, i2c_intf, bus_num):
        self.i2c = i2c_intf
        self.bus_num = bus_num

    def _i2c_dbg_chal_read_flit_aux(self, num_read):
        ''' read a single flit of data '''
        assert num_read <= MAX_FLIT_SIZE
        num_read += 1

        cmd_byte = bytearray([0x40 | num_read])

        self.i2c.write(self.bus_num, cmd_byte)

        flit_data = self.i2c.read(self.bus_num, num_read)

        status_byte = flit_data[0]
        if status_byte >> 7 :
            err_msg = "Command Execution Error: 0x%02x"
            if (status_byte >> 6) == 0x3:
                err_msg += " *** invalid shim action state ***"
            logging.error(err_msg, status_byte)
            return None

        return flit_data


    def i2c_dbg_chal_read_flit(self, num_read):
        flit_data = self._i2c_dbg_chal_read_flit_aux(num_read)
        if flit_data is None:
            return None

        flit_len = flit_data[0] & 0x7F
        return flit_data[1:1+flit_len]


    def i2c_dbg_chal_peek_read_len(self):
        flit_data = self._i2c_dbg_chal_read_flit_aux(0)
        if flit_data is None:
            return None
        return flit_data[0] & 0x7F


    def i2c_dbg_chal_read(self, num_read):

        logging.debug("chal_read: read %d bytes (0x%08x)\n",
                      num_read, num_read)

        data = bytearray()
        read = 0
        try_count = 0

        while read < num_read:
            flit_size = num_read - read
            if flit_size > MAX_FLIT_SIZE:
                flit_size = 64

            flit_data = self.i2c_dbg_chal_read_flit(flit_size)
            if flit_data is not None:
                try_count = 0
                read += len(flit_data)
                data += flit_data
            else:
                try_count += 1
                if try_count > 10:
                    logging.error("Timeout reading %d bytes after %d bytes read",
                                  num_read, read)
                    return None

        logging.debug("Successfully received %d bytes\n%s",
                      len(data), data)
        return data


    def i2c_dbg_chal_fifo_flush(self):

        logging.debug("Flushing the FIFO")

        flushed = False
        while not flushed:
            len_data = self.i2c_dbg_chal_peek_read_len()
            if len_data:
                self.i2c_dbg_chal_read(len_data)
            else:
                flushed = True
        logging.debug("Flushed the FIFO")


    def i2c_dbg_chal_cmd_header_read(self):

        logging.debug("Read command status header")
        len_read = self.i2c_dbg_chal_peek_read_len()
        if len_read < CHAL_HEADER_SIZE or len_read > MAX_FLIT_SIZE:
            logging.error("Unable to read header: got %d (not in 4-64 range)",
                          len_read)
            raise Exception("Error reading header")

        return self.i2c_dbg_chal_read(CHAL_HEADER_SIZE)


    def execute_cmd(self, cmd_no, cmd_data=None, reply_delay_msec=0):

        # Flush
        self.i2c_dbg_chal_fifo_flush()

        logging.debug("challenge cmd: 0x%08x", cmd_no)

        data_len = len(cmd_data) if cmd_data else 0
        size = 4 * 2 + data_len # command/size/data

        # send command
        cmd_buffer = bytearray(1 + 4 * 2) # dbg byte + command + size
        cmd_buffer[0] = 0xC8
        struct.pack_into('<2I', cmd_buffer, 1, size, cmd_no)
        self.i2c.write(self.bus_num, cmd_buffer)

        # send command data
        sent = 0
        while sent < data_len:

            flit_size = min(data_len - sent, MAX_FLIT_SIZE)

            flit_data = bytearray([0x80 + (flit_size & 0x3F)])

            flit_data += cmd_data[sent: sent + flit_size]
            self.i2c.write(self.bus_num, flit_data)
            sent += flit_size


        logging.debug("sent %d bytes\n", data_len)

        # Wait for reply
        if reply_delay_msec:
            time.sleep(reply_delay_msec/1000)

        # Read reply
        header = self.i2c_dbg_chal_cmd_header_read()
        if len(header) != CHAL_HEADER_SIZE:
            logging.error("Cmd 0x%08X : invalid challenge header reply length: %d",
                          cmd_no, header.size())
            return None

        reply_length = header[0] + (header[1] << 8) - CHAL_HEADER_SIZE

        if reply_length > 0:
            header += self.i2c_dbg_chal_read(reply_length)

        logging.info("challenge cmd 0x%08x reply (%d):\n%s",
                     cmd_no, len(header),
                     "".join(["%02x:" % x for x in header]))
        return header



###########################################################################
#
# Error checking and reporting
#
# header is 4 bytes little endian: size | (status << 16)
#
###########################################################################
def cmd_status(response_bytes):
    return  response_bytes[2] & 0xf

def cmd_status_ok(response_bytes):
    ''' second byte is status '''
    return cmd_status(response_bytes) == 0

def cmd_reply_length(response_bytes):
    ''' length is encoded in third and fourth byte little endian  '''
    return response_bytes[0] + (response_bytes[1] << 8)

def report_error(cmd, rdata):
    if rdata is None:
        logging.error("command %s failure: no data returned!", cmd)
    else:
        logging.error("command %s failure = %d; command length = %d -- actual %d",
                      cmd, cmd_status(rdata), cmd_reply_length(rdata), len(rdata))

##########################################################################
#
# Parsing/Extracting utilities
#
#########################################################################

def boot_step_and_version(rdata):
    ''' return boot step (int) and version (stream) '''
    # boot step is the single byte at 20
    # version is the nul terminated string at the end...
    # starting at byte 36
    boot_step = rdata[20]
    version_offset = 36
    magic = int.from_bytes(rdata[version_offset:version_offset+4],
                           'little')

    # some SDK builds contain a magic 0xADDED001 word at offset 36.
    # This has not been released in any official build and has later
    # been changed to add the magic word _after_ the version string.
    # Keep this code in place for compatibility with those intermediate
    # releases. Since this code does not care about any fields _after_
    # the version string, it doesn't currently need updating to support
    # these changes.
    if magic == 0xADDED001:
        version_offset += 4 * 4 # 4 extra 32 bit words

    # find null terminator
    zero_index = rdata[version_offset:].index(0)
    version = rdata[version_offset:version_offset+zero_index]
    return boot_step, version

###########################################################################
#
# Challenge commands
#
###########################################################################


class Challenge:
    ''' high level challenge command interface for enrollment '''
    def __init__(self, bmc_ip_addr, bus_num):
        self.connected = False
        self.bmc = BMC(bmc_ip_addr)
        self.dbg_chal = I2CDbgChallenge(self.bmc, bus_num)

    def __del__(self):
        logging.info('Destroying the connection!')
        if self.connected:
            self.disconnect()

    def connect(self):
        self.connected = self.bmc.connect()
        return self.connected

    def disconnect(self):
        self.bmc.disconnect()

    def get_boot_step_and_version(self):
        ''' check that the chip is in the right boot step
        status returns header (4), tamper_status (4), tamper_timestamp (4)
        status (4), RTC time (4), boot step (1), upgrade(1), etc... '''
        rdata = self.dbg_chal.execute_cmd(CMD.GET_STATUS)

        if rdata and cmd_status_ok(rdata) and cmd_reply_length(rdata) > 36:
            return boot_step_and_version(rdata)

        report_error("GetStatus", rdata)
        return None, None

    def get_serial_number(self):
        ''' get the chip's serial number '''
        rdata = self.dbg_chal.execute_cmd(CMD.GET_SERIAL_NUMBER)

        if rdata and cmd_status_ok(rdata):
            return bytes(rdata[4:])

        report_error("GetSerialNumber", rdata)
        return None

    def prepare_qspi(self):
        rdata = self.dbg_chal.execute_cmd(CMD.PREPARE_QSPI)
        if rdata and cmd_status_ok(rdata):
            return True

        report_error("PrepareQSPI", rdata)
        return False

    def get_enroll_tbs(self):
        rdata = self.dbg_chal.execute_cmd(CMD.GET_ENROLL_INFO)
        if rdata and cmd_status_ok(rdata):
            return bytes(rdata[4:])

        report_error("Enrollment", rdata)
        return None

    def save_enroll_cert(self, cert):

        rdata = self.dbg_chal.execute_cmd(CMD.SET_ENROLL_INFO, cert)

        if rdata and cmd_status_ok(rdata):
            return True

        report_error("WriteEnrollmentCertificate", rdata)
        return False


#########################################################################
#
# Get Enrollment Certificate from f1reg.fungible.com
#
#########################################################################

SERVER_URL_PRE = b"https://f1reg.fungible.com/cgi-bin/"

def get_expected_boot_steps(version):

    url = SERVER_URL_PRE + \
        b"enrollment_boot_step.cgi?bootstep=enrollment&version=" + \
        version
    response = requests.get(url, timeout=10)

    if response.status_code != requests.codes.ok: # pylint: disable=no-member
        logging.warning("Server response for boot step of version %s: %d %s" ,
                        version.decode('ascii'),
                        response.status_code,
                        response.reason)
        return None

    # CSV values: 0x,0x,....
    boot_step_vals=[int(val,0) for val in response.text.split(",")]
    return boot_step_vals

def generate_enrollment_cert(tbs_cert):

    # always print the TBS since it is precious
    print("Enrollment Information:",
          binascii.b2a_hex(tbs_cert).decode('ascii'))

    tbs_cert_64 = binascii.b2a_base64(tbs_cert)

    response = requests.put(SERVER_URL_PRE + b"enrollment_server.cgi",
                            data=tbs_cert_64, timeout=10)

    if response.status_code != requests.codes.ok: # pylint: disable=no-member
        logging.error("Server response: %d %s",
                      response.status_code, response.reason)
        return None

    cert_64 = response.text

    logging.info("CERT: %s", cert_64)

    return binascii.a2b_base64(cert_64)


def get_cert_of_serial_number(serial_no):

    sn_64 = binascii.b2a_base64(serial_no).rstrip()

    url = SERVER_URL_PRE + b"enrollment_server.cgi?cmd=cert&sn=" + sn_64
    response = requests.get(url, timeout=10)

    if response.status_code == requests.codes.not_found: # pylint: disable=no-member
        # expected if there is no cert in the database
        logging.info("No enrollment certificate for this serial number")
        return None

    if response.status_code != requests.codes.ok:  # pylint: disable=no-member
        logging.error("Server response: %d %s",
                      response.status_code, response.reason)
        return None

    cert_64 = response.text

    logging.info("CERT: %s", cert_64)

    return binascii.a2b_base64(cert_64)

##########################################################################
# Auxiliary procedures
#

def report_incorrect_boot_step(boot_step, expected_boot_steps):
    if boot_step > max(expected_boot_steps):
        logging.error("Enrollment not needed: chip is past the boot "\
                      "stage: 0x%X > 0x%X",
                      boot_step, max(expected_boot_steps))
    elif boot_step < min(expected_boot_steps):
        logging.error("Enrollment not possible: chip is stuck at an "\
                      "earlier boot stage: 0x%X < 0x%X",
                      boot_step, min(expected_boot_steps))
    else:
        logging.error("Enrollment not possible: chip is at boot step "\
                      "0x%X not in %s",
                      boot_step,
                      ",".join("0x%X" for eb in expected_boot_steps))


def enrollment_in_rom(boot_step, expected_boot_steps):
    return len(expected_boot_steps)>1 and boot_step == min(expected_boot_steps)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Perform enrollment via I2C")

    log_levels = { logging.getLevelName(a) : a for a in
                   [logging.DEBUG, logging.INFO, logging.WARN, logging.ERROR] }

    parser.add_argument("-c","--chip", type=int, default=0, choices=[0,1],
                          help="chip instance number (default = 0)")

    parser.add_argument("--log", choices=log_levels.keys(),
                          default="ERROR",
                          help="set log level")

    parser.add_argument("-m", "--bmc",
                        help="BMC IP Address or DNS name; "\
                        "do not use for local exectution")

    parser.add_argument("-b", "--bus",
                        help="i2c bus to use; "\
                        "If specified, chip argument is ignored")

    return parser.parse_args()


#########################################################################
#
# Main
#
#########################################################################

def main():

    args = parse_arguments()

    logging.basicConfig()
    logger = logging.getLogger() # root level logger
    logger.setLevel(args.log)

    if args.bus is None:
        args.bus = 3 if args.chip == 0 else 5
    else:
        args.bus = int(args.bus, 0)

    # get enrollment info
    # check for connection

    challenge = Challenge(args.bmc, args.bus)
    status = challenge.connect()
    if status is False:
        logging.error('Connection failed!')
        return False

    logging.info('Connected to challenge interface')
    # verify we are in the correct step
    boot_step, version = challenge.get_boot_step_and_version()
    expected_boot_steps = get_expected_boot_steps(version)

    if expected_boot_steps is None:
        logging.warning("Unable to check for boot step (experimental version)\n"\
                        "Trying anyway")
    elif not boot_step in expected_boot_steps:
        report_incorrect_boot_step(boot_step, expected_boot_steps)
        return False

    logging.info("Chip at the correct boot step; retrieving serial number")
    # Get serial number
    serial_no = challenge.get_serial_number()
    if serial_no is None:
        logging.error("Error getting the chip serial number")
        return False

    cert = get_cert_of_serial_number(serial_no)

    #if the cert is there, write it
    if cert:
        logging.info("Found certificate for this serial number")

        if enrollment_in_rom(boot_step, expected_boot_steps):
            if not challenge.prepare_qspi():
                logging.error("Prepare Flash for writing certificate failed")
                return False

        if challenge.save_enroll_cert(cert):
            print(ENROLL_CERT_INSTALLED % (args.chip, args.bmc))
            return True

        logging.error("Enrollment certificate could not be installed")
        return False

    # cert was not in database: enroll and get tbs information
    tbs_cert = challenge.get_enroll_tbs()
    if not tbs_cert:
        logging.error("Error getting the enrollment information")
        return False

    # get enrollment certificate from enrollment server
    # do not write it, it will be when running this script
    # again on the same chip
    cert = generate_enrollment_cert(tbs_cert)
    if cert:
        print(ENROLL_CERT_GENERATED % (args.chip, args.bmc))
        return True

    logging.error("Error getting the enrollment certificate")
    return False


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
