#! /usr/bin/env python3
#
# Use this script to create the source directory for a run_fwupgrade.py invocation
# Specify the Jenkins build specifier and the version desired.
# Example: python3 sbp_upgrade_prep.py -b 93fc97446560668-19-07-29-15-31 -v 7290
# This will create the upgrade files in a DocHub directory that can be used as
# the source for the run_fwupgrade.py invocation:
# FunSDK/integration_test/emulation/run_fwupgrade.py --image_url http://dochub.fungible.local/doc/sbp_images -u sbpf -v 7290
#

"""

Useful for generating indivisual image (serdes firmware for example) for testing

Usage:

    -b build_path can be found from jenkins job
    -v version number
    -u user
    -d manual description
    -s servername

    python3 ./sbp_upgrade_prep.py -b 66719eafa6814895-19-08-22-16-44 -v 7651 -u insop -d 0x10A0_2347 -s server120


"""

import os
import sys
import struct
import argparse
import subprocess
import json
import paramiko
import tempfile
import firmware_signing_service as fsi

# source
JENKINS_BUILD_URL_FMT = '/demand/demand/Jobs/{0}/flash_image.bin'

# props
JENKINS_PROPS_URL_FMT = '/demand/demand/Jobs/{0}/bld_props.json'

# signing information
GIT_SHOW_CMD_FMT = 'git show {0}:flash_tools/qspi_config_fungible.json'

#destination
DOCHUB_REPO_DIR_USER_FMT = '/project/users/doc/sbp_images/{0}/master/funsdk_flash_images/{1}'

CERTIFICATE_SIZE = 1096
WORD_SIZE = 4
SIGNING_INFO_SIZE = 2048
AUTH_HEADER_SIZE = 76

CERT_MAGIC = 0xB1005EA5

class NOR_IMAGE_FILE(object):

    def __init__(self, file_name):
        self.f = open(file_name, 'rb')

    def __del__(self):
        self.f.close()

    def read_file(self, offset, num_bytes):
        self.f.seek(offset)
        return self.f.read(num_bytes)

    def read_dir_of_dir(self):
        self.f.seek(WORD_SIZE)
        dir_of_dir = struct.unpack('<I', self.f.read(WORD_SIZE))[0]
        return dir_of_dir

    def read_dir(self):
        self.f.seek(self.read_dir_of_dir() + WORD_SIZE)
        dir_data = self.f.read(3 * WORD_SIZE)
        nor_dir = { 'pufr': struct.unpack('<2I', dir_data[:8]) }

        while True:
            addr_data = self.f.read(3 * WORD_SIZE)
            addrs = struct.unpack('<2I',addr_data[:8])
            fourcc = addr_data[8:]
            if fourcc == b'\xFF\xFF\xFF\xFF':
                break

            nor_dir[fourcc.decode()] = addrs

        return nor_dir

    def read_image(self, addr):
        self.f.seek(addr)
        # read the whole header: 2 * 2048 bytes + 76 bytes
        header = self.f.read(2 * SIGNING_INFO_SIZE + AUTH_HEADER_SIZE)
        (image_size, version) = struct.unpack('<2I',
                                              header[2 * SIGNING_INFO_SIZE: 2 * SIGNING_INFO_SIZE + 2 * WORD_SIZE])
        # check it is not a reserved entry (0xFFFFFFFF)
        if image_size == 0xFFFFFFFF:
            return None, None

        image = self.f.read(image_size)
        return header, image


def get_ssh_client(username, servername):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=servername, username=username)
    return ssh_client


def get_disk_image(sftp, build_id, version):
    remotefile_path = JENKINS_BUILD_URL_FMT.format(build_id)
    localfile_path = 'flash_image_{0}.bin'.format(version)
    sftp.get(remotefile_path, localfile_path)
    return NOR_IMAGE_FILE(localfile_path)


def signing_keys(image_spec):
    keys = {}

    signed_images = image_spec['signed_images']
    for fname, values in signed_images.items():
        key = values.get('key')
        if key:
            keys[values['fourcc']] = key
    return keys


def get_signing_keys_from_file(fname):
    image_spec = json.loads(open(fname, 'rb').read())

    return signing_keys(image_spec)


def get_signing_keys(sftp, build_id):
    remotefile_path = JENKINS_PROPS_URL_FMT.format(build_id)
    # read the prop file directly
    bld_props = json.load(sftp.open(remotefile_path))
    print("Build props:")
    print(json.dumps(bld_props, sort_keys=True, indent=4))
    # figure out the sha1 for FunTools --
    sha1s = bld_props['gitHubSha1s']
    funtools_sha1 = bld_props.get('FunTools', None)
    if not funtools_sha1:
        # use the sdk #
        funtools_sha1 = 'bld_' + bld_props["sdks"]["funsdk"]

    # make sure repo is up to date
    git_pull_cmd = "git fetch origin master:master"
    subprocess.check_output(git_pull_cmd.split())

    git_show_cmd = GIT_SHOW_CMD_FMT.format(funtools_sha1)
    image_spec = json.loads(subprocess.check_output(git_show_cmd.split()))

    return signing_keys(image_spec)

