#!/usr/bin/env python3

'''
Copyright (c) 2019-2020 Fungible, inc.
All Rights Reserved.
'''

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

# TODO make configurable
ROOTFS_FILE='fs1600-rootfs-ro.squashfs'

def main():
    parser = argparse.ArgumentParser()
    config = {}

    parser.add_argument('config', nargs='*', help='Configuration file(s)')
    parser.add_argument('--action',
        choices={'all', 'prepare', 'release', 'certificate', 'sign', 'image', 'tarball', 'bundle'},
        default='all',
        help='Action to be performed on the input files')
    parser.add_argument('--sdkdir', default=os.getcwd(), help='SDK root directory')
    parser.add_argument('--destdir', default='RELEASE', help='Destination directory for output')
    parser.add_argument('--force-version', type=int, help='Override firmware versions')
    parser.add_argument('--force-description', help='Override firmware description strings')
    parser.add_argument('--chip', choices=['f1', 's1', 'f1d1'], default='f1', help='Target chip')
    parser.add_argument('--debug-build', dest='release', action='store_false', help='Use debug application binary')
    parser.add_argument('--default-config-files', dest='default_cfg', action='store_true')

    args = parser.parse_args()

    if args.default_cfg == False and len(args.config) == 0:
        parser.error("One of '--default-config-files' or a list of config files is required")

    funos_suffixes = ['', args.chip]
    if args.release:
        funos_suffixes.append('release')

    funos_appname = "funos{}.stripped".format('-'.join(funos_suffixes))

    def wanted(action):
        if args.action == 'all':
            return True
        elif args.action == 'release':
            return action in ['sign', 'image', 'tarball', 'bundle']
        else:
            return action == args.action

    if args.default_cfg:
        if wanted('prepare'):
            args.config = [
                'bin/flash_tools/qspi_config_fungible.json',
                'bin/flash_tools/mmc_config_fungible.json',
                'bin/flash_tools/key_bag_config.json',
                'FunSDK/nvdimm_fw/nvdimm_fw_config.json' ]
        else:
            args.config = [ 'image.json' ]

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

        utils = [ "bin/flash_tools/generate_flash.py",
                  "bin/flash_tools/make_emulation_emmc.py",
                  "bin/flash_tools/firmware_signing_service.py",
                  "bin/flash_tools/key_bag_create.py",
                  "bin/flash_tools/key_replace.py",
                  "bin/flash_tools/eeprom_replace.py",
                  "bin/flash_tools/flash_utils.py",
                  "bin/flash_tools/gen_hash_tree.py",
                  "bin/flash_tools/" + os.path.basename(__file__),
                  "bin/Linux/x86_64/mkimage",
                  "bin/scripts/gen_fgpt.py",
                  "bin/scripts/xdata.py" ]
        utils.append(os.path.join('FunSDK/sbpfw/eeproms', eeprom_list))

        for app in utils:
            shutil.copy2(os.path.join(args.sdkdir, app), os.path.basename(app))

        shutil.rmtree('install_tools', ignore_errors=True)
        shutil.copytree(os.path.join(args.sdkdir, 'bin/flash_tools/install_tools'),
            'install_tools')
        shutil.copy2(os.path.join(args.sdkdir, 'deployments', ROOTFS_FILE), ROOTFS_FILE)

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

        cmd = [ 'python3', 'gen_fgpt.py', 'fgpt.unsigned' ]
        subprocess.call(cmd)

        cmd = [ 'python3', 'xdata.py',
                '-r',
                '--data-offset=4096',
                '--data-alignment=512',
                '--padding=4',
                'fvos.unsigned',
                'add',
                os.path.join(args.sdkdir,
                    'bin/cc-linux-yocto/mips64hv/vmlinux.bin') ]
        subprocess.call(cmd)

        cmd = [ 'python3', 'gen_hash_tree.py',
                '-O', 'fvht.bin',
                'hash',
                '-N', 'rootfs.hashtree',
                '--to-sign', 'fvht.unsigned',
                '-I', ROOTFS_FILE ]
        subprocess.call(cmd)

        with open("image.json", "w") as f:
            json.dump(config, f, indent=4)

        gf.run('key_injection')
        os.chdir(curdir)

    if wanted('certificate'):
        sdkpaths = []
        sdkpaths.append(os.path.abspath(args.destdir))
        gf.set_search_paths(sdkpaths)
        os.chdir(args.destdir)
        gf.run('certificates')
        os.chdir(curdir)

    if wanted('sign'):
        sdkpaths = []
        sdkpaths.append(os.path.abspath(args.destdir))
        gf.set_search_paths(sdkpaths)
        os.chdir(args.destdir)
        gf.run('key_injection', keep_output=True)
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

        cmd = [ 'python3', 'gen_hash_tree.py',
                '-O', 'fvht.bin',
                'insert',
                '--signed', 'fvht.signed' ]
        subprocess.call(cmd)

        with open(eeprom_list) as f:
            eeproms = json.load(f)
            for skuid, value in eeproms.items():
                er.replace('qspi_image_hw.bin',
                    'qspi_image_hw.bin.{}'.format(skuid), value['filename'] + '.bin')

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
        tarfiles.append('fvht.bin')
        tarfiles.append(ROOTFS_FILE)
        tarfiles.extend(glob.glob('qspi_image_hw.bin*'))

        with tarfile.open('{chip}_sdk_signed_release.tgz'.format(chip=args.chip), mode='w:gz') as tar:
            for f in tarfiles:
                tar.add(f)

        os.chdir(curdir)

    if wanted('bundle'):
        os.chdir(args.destdir)
        shutil.rmtree('bundle_installer', ignore_errors=True)
        os.mkdir('bundle_installer')
        bundle_images = []

        with open("image.json") as f:
            images = json.load(f)
            bundle_images.extend([key for key,value in images['signed_images'].items()
                                if not value.get("no_export", False)])
            bundle_images.extend([key for key,value in images['signed_meta_images'].items()
                                if not value.get("no_export", False)])

        with open("mmc_image.json") as f:
            images = json.load(f)
            bundle_images.extend([key for key,value in images['generated_images'].items()
                                if not value.get("no_export", False)])

        bundle_images.extend([
            'install_tools/run_fwupgrade.py',
            'install_tools/setup.sh',
            'fvht.bin',
            ROOTFS_FILE
        ])

        for f in bundle_images:
            os.symlink(os.path.join(args.destdir, f), os.path.join('bundle_installer', os.path.basename(f)))

        makeself = [
            'makeself',
            '--follow',
            'bundle_installer',
            'setup_bundle.sh',
            'CCLinux/FunOS installer',
            './setup.sh'
        ]

        subprocess.call(makeself)

        os.chdir(curdir)

if __name__=="__main__":
    main()
