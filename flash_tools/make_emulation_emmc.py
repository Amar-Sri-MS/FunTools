#!/usr/bin/env python3

'''
Copyright (c) 2019-2020 Fungible, inc.
All Rights Reserved.
'''

import argparse
import binascii
import json
import os
import platform
import shutil
import subprocess
import tempfile

import os_utils

class GlobalVars(object):
    pass


g = GlobalVars()

KB = 1024
MB = KB ** 2
GB = KB ** 3

# LOAD_ADDR specifies an address in RAM where the data from MMC should be loaded to
# The exact location is not very important as long as it doesn't overlap with the
# execution address that u-boot will relocate data to (this is important for elf files,
# and might not be relevant if file format is changed and the data is loaded directly
# into the execution address)
LOAD_ADDR = 0xa800000021000000

# Block size used by u-boot when operating on a raw MMC device. Unless a filesystem
# is used on top of the MMC, u-boot will only perform block-aligned block-size accesses,
# so it is important to ensure data is correctly aligned
BLOCK_SIZE = 512

# Base offset of second software partition
PARTITION_OFFSET = 1 * GB

# When FunOS is stored as raw data, byte offset from the beginning of the eMMC memory
# For dual partition image, this is the offset from the beginning of the second blob, ie.
# the second partition table
FUNOS_OFFSET = 33 * MB

# Similarily to how FunOS is stored, config blob is stored as raw data blob at an offset
# from the beginning of eMMC memory (or second partition table).
CCFG_OFFSET = PARTITION_OFFSET - 1 * MB

# see eSecure_rsa_structs.h::fw_fun_header_t for a description of
# the signature structure format. Signing info is always prepended to
# the signed content.
# The complete signature consists of:
#   .. signing_info_t (customer signature)
#   .. signing_info_t (fungible signature)
#   .. fw_fun_auth_header_t (firmware header)
FUN_SIGNATURE_SIZE = 4172



def pad_file(infile_name, outfile_name, size):
    """Append zeros to the end of file to extend its size to @size"""
    cmd = ['dd',
           'if={}'.format(infile_name),
           'of={}'.format(outfile_name),
           'ibs={:d}'.format(size),
           'conv=sync']
    subprocess.call(cmd)

def trunc_file(infile_name, outfile_name, size):
    """Remove bytes from end of file to truncate its size to @size"""
    cmd = ['dd',
           'if={}'.format(infile_name),
           'of={}'.format(outfile_name) ]
    if platform.system() == 'Linux':
        cmd.extend([
           'count={:d}'.format(size),
           'iflag=count_bytes'])
    else:
        # MacOS dd is dumb ...
        cmd.extend([
            'count=1',
            'bs={:d}'.format(size)
        ])
    subprocess.call(cmd)

def trunc_head_file(infile_name, outfile_name, size):
    """Remove @size bytes from beginning of file"""
    with open(outfile_name, 'wb') as outfile:
        with open(infile_name, 'rb') as infile:
            infile.seek(size, 0)
            while True:
                data = infile.read(4096)
                if data:
                    outfile.write(data)
                else:
                    break


def merge_file(infile_name, outfile_name):
    """Append infile file to the end of outfile file"""
    with open(outfile_name, 'ab') as outfile:
        with open(infile_name, 'rb') as infile:
            outfile.seek(0, 2)
            while True:
                data = infile.read(4096)
                if data:
                    outfile.write(data)
                else:
                    break


def gen_hex_file(infile_name, outfile_name, append, width, reverse):
    mode = 'a' if append else 'w'
    with open(outfile_name, mode) as outfile:
        with open(infile_name, 'rb') as infile:
            while True:
                data = infile.read(width)
                if data:
                    if reverse:
                        data = bytes(reversed(data))
                    outfile.write(data.hex().upper() + '\n')
                else:
                    break


def crc32(filename):
    size = 65536
    res = 0
    with open(filename, 'rb') as f:
        b = f.read(size)
        while(len(b)):
            res = binascii.crc32(b, res)
            b = f.read(size)

    return res & 0xffffffff


