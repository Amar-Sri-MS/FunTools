#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create EDK2 variable store image

static check:
% mypy create-varstore.py

format:
% python3 -m black create-varstore.py
"""

from typing import List, Optional, Type, Dict, Any, Tuple, Union
import argparse
import codecs
import io
import struct
import uuid

###
##  parse_args
#
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create an initialized ACU UEFI variable store backing blob")

    parser.add_argument("--timeout", action="store", type=int,
                        help="Add a timeout variable with the specified value")

    parser.add_argument("--guid-part-path", action="store", type=str,
                        help='String of the form: "name,part-number,start-lba,size-lba,guid,path". Boot0000 is created as first in BootOrder')
    # Required positional argument
    parser.add_argument("out_file", help="Output File", type=argparse.FileType('w+b'))

    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Verbosity (-v, -vv, etc)")

    args: argparse.Namespace = parser.parse_args()
    return args

EFI_SYSTEM_NV_DATA_FV_GUID      = uuid.UUID('{fff12b8d-7696-4c8b-a9852747075b4f50}')
EFI_AUTHENTICATED_VARIABLE_GUID = uuid.UUID('{aaf32c78-947b-439a-a1802e144ec37792}')
EFI_GLOBAL_VARIABLE_GUID        = uuid.UUID('{8be4df61-93ca-11d2-aa0d00e098032b8c}')

EFI_FVH_SIGNATURE = b'_FVH'
EFI_FVH_REVISION  = 0x02

EFI_FVB2_READ_DISABLED_CAP   = 0x00000001
EFI_FVB2_READ_ENABLED_CAP    = 0x00000002
EFI_FVB2_READ_STATUS         = 0x00000004
EFI_FVB2_WRITE_DISABLED_CAP  = 0x00000008
EFI_FVB2_WRITE_ENABLED_CAP   = 0x00000010
EFI_FVB2_WRITE_STATUS        = 0x00000020
EFI_FVB2_LOCK_CAP            = 0x00000040
EFI_FVB2_LOCK_STATUS         = 0x00000080
EFI_FVB2_STICKY_WRITE        = 0x00000200
EFI_FVB2_MEMORY_MAPPED       = 0x00000400
EFI_FVB2_ERASE_POLARITY      = 0x00000800
EFI_FVB2_READ_LOCK_CAP       = 0x00001000
EFI_FVB2_READ_LOCK_STATUS    = 0x00002000
EFI_FVB2_WRITE_LOCK_CAP      = 0x00004000
EFI_FVB2_WRITE_LOCK_STATUS   = 0x00008000
EFI_FVB2_ALIGNMENT           = 0x001F0000
EFI_FVB2_ALIGNMENT_1         = 0x00000000
EFI_FVB2_ALIGNMENT_2         = 0x00010000
EFI_FVB2_ALIGNMENT_4         = 0x00020000
EFI_FVB2_ALIGNMENT_8         = 0x00030000
EFI_FVB2_ALIGNMENT_16        = 0x00040000
EFI_FVB2_ALIGNMENT_32        = 0x00050000
EFI_FVB2_ALIGNMENT_64        = 0x00060000
EFI_FVB2_ALIGNMENT_128       = 0x00070000
EFI_FVB2_ALIGNMENT_256       = 0x00080000
EFI_FVB2_ALIGNMENT_512       = 0x00090000
EFI_FVB2_ALIGNMENT_1K        = 0x000A0000
EFI_FVB2_ALIGNMENT_2K        = 0x000B0000
EFI_FVB2_ALIGNMENT_4K        = 0x000C0000
EFI_FVB2_ALIGNMENT_8K        = 0x000D0000
EFI_FVB2_ALIGNMENT_16K       = 0x000E0000
EFI_FVB2_ALIGNMENT_32K       = 0x000F0000
EFI_FVB2_ALIGNMENT_64K       = 0x00100000
EFI_FVB2_ALIGNMENT_128K      = 0x00110000
EFI_FVB2_ALIGNMENT_256K      = 0x00120000
EFI_FVB2_ALIGNMENT_512K      = 0x00130000
EFI_FVB2_ALIGNMENT_1M        = 0x00140000
EFI_FVB2_ALIGNMENT_2M        = 0x00150000
EFI_FVB2_ALIGNMENT_4M        = 0x00160000
EFI_FVB2_ALIGNMENT_8M        = 0x00170000
EFI_FVB2_ALIGNMENT_16M       = 0x00180000
EFI_FVB2_ALIGNMENT_32M       = 0x00190000
EFI_FVB2_ALIGNMENT_64M       = 0x001A0000
EFI_FVB2_ALIGNMENT_128M      = 0x001B0000
EFI_FVB2_ALIGNMENT_256M      = 0x001C0000
EFI_FVB2_ALIGNMENT_512M      = 0x001D0000
EFI_FVB2_ALIGNMENT_1G        = 0x001E0000
EFI_FVB2_ALIGNMENT_2G        = 0x001F0000
EFI_FVB2_WEAK_ALIGNMENT      = 0x80000000

VARIABLE_STORE_FORMATTED = 0x5a
VARIABLE_STORE_HEALTHY   = 0xfe

VARIABLE_DATA  = 0x55AA

VAR_IN_DELETED_TRANSITION  = 0xfe     # Variable is in obsolete transition.
VAR_DELETED                = 0xfd     # Variable is obsolete.
VAR_HEADER_VALID_ONLY      = 0x7f     # Variable header has been valid.
VAR_ADDED                  = 0x3f     # Variable has been completely added.

EFI_VARIABLE_NON_VOLATILE                = 0x00000001
EFI_VARIABLE_BOOTSERVICE_ACCESS          = 0x00000002
EFI_VARIABLE_RUNTIME_ACCESS              = 0x00000004
EFI_VARIABLE_HARDWARE_ERROR_RECORD       = 0x00000008
EFI_VARIABLE_AUTHENTICATED_WRITE_ACCESS  = 0x00000010
EFI_VARIABLE_TIME_BASED_AUTHENTICATED_WRITE_ACCESS  = 0x00000020

VARIABLE_ATTRIBUTE_NV_BS           = (EFI_VARIABLE_NON_VOLATILE | EFI_VARIABLE_BOOTSERVICE_ACCESS)
VARIABLE_ATTRIBUTE_BS_RT           = (EFI_VARIABLE_BOOTSERVICE_ACCESS | EFI_VARIABLE_RUNTIME_ACCESS)
VARIABLE_ATTRIBUTE_BS_RT_AT        = (VARIABLE_ATTRIBUTE_BS_RT | EFI_VARIABLE_TIME_BASED_AUTHENTICATED_WRITE_ACCESS)
VARIABLE_ATTRIBUTE_NV_BS_RT        = (VARIABLE_ATTRIBUTE_BS_RT | EFI_VARIABLE_NON_VOLATILE)
VARIABLE_ATTRIBUTE_NV_BS_RT_HR     = (VARIABLE_ATTRIBUTE_NV_BS_RT | EFI_VARIABLE_HARDWARE_ERROR_RECORD)
VARIABLE_ATTRIBUTE_NV_BS_RT_AT     = (VARIABLE_ATTRIBUTE_NV_BS_RT | EFI_VARIABLE_TIME_BASED_AUTHENTICATED_WRITE_ACCESS)
VARIABLE_ATTRIBUTE_AT              = EFI_VARIABLE_TIME_BASED_AUTHENTICATED_WRITE_ACCESS
VARIABLE_ATTRIBUTE_NV_BS_RT_HR_AT  = (VARIABLE_ATTRIBUTE_NV_BS_RT_HR | VARIABLE_ATTRIBUTE_AT)
VARIABLE_ATTRIBUTE_AT_AW           = (EFI_VARIABLE_TIME_BASED_AUTHENTICATED_WRITE_ACCESS | EFI_VARIABLE_AUTHENTICATED_WRITE_ACCESS)
VARIABLE_ATTRIBUTE_NV_BS_RT_AW     = (VARIABLE_ATTRIBUTE_NV_BS_RT | EFI_VARIABLE_AUTHENTICATED_WRITE_ACCESS)
VARIABLE_ATTRIBUTE_NV_BS_RT_HR_AT_AW = (VARIABLE_ATTRIBUTE_NV_BS_RT_HR | VARIABLE_ATTRIBUTE_AT_AW)

LOAD_OPTION_ACTIVE          = 0x00000001
LOAD_OPTION_FORCE_RECONNECT = 0x00000002
LOAD_OPTION_HIDDEN          = 0x00000008
LOAD_OPTION_CATEGORY        = 0x00001F00
LOAD_OPTION_CATEGORY_BOOT   = 0x00000000
LOAD_OPTION_CATEGORY_APP    = 0x00000100

###
## write_header
#
def write_header(f: io.BufferedIOBase) -> None:
    # First the EFI_FIRMWARE_VOLUME_HEADER
    block_size = 0x200
    zero_vector = bytes(16)
    fv_length = 0x30000
    attributes = EFI_FVB2_READ_ENABLED_CAP | EFI_FVB2_READ_STATUS | EFI_FVB2_STICKY_WRITE | EFI_FVB2_MEMORY_MAPPED | EFI_FVB2_WRITE_STATUS | EFI_FVB2_WRITE_ENABLED_CAP
    f.write(zero_vector)
    f.write(EFI_SYSTEM_NV_DATA_FV_GUID.bytes_le)
    # HeaderLength and Checksum initially written as zero, filled in later.
    f.write(struct.pack('<Q4sIHHHBB', fv_length, EFI_FVH_SIGNATURE, attributes, 0, 0, 0, 0, EFI_FVH_REVISION))
    f.write(struct.pack('<IIII', int(fv_length / block_size), block_size, 0, 0))
    header_length = f.tell()
    f.seek(0x30) # HeaderLength
    f.write(struct.pack('<H', header_length));
    f.seek(0)
    # Calculate Checksum
    sum = 0;
    for i in range(int(header_length / 2)):
        two = f.read(2)
        (two_val,) = struct.unpack('<H', two)
        sum += two_val
    checksum = 0x10000 - (sum & 0xffff)
    f.seek(0x32) # Checksum
    f.write(struct.pack('<H', checksum))
    f.seek(header_length)

    # Next VARIABLE_STORE_HEADER
    f.write(EFI_AUTHENTICATED_VARIABLE_GUID.bytes_le) # Signature
    # (Size, Format, State, Reserved, Reserved1)
    f.write(struct.pack('<IBBHI', int(0x10000 - header_length), VARIABLE_STORE_FORMATTED, VARIABLE_STORE_HEALTHY, 0, 0))
    return

###
## str_to_varstore_str
#
def str_to_varstore_str(string: str) -> bytes:
    # Convert python string to UTF16LE null terminated used everywhere
    # in the varstore.
    return codecs.encode(string, encoding = 'utf_16_le') + bytes(2)

###
## pad_to_p2
#
def pad_to_p2(f: io.BufferedIOBase, p2: int):
    #
    # Pad out the file with 0xff bytes to the power-of-two boundary
    #
    boundary = 1 << p2
    mask = boundary - 1
    pos = f.tell()
    pad = (boundary - (pos & mask)) & mask
    f.write(pad * b'\xff')


###
## write_var
#
def write_var(f: io.BufferedIOBase, name: str, guid: uuid.UUID, attributes: int, data: bytes) -> None:
    # Write variable with an array of bytes
    null_time = bytes(16)
    name_bytes = str_to_varstore_str(name)
    name_size = len(name_bytes)
    data_size = len(data)
    # (StartId, State, Reserved, Attributes, MonotonicCount, TimeStamp, PubKeyIndex, NameSize, DataSize)
    f.write(struct.pack('<HBBIQ16sIII', VARIABLE_DATA, VAR_ADDED, 0, attributes, 0, null_time, 0, name_size, data_size))
    f.write(guid.bytes_le)
    f.write(name_bytes)
    f.write(data)
    pad_to_p2(f, 2) # Move to 4-byte boundary

###
## write_var2 - Write a 2-byte integer variable
#
def write_var2(f: io.BufferedIOBase, name: str, guid: uuid.UUID, attributes: int, value: int) -> None:
    # Write a 2-byte integer variable
    data = struct.pack('<H', int(value & 0xffff))
    write_var(f, name, guid, attributes, data)

def device_path_end() -> bytes:
    # Type: 7F
    # SubType: FF
    return struct.pack('<BBH', 0x7f, 0xff, 4)

def file_path_media_device_path(path: str) -> bytes:
    # Type: 4
    # SubType: 4
    path_name = str_to_varstore_str(path)
    return struct.pack('<BBH', 4, 4, len(path_name) + 4) + path_name

def guid_partition_harddrive_device_path(part_num: int, lba_start: int, lba_size: int, guid: uuid.UUID) -> bytes:
    # Type: 4
    # SubType: 1
    assert len(guid.bytes_le) == 16
    rv = struct.pack('<BBHIQQ16sBB', 4, 1, 42, part_num, lba_start, lba_size, guid.bytes_le, 2, 2)
    return rv

###
## create_efi_load_option
#
def create_efi_load_option(attributes: int, description: str, dev_path: List[bytes],
                           optional_data: Union[bytes, None] = None) -> bytes:
    dev_path_size = 0
    for elt in dev_path:
        dev_path_size += len(elt)
    rv = struct.pack('<IH', attributes, int(dev_path_size)) + str_to_varstore_str(description)
    for elt in dev_path:
        rv += elt
    if optional_data:
        rv += optional_data
    return rv


###
##  main
#
def main() -> int:
    args: argparse.Namespace = parse_args()

    f = args.out_file;

    write_header(f)

    if args.timeout:
        write_var2(f, "Timeout", EFI_GLOBAL_VARIABLE_GUID, VARIABLE_ATTRIBUTE_NV_BS_RT, args.timeout)

    if args.guid_part_path:
        (name, part_num, start_lba, size_lba, guid, path) = args.guid_part_path.split(',', maxsplit=5)
        id = uuid.UUID('{' + guid + '}')
        dp = [guid_partition_harddrive_device_path(int(part_num), int(start_lba), int(size_lba), id),
              file_path_media_device_path(path),
              device_path_end()]
        load_option = create_efi_load_option(LOAD_OPTION_ACTIVE, name, dp)
        write_var(f, "Boot0000", EFI_GLOBAL_VARIABLE_GUID, VARIABLE_ATTRIBUTE_NV_BS_RT, load_option);
        write_var2(f, "BootOrder", EFI_GLOBAL_VARIABLE_GUID, VARIABLE_ATTRIBUTE_NV_BS_RT, 0)
    # Pad with FF to 64K boundry
    pad_to_p2(f, 16)

    # Two empty 64K blocks
    f.write(bytes(2 * 0x10000))
    f.close()
    return 0

###
##  entrypoint
#
if __name__ == "__main__":
    main()
