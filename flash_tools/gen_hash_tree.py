#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate SHA512 hash tree file for use with FunVisor

For a SHA512 hash, the size is 64 bytes (512 bits / 8 bits per byte ==
64 bytes), which allows 64 hashes to be stored in a 4096 byte
block. The format of the tree is at the Nth level (the leaves) we have
hashes of each file block.  At level N-1 we have hashes over a block
of hashes from Level N. At the root we have a single hash over the
block of 64 1st level hashes. With a tree of depth N we can cover a
file of size (4096 * 64^N). The number of hashes at each level are
then: 64, 4096, 262114, 16777216, ...

A request to read a block from the underlying file is authenticated by
first calculating its hash, and then comparing it to the hash stored
in the table, this is iterated until the root of the tree is
reached. For a file of size smaller than 1GiB, any block can be
authenticated with four block reads and a hash calculation (four
hashes) at each level. The hash blocks closer to the root may be
cached to reduce the authentication effort.

To guard against file contents being changed after authentication, we
must authenticate on each block read. Without the use of a hash tree,
the entire 1GiB file would have to be read and hashed each time it
needed to be authenticated. For a file backing a long lived file
system, the number of block reads done in the life of the system make
this authentication technique impractical.

File format for the hash tree is (in 4096 byte blocks):

0..1:   Fungible signature over:
           [4 bytes: zero fill to achieve 8 byte alignement]
           [8 bytes: little-endian input file size]
           [64 bytes: SHA512 of tree root block (in block 2)]
           [72 bytes: 36 UTF-16LE code units target partition name]

        This structure is duplicated at offset 8192 - 148 (very end of
        the 2nd block)

2:      1st level hashes, SHA512 hashes of the 64 2nd level hash blocks

3..66:  2nd level hashes, SHA512 hashes of the 4096 3rd level hash blocks

67.. :  3rd level hashes, SHA512 hashes of up to 262144 file blocks

With 3 levels, a file of up to 2^30 bytes can be hashed.  For larger
files, an additional hash level is added.

