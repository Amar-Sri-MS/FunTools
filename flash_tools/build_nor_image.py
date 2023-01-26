#! /usr/bin/env python3
#
# Use this script to build a NOR image from scratch and perform more steps after.
#


import os
import sys
import argparse
import binascii
import subprocess
import fnmatch
import tarfile
import json
import gzip
from tempfile import mkstemp
import shutil
import requests

# optional imports to copy images to a web server
try:
    import paramiko
    from scp import SCPClient
except:
    pass

DESCRIPTION = '''Use this script to build the NOR image from sources, and
optionally perform more tasks afterwards. The host image is copied from
the FunSDK.
'''

EPILOG = '''
Examples:

* Simple build of the current SBPFirmware branch:

python3 build_nor_image.py

* Simple build of the current SBPFirmware branch for s1:

python3 build_nor_image.py -c s1

* Production build of the current SBPFirmware branch for s1:

python3 build_nor_image.py -c s1 -p

* Simple build of the current SBPFirmware branch for s1.
Image includes an enrollment certificate (secure boot)

python3 build_nor_image.py -c s1 -n ~/mac/Downloads/1234_enrollment_cert.bin

* Build and copy the file to dochub for upgrade

python3 build_nor_image.py -u ferino -v 12910

---
'''


EEPROM_PREFIX = "eeprom_"

CONFIG_JSON = "image.json"

NOR_IMAGE_FILE_NAME = "qspi_image_hw.bin"

BMC_INSTALL_DIR = "/mnt/sdmmc0p1/scripts"

#destination
DOCHUB_REPO_DIR_USER_FMT = '/project-fe/doc/sbp_images/{0}/{1}'

LOCAL_DIR_FMT = '/var/www/html/sbp_images/{0}'

# default eeprom for (chip, emulation) combination
DEFAULT_EEPROMS = {
    ('f1', True)    : 'eeprom_emu_compute2',
    ('f1', False)   : 'eeprom_f1_fs800',

    ('s1', True)    : 'eeprom_emu_s1_compute',
    ('s1', False)   : 'eeprom_s1_fc200_1_0GHz_SoC',

    ('f1d1', True)  : 'eeprom_emu_f1d1_compute_ddr',
    ('f1d1', False) : 'eeprom_f1d1_fs800v2_1_1GHz_SoC_1_7GHz_PC',

    ('s2', True)    : 'eeprom_emu_s2_compute',
    ('s2', False)   : 'eeprom_s2_qemu',      #FIXME WHEN SILICON
}

def remove_prefix(a_str, prefix):
    ''' remove a prefix from string if it is there '''
    if a_str.startswith(prefix):
        return a_str[len(prefix):]
    return a_str

def compress_file(src_path):
    with open(src_path, 'rb') as f_in:
        with gzip.open(src_path + '.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

def generate_dynamic_config(chip, eeprom):
    ''' generate on the fly a config string specifying the eeprom and the host '''
    uboot_rel_dir = "FunSDK/FunSDK/u-boot/" + chip + "/u-boot.bin"
    host_location = os.path.join(os.environ["WORKSPACE"], uboot_rel_dir)

    eeprom_source = {"source" : eeprom}
    signed_images = {"eeprom_packed.bin" : eeprom_source}
    host_source = {"source" : host_location}
    signed_images["host_firmware_packed.bin"] = host_source
    top_dir = {"signed_images" : signed_images}

    return json.dumps(top_dir, indent=4).encode('ascii')


def generate_nor_image(args, script_directory,
                       images_directory, eeprom_directory):
    ''' create the NOR image in images_directory with the arguments supplied '''
    #  fixed arguments
    run_args = ["python3",
                os.path.join(script_directory, "generate_flash.py"),
                "--fail-on-error",
                "--chip", args.chip,
                "--config-type", "json",
                "--source-dir", images_directory,
                "--source-dir", eeprom_directory,
                "--out-config", CONFIG_JSON]

    # optional arguments
    if args.version:
        run_args.extend(["--force-version", args.version])

    if args.description:
        run_args.extend(["--force-description", args.description])

    if args.enrollment_certificate:
        run_args.extend(["--enroll-cert", args.enrollment_certificate])

    # config files
    run_args.extend([os.path.join(script_directory, f) for f in
                     ["qspi_config_fungible.json", "key_bag_config.json"]])

    if args.customer:
        run_args.extend([os.path.join(script_directory,
                                      "qspi_config_customer.json")])

    # stdin input will be used to send the config that was generated on the fly
    run_args.append("-")

    print(run_args)

    # generate a config string on the fly: host for the chip, eeprom
    extra_config = generate_dynamic_config(args.chip, args.eeprom)

    subprocess.run(run_args, input=extra_config, cwd=images_directory,
                   check=True, stdout=sys.stdout, stderr=sys.stderr)

    # compress the Nor image file preemptively
    full_nor_image_path = os.path.join(images_directory, NOR_IMAGE_FILE_NAME)
    compress_file(full_nor_image_path)


def generate_eeprom_signed_images(script_directory, images_directory,
                                  eeprom_directory, version, eeprom):
    ''' sign all the eeproms and place them in the images_directory '''
    #  fixed arguments
    run_args = ["python3",
                os.path.join(script_directory, "generate_flash.py"),
                "--fail-on-error",
                "--action", "sign",
                "--config-type", "json",
                "--source-dir", eeprom_directory]

    # optional arguments
    if version:
        run_args.extend(["--force-version", version])

    # stdin input will be used to send the config that was generated on the fly
    run_args.append("-")

    extra_config = b'''
    {
        "signed_images": {
        "eeprom_list": {
            "source": "%s",
            "version": 1,
            "fourcc": "eepr",
            "key": "fpk3",
            "cert": "",
            "customer_cert": "",
            "description": ""
        }
    }
    }
    ''' % eeprom.encode('utf-8') if eeprom else b"@file:eeprom_list.json"

    subprocess.run(run_args, input=extra_config, cwd=images_directory,
                   check=True, stdout=sys.stdout, stderr=sys.stderr)

def get_ssh_client(username, servername, password=None):
    ''' get a ssh client instance '''
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=servername, username=username, password=password)
    return ssh_client

