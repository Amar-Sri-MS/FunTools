#!/usr/bin/env python3

import argparse
import os
import sys
import subprocess
import tempfile

def run():
    rootdir = os.path.dirname(os.path.realpath(sys.argv[0]))

    parser = argparse.ArgumentParser(description='Generate an emmc image')

    parser.add_argument('-v', '--version', type=int, default=1, help='Image version')
    parser.add_argument('-d', '--destination', help='Emmc image location', required=True)
    parser.add_argument('funos', nargs=1, help='Path to FunOS application')

    args = parser.parse_args()

    try:
        destdir = os.path.realpath(args.destination)
        os.makedirs(destdir)
    except FileExistsError:
        pass

    appfile = os.path.realpath(args.funos[0])

    with tempfile.TemporaryDirectory() as tmpdir:
        curdir = os.curdir
        os.chdir(tmpdir)

        gen_boot_img = [os.path.join(rootdir, 'make_emulation_emmc.py'),
            '--workspace', os.getenv('WORKSPACE', '.'),
            '--outdir', destdir,
            '--filesystem', '--signed', '--bootscript-only',
            '--appfile', appfile]
        subprocess.call(gen_boot_img)

        # temporary until we have better handling of various filenames
        # inside the json file
        os.link(appfile, os.path.join(tmpdir, 'funos-f1.stripped'))

        sign_cmd = [os.path.join(rootdir, 'generate_flash.py'),
            '--source-dir', tmpdir,
            '--source-dir', destdir,
            '--action', 'sign',
            '--force-version', str(args.version),
            os.path.join(rootdir, 'mmc_config_fungible.json'),
            os.path.join(rootdir, 'key_bag_config.json')]

        subprocess.call(sign_cmd)

        gen_boot_img = [os.path.join(rootdir, 'make_emulation_emmc.py'),
            '--workspace', os.getenv('WORKSPACE', '.'),
            '--outdir', destdir,
            '--filesystem', '--signed',
            '--appfile', 'funos.signed.bin',
            '--fsfile', 'boot.img.signed']
        subprocess.call(gen_boot_img)

        os.chdir(curdir)




if __name__ == '__main__':
    run()
