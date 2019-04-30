#!/usr/bin/python

import argparse
import binascii
import os
import shutil
import subprocess
import tempfile


class GlobalVars(object):
    pass


g = GlobalVars()

# LOAD_ADDR specifies an address in RAM where the data from MMC should be loaded to
# The exact location is not very important as long as it doesn't overlap with the
# execution address that u-boot will relocate data to (this is important for elf files,
# and might not be relevant if file format is changed and the data is loaded directly
# into the execution address)
LOAD_ADDR = 0xffffffff91000000

# Block size used by u-boot when operating on a raw MMC device. Unless a filesystem
# is used on top of the MMC, u-boot will only perform block-aligned block-size accesses,
# so it is important to ensure data is correctly aligned
BLOCK_SIZE = 512

# When FunOS is stored as raw data, byte offset from the beginning of the eMMC memory
# For dual partition image, this is the offset from the beginning of the second blob, ie.
# the second partition table
FUNOS_OFFSET = 33 * 1024 * 1024

# Similarily to how FunOS is stored, linux is stored as raw data blob at an offset
# from the beginning of eMMC memory (or second partition table).
LINUX_OFFSET = 128 * 1024 * 1024

# LINUX_LOAD_ADDR specifies where the linux image should start in RAM. This memory
# block will be mapped into the VZ Guest
LINUX_LOAD_ADDR = 0x9000000010100000

# see eSecure_rsa_structs.h::fw_fun_header_t for a description of
# the signature structure format. Signing info is always prepended to
# the signed content.
# The complete signature consists of:
#   .. signing_info_t (customer signature)
#   .. signing_info_t (fungible signature)
#   .. fw_fun_auth_header_t (firmware header)
FUN_SIGNATURE_SIZE = 4172

# Base offset of second software partition
PARTITION_OFFSET = 1024 * 1024 * 1024


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
           'of={}'.format(outfile_name),
           'count={:d}'.format(size),
           'iflag=count_bytes']
    subprocess.call(cmd)

def merge_file(infile_name, outfile_name):
    """Append infile file to the end of outfile file"""
    cmd = ['dd',
           'if={}'.format(infile_name),
           'of={}'.format(outfile_name),
           'oflag=append',
           'conv=notrunc']
    subprocess.call(cmd)

def gen_hex_file(infile_name, outfile_name, append):
    mode = 'ab' if append else 'wb'
    cmd = ['hexdump',
           '-v',
           '-e', '64/1 "%02X"',
           '-e', '"\n"']
    with open(outfile_name, mode) as outfile:
        with open(infile_name) as infile:
            subprocess.call(cmd, stdin=infile, stdout=outfile)


def crc32(filename):
    size = 65536
    res = 0
    with open(filename, 'rb') as f:
        b = f.read(size)
        while(len(b)):
            res = binascii.crc32(b, res)
            b = f.read(size)

    return res & 0xffffffff


