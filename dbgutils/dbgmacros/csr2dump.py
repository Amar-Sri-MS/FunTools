#!/usr/bin/env python

"""
DDR read/write/copy utilities

Usage:
------
python csr2dump.py --dut S1DB-4 --mode jtag
"""
from csrutils.csrutils import *
from csr2utils import *
import time

logger = logging.getLogger("csr2dump")
logger.setLevel(logging.INFO)

# HSU csr dump
def _hu_csr2_dump():
    csr_name = 'hu0.fmr.switch_stat_cnt_0'
    for i in range(82):
        csr_name_full = csr_name + '[{}]'.format(i)
        print('csr: {}'.format(csr_name_full))
        csr2utils.csr2_peek_internal(csr_name_full)

    csr_name = 'hu0.fmr.switch_stat_cnt_1'
    for i in range(8):
        csr_name_full = csr_name + '[{}]'.format(i)
        print('\ncsr: {}'.format(csr_name_full))
        csr2utils.csr2_peek_internal(csr_name_full)

    csr_name = 'hu0.fmr.switch_stat_cnt_2'
    for i in range(56):
        csr_name_full = csr_name + '[{}]'.format(i)
        print('\ncsr: {}'.format(csr_name_full))
        csr2utils.csr2_peek_internal(csr_name_full)

    csr_name = 'hu1.fmr.switch_stat_cnt_0'
    for i in range(82):
        csr_name_full = csr_name + '[{}]'.format(i)
        print('\ncsr: {}'.format(csr_name_full))
        csr2utils.csr2_peek_internal(csr_name_full)

    csr_name = 'hu1.fmr.switch_stat_cnt_1'
    for i in range(8):
        csr_name_full = csr_name + '[{}]'.format(i)
        print('\ncsr: {}'.format(csr_name_full))
        csr2utils.csr2_peek_internal(csr_name_full)

    csr_name = 'hu1.fmr.switch_stat_cnt_2'
    for i in range(56):
        csr_name_full = csr_name + '[{}]'.format(i)
        print('\ncsr: {}'.format(csr_name_full))
        csr2utils.csr2_peek_internal(csr_name_full)

def hu_csr2_dump(perioc_interval=0):
    if perioc_interval > 0:
        iter_cnt = 0
        while True:
            print('\n\nhu_csr_dump: iteration: {}'.format(iter_cnt))
            _hu_csr2_dump()
            time.sleep(perioc_interval)
            iter_cnt += 1
    else:
        _hu_csr2_dump()

# MIO2 csrs
mio2_csr_list = ['mio2.i2c_m0_pad_cfg',
                 'mio2.i2c_sl_pad_cfg',
                 'mio2.non_fatal_int.diag']

def _mio2_csr_dump():
    for num,csr in enumerate(mio2_csr_list):
        print('csr: [{}/{}] {}'.format(num+1, len(mio2_csr_list), csr))
        csr2utils.csr2_peek_internal(csr);

def mio2_csr_dump(perioc_interval=0):
    if perioc_interval > 0:
        iter_cnt = 0
        while True:
            print('\n\nmio2_csr_dump: iteration: {}'.format(iter_cnt))
            _mio2_csr_dump()
            time.sleep(perioc_interval)
            iter_cnt += 1
    else:
        _mio2_csr_dump()

# Main
def main():
    parser = argparse.ArgumentParser(
        description="csr read/write utilities")

    parser.add_argument("--dut", required=True, type=str, help="Dut name")
    parser.add_argument("--mode", required=True, type=str, help="Dut name")
    parser.add_argument("--hu", action='store_true', help="hu csrs")
    parser.add_argument("--mio2", action='store_true', help="mio2 csrs")
    parser.add_argument("--period", type=int, default=0, choices=range(31), help="peridoc dump interval")

    args = parser.parse_args()
    print args

    probe = connect(dut_name=args.dut, mode=args.mode, force_connect=True)
    if not probe:
        logger.error('Failed to connect to dut:{0}'.format(args.dut))
        return

    if args.hu:
        hu_csr2_dump(args.period)

    if args.mio2:
        mio2_csr_dump(args.period)

    probe.disconnect()

if __name__== "__main__":
    main()