def scp_file(ssh_client, target_dir, file_name):
    def progress(filename, size, sent):
        sys.stdout.write("copying file to %s progress: %.2f%%   \r" %
                         (filename.decode('utf-8'), float(sent)/float(size)*100))

    target_file_name = os.path.join(target_dir, os.path.basename(file_name))
    with SCPClient(ssh_client.get_transport(), progress=progress) as scp:
        scp.put(file_name, target_file_name)


def generate_update_tar_file(args, built_images_dir):
    ''' generate the TAR file used for update and optionally upload it to dochub '''
    def tar_filter(tar_info):
        if tar_info.isdir():
            return tar_info

        base_name = os.path.basename(tar_info.name)

        if fnmatch.fnmatch(base_name, '*.bin'):
            return tar_info

        if fnmatch.fnmatch(base_name, '*.json'):
            return tar_info

        return None

    tar_root = "{}_dev_signed".format(args.chip)
    tar_file_name = os.path.join(built_images_dir, tar_root) + ".tgz"

    with tarfile.open(tar_file_name, mode='w:gz') as f:
        f.add(built_images_dir, arcname=tar_root, filter=tar_filter)

    if args.user:
        ssh_client = get_ssh_client(args.user, args.dochub)

        repo_dir = DOCHUB_REPO_DIR_USER_FMT.format(args.user, args.version)

        print("upgrade file will be stored at", repo_dir)

        # make sure the directory exists
        _, stdout, _ = ssh_client.exec_command('mkdir -p ' + repo_dir +  ' 2>&1')
        for line in iter(stdout.readline, ""):
            print(line, end="")

        scp_file(ssh_client, repo_dir, tar_file_name)
    else:
        # move to /var/www/sbp_images directory (must be writable by current user)
        local_dir = LOCAL_DIR_FMT.format(args.version)
        os.makedirs(local_dir, exist_ok=True)
        dest = os.path.join(local_dir, os.path.basename(tar_file_name))
        shutil.move(tar_file_name, dest)
        print("File ready for upgrade: %s" % dest)

def generate_tar_file(args, built_images_dir):
    ''' package the NOR image and the signed eeproms '''

    def tar_filter(tar_info):
        if tar_info.isdir():
            return tar_info

        base_name = os.path.basename(tar_info.name)

        if fnmatch.fnmatch(base_name, 'eeprom_*.bin'):
            return tar_info

        if base_name == NOR_IMAGE_FILE_NAME:
            return tar_info

        return None

    TGZ_FORMAT = "build_{chip}_{emulation}{debug}_{version}"
    tar_root = TGZ_FORMAT.format(**vars(args))
    tar_file_name = os.path.join(built_images_dir, tar_root) + ".tgz"

    with tarfile.open(tar_file_name, mode='w:gz') as f:
        f.add(built_images_dir, arcname=tar_root, filter=tar_filter)

    return tar_file_name, tar_root


