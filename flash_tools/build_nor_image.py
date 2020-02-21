#! /usr/bin/env python3
#
# Use this script to build a NOR image from scratch
#

import os
import sys
import struct
import argparse
import subprocess
import json
import tempfile
import shutil

EEPROM_PREFIX="eeprom_"

# arguments are always:
# 0: _machine, 1: _debug or '', 2 sbp directory, 3: build base directory

# the build directory is SBPDirectory/BUILD_BASE_DIR_f1_0_debug or SBPDirectory/BUILD_BASE_DIR_s1_0
BUILD_DIR_FORMAT="{2}/{3}{0}_0{1}"

# the target is like "build_debug_target_f1_0" or "build_target_s1_0"
# The final 0 means it is not an emulation build
MAKE_CMD_FORMAT='BUILD_BASE_DIR={3} make -C {2} build{1}_target{0}_0'


def remove_prefix(s, prefix):
    if s.startswith(prefix):
        return s[len(prefix):]
    return s


def generate_dynamic_config( chip, eeprom):

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

    flash_script = os.path.join(script_directory, "generate_flash.py")

    config_files = [os.path.join(script_directory, f) for f in
                    ["qspi_config_fungible.json", "key_bag_config.json"]]

    options_fmt = "--fail-on-error --config-type json --source-dir {0} --source-dir {1}"

    options_args = options_fmt.format(images_directory,
                                      os.path.join(sbp_directory,
                                                   "software/eeprom"))
    if version:
        options_args += " --force-version {0}".format(int(version,0))

    if enrollment_cert:
        options_args += " --enroll-cert {0}".format(enrollment_cert)

    run_args = ['python3', flash_script, *(options_args.split()), *config_files, "-"]

    print(run_args)

    result = subprocess.run(run_args, input=extra_config, cwd=images_directory,
                            stdout=sys.stdout, stderr=sys.stderr)



def main():

    script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))

    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument("-b", "--build-dir", action='store',
                            default="image_build",
                            help="root for name of sub directory in which SPB will be built")
    arg_parser.add_argument("-c", "--chip", action='store',
                            default='f1', choices=['f1','s1'],
                            help="Machine (f1,s1), default = f1")
    arg_parser.add_argument("-e", "--eeprom", action='store',
                            help="eeprom type")
    arg_parser.add_argument("-n", "--enrollment-certificate", action='store',
                            metavar = 'FILE',
                            help="enrollment certificate to add to the image")
    arg_parser.add_argument("-p", "--production", action='store_true',
                             help="Production build")
    arg_parser.add_argument("-s", "--sbp", action='store',
                            help="SBP Firmware directory")
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
        args.eeprom = EEPROM_PREFIX + args.chip
    else:
        # Jenkins or other legacy users might specify the eeprom in
        # a weird way...be nice
        args.eeprom = remove_prefix(args.eeprom, "fungible_")
        if not args.eeprom.startswith(EEPROM_PREFIX):
            args.eeprom = EEPROM_PREFIX + args.eeprom


    # enrollment certificate
    if args.enrollment_certificate:
        args.enrollment_certificate = os.path.abspath(
            args.enrollment_certificate)

    # build the argument list for the FMT strings
    fmt_args = ["_" + args.chip]
    if args.production:
        fmt_args.append("")
    else:
        fmt_args.append("_debug")

    fmt_args.append(args.sbp)
    fmt_args.append(args.build_dir)

    extra_config = generate_dynamic_config(args.chip, args.eeprom)

    build_dir = BUILD_DIR_FORMAT.format(*fmt_args)
    # images will be in build_dir/install
    built_images_dir = os.path.join(build_dir, "install")

    make_cmd = MAKE_CMD_FORMAT.format(*fmt_args)

    # build the images in the build_dir
    build_result = subprocess.run(make_cmd, shell=True,
                                  stdout=sys.stdout, stderr=sys.stderr)

    # now generate a NOR image -- fungible signed by default for the moment
    generate_nor_image(script_dir, args.sbp, built_images_dir, extra_config,
                       args.version, args.enrollment_certificate)


if __name__ == '__main__':
    main()