def save_signed_image(firmware_sign, image, version, ftype, sign_key, cert, description):

    # save the image to a file
    with open(ftype, 'wb') as f:
        f.write(image)

    # save the certificate if provided
    cert_file = None
    if cert:
         _, cert_file = tempfile.mkstemp(prefix='signing_cert')
         with open(cert_file, 'wb') as f:
             f.write(cert)
    try:

        # the firmware service will do the right thing and replace it with a signed one
        # ftype arguments: 1->infile, 2->outfile, 3->fourcc
        firmware_sign.image_gen(ftype, ftype, ftype, version, description, sign_key,
                            cert_file, None, None)
    finally:
        if cert_file:
            os.remove(cert_file)



def get_certificate(header):
    ''' look for a certificate in the header '''
    cert = header[SIGNING_INFO_SIZE:SIGNING_INFO_SIZE+CERTIFICATE_SIZE]
    magic = struct.unpack('<I', cert[:4])[0]
    if magic == CERT_MAGIC:
        return cert
    return None

def explode_disk_image(nor_image_file, signing_keys, version_nr, description,
                       override_cert):
    directory = nor_image_file.read_dir()
    images = {}
    #create instance of signing service
    firmware_sign = fsi.FirmwareSigningService.create(fsi.FirmwareSigningService.MOD_NET)

    for fourcc, addrs in directory.items():
        header,image = nor_image_file.read_image(addrs[0])
        if image is not None:
            cert = get_certificate(header)
            if cert and override_cert:
                cert = override_cert
            key = signing_keys.get(fourcc)
            save_signed_image(firmware_sign, image, version_nr, fourcc,
                              key, cert, description)
            images[fourcc] = { 'fourcc': fourcc }

    # generate a dummy emmc.bin file to satisfy the script
    with open('emmc_image.bin', 'w') as f:
        f.write('Place holder for emmc.bin needed by upgrade script')
        f.write('Replace with real version if emmc upgrade is desired')

    # also generate the special pufr+frmw aka sbpf that is not on the image
    sbpf_image = open('pufr', 'rb').read()
    sbpf_image += open('frmw', 'rb').read()
    cert = get_certificate(sbpf_image)

    save_signed_image(firmware_sign, sbpf_image, version_nr, 'sbpf',
                       None, cert, description)
    images['sbpf'] = { 'fourcc': 'sbpf' }

    return { 'signed_images' : images }


def store_images(ssh_client, sftp, images, version, username):
    """
    Store image on the dochub
    """

    repo_dir = DOCHUB_REPO_DIR_USER_FMT.format(username, version)

    print("Split file(s) will be stored at", repo_dir)

    # make sure the directory exists
    _, stdout, _ = ssh_client.exec_command('mkdir -p ' + repo_dir +  ' 2>&1')
    for line in iter(stdout.readline, ""):
        print(line, end="")

    signed_images = images['signed_images']
    print("Signed_images:")
    print(json.dumps(signed_images, indent=2))
    for fourcc in signed_images:
        sftp.put(fourcc, os.path.join(repo_dir, fourcc))

    sftp.put('emmc_image.bin', os.path.join(repo_dir, 'emmc_image.bin'))

    with sftp.open(os.path.join(repo_dir, 'image.json'), 'w') as f:
        json.dump(images, f)


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-b", "--build", action='store',
                            required=True,
                            help="build number generated by Jenkins (e.g. 985d0a713458964-19-03-13-04-36)")
    arg_parser.add_argument("-v", "--version", action='store',
                            required=True,
                            help="Version number for the images")
    arg_parser.add_argument("-u", "--username", action='store',
                            required=True,
                            help="username")
    arg_parser.add_argument("-s", "--servername", action='store', default='server1',
                            required=False,
                            help="servername")
    arg_parser.add_argument("-d", "--description", action='store',
                            default='NO_DESC',
                            help="description")
    arg_parser.add_argument("-j", "--json-spec", action='store',
                            help='''(Optional) JSON file used for key signing specification''')

    arg_parser.add_argument("-c", "--certificate", action='store',
                            help='''(Optional) Start Certificate''')
    args = arg_parser.parse_args()

    version_nr = int(args.version, 0)

    if args.certificate:
        override_cert = open(args.certificate, 'rb').read()
    else:
        override_cert = None

    ssh_client = get_ssh_client(args.username, args.servername)
    sftp = ssh_client.open_sftp()
    disk_image = get_disk_image(sftp, args.build, version_nr)
    if args.json_spec:
        signing_keys = get_signing_keys_from_file(args.json_spec)
    else:
        signing_keys = get_signing_keys(sftp, args.build)
    images = explode_disk_image(disk_image, signing_keys, version_nr,
                                args.description, override_cert)
    store_images(ssh_client, sftp, images, version_nr, args.username)



if __name__ == '__main__':
    main()