def extract_tar_to_bmc(ssh_client, tar_file_name):
    ''' copy tar file to bmc: sftp not available on bmc '''

    scp_file(ssh_client, BMC_INSTALL_DIR, tar_file_name)

    # now extract it
    print("extracting tar file {0}".format(tar_file_name))
    tar_extract_cmd = "tar xzf {0} -C {1} && rm {0}".format(tar_file_name, BMC_INSTALL_DIR)
    _, _, stderr = ssh_client.exec_command(tar_extract_cmd)
    for line in iter(stderr.readline, ""):
        print(line, end="")


def parse_args():
    ''' parse the command line arguments '''
    arg_parser = argparse.ArgumentParser(description=DESCRIPTION,
                                         epilog=EPILOG,
                                         formatter_class=argparse.RawDescriptionHelpFormatter)

    arg_parser.add_argument("-b", "--build-dir", action='store',
                            default="image_build",
                            help='''root for name of sub directory in which SPB will be built
                            default is "image_build" ''')
    arg_parser.add_argument("-c", "--chip", action='store',
                            default='f1',
                            choices=['f1', 's1', 'f1d1', 's2', 'f2'],
                            help="Machine (f1,s1,etc...), default = f1")
    arg_parser.add_argument("-e", "--eeprom", action='store',
                            help="eeprom type")
    arg_parser.add_argument("--no-recompile", action='store_false',
                            dest="recompile",
                            help="Do not compile software, just build image")
    arg_parser.add_argument("--sign-all-eeproms", action='store_true',
                            help="Sign all eeproms -- legacy behavior")
    arg_parser.add_argument("--emulation", action='store_const', const=1, default=0,
                            help="emulation_build")
    arg_parser.add_argument("-n", "--enrollment-certificate", action='store',
                            metavar='FILE',
                            help="enrollment certificate to add to the image")
    bld_type = arg_parser.add_mutually_exclusive_group()
    bld_type.add_argument("-p", "-r", "--release", "--production",
                          action='store_const', const='', dest='debug',
                          help="Production/Release build")
    bld_type.add_argument("-V", "--verbose", action='store_const', const='_verbose', dest='debug',
                          help="Production/Release build with verbose logging")
    bld_type.add_argument("-T", "--test", action='store_const', const='_test', dest='debug',
                          help="Production/Release build with all tests")
    # default to --debug
    arg_parser.set_defaults(debug='_debug')

    arg_parser.add_argument("--customer", action='store_true',
                            help="Customer build: sign with customer keys")
    arg_parser.add_argument("-s", "--sbp", action='store',
                            help="SBP Firmware directory, default is $WORKSPACE/SBPFirmware")
    arg_parser.add_argument("-v", "--version", action='store',
                            help="Force version for image -- useful for update")
    arg_parser.add_argument("--description", action='store',
                            help="Force description for image")

    arg_parser.add_argument("--tar", action='store_true',
                            default='--bmc' in sys.argv,
                            help="generate tgz file with the image and all eeproms")

    arg_parser.add_argument("-l", "--local", action='store_true',
                          help='''create a tgz file locally for use with run_fwupgrade.py
                          as /var/www/sbp_images''')

    arg_parser.add_argument("--bmc", action='store',
                            help="BMC on which to store the build (for install/recovery)")

    arg_parser.add_argument("-u", "--user", action='store', metavar='USERNAME',
                                help='''create a tgz file on dochub for use with run_fwupgrade.py
                            as dochub.fungible.local/doc/sbp_images/<username>/<version>/''')

    arg_parser.add_argument("--dochub", action='store', metavar='SERVER',
                                default='vnc-shared-01.fungible.local',
                                help='''server to use to copy file on dochub. cf."--user" arg''')

    return arg_parser.parse_args()


