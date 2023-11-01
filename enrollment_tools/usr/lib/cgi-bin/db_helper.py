#! /usr/bin/env python3.9

##############################################################################
#  db_helper.py
#
#  Copyright (c) 2018-2020. Fungible, inc. All Rights Reserved.
#  Copyright (c) 2023. Microsoft Corporation. All Rights Reserved.
#
##############################################################################

''' module implementing chip enrollment: enrollment certificate generation,
provision and storage
'''

from contextlib import closing

# db connection
import psycopg2


# register_dpu: select or insert for serial_info, serial_nr returning chip_id
INSERT_CHIP_STMT = "SELECT register_dpu(%s, %s)"

SN_DESC = (
    ('serial_info', 8),
    ('serial_nr', 16))

SN_LEN = sum(desc[1] for desc in SN_DESC)

ID_FLD = 'chip_id'

def make_slicer_of(b):
    ''' return an object that will slice a string into multiple buffers '''
    offset = [0]

    def make_buff(size):
        ''' create a buffer at the current offset of the specified size '''
        ret = b[offset[0]:offset[0]+size]
        offset[0] += size
        return ret

    return make_buff


def get_sn_values(sn):
    ''' slice the sn into constituent buffers dictionary '''
    slicer = make_slicer_of(sn)
    return {desc[0]: slicer(desc[1]) for desc in SN_DESC }


def insert_select_chip_id(cur, serial_info, serial_nr):
    ''' returns chip_id foreign key for serial_info, serial_nr
    will insert values into fungible_dpus table if missing '''
    cur.execute(INSERT_CHIP_STMT, (serial_info,serial_nr) )
    return cur.fetchone()[0]

def pack_bytes_with_len_prefix(b, size):
    ''' used to transform signature/modulus to proper format '''
    len_b = len(b)
    ret = len_b.to_bytes(4, byteorder='little') + b # LE length prefix
    len_pad = size - (4 + len_b)
    if len_pad > 0:
        ret += b'\x00' * len_pad
    return ret

def db_func(func, arg1):
    ''' execute arbitrary function within the context of a db connection
    all operations in the function are wrapped in a transaction automatically
    (feature of  psycopg2)'''
    with closing(psycopg2.connect("dbname=enrollment_db")) as db_conn:
        return func(db_conn, arg1)
