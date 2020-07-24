#!/usr/bin/env python3

import struct
import sys
import os
import configparser
import glob
import json
import argparse
import shutil
import subprocess
import tarfile
import generate_flash as gf
import flash_utils
import eeprom_replace as er


HOST_FIRMWARE_CONFIG_OVERRIDE="""
{ "signed_images": {
     "host_firmware_packed.bin": {
         "source":"u-boot.bin"
         }
     }
}
"""

#TODO (make configurable for S1 and other)
EEPROM_CONFIG_OVERRIDE="""
{ "signed_images": {
     "eeprom_packed.bin": {
         "source":"eeprom_f1_dev_board"
         }
     }
}
"""

FUNOS_CONFIG_OVERRIDE="""
{{ "signed_images": {{
     "funos.signed.bin": {{
         "source":"{funos_appname}"
         }}
     }}
}}
"""

EEPROM_LIST_CONFIG_OVERRIDE="""
{{ "signed_images": {{
     "eeprom_list": {{
         "source":"@file:{eeprom_list}"
         }}
     }}
}}
"""

def main():
    parser = argparse.ArgumentParser()
    config = {}

    parser.add_argument('config', nargs='+', help='Configuration file(s)')
    parser.add_argument('--action',
        choices={'all', 'prepare', 'certificate', 'sign', 'image', 'tarball'},
        default='all',
        help='Action to be performed on the input files')
    parser.add_argument('--sdkdir', required=True, help='SDK root directory')
    parser.add_argument('--destdir', required=True, help='Destination directory for output')
    parser.add_argument('--key-name-suffix', default='', help='Suffix for key name')
    parser.add_argument('--force-version', type=int, help='Override firmware versions')
    parser.add_argument('--force-description', help='Override firmware description strings')
    parser.add_argument('--with-hsm', action='store_true', help='Use HSM for signing')
    parser.add_argument('--chip', choices=['f1', 's1', 'f1d1'], default='f1', help='Target chip')
    parser.add_argument('--debug-build', dest='release', action='store_false', help='Use debug application binary')

    args = parser.parse_args()

    use_hsm = args.with_hsm
    use_net = not use_hsm

    funos_suffixes = ['', args.chip]
    if args.release:
        funos_suffixes.append('release')

    funos_appname = "funos{}.stripped".format('-'.join(funos_suffixes))

    wanted = lambda action : args.action in ['all', action]

    for config_file in args.config:
        if config_file == '-':
            gf.merge_configs(config, json.load(sys.stdin,encoding='ascii'))
        else:
            with open(config_file, 'r') as f:
                gf.merge_configs(config, json.load(f,encoding='ascii'))

    eeprom_list = '{}_eeprom_list.json'.format(args.chip)

    if wanted('prepare'):
        gf.merge_configs(config, json.loads(EEPROM_CONFIG_OVERRIDE))
        gf.merge_configs(config, json.loads(HOST_FIRMWARE_CONFIG_OVERRIDE))
        gf.merge_configs(config, json.loads(FUNOS_CONFIG_OVERRIDE.format(funos_appname=funos_appname)))
        gf.merge_configs(config, json.loads(EEPROM_LIST_CONFIG_OVERRIDE.format(eeprom_list=eeprom_list)))

    gf.set_config(config)

    if args.force_version:
        gf.set_versions(args.force_version)

    if args.force_description:
        gf.set_description(args.force_description, True)

    curdir = os.getcwd()

    if wanted('prepare'):
        # paths to application binaries in SDK tree
        paths = [ "bin",
                "FunSDK/sbpfw/roms",
                "FunSDK/sbpfw/eeproms",
                "FunSDK/nvdimm_fw",
                "feature_sets",
                ]
        sdkpaths = [os.path.join(args.sdkdir, path) for path in paths]

        paths_chip_specific = [ "FunSDK/u-boot/{chip}",
                "FunSDK/sbpfw/firmware/chip_{chip}_emu_0",
                "FunSDK/sbpfw/pufrom/chip_{chip}_emu_0",
                ]
        sdkpaths.extend(
            [os.path.join(args.sdkdir, path.format(chip=args.chip)) for path in paths_chip_specific])

        # temporary as gf.run() doesn't support configurable target location
        if not os.path.exists(args.destdir):
            os.mkdir(args.destdir)
        os.chdir(args.destdir)
        gf.set_search_paths(sdkpaths)

        gf.run('sources')

        utils = [ "bin/flash_tools/generate_firmware_image.py",
                  "bin/flash_tools/generate_flash.py",
                  "bin/flash_tools/gen_start_cert.sh",
                  "bin/flash_tools/make_emulation_emmc.py",
                  "bin/flash_tools/firmware_signing_service.py",
                  "bin/flash_tools/enrollment_service.py",
                  "bin/flash_tools/key_bag_create.py",
                  "bin/flash_tools/key_replace.py",
                  "bin/flash_tools/eeprom_replace.py",
                  "bin/flash_tools/flash_utils.py",
                  "bin/flash_tools/sign_release.sh",
                  "bin/flash_tools/" + os.path.basename(__file__),
                  "bin/Linux/x86_64/mkimage" ]
        utils.append(os.path.join('FunSDK/sbpfw/eeproms', eeprom_list))

        for app in utils:
            shutil.copy2(os.path.join(args.sdkdir, app), os.path.basename(app))

        #TODO(mnowakowski)
        #     skip direct invocation and import make_emulation_emmc
        cmd = [ 'python', 'make_emulation_emmc.py',
                '-w', '.',
                '-o', '.',
                '--appfile', funos_appname,
                '--filesystem',
                '--signed',
                '--bootscript-only']
        subprocess.call(cmd)

        with open("image.json", "w") as f:
            json.dump(config, f, indent=4)

        gf.run('key_injection', net=use_net, hsm=use_hsm)
        os.chdir(curdir)

    if wanted('certificate'):
        sdkpaths = []
        sdkpaths.append(os.path.abspath(args.destdir))
        gf.set_search_paths(sdkpaths)
        os.chdir(args.destdir)
        gf.run('certificates', net=use_net, hsm=use_hsm)
        os.chdir(curdir)

    if wanted('sign'):
        sdkpaths = []
        sdkpaths.append(os.path.abspath(args.destdir))
        gf.set_search_paths(sdkpaths)
        os.chdir(args.destdir)
        gf.run('key_injection', net=use_net, hsm=use_hsm, keep_output=True, key_name_suffix=args.key_name_suffix)
        gf.run('certificates', net=use_net, hsm=use_hsm)
        gf.run('sign', net=use_net, hsm=use_hsm, key_name_suffix=args.key_name_suffix)
        os.chdir(curdir)

    if wanted('image'):
        sdkpaths = []
        sdkpaths.append(os.path.abspath(args.destdir))
        gf.set_search_paths(sdkpaths)
        os.chdir(args.destdir)
        gf.run('flash')

        #TODO(mnowakowski)
        #     skip direct invocation and import make_emulation_emmc
        cmd = [ 'python', 'make_emulation_emmc.py',
                '-w', '.',
                '-o', '.',
                '--appfile', 'funos.signed.bin',
                '--fsfile', 'boot.img.signed',
                '--filesystem',
                '--signed' ]
        subprocess.call(cmd)

        with open(eeprom_list) as f:
            eeproms = json.load(f)
            for skuid, value in eeproms.items():
                er.replace('qspi_image_hw.bin',
                    'qspi_image_hw.bin.{}'.format(skuid), value['filename'])

        os.chdir(curdir)

    if wanted('tarball'):
        os.chdir(args.destdir)
        tarfiles = []

        with open("image.json") as f:
            images = json.load(f)
            tarfiles.extend([key for key,value in images['signed_images'].items()
                                if not value.get("no_export", False)])
            tarfiles.extend([key for key,value in images['signed_meta_images'].items()
                                if not value.get("no_export", False)])

        with open("mmc_image.json") as f:
            images = json.load(f)
            tarfiles.extend([key for key,value in images['generated_images'].items()
                                if not value.get("no_export", False)])

        tarfiles.append('image.json')
        tarfiles.append('mmc_image.json')
        tarfiles.extend(glob.glob('qspi_image_hw.bin*'))

        with tarfile.open('{chip}_sdk_signed_release.tgz'.format(chip=args.chip), mode='w:gz') as tar:
            for f in tarfiles:
                tar.add(f)

        os.chdir(curdir)

if __name__=="__main__":
    main()