def sanitize_args(args, eeproms_dir):
    ''' sanitize the args and provide meaningful defaults '''

    # can we scp?
    can_scp = { 'paramiko', 'scp' } <= sys.modules.keys()
    if not can_scp and (args.bmc or args.user):
        args.bmc = args.user = 0  # contrast to None

    # sbp firmware directory
    if args.sbp is None:
        args.sbp = "{0}/SBPFirmware".format(os.environ['WORKSPACE'])
    else:
        args.sbp = os.path.abspath(args.sbp)

    # eeprom
    # verify the file exists; if not show the list
    eeprom_files = sorted(os.listdir(eeproms_dir))

    if args.eeprom is None:
        try:
            args.eeprom = DEFAULT_EEPROMS[(args.chip,args.emulation)]
        except KeyError:
            print("*** no default eeprom for that chip: %s\n" % args.chip)
            print("Please specify an eeprom to use with the -e/--eeprom option")
            sys.exit(1)

        # verify somebody did not remove the default
        if not args.eeprom in eeprom_files:
            # select a matching one....
            matches = [e for e in eeprom_files if e.startswith(args.eeprom)]
            if len(matches):
                args.eeprom = matches[0]
            else:
                print("*** could not find suitable default; please report as bug. ***")
                print("in the meantime, select one of the available eeproms (-e optional):")
                print("\n".join(eeprom_files))
                sys.exit(1)

    else:
        # Jenkins or other legacy users might specify the eeprom in
        # a weird way...be nice
        sane_eeprom = remove_prefix(args.eeprom, "fungible_")
        if not sane_eeprom.startswith(EEPROM_PREFIX):
            sane_eeprom = EEPROM_PREFIX + sane_eeprom

        # verify the file exists; if not show the list
        if not sane_eeprom in eeprom_files:
            print("eeprom name entered ws not found: \"{0}\"".format(args.eeprom))
            print("Available eeproms are:")
            print("\n".join(eeprom_files))
            sys.exit(1)

        args.eeprom = sane_eeprom

    # enrollment certificate
    if args.enrollment_certificate:
        args.enrollment_certificate = os.path.abspath(args.enrollment_certificate)
    elif args.emulation:
        # as a convenience, get the canonical start certificate from server and use it
        ENROLL_CERT_URL = "https://f1reg.fungible.com/cgi-bin/enrollment_server.cgi"
        EMULATION_SN = b'\0' * 22 + b'\x12\x34'
        sn_64 = binascii.b2a_base64(EMULATION_SN)

        server_response = requests.get(ENROLL_CERT_URL,
                                       params={'cmd':'cert',
                                               'sn': sn_64})
        enrollment_cert = binascii.a2b_base64(server_response.text)
        file_no, args.enrollment_certificate = mkstemp()
        os.write(file_no, enrollment_cert)
        os.close(file_no)

    return args


def main():

    ''' main '''
    script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    eeproms_dir = os.path.join(os.environ['WORKSPACE'],
                               'FunSDK/FunSDK/dpu_eepr')

    args = sanitize_args(parse_args(), eeproms_dir)

    BUILD_DIR_FORMAT = "{sbp}/{build_dir}_{chip}_{emulation}{debug}"

    # the target is like "build_debug_target_f1_0" or "build_target_s1_0"
    # the final 0 is for normal builds, 1 for emulation builds
    MAKE_CMD_FORMAT = 'BUILD_BASE_DIR={build_dir} make -C {sbp} build{debug}_target_{chip}_{emulation}'

    build_dir = BUILD_DIR_FORMAT.format(**vars(args))
    make_cmd = MAKE_CMD_FORMAT.format(**vars(args))

    if args.recompile:
        # build the images in the build_dir
        subprocess.run(make_cmd, shell=True, check=True,
                       stdout=sys.stdout, stderr=sys.stderr)

    # images will be in build_dir/install
    built_images_dir = os.path.join(build_dir, "install")

    generate_eeprom_signed_images(script_dir, built_images_dir,
                                  eeproms_dir, args.version,
                                  None if args.sign_all_eeproms else args.eeprom)

    # now generate a NOR image
    generate_nor_image(args, script_dir, built_images_dir, eeproms_dir)

    print("*** Images in {0} ***".format(built_images_dir))

    # generate the tgz file for update
    if args.user or args.local:
        generate_update_tar_file(args, built_images_dir)

    if args.tar:
        tar_file, tar_dir = generate_tar_file(args, built_images_dir)
        print("*** Tar file {0} ***".format(tar_file))

        if args.bmc:
            ssh_client = get_ssh_client('sysadmin', args.bmc, 'superuser')
            extract_tar_to_bmc(ssh_client, tar_file)
            print("*** Directory with images on {0}: {1} ***".format(
                args.bmc, os.path.join(BMC_INSTALL_DIR, tar_dir)))

    if args.bmc == 0 or args.user == 0:
        print('!!!! The "bmc" or "user" option were ignored because '\
        'the "paramiko" and/or "scp" modules are not currently installed !!!!')

if __name__ == '__main__':
    main()