"""

import abc
import argparse
import hashlib
import io
import math
import struct

from argparse import ArgumentParser, Namespace
from typing import BinaryIO

BLOCK_BITS: int = 12
BLOCK_SIZE: int = pow(2, BLOCK_BITS)

HASH_BITS: int = 6
HASH_SIZE: int = pow(2, HASH_BITS)

HASH_PER_BLOCK: int = pow(2, BLOCK_BITS - HASH_BITS)

TO_SIGN_SIZE: int = 148
SIGNED_SIZE: int = TO_SIGN_SIZE + 0x104c

###
## HashSink
#
class HashSink(abc.ABC):

    @abc.abstractmethod
    def add_data(self, data: bytes) -> None:
        """Add data to the hash"""
        pass

    @abc.abstractmethod
    def source_eof(self) -> None:
        """Indicate that no more data is expected"""
        pass

###
## HashRoot
#
class HashRoot(HashSink):
    def __init__(self):
        self.hash = hashlib.sha512()

    def add_data(self, data: bytes) -> None:
        self.hash.update(data)

    def source_eof(self) -> None:
        print("Hash: %s" % self.hash.hexdigest())

###
## HashNode
#
class HashNode(HashSink):
    parent: HashSink
    file: BinaryIO
    file_offset: int
    max_file_offset: int
    pos: int
    expected_data_size: int

    def __init__(self, parent: HashSink, file: BinaryIO,
                 file_offset: int, max_file_offset: int, expected_data_size: int):
        self.parent = parent
        self.file = file
        self.hash = hashlib.sha512()
        self.file_offset = file_offset
        self.max_file_offset = max_file_offset
        self.expected_data_size = expected_data_size
        self.pos = 0
        return

    def _write_hash(self) -> None:
        self.file.seek(self.file_offset)
        digest = self.hash.digest()
        self.file.write(digest)
        self.parent.add_data(digest)
        self.file_offset += len(digest)
        self.hash = hashlib.sha512()
        self.pos = 0
        return

    def add_data(self, data: bytes) -> None:
        if (len(data) != self.expected_data_size):
            raise RuntimeError("Illegal data block size: %d" % len(data))
        self.hash.update(data)
        self.pos += len(data);
        if (self.pos > BLOCK_SIZE):
            raise RuntimeError("Blocksize overrun: %d" % self.pos)
        if (self.pos == BLOCK_SIZE):
            self._write_hash()
        return

    def source_eof(self) -> None:
        # For the last level, the last block of hashes may be
        # partially filled if the underlying file is smaller than what
        # would fill the entire block. Emit hashes as if the
        # underlying file were padded out with zeros to the hash block
        # boundary.
        while ((self.file_offset & (BLOCK_SIZE - 1)) != 0):
            self.add_data(bytes(self.expected_data_size))

        # complete the level corresponding to positions beyond
        # the end of the input file with valid data so parent
        # hashes can be calculated.
        fill = bytes(HASH_SIZE)
        while (self.file_offset < self.max_file_offset):
            self.parent.add_data(fill)
            self.file_offset += len(fill)

        self.parent.source_eof()
        return

###
## hash_file_pos_for_level
#
def hash_file_pos_for_level(level: int) -> int:
    """Return the offset of the hashes at the specified level.

    Each level contains HASH_PER_BLOCK times as many hashes as the
    previous level.  Start offset is just the sum of the first N
    elements of this geometric series offset by a constant.
    """
    block_offset = 2
    start_block = int((pow(HASH_PER_BLOCK, level) - 1) / (HASH_PER_BLOCK - 1))
    return  BLOCK_SIZE * (start_block + block_offset)

###
## do_gen_tree
#
def do_gen_tree(opts: Namespace) -> int:

    # GPT allows up to 36 characters, but we limit to 35 to allow for null termination.
    if (len(opts.partition_name) > 35):
        print("Error: Partition name exceeds 35")
        return 1

    in_file = open(opts.in_file, mode = 'rb')
    hash_file = open(opts.hash_file, mode = 'wb')
    to_sign_file = open(opts.to_sign, mode = 'wb')

    in_file.seek(0, io.SEEK_END)
    in_len = in_file.tell()
    in_file.seek(0, io.SEEK_SET)

    if (in_len <= BLOCK_SIZE):
        print("Error: Input file must be larger than %d" % BLOCK_SIZE)
        return 1

    bits_needed = math.ceil(math.log2(in_len))
    levels_needed = math.ceil((bits_needed - BLOCK_BITS) / (BLOCK_BITS - HASH_BITS))

    print("Input file len: %d, bits needed: %d, levels: %d" % (in_len, bits_needed, levels_needed))

    hr: HashRoot = HashRoot()
    parent: HashSink = hr

    for level in range(levels_needed):
        if (level == levels_needed - 1):
            expected_data_size = BLOCK_SIZE
        else:
            expected_data_size = HASH_SIZE
        this_level_start = hash_file_pos_for_level(level)
        next_level_start = hash_file_pos_for_level(level + 1)
        hn = HashNode(parent, hash_file, this_level_start, next_level_start, expected_data_size)
        parent = hn

    while True:
        block_data = in_file.read(BLOCK_SIZE)
        if (len(block_data) == 0):
            hn.source_eof()
            break
        hn.add_data(block_data)

    partition_name_blob = bytearray(72)
    partition_name_bytes = opts.partition_name.encode("utf-16le")
    partition_name_blob[0:len(partition_name_bytes)] = partition_name_bytes

    hash_file.seek(2 * BLOCK_SIZE - 8 - HASH_SIZE - len(partition_name_blob))
    hash_file.write(struct.pack('<Q', in_len)) # 8 bytes LE file size
    hash_file.write(hr.hash.digest()) # The root hash
    hash_file.write(partition_name_blob)
    hash_file.close()
    in_file.close()

    to_sign_file.write(bytes(4))                  # 4 bytes zero padding
    to_sign_file.write(struct.pack('<Q', in_len)) # LE length
    to_sign_file.write(hr.hash.digest())          # SHA512 root hash
    to_sign_file.write(partition_name_blob)       # UTF-16LE patition name
    current_pos = to_sign_file.tell()
    assert (current_pos == TO_SIGN_SIZE)
    to_sign_file.close()

    return 0

###
##
#
def do_insert(opts: Namespace) -> int:
    hash_file = open(opts.hash_file, mode = 'r+b')
    signed_file = open(opts.signed, mode = 'rb')

    # Put the signed blob in the beginning of the hash file.
    signed_blob = signed_file.read(SIGNED_SIZE)
    hash_file.write(signed_blob)
    hash_file.seek(2 * BLOCK_SIZE - TO_SIGN_SIZE)
    duplicate_hashinfo = hash_file.read(TO_SIGN_SIZE)
    hash_file.close()
    signed_file.close()

    hashinfo = signed_blob[-TO_SIGN_SIZE:len(signed_blob)]

    assert(duplicate_hashinfo == hashinfo)
    return 0

###
## main
#
def main() -> int:
    """Entrypoint"""
    parser = ArgumentParser(description = "File hash tree builder")
    parser.add_argument('-O', dest = 'hash_file',
                        help = 'Output hash file', required = True)
    subparsers = parser.add_subparsers(dest='command', help = "command")
    hash_parser = subparsers.add_parser('hash', help = 'Generate hash tree and file to sign')
    hash_parser.add_argument('--name', '-N', dest = 'partition_name',
                             help = 'Target partition name', required = True)
    hash_parser.add_argument('--to-sign', '-S',
                             help = 'File of output hash contents to be signed',
                             required = True)
    hash_parser.add_argument('-I', dest = 'in_file', metavar = 'FILE_TO_HASH',
                             help = 'Input file to hash', required = True)

    insert_parser = subparsers.add_parser('insert',
                                          help = 'Insert signed hash into hash tree file')
    insert_parser.add_argument('--signed', '-s',
                               help = 'File of signed hash contents to be inserted to the hash file',
                               required = True)

    opts = parser.parse_args()

    if (opts.command == 'hash'):
        return do_gen_tree(opts)
    if (opts.command == 'insert'):
        return do_insert(opts)
    else:
        print("Error: Unrecognized command \"%s\"" % opts.command)
        parser.print_help()
        return 1

###
## entrypoint
#
if __name__ == "__main__":
    main()