def gen_boot_script(filename, funos_start_blk, ccfg_start_blk):
    """Generate a u-boot boot script

    This is the default boot script to be loaded by u-boot.
    Its location and name are hardcoded in u-boot's built-in
    cmdline.
    If a filesystem is expected to be used (--filesystem),
    boot.img script file is generated. For a raw boot image without
    a filesystem, the boot.img script is padded to occupy
    1st full sector of the memory (512 bytes)
    """
    boot_img = os.path.join(g.outdir, 'boot.img')

    def filesize(f):
        hdr = FUN_SIGNATURE_SIZE if g.signed else 0
        return BLOCK_SIZE * int((os.path.getsize(f) + hdr + BLOCK_SIZE - 1) / BLOCK_SIZE)

    with open(filename, 'w') as outfile:
        outfile.write('if test -n "${mmcpart}"; then '\
                            'setexpr mmcstart ${mmcpart} - 1; else ' \
                            'setexpr mmcstart 0; ' \
                      'fi\n')

        outfile.write('setexpr funos_mmcstart ${{mmcstart}} * 0x{offset:x}\n'.format(
                offset=int(PARTITION_OFFSET/BLOCK_SIZE)))
        outfile.write('setexpr ccfg_mmcstart ${{funos_mmcstart}} + 0x{ccfg_start_blk:x}\n'.format(
                ccfg_start_blk=ccfg_start_blk))
        outfile.write('setexpr funos_mmcstart ${{funos_mmcstart}} + 0x{mmc_start_blk:x}\n'.format(
                mmc_start_blk=funos_start_blk))
        outfile.write('mmc read 0x{load_addr:x} ${{funos_mmcstart}} 0x{load_size_blk:x};\n'.format(
            load_addr=LOAD_ADDR,
            load_size_blk=int(filesize(g.appfile) / BLOCK_SIZE)))
        if g.crc:
            outfile.write('crc32 -v 0x{load_addr:x} {load_size:x} {crc:x};'.format(
                load_addr=LOAD_ADDR,
                load_size=os.path.getsize(g.appfile),
                crc=filesize(g.appfile)))
        if g.signed:
            outfile.write('authfw 0x{load_addr:x} {load_size:x};\n'.format(
                load_addr=LOAD_ADDR,
                load_size=filesize(g.appfile)))
        outfile.write('elf_get_extent ${loadaddr};\n')
        blob_mmc_addr = int(filesize(g.appfile) / BLOCK_SIZE) # relative to funos mmc addr
        blob_addr = 0 # relative to elf_extent
        for blob in g.blob:
            # for each of the blobs calculate mmc and load location
            # all blobs are stored sector-aligned after funos directly in emmc
            # and loaded into RAM directly after funos runtime space
            # This is somewhat limited by the amount of RAM before u-boot runtime,
            # so loading a few hundred MBs of blobs would not work and will
            # result in uboot crashing ... alternatively we could load in a higher
            # memory region, but then we'll have more fragmentation in memory.
            # Something to consider if needed in the future.
            outfile.write('setexpr blob_addr ${{elf_extent}} + 0x{blob_addr:x}\n'.format(
                blob_addr=blob_addr))
            outfile.write('setexpr blob_mmcstart ${{funos_mmcstart}} + 0x{blob_mmc_addr:x}\n'.format(
                blob_mmc_addr=blob_mmc_addr))
            outfile.write('mmc dev; mmc read ${{blob_addr}} ${{blob_mmcstart}} 0; loadblob ${{blob_addr}};\n'.format())
            blob_mmc_addr += int(filesize(blob) / BLOCK_SIZE)
            blob_addr += filesize(blob)

        outfile.write('setexpr ccfg_addr ${{elf_extent}} + 0x{blob_addr:x}\n'.format(
                blob_addr=blob_addr))
        outfile.write('mmc dev; mmc read ${ccfg_addr} ${ccfg_mmcstart} 0; loadblob ${ccfg_addr};\n')
        outfile.write('setenv bss_clear 0;\n')
        outfile.write('bootelf -p ${loadaddr};\n')

    # default location in full Fungible workspace
    mkimage_path = os.path.join(g.workspace, 'u-boot', 'tools', 'mkimage')
    if not os.path.isfile(mkimage_path):
        # fallback for the current working directory root
        mkimage_path = os.path.join(g.workspace, 'mkimage')
    if not os.path.isfile(mkimage_path):
        # last resort - assume there's on in the $PATH
        mkimage_path = 'mkimage'

    cmd = [ mkimage_path,
           '-A', 'mips64',
           '-T', 'script',
           '-C', 'none',
           '-n', 'mmc boot script',
           '-d', filename,
           boot_img]
    subprocess.call(cmd)


def gen_fs(files):
    """Generate a filesystem image

    Generate a filesystem image to be programmed to the eMMC.
    The image consists of a DOS-style partition table and an
    ext4 partition containing boot script and the application
    file (--appfile).
    The following assumptions are made:
    * boot script is called 'boot.img' (as generated by @gen_boot_script())
    * the ext4 partition is 64M (likely to be changed in the future)
    """

    output_fs = os.path.join(g.outdir, 'emmc.ext4')
    # prepare fs contents
    tempdir = tempfile.mkdtemp()
    if files:
        for f in files:
            shutil.copy(f, tempdir)
    else:
        shutil.copy(os.path.join(g.outdir, 'boot.img'), tempdir)
    cmd = [ os_utils.path_fixup('mkfs.ext4'),
           '-E', 'offset=4096',  # partition offset
           '-d', tempdir,  # filesystem contents
           '-F',  # force output
           '-b', '4k',  # 4k blocks
           output_fs,  # destination filename
           '30M'  # filesystem size
           ]

    subprocess.call(cmd)
    shutil.rmtree(tempdir)
    with tempfile.NamedTemporaryFile() as f:
        # A temporary large file is required here so that it is big enough
        # to contain both partitions requested from sfdisk - as sfdisk will
        # reject creating partition pointers to offsets greater than the
        # 'device' size (device in this context is the file that is being changed)
        pad_file(output_fs, f.name, 1124 * MB)
        cmd = [ os_utils.path_fixup('sfdisk'),
            '-X', 'dos',  # partition label
            '--color=never',
            f.name]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        sfdiskcmds = ['start=4KiB, size=32MiB, type=83, bootable', #32MB@4KB
                      'start={part_offset}KiB, size=32MiB, type=83'.format(
                          part_offset=int(PARTITION_OFFSET/KB)+4)  #32MB@(base offset+4KB)
                    ]
        p.communicate(input="\n".join(sfdiskcmds).encode())
        trunc_file(f.name, output_fs, FUNOS_OFFSET)
    return output_fs


