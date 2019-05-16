#!/usr/bin/env python3
# Copyright (c) 2018 Fungible,inc. All Rights reserved.
#

import argparse
import enrollment_service as es
import mmap
import generate_firmware_image as GFI
import struct
import sys


class RsaModulus(object):
    MOD_HSM = 1 << 0
    MOD_NET = 1 << 1

    def __init__(self, name, modulus):
        self.modulus = modulus
        self.name = name

    @staticmethod
    def create(name, mode):
        config = {
            "fpk3" :
                { "type": HsmRsaModulus,
                  "mode": RsaModulus.MOD_HSM },
            "fpk4" :
                { "type": EnrollmentModulus,
                  "mode": RsaModulus.MOD_NET },
            "fpk5" :
                { "type": HsmRsaModulus,
                  "mode": RsaModulus.MOD_HSM },
        }
        try:
            c = config[name]
            if (c["mode"] & mode) != c["mode"]:
                raise TypeError("Operating mode {} not available".format(c["mode"]))
            return c["type"](name)
        except:
            raise

class EnrollmentModulus(RsaModulus):
    def __init__(self, name):
        m = es.GetModulus()
        super().__init__(name, m)

class HsmRsaModulus(RsaModulus):
    def __init__(self, name):
        m = GFI.get_create_public_rsa_modulus(name)
        super().__init__(name, m)

class AppFpk(mmap.mmap):
    def __find_key_loc(self, n):
        m1 = bytearray([0xF0 + n] * 4)
        m2 = bytearray([0x0F + (n << 4)] * 4)
        pos1 = self.rfind(m1)
        pos2 = self.rfind(m2)
        if pos2 == -1:
            raise Exception("Missing trailing marker")
        if pos1 == -1:
            raise Exception("Missing initial marker")
        if pos2 - pos1 != 512 + 4 + 4:
            raise Exception("Wrong marker offset: {}".format(pos2-pos1))
        return pos1

    def validate(self, n):
        init_modulus = bytearray([16*n + n] * 4)
        pos = self.__find_key_loc(n)
        if self.find(init_modulus, pos) - pos != 4:
            # default length placeholder not found, check if something that
            # looks like a real length is stored
            val = struct.unpack("<l", self[pos+4:pos+8])[0]
            if(val > 512):
                raise Exception("Invalid modulus length: {:x}".format(val))
            return 1
        else:
            # default length placeholder, so the modulus should be
            # filled in with placeholder data 0xDEADC0DE
            for offset in range(pos+8, pos+8+512, 4):
                if self[offset:offset+4] != bytearray([0xDE, 0xAD, 0xC0, 0xDE]):
                    raise Exception(
                        "Modulus length unset, data placeholder missing")
        return 0

    def update_key(self, n, key, hsm, net):
        ret = 0
        pos = self.__find_key_loc(n)
        self.seek(pos+4)
        if not key:
            key = "fpk" + str(n)

        try:
            mode = 0
            if hsm:
                mode |= RsaModulus.MOD_HSM
            if net:
                mode |= RsaModulus.MOD_NET
            modulus = RsaModulus.create(key, mode).modulus
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
            self.seek(pos+4)
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
def update_file(file, number, app, key, hsm = False, net = False):
    try:
        ret = app.update_key(number, key, hsm, net)
        print("Key {} {}updated in {}".format(number, "not " if ret == 1 else "", file))
    except Exception as e:
        print("Key {} not found in {}:{}".format(number, file, e))
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

def main():
    parser = argparse.ArgumentParser(
        description="Process app binaries to modify FPKs")

    parser.add_argument("-n", "--number", help="fpk number",
                        choices=[3, 4, 5],
                        type=int,
                        required=True)
    parser.add_argument("--key", help="Key name (in HSM) to be used")
    parser.add_argument("file", help="file to update",
                        metavar="FILE")
    parser.add_argument("--have-hsm", action='store_true', help='Script can access an HSM')
    parser.add_argument("--have-net", action='store_true', help='Script can access network')

    cmd = parser.add_mutually_exclusive_group(required=True)
    cmd.add_argument("--verify", action='store_true')
    cmd.add_argument("--update", action='store_true')


    args = parser.parse_args()

    if args.update:
        return update_file(args.file, args.number, key=args.key, hsm=args.have_hsm, net=args.have_net)
    elif args.verify:
        return check_file(args.file, args.number)


if __name__ == "__main__":
    sys.exit(main())
