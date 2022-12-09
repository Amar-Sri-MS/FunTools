#!/usr/bin/env python3

##############################################################################
#  test_enrollment_client.py
#
#  Unit testing of ../enrollment_client.py
#
#  Copyright (c) 2022. Fungible, inc. All Rights Reserved.
#
##############################################################################

import sys
import os

# add parent of parent directory to import path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enrollment_client import boot_step_and_version


BOOT_STEP_VERSION_TESTS = (
    ("status_reply_v0.bin", 0x22, b"bld_17833-602e803b3"),
    ("status_reply_v1.bin", 0xE4, b"bld_113635-e63927add"))


def boot_step_and_version_test():
    err = 0
    my_dir = os.path.dirname(os.path.abspath(__file__))
    for bsv_test in BOOT_STEP_VERSION_TESTS:
        input_path = os.path.join(my_dir, bsv_test[0])
        with open(input_path, 'rb') as f:
            b_str = f.read()

        c_step, c_ver = boot_step_and_version(b_str)
        if c_step != bsv_test[1]:
            print("Error reading boot step: expected %d got %d" %
                  (c_step, bsv_test[1]), file=sys.stderr)
            err += 1

        if c_ver != bsv_test[2]:
            print("Error reading version: expected '%s' got '%s'" %
                  (c_ver, bsv_test[2]), file=sys.stderr)
            err += 1

    return err



def main():
    err = 0
    err += boot_step_and_version_test()
    return err


if __name__ == '__main__':
    main()
