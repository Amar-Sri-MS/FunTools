#!/usr/bin/env python3

import struct
import sys
import os
import configparser
import json
import argparse
import shutil
import subprocess
import generate_flash as gf


#TODO (make configurable for S1 and other)
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
         "source":"eeprom_f1"
         }
     }
}
"""

def main():
    parser = argparse.ArgumentParser()
    flash_content = None
    config = {}

    parser.add_argument('config', nargs='+', help='Configuration file(s)')
    parser.add_argument('--action',
        choices={'all', 'prepare', 'sign', 'image'},
        default='all',
        help='Action to be performed on the input files')
    parser.add_argument('--sdkdir', required=True, help='SDK root directory')
    parser.add_argument('--destdir', required=True, help='Destination directory for output')
    parser.add_argument('--force-version', type=int, help='Override firmware versions')
    parser.add_argument('--force-description', help='Override firmware description strings')

    args = parser.parse_args()

    wanted = lambda action : args.action in ['all', action]

    for config_file in args.config:
        if config_file == '-':
            gf.merge_configs(config, json.load(sys.stdin,encoding='ascii'))
        else:
            with open(config_file, 'r') as f:
                gf.merge_configs(config, json.load(f,encoding='ascii'))

    gf.merge_configs(config, json.loads(EEPROM_CONFIG_OVERRIDE))
    gf.merge_configs(config, json.loads(HOST_FIRMWARE_CONFIG_OVERRIDE))
    gf.set_config(config)

    if args.force_version:
        gf.set_versions(args.force_version)

    if args.force_description:
        gf.set_description(args.force_description)

    curdir = os.getcwd()

    if wanted('prepare'):
        # paths to application binaries in SDK tree
        paths = [ "bin",
                "FunSDK/u-boot",
                "FunSDK/sbpfw/roms",
                "FunSDK/sbpfw/eeproms",
                "FunSDK/sbpfw/firmware/chip_f1_emu_0",
                "FunSDK/sbpfw/pufrom/chip_f1_emu_0",
                ]
        sdkpaths = [os.path.join(args.sdkdir, path) for path in paths]

        # temporary as gf.run() doesn't support configurable target location
        if not os.path.exists(args.destdir):
            os.mkdir(args.destdir)
        os.chdir(args.destdir)
        gf.set_search_paths(sdkpaths)

        gf.run('sources')

        utils = [ "bin/flash_tools/generate_firmware_image.py",
                  "bin/flash_tools/generate_flash.py",
                  "bin/flash_tools/make_emulation_emmc.py",
                  "bin/flash_tools/key_replace.py",
                  "bin/flash_tools/enrollment_service.py", # FIXME(Marcin) delete this
                  "bin/flash_tools/f1registration.ca.pem", # FIXME(Marcin) delete this
                  "bin/flash_tools/" + os.path.basename(__file__),
                  "bin/Linux/x86_64/mkimage" ]
        for app in utils:
            shutil.copy2(os.path.join(args.sdkdir, app), os.path.basename(app))

        #TODO(mnowakowski)
        #     skip direct invocation and import make_emulation_emmc
        cmd = [ 'python', 'make_emulation_emmc.py',
                '-w', '.',
                '-o', '.',
                '--appfile', 'funos-f1.stripped',
                '--filesystem',
                '--signed',
                '--bootscript-only']
        subprocess.call(cmd)

        with open("image.json", "w") as f:
            json.dump(config, f, indent=4)

        gf.run('key_injection', net=True, hsm=False)
        os.chdir(curdir)

    if wanted('sign'):
        sdkpaths = []
        sdkpaths.append(os.path.abspath(args.destdir))
        gf.set_search_paths(sdkpaths)
        os.chdir(args.destdir)
        gf.run('key_injection', net=False, hsm=True, keep_output=True)
        gf.run('certificates')
        gf.run('sign')
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

        os.chdir(curdir)

if __name__=="__main__":
    main()
