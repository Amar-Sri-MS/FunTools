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


hu_csr_list = ['mio2.i2c_m0_pad_cfg',
               'mio2.i2c_sl_pad_cfg',
               'mio2.non_fatal_int.diag']

def _csr2dump():
    for num,csr in enumerate(hu_csr_list):
        logger.info('csr: [{}/{}] {}'.format(num+1, len(hu_csr_list), csr))
        csr2utils.csr2_peek_internal(csr);

def main():
    parser = argparse.ArgumentParser(
        description="DDR memory read/write utilities")

    parser.add_argument("--dut", required=True, type=str, help="Dut name")
    parser.add_argument("--mode", required=True, type=str, help="Dut name")

    args = parser.parse_args()

    probe = connect(dut_name=args.dut, mode=args.mode, force_connect=True)
    if not probe:
        logger.error('Failed to connect to dut:{0}'.format(args.dut))
        return

    _csr2dump()

    probe.disconnect()

if __name__== "__main__":
    main()
