#!/usr/bin/env python

"""
Sample debug macros
Individual module owners can write their utilities similar to this

Usage:
-----
$python
Python 2.7.12 (default, Nov 12 2018, 14:36:49)
[GCC 5.4.0 20160609] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> from dbgmacros.test_macros import *
>>> connect('TPOD28', 'i2c')
>>> connect('FS2-F1_1', 'pcie')
>>> dump_hbm(0x4000, 100)
"""

from csrutils.csrutils import *

logger = logging.getLogger("dbgmacros")
logger.setLevel(logging.INFO)

def dump_hbm(start_addr, num_bytes):
    if (start_addr & 0xFF != 0):
       logger.error('start_addr should be 256 byte aligned')
       return
    cache_line_addr = start_addr >> 6;
    csr_replay_data = list()
    # Round of to 256 byte boundary
    # Number of 64-byte words to read
    if (num_bytes & 0xff):
        logger.info('Rounded-off num_bytes:{0} to {1}'.format(
            num_bytes, (num_bytes+255) & ~0xff))
    num_reads_256bytes = (num_bytes + 255) >> 8
    num_64byte_words = num_reads_256bytes * 32
    num_reads = num_reads_256bytes * 4
    logger.info('Reading 256byte_reads: {0}'
            ' num_reads: {1} num_words:{2}'.format(
            num_reads_256bytes, num_reads, num_64byte_words))

    read_data_words = [None] * num_64byte_words
    cnt = 0
    while (cnt < num_reads):
        skip_addr = 0
        if(cnt & 0x2):
            skip_addr = constants.MUH_RING_SKIP_ADDR
        if (cnt & 0x1):
            skip_addr += constants.MUH_SNA_ANODE_SKIP_ADDR
        csr_addr = constants.MEM_RW_CMD_CSR_ADDR
        csr_addr += skip_addr
        muh_sna_cmd_addr = (cache_line_addr/4) + (cnt/4)
        csr_val = muh_sna_cmd_addr << 37;
        csr_val |= 0x1 << 63; #READ
        logger.debug('csr_val: {0}'.format(csr_val))
        (status, data) = dbgprobe().csr_poke(csr_addr, [csr_val])
        if status is True:
            logger.debug("Poke:{0} addr: {1} Success!".format(cnt, hex(muh_sna_cmd_addr)))
        else:
            error_msg = data
            logger.error("CSR Poke failed! Addr: {0} Error: {1}".format(hex(csr_addr), error_msg))
            return

        csr_addr = constants.MEM_RW_STATUS_CSR_ADDR
        csr_addr += skip_addr
        (status, data) = dbgprobe().csr_peek(csr_addr, 1)
        if status is True:
            word_array = data
            if word_array is None or not word_array:
                logger.error("Failed get cmd status! Error in csr peek!!!")
                return
            cmd_status_done = word_array[0]
            cmd_status_done = cmd_status_done >> 63
            if cmd_status_done != 1:
                logger.error("Failed cmd status != Done!")
                return
            else:
                logger.debug('Data ready!')
        else:
            error_msg = data
            logger.error('Error! {0}!'.format(error_msg))
            return

        for i in range(8):
            csr_addr = constants.MEM_RW_DATA_CSR_ADDR + skip_addr
            csr_addr += i * 8
            (status, data) = dbgprobe().csr_peek(csr_addr, 1)
            if status is True:
                logger.debug('peek word:{0} success!!!'.format(i))
                logger.debug('Read value:{0}'.format(data))
                read_data_words[(cnt * 8) + i] = data[0]
            else:
                error_msg = data
                logger.error("Error! {0}!".format(error_msg))

        cnt += 1

    if (cnt == num_reads):
        logger.info('Succesfully read {0} words! starting from {1}'.format(
                                                num_reads * 8, hex(start_addr)))
        for i in range(num_64byte_words):
            logger.info('Address: {0}  Data: 0x{1}'.format(
                hex(start_addr+(i*8)), hex(read_data_words[i])[2:].zfill(16)));
    else:
        logger.error('Read un-successful')
        return