def run():
    parser = argparse.ArgumentParser(description='Generate an emmc image file')

    parser.add_argument('-w', '--workspace',
                        help='Workspace directory', required=True)
    parser.add_argument(
        '-o', '--outdir', help='Output directory', required=True)
    parser.add_argument('-f', '--appfile',
                        help='Application file', required=True)
    parser.add_argument(
        '-c', '--crc', help='Add crc check step', action='store_true')
    parser.add_argument(
        '--filesystem', help='[ignored]', action='store_true')
    parser.add_argument(
        '--hex', help='Generate output in hex format (for Palladium)', action='store_true')
    parser.add_argument(
        '--hex-width', help='Hex output width in bytes (F1,S1 need 64, F1D1 needs 32)',
        type=int, default=32
    )
    parser.add_argument(
        '--hex-reverse', help='Hex output should have bytes reversed in each output line',
        action='store_true'
    )
    parser.add_argument(
        '--signed', help='Input images are signed', action='store_true')
    parser.add_argument(
        '--fsfile', help='File(s) to put in the filesystem', action='append')
    parser.add_argument(
        '--bootscript-only', help='Only generate system boot script', action='store_true')
    parser.add_argument(
        '--blob', default=[], help='Signed blobs to put in emmc', action='append')

    parser.parse_args(namespace=g)

    if len(g.blob) > 3:
        # This is a limitation of u-boot at the moment. We can remove this check
        # when u-boot is fixed to support more easily. On the other hand we should
        # not really need to embed more files in emmc, so that should not be
        # a major problem
        parser.error("At most 3 blobs can be provided")

    # there are 2 code paths when we want to generate bootscript
    # 1) with bootscript-only the bootscript is generated, it is later signed
    #    and passed to this script as fsfile together with filesystem flag
    # 2) when we don't need a signed bootloader, then the script is
    #    invoked only once and the boot.img is immediately embedded in the
    #    filesystem (see gen_fs()), so in this scenario generate the script
    #    and continue execution
    if g.bootscript_only:
        gen_boot_script(os.path.join(g.outdir, 'bootloader.scr'), int(FUNOS_OFFSET / BLOCK_SIZE),
                    int(CCFG_OFFSET / BLOCK_SIZE))
        if g.bootscript_only:
            return

    g.work_file = os.path.join(g.outdir, os.path.basename(g.appfile) + '.pad')

    pad_file(g.appfile, g.work_file, BLOCK_SIZE)

    outfile_hex = os.path.join(g.outdir, 'emmc_image.hex')
    outfile_bin = os.path.join(g.outdir, 'emmc_image.bin')

    files = []

    fs = gen_fs(g.fsfile)
    pad_file(fs, outfile_bin, FUNOS_OFFSET)
    merge_file(g.work_file, outfile_bin)
    files.append(outfile_bin)

    for b in g.blob:
        blob_padded = os.path.join(g.outdir, os.path.basename(b) + '.pad')
        pad_file(b, blob_padded, BLOCK_SIZE)
        merge_file(blob_padded, outfile_bin)

    outfile_mmc0 = os.path.join(g.outdir, 'mmc0_image.bin')
    outfile_mmc1 = os.path.join(g.outdir, 'mmc1_image.bin')
    trunc_file(outfile_bin, outfile_mmc0, 4 * KB)
    trunc_head_file(outfile_bin, outfile_mmc1, 4 * KB)

    if g.hex:
        for f in enumerate(files):
            gen_hex_file(f[1], outfile_hex, bool(f[0]), g.hex_width, g.hex_reverse)

    output_descr = {
        'emmc_image.bin' : { 'description':'complete eMMC image', 'no_bundle':True },
        'mmc0_image.bin' : { 'description':'eMMC partition table', 'no_bundle':False },
        'mmc1_image.bin' : { 'description':'eMMC boot partition and FunOS', 'no_bundle':False },
    }

    os.remove(g.work_file)

    with open("mmc_image.json", "w") as f:
        config = { 'generated_images' : {}}
        for k,v in output_descr.items():
            config['generated_images'][k] = { 'description' : v['description'],
                'no_bundle' : v['no_bundle'] }
        json.dump(config, f, indent=4)

if __name__ == '__main__':
    run()
