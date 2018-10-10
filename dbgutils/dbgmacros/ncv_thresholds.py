#!/usr/bin/env python

'''
Debug utilities for NCV thresholds 
'''

from csrutils.csrutils import *

logger = logging.getLogger("dbgmacros")
logger.setLevel(logging.INFO)

def show_global_ncv_thrsholds():
    print('NWQM NCV THRESHOLDS:')
    probe = dbgprobe()
    for i in range(15):
        csr_meta = csr_get_metadata('nwqm_wu_crd_cnt_ncv_th_{}'.format(i+1), None, None, 'nu', 0, 
                None, None, None)

        csr_addr = csr_get_addr(csr_meta, None, None, None)
        if csr_addr is None:
            print("Error get csr address!!!")
            return
        logger.debug("csr address: {0}".format(hex(csr_addr)))
        csr_width_words = csr_get_width_bytes(csr_meta) >> 3
        (status, data) = probe.csr_peek(csr_addr, csr_width_words)
        if status is True:
            word_array = data
            fields_objs = csr_meta.get("fld_lst", None)
            field_val = csr_get_field_val(csr_meta, word_array, 'val')
            print('\tTHR-{}: {}'.format(i, [hex(x) for x in field_val]))
        else:
            error_msg = data
            print("Error! {0}!".format(error_msg))

def show_pc_cmh_ncv_thrsholds():
    probe = dbgprobe()
    for i in range(16):
        print('CC CMH NCV PROFILE:{}'.format(i))
        csr_meta = csr_get_metadata('pc_cmh_cwqm_q_depth_ncv_th_cfg', None, i, 'cc', 0, 
                None, None, None)

        csr_addr = csr_get_addr(csr_meta, None, None, i)
        if csr_addr is None:
            print("Error get csr address!!!")
            return
        logger.debug("csr address: {0}".format(hex(csr_addr)))
        csr_width_words = csr_get_width_bytes(csr_meta) >> 3
        (status, data) = probe.csr_peek(csr_addr, csr_width_words)
        if status is True:
            word_array = data
            for t in range(15):
                field_val = csr_get_field_val(csr_meta, word_array, 'th_{}'.format(t+1))
                print('\tTHR-{}: {}'.format(t, [hex(x) for x in field_val]))
        else:
            error_msg = data
            print("Error! {0}!".format(error_msg))


    print('CC NCV ACTIVE PROFILES:'.format())
    for i in range(24): 
        csr_meta = csr_get_metadata('pc_cmh_cwqm_vp_q_depth_ncv_th_sel_cfg', None, i, 'cc', 0,
                None, None, None)
        csr_addr = csr_get_addr(csr_meta, None, None, i)
        if csr_addr is None:
            print("Error get csr address!!!")
            return
        logger.debug("csr address: {0}".format(hex(csr_addr)))
        csr_width_words = csr_get_width_bytes(csr_meta) >> 3 
        (status, data) = probe.csr_peek(csr_addr, csr_width_words)
        if status is True:
            word_array = data
            hi_thr_prof = csr_get_field_val(csr_meta, word_array, 'hi_th_sel')
            low_thr_prof = csr_get_field_val(csr_meta, word_array, 'lo_th_sel')
            print('vp-{} hi_thr_prof: {} low_thr_prof: {}'.format(i, hi_thr_prof, low_thr_prof))
        else:
            error_msg = data
            print("Error! {0}!".format(error_msg))