def write_hbm(start_addr, data_words):
    if (start_addr & 0x3F != 0):
       logger.error('start_addr should be 64 byte aligned for cache line alignment')
       return
    if len(data_words) != 8:
        logger.error('Number of words should be 8 to match one cache line length')
        return

    skip_addr = 0
    if(start_addr & 0x2):
        skip_addr = constants.MUH_RING_SKIP_ADDR
    if (start_addr & 0x1):
        skip_addr += constants.MUH_SNA_ANODE_SKIP_ADDR
    csr_addr = constants.MEM_RW_CMD_CSR_ADDR
    csr_addr += skip_addr
    for i in range(8):
        csr_val = data_words[i]
        csr_addr = constants.MEM_RW_DATA_CSR_ADDR + skip_addr
        csr_addr += i * 8
        (status, data) = dbgprobe().csr_fast_poke(csr_addr, [csr_val])
        if status is True:
            logger.info('Write value:{0}'.format(hex(csr_val)))
            logger.debug("poke success!!!")
        else:
            error_msg = data
            logger.error("Error! {0}!".format(error_msg))
            sys.exit(1)

    csr_addr = constants.MEM_RW_CMD_CSR_ADDR
    csr_addr += skip_addr
    muh_sna_cmd_addr = start_addr/4
    csr_val = muh_sna_cmd_addr << 37;
    csr_val |= 0x0 << 63;
    logger.debug('csr_val: {0}'.format(csr_val))
    (status, data) = dbgprobe().csr_fast_poke(csr_addr, [csr_val])
    if status is True:
        logger.info("Poke:addr: {0} Success!".format(hex(muh_sna_cmd_addr)))
    else:
        error_msg = data
        logger.error("CSR Poke failed! Addr: {0} Error: {1}".format(hex(csr_addr), error_msg))
        sys.exit(1)
    csr_addr = constants.MEM_RW_STATUS_CSR_ADDR
    csr_addr += skip_addr
    (status, data) = dbgprobe().csr_peek(csr_addr, 1)
    if status is True:
        word_array = data
        if word_array is None or not word_array:
            logger.error("Failed get cmd status! Error in csr peek!!!")
            sys.exit(1)
        cmd_status_done = word_array[0]
        cmd_status_done = cmd_status_done >> 63
        if cmd_status_done != 1:
            logger.error("Failed cmd status != Done!")
            sys.exit(1)
        else:
            logger.info('Data ready!')
    else:
        error_msg = data
        logger.error('Error! {0}!'.format(error_msg))
        sys.exit(1)

    logger.info('Succesfully wrote cache line!')
    return

def show_global_ncv_thrsholds():
    print('NWQM NCV THRESHOLDS:')
    probe = dbgprobe()
    for i in range(15):
        csr_meta = csr_get_metadata(csr_name='nwqm_wu_crd_cnt_ncv_th_{}'.format(i+1),
                                    ring_name='nu', ring_inst=0)
        csr_addr = csr_get_addr(csr_meta)
        logger.debug("csr address: {0}".format(hex(csr_addr)))
        csr_width_words = csr_get_width_bytes(csr_meta) >> 3
        (status, resp_data) = probe.csr_peek(csr_addr, csr_width_words)
        if status is True:
            word_array = resp_data
            fields_objs = csr_meta.get("fld_lst", None)
            field_val = csr_get_field_val(csr_meta, word_array, 'val')
            print('\tTHR-{}: {}'.format(i, [hex(x) for x in field_val]))
        else:
            error_msg = resp_data
            print("Error! {0}!".format(error_msg))

def show_pc_cmh_ncv_thrsholds():
    probe = dbgprobe()
    for i in range(16):
        print('CC CMH NCV PROFILE:{}'.format(i))
        csr_meta = csr_get_metadata(csr_name='pc_cmh_cwqm_q_depth_ncv_th_cfg',
                                   ring_name='cc', ring_inst=0)
        csr_addr = csr_get_addr(csr_meta, csr_entry=i)
        logger.debug("csr address: {0}".format(hex(csr_addr)))
        csr_width_words = csr_get_width_bytes(csr_meta) >> 3
        (status, resp_data) = probe.csr_peek(csr_addr, csr_width_words)
        if status is True:
            word_array = resp_data
            for t in range(15):
                field_val = csr_get_field_val(csr_meta, word_array, 'th_{}'.format(t+1))
                print('\tTHR-{}: {}'.format(t, [hex(x) for x in field_val]))
            print("test code====>")
            csr_show(csr_meta, resp_data)
        else:
            error_msg = resp_data
            print("Error! {0}!".format(error_msg))


    print('CC NCV ACTIVE PROFILES:'.format())
    for i in range(24):
        csr_meta = csr_get_metadata(csr_name='pc_cmh_cwqm_vp_q_depth_ncv_th_sel_cfg',
                                    ring_name='cc', ring_inst=0)
        csr_addr = csr_get_addr(csr_meta, csr_entry=i)
        logger.debug("csr address: {0}".format(hex(csr_addr)))
        csr_width_words = csr_get_width_bytes(csr_meta) >> 3
        (status, resp_data) = probe.csr_peek(csr_addr, csr_width_words)
        if status is True:
            word_array = resp_data
            hi_thr_prof = csr_get_field_val(csr_meta, word_array, 'hi_th_sel')
            low_thr_prof = csr_get_field_val(csr_meta, word_array, 'lo_th_sel')
            print('vp-{} hi_thr_prof: {} low_thr_prof: {}'.format(i, hi_thr_prof, low_thr_prof))
        else:
            error_msg = resp_data
            print("Error! {0}!".format(error_msg))

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
