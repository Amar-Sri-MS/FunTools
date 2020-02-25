#! /usr/bin/env python3
#
# Use this script to build a NOR image from scratch and perform more steps after.
#


import os
import sys
import struct
import argparse
import subprocess
import json
import tempfile
import shutil

import paramiko


DESCRIPTION='''Use this script to build the NOR image from sources, and
optionally perform more tasks afterwards. The host image is copied from
the FunSDK.
'''

EPILOG='''
Examples:

* Simple build of the current SBPFirmware branch:

python3 build_nor_image.py

* Simple build of the current SBPFirmware branch for s1:

python3 build_nor_image.py -c s1

* Production build of the current SBPFirmware branch for s1:

python3 build_nor_image.py -c s1 -p

* Simple build of the current SBPFirmware branch for s1 and
store the image on DocHub for use with PROMIRA NOR programmer

python3 build_nor_image.py -c s1 -u insop

* Simple build of the current SBPFirmware branch for s1 and
store the image on DocHub for use with PROMIRA NOR programmer.
Image includes an enrollment certificate (secure boot)

python3 build_nor_image.py -c s1 -u insop -n ~/mac/Downloads/1234_enrollment_cert.bin

* Build for updating an existing F1: all jobs are scheduled.
The run_fw_upgrade.sh is a script on the server that will schedule an upgrade job

python3 build_nor_image.py -u ferino -v 9600 -r ./run_fw_upgrade.sh

---
'''


EEPROM_PREFIX="eeprom_"

# do not change this: hardcoded in upgrade script
CONFIG_JSON="image.json"

def remove_prefix(s, prefix):
    if s.startswith(prefix):
        return s[len(prefix):]
    return s


def generate_dynamic_config( chip, eeprom):
    ''' generate on the fly a config string specifying the eeprom and the host '''
    uboot_rel_dir = "FunSDK/FunSDK/u-boot/" + chip + "/u-boot.bin"
    host_location = os.path.join(os.environ["WORKSPACE"], uboot_rel_dir)

    eeprom_source = { "source" : eeprom }
    signed_images = { "eeprom_packed.bin" : eeprom_source }
    host_source = { "source" : host_location }
    signed_images["host_firmware_packed.bin"] = host_source
    top_dir = { "signed_images" : signed_images }

    return json.dumps(top_dir, indent=4).encode('ascii')


def generate_nor_image(script_directory, sbp_directory, images_directory,
                       extra_config, version, enrollment_cert):

    # copy the start certificate to the images directory
    shutil.copy2(os.path.join(sbp_directory,
                              "software/production/development_start_certificate.bin"),
                 os.path.join(images_directory,
                              "start_certificate.bin"))
    #  fixed arguments
    run_args = ["python3",
                os.path.join(script_directory, "generate_flash.py"),
                "--fail-on-error",
                "--config-type", "json",
                "--source-dir", images_directory,
                "--source-dir", os.path.join(sbp_directory,
                                             "software/eeprom"),
                "--out-config", CONFIG_JSON]

    # optional arguments
    if version:
        run_args.extend(["--force-version", version])

    if enrollment_cert:
        run_args.extend(["--enroll-cert", enrollment_cert])

    # config files
    run_args.extend([os.path.join(script_directory, f) for f in
                    ["qspi_config_fungible.json", "key_bag_config.json"]])

    # stdin input will be used to send the config that was generated on the fly
    run_args.append("-")

    print(run_args)

    result = subprocess.run(run_args, input=extra_config, cwd=images_directory,
                            stdout=sys.stdout, stderr=sys.stderr)


def get_ssh_client(username, servername):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=servername, username=username)
    return ssh_client


def save_update_images_to_server(username, version, remote_cmd, images_directory):

    DOCHUB_REPO_DIR_USER_FMT = '/project/users/doc/sbp_images/{user}/master/funsdk_flash_images/{version}'

    # no version provided -> place in directory 0: used for PROMIRA
    if not version:
        version = "0"

    repo_dir = DOCHUB_REPO_DIR_USER_FMT.format(user=username, version=version)

    print("Copying images to ", repo_dir)

    ssh_client = get_ssh_client(username, "server1")
    sftp = ssh_client.open_sftp()

    # make sure the directory exists
    _, stdout, _ = ssh_client.exec_command('mkdir -p ' + repo_dir +  ' 2>&1')
    for line in iter(stdout.readline, ""):
        print(line, end="")

    # change current remote directory
    sftp.chdir(repo_dir)

    # read the config: figure out what to copy
    config_file = os.path.join(images_directory, CONFIG_JSON)
    with open(config_file, "r") as f:
        config = json.load(f)

    # copy all the images
    images = config["signed_images"]
    for f in images.keys():
        # only some were created for the NOR image
        try:
            sftp.put(os.path.join(images_directory, f), f)
        except FileNotFoundError:
            pass

    images = config["signed_meta_images"]
    for f in images.keys():
        # only some were created
        try:
            sftp.put(os.path.join(images_directory, f), f)
        except FileNotFoundError:
            pass

    # config
    sftp.put(config_file, CONFIG_JSON)

    # dummy eemmc_image.bin required by upgrade script
    with sftp.file("emmc_image.bin", "w") as dummy_emmc:
        dummy_emmc.write("Place holder for eemmc_image.bin needed by upgrade script")
        dummy_emmc.write("Replace with real version if emmc upgrade is desired")

    # copy the NOR image too for use with NOR Programmer (PROMIRA)
    nor_image = config["output_format"]["output"] + ".bin"
    sftp.put(os.path.join(images_directory, nor_image), nor_image)

    # if there is a command to run, do it pass version as argument
    if remote_cmd:
        full_cmd = "{0} {1}".format(remote_cmd, version)
        print("Executing command {0}".format(full_cmd))
        _, stdout, stderr = ssh_client.exec_command(full_cmd)
        for line in iter(stdout.readline, ""):
            print(line, end="")

