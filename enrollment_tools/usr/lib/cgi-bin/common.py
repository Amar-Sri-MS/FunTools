
##############################################################################
#  common.py
#
#
#  Copyright (c) 2018-2019. Fungible, inc. All Rights Reserved.
#  Copyright (c) 2023. Microsoft Corporation. All Rights Reserved.
#
##############################################################################


import sys
import binascii
import datetime
import textwrap

MAX_SIGNATURE_SIZE = 512

# shared location for all: esay installation
DPU_REG_PATH='/var/lib/dpu_reg/'

#################################################################################
#
# Logging Apache style
#
#################################################################################
def log(msg):
    dt_stamp = datetime.datetime.now().strftime("%c")
    print(f"{dt_stamp} [enrollment] {msg}", file=sys.stderr)


###########################################################################
#
# HTTP common routines
#
###########################################################################

def send_response_body(body, filename=None):
    print("Status: 200 OK")
    if filename:
        print(f"Content-Disposition: attachment; filename = {filename}")
    print(f"Content-length:{len(body)}\n")
    print(f"{body}\n")


def send_binary_buffer(bin_buffer, form, filename=None):

    oformat = form.getvalue("format", "hex")
    if oformat == "hex":
        bin_str = binascii.b2a_hex(bin_buffer).decode('ascii')
    elif oformat == "base64":
        bin_str = textwrap.fill(
            binascii.b2a_base64(bin_buffer).decode('ascii'),
            width=57)
    elif oformat == "c_struct":
        bin_c_struct = f"{len(bin_buffer)},\n{{\n"

        for pos,val in enumerate(bin_buffer):
            bin_c_struct += f"0x{val:02x}, "
            if pos % 8 == 7:
                bin_c_struct += "\n"
        if len(bin_buffer) %8 != 0:
            bin_c_struct += "\n"
        bin_c_struct += "}"
        bin_str = bin_c_struct
    else:
        raise ValueError(f"Unknown format: {oformat}")

    send_response_body(bin_str, filename)
