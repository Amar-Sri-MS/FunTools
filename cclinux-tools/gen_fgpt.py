#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate GPT install blob for use with FunVisor

File format:

4 bytes zero
8 bytes Region 0 LBA LE
8 bytes Region 1 LBA LE
5 * 4096 bytes Primary GPT header
5 * 4096 bytes Secondary GPT header

The final firmware image is formed by signing the output of this
script (assumed to be j.bin) like this:

sign_for_development.py --fourcc fgpt j.bin -o fgpt.signed --sign_key hkey1

"""

import argparse
import struct
import subprocess
import tempfile

###
## main
#
def main() -> int:
    """Entrypoint"""

    dev_size = 0x1c00000 * 0x200 # 14Gib
    header_size = 4096 * 5

    parser = argparse.ArgumentParser(description = 'GPT install blob builder')
    parser.add_argument('out_file', type=argparse.FileType('wb'), help = 'Output file')
    opts = parser.parse_args()

    blob_file = opts.out_file

    dev_file = tempfile.NamedTemporaryFile(mode='w+b')
    # Make a sparse file by writing 0 at very end.
    dev_file.seek(dev_size - 4)
    dev_file.write(struct.pack('<I', 0))
    dev_file.flush()

    #subprocess.run(['ls', '-l', dev_file.name])

    rv = subprocess.run(['parted', '-s', dev_file.name, '--', 'mklabel', 'gpt',
                         'mkpart', 'bxdata', 'ext2', '8192s', '65535s',
                         'mkpart', 'root', 'ext2', '65536s', '4194303s',
                         'mkpart', 'persist', 'ext2', '4194304s', '27262975s',
                         'mkpart', 'root.hashtree', 'ext2', '27262976s', '-1M'])

    rv.check_returncode()

    # Write the headers.
    blob_file.write(struct.pack('<I', 0))
    blob_file.write(struct.pack('<Q', 0x0400000))
    blob_file.write(struct.pack('<Q', 0x2000000))

    dev_file.seek(0)
    primary = dev_file.read(header_size)
    if (len(primary) != header_size):
        raise RuntimeError("Short read: %d" % len(primary))

    dev_file.seek(dev_size - header_size)

    secondary = dev_file.read(header_size)
    if (len(secondary) != header_size):
        raise RuntimeError("Short read: %d" % len(primary))

    blob_file.write(primary)
    blob_file.write(secondary)
    blob_file.close()

    return 0

###
## entrypoint
#
if __name__ == "__main__":
    main()

