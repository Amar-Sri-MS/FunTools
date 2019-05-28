#!/usr/bin/env python

"""
Scan through all the interrupts and dump whether they are enabled or not

Usage:
-----
$python
Python 2.7.12 (default, Nov 12 2018, 14:36:49)
[GCC 5.4.0 20160609] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> from csr_scan.csr_intr_mask_scan import *
>>> connect('TPOD28', 'i2c')
>>> csr_intr_mask_scan()
"""

import yaml
import re
import sys
from csrutils.csrutils import *

logger = logging.getLogger("csr_intr_mask_scan")
logger.setLevel(logging.INFO)


def isr_names(isrs):
    return isrs.keys()

def isr_type(isr_name, isrs):
    isr_obj = isrs.get(isr_name, None)
    isr_type = isr_obj.get('TYPE', None)
    if 'NON_FATAL' in isr_type:
        return 'NON_FATAL'
    else:
        return 'FATAL'

def csr_intr_fields(isr_obj):
    return isr_obj.get('FLD', None)

def isr_fatal():
    with open('/tmp/isr_db.yaml') as f:
        csrs_json = yaml.load(f)
        return csrs_json
    return None

logfile = None
def isr_mask_scan(csr_name, csr_meta_obj):
    global logfile
    logger.debug(csr_meta_obj)
    for i in range(csr_meta_obj.get("an_inst_cnt", None)):
        for j in range(csr_meta_obj.get("csr_count")):
            for m in range(csr_meta_obj.get("csr_n_entries", None)):
                csr_addr = csr_get_addr(csr_meta_obj, anode_inst=i, csr_inst=j, csr_entry=m)
                csr_width_words = csr_get_width_bytes(csr_meta_obj) >> 3
                (status, resp_data) = dbgprobe().csr_peek(csr_addr=csr_addr,
                                        csr_width_words=csr_width_words,
                                        chip_inst=1)
                if status is True:
                    word_array = resp_data
                    for x in word_array:
                        if (x != 0):
                           return (0, 'ENABLED')
                    return (0, "DISABLED")
                    #logfile.write('\tCSR:{} ADDR:{}\n'.format(csr_name, hex(csr_addr)))
                    #csr_show(csr_meta_obj, resp_data)
                else:
                    err_msg = resp_data
                    #logger.debug("Error! {0}!".format(error_msg))
                    err_code = err_msg.split(':')
                    #logfile.write(('\t***READ ERROR({})*** CSR:{} ADDR:{}\n').format(
                    #    error_code[1], csr_name, hex(csr_addr)))
                    err_msg = 'ERR_CODE({}) ADDR:{}'.format(err_code[1], hex(csr_addr))
                    return (err_code, err_msg)

def csr_intr_mask_scan():
    fatal_isrs = isr_fatal()
    global logfile
    for k,v in fatal_isrs.iteritems():
        logfile.write("\n{}\n".format(k))
        logger.info("BLOCK:{}".format(k))
        for t in ['FATAL', 'NON_FATAL']:
            logfile.write('    [{}]\n'.format(t))
            for i in isr_names(v):
                type = isr_type(i, v)
                if type == t:
                    i = re.sub(r'_stat$', "_mask", i)
                    logger.info('CSR:{}'.format(i))
                    logger.debug(csr_metadata_objs(i))
                    for x in csr_metadata_objs(i):
                        (err_code, err_msg) = isr_mask_scan(i, x)
                        if err_code == 0  :
                            logfile.write('        [{}] '.format(err_msg))
                        else:
                            logfile.write('        [ERROR] ')
                        logfile.write('CSR:{} RING:{} RINST:{} AN:{} AN_PATH:{} '.format(
                                i, x.get('ring_name', None),
                                x.get('ring_inst', None),
                                x.get('an', None), x.get('an_path', None)))
                        if err_code !=0:
                            logfile.write(err_msg)
                        logfile.write('\n')
    logger.info("Scanning finished!")



def main():
    global logfile
    logfile = open("/tmp/isr_output.txt","w")
    #connect(dut_name='FS2-F1_1', mode='pcie')
    probe = connect(dut_name='FS1', mode='i2c')
    csr_intr_mask_scan()
    probe.disconnect()

if (__name__ == "__main__"):
    main()