def main():

    script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))

    arg_parser = argparse.ArgumentParser(description=DESCRIPTION,
                                         epilog=EPILOG,
                                         formatter_class=argparse.RawDescriptionHelpFormatter)

    arg_parser.add_argument("-b", "--build-dir", action='store',
                            default="image_build",
                            help='''root for name of sub directory in which SPB will be built
                            default is "image_build" ''')
    arg_parser.add_argument("-c", "--chip", action='store',
                            default='f1', choices=['f1','s1'],
                            help="Machine (f1,s1), default = f1")
    arg_parser.add_argument("-e", "--eeprom", action='store',
                            help="eeprom type")
    arg_parser.add_argument("-n", "--enrollment-certificate", action='store',
                            metavar = 'FILE',
                            help="enrollment certificate to add to the image")
    arg_parser.add_argument("-p", "--production", action='store_true',
                             help="Production build: very few log messages")
    arg_parser.add_argument("-r", "--run", action='store',
                            help='''command to run on the server after images are stored.
                            version is passed as first argument to this command''')
    arg_parser.add_argument("-s", "--sbp", action='store',
                            help="SBP Firmware directory, default is $WORKSPACE/SBPFirmware")
    arg_parser.add_argument("-u", "--username", action='store',
                            help="User name to store images for update")
    arg_parser.add_argument("-v", "--version", action='store',
                            help="Force version for image -- useful for update")

    args = arg_parser.parse_args()

    # defaults and arguments sanitization

    # sbp firmware directory
    if args.sbp is None:
        args.sbp = "{0}/SBPFirmware".format(os.environ['WORKSPACE'])
    else:
        args.sbp = os.path.abspath(args.sbp)

    # eeprom
    if args.eeprom is None:
        if args.chip == 'f1':
            args.eeprom = "eeprom_f1"
        elif args.chip == 's1':
            args.eeprom = "eeprom_s1_dev_board_r1"
    else:
        # Jenkins or other legacy users might specify the eeprom in
        # a weird way...be nice
        sane_eeprom = remove_prefix(args.eeprom, "fungible_")
        if not sane_eeprom.startswith(EEPROM_PREFIX):
            sane_eeprom = EEPROM_PREFIX + sane_eeprom

        # verify the file exists; if not show the list
        eeprom_files = [f for f in os.listdir(os.path.join(args.sbp, "software/eeprom"))]
        if not sane_eeprom in eeprom_files:
            print("eeprom name entered ws not found: \"{0}\"".format(args.eeprom))
            print("Available eeproms are:")
            print("\n".join(eeprom_files))
            sys.exit(1)

        args.eeprom = sane_eeprom

    # enrollment certificate
    if args.enrollment_certificate:
        args.enrollment_certificate = os.path.abspath(args.enrollment_certificate)

    # the build directory is SBPDirectory/BUILD_BASE_DIR_f1_0_debug or SBPDirectory/BUILD_BASE_DIR_s1_0
    BUILD_DIR_FORMAT="{sbp}/{build_dir}_{chip}_0{_debug}"

    # the target is like "build_debug_target_f1_0" or "build_target_s1_0"
    # The final 0 means it is not an emulation build
    MAKE_CMD_FORMAT='BUILD_BASE_DIR={build_dir} make -C {sbp} build{_debug}_target_{chip}_0'

    # args.production translate to a _debug
    args._debug = "" if args.production else "_debug"

    build_dir = BUILD_DIR_FORMAT.format(**vars(args))
    make_cmd = MAKE_CMD_FORMAT.format(**vars(args))

    # build the images in the build_dir
    build_result = subprocess.run(make_cmd, shell=True,
                                  stdout=sys.stdout, stderr=sys.stderr)

    # images will be in build_dir/install
    built_images_dir = os.path.join(build_dir, "install")

    # generate a config string on the fly: host for the chip, eeprom
    extra_config = generate_dynamic_config(args.chip, args.eeprom)

    # now generate a NOR image -- fungible signed by default for the moment
    generate_nor_image(script_dir, args.sbp, built_images_dir, extra_config,
                       args.version, args.enrollment_certificate)

    print("Images are all in {0}".format(built_images_dir))

    # if user name specified, do remote work: copy and maybe run
    if args.username:
        save_update_images_to_server(args.username, args.version, args.run, built_images_dir)

if __name__ == '__main__':
    main()
