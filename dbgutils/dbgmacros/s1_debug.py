#!/usr/bin/env python2.7

"""
Sample s1 debug utility functions for convenient debugging

Usage:
------
python s1_debug.py --dut S1DB-4 --mode jtag <options>
"""
from csrutils.csrutils import *
from csr2utils import *
import time

logger = logging.getLogger("s1_debug")
logger.setLevel(logging.INFO)

# HSU csr dump
def _hu_csr2_dump():
    csr_name = 'hu0.fmr.switch_stat_cnt_0'
    for i in range(82):
        csr_name_full = csr_name + '[{}]'.format(i)
        print('csr: {}'.format(csr_name_full))
        csr2utils.csr2_peek(csr_name_full)

    csr_name = 'hu0.fmr.switch_stat_cnt_1'
    for i in range(8):
        csr_name_full = csr_name + '[{}]'.format(i)
        print('\ncsr: {}'.format(csr_name_full))
        csr2utils.csr2_peek(csr_name_full)

    csr_name = 'hu0.fmr.switch_stat_cnt_2'
    for i in range(56):
        csr_name_full = csr_name + '[{}]'.format(i)
        print('\ncsr: {}'.format(csr_name_full))
        csr2utils.csr2_peek(csr_name_full)

    csr_name = 'hu1.fmr.switch_stat_cnt_0'
    for i in range(82):
        csr_name_full = csr_name + '[{}]'.format(i)
        print('\ncsr: {}'.format(csr_name_full))
        csr2utils.csr2_peek(csr_name_full)

    csr_name = 'hu1.fmr.switch_stat_cnt_1'
    for i in range(8):
        csr_name_full = csr_name + '[{}]'.format(i)
        print('\ncsr: {}'.format(csr_name_full))
        csr2utils.csr2_peek(csr_name_full)

    csr_name = 'hu1.fmr.switch_stat_cnt_2'
    for i in range(56):
        csr_name_full = csr_name + '[{}]'.format(i)
        print('\ncsr: {}'.format(csr_name_full))
        csr2utils.csr2_peek(csr_name_full)

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
        csr2utils.csr2_peek(csr);

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

def mio2_cfg():
    csr = 'mio2.scratchpad'
    print('configuring csr: {}'.format(csr))
    csr2utils.csr2_poke(csr, [0x1234567AA2345678]);
    csr2utils.csr2_peek(csr);
    print('configuring csr: {}'.format(csr))
    csr2utils.csr2_poke(csr, [0x1234567AA2345]);
    csr2utils.csr2_peek(csr);

# Main
def main():
    parser = argparse.ArgumentParser(
        description="s1 debug utilities")

    parser.add_argument("--dut", required=True, type=str, help="Dut name")
    parser.add_argument("--mode", required=True, type=str, help="Dut name")
    parser.add_argument("--dump-hu", action='store_true', help="hu csrs")
    parser.add_argument("--dump-mio2", action='store_true', help="mio2 csrs")
    parser.add_argument("--mio2-cfg", action='store_true', help="Write mio2 config")
    parser.add_argument("--period", type=int, default=0, choices=range(31), help="peridoc dump interval")

    args = parser.parse_args()
    print args

    probe = connect(dut_name=args.dut, mode=args.mode, force_connect=True)
    if not probe:
        logger.error('Failed to connect to dut:{0}'.format(args.dut))
        return

    if args.dump_hu:
        hu_csr2_dump(args.period)

    if args.dump_mio2:
        mio2_csr_dump(args.period)

    if args.mio2_cfg:
        mio2_cfg()

    probe.disconnect()

if __name__== "__main__":
    main()
