#############################################################################
#   sn_validation.py
#
#   Copyright (c) 2019. Fungible, inc. All Rights Reserved.
#
#   This file is imported by the enrollment server main script and
#   must implement a function called check:
#
#   def check( serial_info, serial_nr)
#
#   This function must raise a ValueError if the serial info or serial
#   number passed as argument is not valid.
#
#
#############################################################################


def check(serial_info, serial_nr):
    # at this stage of development, serial info should be all zeroes,
    # and only the last 2 bytes of the serial number can be non zeroes

    for b in serial_info:
        if b != 0:
            raise ValueError("Serial Info must be zero")

    for b in serial_nr[:-2]:
        if b != 0:
            raise ValueError("First 14 bytes of Serial Number must be zero")
