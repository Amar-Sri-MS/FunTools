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
           [8 bytes: little-endian input file size]
           [64 bytes: SHA512 of tree root block (in block 2)]

        This structure is duplicated at offset 8192 - 72 (very end of
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

from typing import BinaryIO

BLOCK_BITS: int = 12
BLOCK_SIZE: int = pow(2, BLOCK_BITS)

HASH_BITS: int = 6
HASH_SIZE: int = pow(2, HASH_BITS)

HASH_PER_BLOCK: int = pow(2, BLOCK_BITS - HASH_BITS)

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
        # complete the level corresponding to positions beyound
        # the end of the input file with valid data so parent
        # hashes can be calculated.
        fill_digest = hashlib.sha512().digest()
        while (self.file_offset < self.max_file_offset):
            self.parent.add_data(fill_digest)
            self.file_offset += len(fill_digest)

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
## main
#
def main() -> int:
    """Entrypoint"""
    parser = argparse.ArgumentParser(description = 'File hash tree builder')
    parser.add_argument('in_file', type=argparse.FileType('rb'), help = 'Input file')
    parser.add_argument('hash_file', type=argparse.FileType('wb'), help = 'Output hash file')
    opts = parser.parse_args()

    in_file = opts.in_file
    hash_file = opts.hash_file

    in_file.seek(0, io.SEEK_END)
    in_len = in_file.tell()
    in_file.seek(0, io.SEEK_SET)

    if (in_len <= BLOCK_SIZE):
        print("Error: Input file must be larger than %d" % BLOCK_SIZE)
        return 1

    bits_needed = math.ceil(math.log2(in_len))
    levels_needed = math.ceil((bits_needed - BLOCK_BITS) / HASH_BITS)

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

    hash_file.seek(2 * BLOCK_SIZE - 8 - HASH_SIZE, io.SEEK_SET)
    hash_file.write(struct.pack('<Q', in_len)) # 8 bytes LE file size
    hash_file.write(hr.hash.digest()) # The root hash
    hash_file.close()
    in_file.close()

    return 0

###
## entrypoint
#
if __name__ == "__main__":
    main()