def gen_boot_script(filename, funos_start_blk, linux_start_blk=-1):
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
    boot_pad_img = os.path.join(g.outdir, 'boot.pad.img')

    def filesize(f):
        hdr = FUN_SIGNATURE_SIZE if g.signed else 0
        return BLOCK_SIZE * (int((os.path.getsize(f) + hdr + BLOCK_SIZE - 1)) / BLOCK_SIZE)

    with open(filename, 'w') as outfile:
        outfile.write('if test -n "${mmcpart}"; then '\
                            'setexpr mmcstart ${mmcpart} - 1; else ' \
                            'setexpr mmcstart 0; ' \
                      'fi\n')

        if linux_start_blk >= 0:
            load_offset = FUN_SIGNATURE_SIZE if g.signed else 0
            outfile.write('setexpr linux_mmcstart ${{mmcstart}} * 0x{offset:x}\n'.format(
                    offset=PARTITION_OFFSET/BLOCK_SIZE))
            outfile.write('setexpr linux_mmcstart ${{linux_mmcstart}} + 0x{mmc_start_blk:x}\n'.format(
                    mmc_start_blk=linux_start_blk))
            outfile.write('mmc read 0x{load_addr:x} ${{linux_mmcstart}} 0x{load_size_blk:x};\n'.format(
                    load_addr=LINUX_LOAD_ADDR - load_offset,
                    load_size_blk=filesize(g.linux) / BLOCK_SIZE))
            if g.signed:
                outfile.write('authfw 0x{load_addr:x} {load_size:x};\n'.format(
                    load_addr=LINUX_LOAD_ADDR - load_offset,
                    load_size=os.path.getsize(g.linux)))

        outfile.write('setexpr funos_mmcstart ${{mmcstart}} * 0x{offset:x}\n'.format(
                offset=PARTITION_OFFSET/BLOCK_SIZE))
        outfile.write('setexpr funos_mmcstart ${{funos_mmcstart}} + 0x{mmc_start_blk:x}\n'.format(
                mmc_start_blk=funos_start_blk))
        outfile.write('mmc read 0x{load_addr:x} ${{funos_mmcstart}} 0x{load_size_blk:x};\n'.format(
            load_addr=LOAD_ADDR,
            load_size_blk=filesize(g.appfile) / BLOCK_SIZE))
        if g.crc:
            outfile.write('crc32 -v 0x{load_addr:x} {load_size:x} {crc:x};'.format(
                load_addr=LOAD_ADDR,
                load_size=os.path.getsize(g.appfile),
                crc=filesize(g.appfile)))
        if g.signed:
            outfile.write('authfw 0x{load_addr:x} {load_size:x};\n'.format(
                load_addr=LOAD_ADDR,
                load_size=os.path.getsize(g.appfile)))
            outfile.write('bootelf -p ${loadaddr};\n')
        else:
            outfile.write('bootelf -p 0x{load_addr:x};\n'.format(
                load_addr=LOAD_ADDR))

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
    pad_file(boot_img, boot_pad_img, BLOCK_SIZE)


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
    cmd = ['mkfs.ext4',
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
        pad_file(output_fs, f.name, 1124 * 1024 * 1024)
        cmd = ['sfdisk',
            '-X', 'dos',  # partition label
            f.name]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        sfdiskcmds = ['start=4KiB, size=32MiB, type=83, bootable', #32MB@4KB
                      'start={part_offset}KiB, size=32MiB, type=83'.format(
                          part_offset=(PARTITION_OFFSET/1024)+4)  #32MB@(base offset+4KB)
                    ]
        p.communicate(input="\n".join(sfdiskcmds))
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
    parser.add_argument('--linux', help='Path to linux image', metavar='VMLINUX')
    parser.add_argument(
        '-c', '--crc', help='Add crc check step', action='store_true')
    parser.add_argument(
        '--filesystem', help='Generate filesystem for eMMC', action='store_true')
    parser.add_argument(
        '--hex', help='Generate output in hex format (for Palladium)', action='store_true')
    parser.add_argument(
        '--signed', help='Input images are signed', action='store_true')
    parser.add_argument(
        '--fsfile', help='File(s) to put in the filesystem', action='append')
    parser.add_argument(
        '--bootscript-only', help='Only generate system boot script', action='store_true')

    parser.parse_args(namespace=g)

    linux_start_blk = (LINUX_OFFSET / BLOCK_SIZE) if g.linux else -1
    gen_boot_script(os.path.join(g.outdir, 'bootloader.scr'), FUNOS_OFFSET / BLOCK_SIZE,
                    linux_start_blk)

    if g.bootscript_only:
        return

    g.work_file = os.path.join(g.outdir, os.path.basename(g.appfile) + '.pad')

    pad_file(g.appfile, g.work_file, BLOCK_SIZE)

    outfile_hex = os.path.join(g.outdir, 'emmc_image.hex')
    outfile_bin = os.path.join(g.outdir, 'emmc_image.bin')

    files = []
    if g.filesystem:
        fs = gen_fs(g.fsfile)
        pad_file(fs, outfile_bin, FUNOS_OFFSET)
        merge_file(g.work_file, outfile_bin)
        if g.linux:
            os.rename(outfile_bin, outfile_bin + ".tmp")
            pad_file(outfile_bin + ".tmp", outfile_bin, LINUX_OFFSET)
            os.remove(outfile_bin + ".tmp")
            pad_file(g.linux, g.linux + ".tmp", BLOCK_SIZE)
            merge_file(g.linux + ".tmp", outfile_bin)
            os.remove(g.linux + ".tmp")
        files.append(outfile_bin)
    else:
        files.append(os.path.join(g.outdir, 'boot.pad.img'))
        files.append(g.work_file)

    if g.hex:
        for f in enumerate(files):
            gen_hex_file(f[1], outfile_hex, bool(f[0]))


if __name__ == '__main__':
    run()
