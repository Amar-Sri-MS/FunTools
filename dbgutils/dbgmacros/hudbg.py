#!/usr/bin/env python2.7

"""
HU debug macros

Usage:
-----
$python
Python 2.7.12 (default, Nov 12 2018, 14:36:49)
[GCC 5.4.0 20160609] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> from dbgmacros.hudbg import *
>>> connect('TPOD28', 'i2c')
>>> connect('FS2-F1_1', 'pcie')
>>> show_db_vp_fid(0, 0, 272)
"""

from csrutils.csrutils import *

logger = logging.getLogger("hudbg")
logger.setLevel(logging.INFO)

def show_db_addr_by_fid(ring, start=0, end=272):
    """
    HSU_PTA_DOORBELL_ADDRESS_MAPPING_TABLE by fid

    """
    assert ring < 4
    assert end <= 272
    assert start >= 0
    print("dump HSU_PTA_DOORBELL_ADDRESS_MAPPING_TABLES ring=%d, fid from %d to %d" % (ring, start, end))
    probe = dbgprobe()
    for i in range(start, end):
        f_str = "pf" if i >= 0x100 else "vf"
        print('db address entry by fid 0x%x (%d), %s' % (i, i, f_str))
        csr_meta = csr_get_metadata(csr_name='hsu_pta_doorbell_address_mapping_table',
                                   ring_name='hsu', ring_inst=ring)
        csr_addr = csr_get_addr(csr_meta, csr_entry=i)
        logger.debug("csr address: {0}".format(hex(csr_addr)))
        csr_width_words = csr_get_width_bytes(csr_meta) >> 3
        (status, resp_data) = probe.csr_peek(csr_addr, csr_width_words)
        if status is True:
            word_array = resp_data
            csr_show(csr_meta, resp_data)
        else:
            error_msg = resp_data
            print("Error! {0}!".format(error_msg))

def show_db_lut_by_id(ring, start=0, end=1024):
    """
    show HSU_PTA_VP_LOOKUP_TABLE per table index
    csr raw: [ 0x0500000000000000 ]
	vp_id: [ 0x0000000000000005 ]
	__rsvd: [ 0x0000000000000000 ]
    """
    assert ring < 4
    assert start >= 0
    assert end <=1024

    print("dump HSU_PTA_VP_LOOKUP_TABLE ring=%d, lut id from %d to %d" % (ring, start, end))
    probe = dbgprobe()
    for i in range(start, end):
        print('db vp lut entry by id 0x%x (%d)' % (i, i))
        csr_meta = csr_get_metadata(csr_name='hsu_pta_vp_lookup_table',
                                   ring_name='hsu', ring_inst=ring)
        csr_addr = csr_get_addr(csr_meta, csr_entry=i)
        logger.debug("csr address: {0}".format(hex(csr_addr)))
        csr_width_words = csr_get_width_bytes(csr_meta) >> 3
        (status, resp_data) = probe.csr_peek(csr_addr, csr_width_words)
        if status is True:
            word_array = resp_data
            csr_show(csr_meta, resp_data)
        else:
            error_msg = resp_data
            print("Error! {0}!".format(error_msg))

def show_db_vp_fid(ring, start=0, end=272):
    """
    show HSU_PTA_DOORBELL_REGION_LUT per fid
    this includes fields like this
            doorbell_base: [ 0x000971e6df197cd6 ]
            doorbell_limit: [ 0x0002840ac50580ec ]
            doorbell_stride: [ 0x0000000000000004 ]
            doorbell_access_size: [ 0x0000000000000000 ]
            sticky_sq_msb: [ 0x0000000000000000 ]
            sticky_cq_msb: [ 0x0000000000000000 ]
            crc_profile: [ 0x0000000000000005 ]
            vp_lut_base: [ 0x000000000000000a ]
            vp_lut_range: [ 0x0000000000000001 ]

    """
    assert ring < 4
    assert end <= 272
    assert start >= 0
    print("dump HSU_PTA_DOORBELL_REGION_LUT ring=%d, fid from %d to %d" % (ring, start, end))
    probe = dbgprobe()
    for i in range(start, end):
        f_str = "pf" if i >= 0x100 else "vf"
        print('db lut entry by fid 0x%x (%d), %s' % (i, i, f_str))
        csr_meta = csr_get_metadata(csr_name='hsu_pta_doorbell_region_lut',
                                   ring_name='hsu', ring_inst=ring)
        csr_addr = csr_get_addr(csr_meta, csr_entry=i)
        logger.debug("csr address: {0}".format(hex(csr_addr)))
        csr_width_words = csr_get_width_bytes(csr_meta) >> 3
        (status, resp_data) = probe.csr_peek(csr_addr, csr_width_words)
        if status is True:
            word_array = resp_data
            csr_show(csr_meta, resp_data)
        else:
            error_msg = resp_data
            print("Error! {0}!".format(error_msg))
