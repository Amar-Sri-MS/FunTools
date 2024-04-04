#!/usr/bin/env python3
# Copyright (c) 2018 Fungible,inc. All Rights reserved.
#

import argparse
import mmap
import firmware_signing_service as fss
import struct
import sys

SIZEOF_MODULUS_SIZE=4
SIZE_OF_CDI=32
MARKER_SIZE=4

class AppFpk(mmap.mmap):

    def __find_pattern(self, n, marker):
        m1 = bytearray([(marker << 4) + n] * MARKER_SIZE)
        m2 = bytearray([marker + (n << 4)] * MARKER_SIZE)
        pos1 = self.rfind(m1)
        pos2 = self.rfind(m2)
        if pos2 == -1:
            raise Exception("Missing trailing marker")
        if pos1 == -1:
            raise Exception("Missing initial marker")
        return pos1+MARKER_SIZE, pos2 - (pos1+MARKER_SIZE) # point past the m1 marker

    def get_key_loc(self, n):
        # "F" pattern, size=4, modulus=512
        start,size = self.__find_pattern(n, 0x0F)
        if size != SIZEOF_MODULUS_SIZE+512:
            raise Exception("Size of key {}: {} expected 516".
                            format(n, size))
        return start

    def get_dice_loc(self):
        # "D" pattern, multiple of key=48, cert=640
        start,size = self.__find_pattern(0x0C, 0x0D)
        print("DICE marker found: %08x %08x" % (start,size))
        return start

    def validate(self, n):
        # place holder for size example: 0x5555_5555
        init_modulus = bytearray([16*n + n] * MARKER_SIZE)
        pos = self.get_key_loc(n)
        if self.find(init_modulus, pos) != pos:
            # default length placeholder not found, check if something that
            # looks like a real length is stored
            val = struct.unpack("<l", self[pos:pos+SIZEOF_MODULUS_SIZE])[0]
            if(val > 512):
                raise Exception("Invalid modulus length: {:x}".format(val))
            return 1
        else:
            # default length placeholder, so the modulus should be
            # filled in with placeholder data 0xDEADC0DE
            for offset in range(pos+SIZEOF_MODULUS_SIZE,
                                pos+SIZEOF_MODULUS_SIZE+512, MARKER_SIZE):
                if self[offset:offset+MARKER_SIZE] != bytearray([0xDE, 0xAD,
                                                                 0xC0, 0xDE]):
                    raise Exception(
                        "Modulus length unset, data placeholder missing")
        return 0

    def update_key(self, n, key):
        ret = 0
        pos = self.get_key_loc(n)
        self.seek(pos)
        if not key:
            key = "fpk" + str(n)

        try:
            modulus = fss.get_modulus(key)
        except TypeError as e:
            print(str(e))
            return 1
        except:
            raise
        stored_mod_len = struct.unpack("<l", self.read(4))[0]
        stored_mod = self.read(stored_mod_len)

        if (stored_mod_len == len(modulus)) and \
           (stored_mod == modulus):
           ret = 1
        else:
            self.seek(pos)
            self.write(struct.pack("<l", len(modulus)))
            self.write(modulus)
        self.seek(0)
        return ret


def app_fpk_process(func):
    def wrapper(file, number, *args, **kwargs):
        with open(file, "r+b") as f:
            with AppFpk(f.fileno(), 0) as app:
                return func(file, number, app, *args, **kwargs)
    return wrapper


@app_fpk_process
def update_file(file, number, app, key):
    try:
        ret = app.update_key(number, key)
        print("Key {} {}updated in {} with '{}' (net)".
              format(number, "not " if ret == 1 else "", file, key))
    except RuntimeError as e:
        print("Unexpected error when processing key {} for {}:{}".format(number, file, e))
        raise
    except Exception as e:
        print("Key {} not found in {}:{}".format(number, file, e))
        raise
    return 0


@app_fpk_process
def check_file(file, number, app):
    try:
        res = app.validate(number)
        print("Key {} in {}: {}".format(n, file,
                                        "OK" if res == 1 else "Placeholder"))
        return 0
    except Exception as e:
        print("Key {} not found in {}. Error: {}".format(number, file, e))
        return 1

@app_fpk_process
def get_key_loc(file, number, app):
    try:
        return app.get_key_loc(number)
    except Exception as e:
        print("Key {} not found in {}. Error: {}".format(number, file, e))
        return 0xFFFF_FFFF

@app_fpk_process
def get_dice_loc(file, number, app):
    try:
        print("DICE loc for %s" % file)
        return app.get_dice_loc()
    except Exception as e:
        # swallow the exception: just looking and not expecting anything
        return 0xFFFF_FFFF


def main():
    parser = argparse.ArgumentParser(
        description="Process app binaries to modify FPKs")

    parser.add_argument("-n", "--number", help="fpk number",
                        choices=[3, 4, 5],
                        type=int,
                        required=True)
    parser.add_argument("--key", help="Key name to be used")
    parser.add_argument("file", help="file to update",
                        metavar="FILE")

    cmd = parser.add_mutually_exclusive_group(required=True)
    cmd.add_argument("--verify", action='store_true')
    cmd.add_argument("--update", action='store_true')

    args = parser.parse_args()

    if args.update:
        return update_file(args.file, args.number, key=args.key)
    elif args.verify:
        return check_file(args.file, args.number)


if __name__ == "__main__":
    sys.exit(main())
