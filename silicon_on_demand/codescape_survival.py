#!/usr/bin/env python3

## A set of functions to import into your codescape scripting to make
## life easier.

import os
import sys
import time

# import everything here, from your script, just import everything, too!
from imgtec.console import *

ADDR_AXI_REMAP =       0x37020000
ADDR_AXIM      =       0xC0000000
XKPHYS_UC = (0x2 <<62) | (((2) & 0x7) << 59)
XKPHYS_NC = (0x2 <<62) | (((1) & 0x7) << 59)
CCU_BASE = 0x0000080000000000
UBOOT_RESET    =       0xFFFFFFFFA0100000

# Kevin's magic CSR reset value version 1
# val = 0x2092104884c90080

def set_axim(addr):
    addr >>= 30
    word(ADDR_AXI_REMAP+0, addr)
    word(ADDR_AXI_REMAP+4, addr >> 32)

def csr_read_sbp(address):
    if (device() != thread(9,0,0)):
        print("not on SBP")
        return
    set_axim(address)
    address = address & 0x3FFFFFFF
    ret_lo = word(ADDR_AXIM | address)
    ret_hi = word(ADDR_AXIM | address + 4)
    return (ret_hi << 32) | ret_lo

def csr_write_sbp(address, val):
    if (device() != thread(9,0,0)):
        print("not on SBP")
        return
    set_axim(address)
    address = address & 0x3FFFFFFF
    doubleword(ADDR_AXIM | address, val)

def csr_read_n_sbp(address, count = 1):
    for i in range(0, count):
        addr = address + 8 * i
        print("%0.16x: %0.16x" % (addr, csr_read(addr)))

def xkw(address):
    return eword(XKPHYS_UC | address)

def xkd(address, wr=None):
    if (wr is None):
        # read
        return doubleword(XKPHYS_UC | address)
    else:
        doubleword(XKPHYS_UC | address, wr)

def csr_read_pc(address):
    if (device() == thread(9,0,0)):
        print("not on CC")
        return
    CSR_VADDR = XKPHYS_UC | CCU_BASE | address
    return doubleword(CSR_VADDR)

def csr_write_pc(address, val):
    if (device() == thread(9,0,0)):
        print("not on CC")
        return
    CSR_VADDR = XKPHYS_UC | CCU_BASE | address
    doubleword(CSR_VADDR, val)

def csr_read(address):
    try:
        # if (device() != thread(10,0,0)):
        if (False):
            return csr_read_pc(address)
        else:
            return csr_read_sbp(address)
    except:
        print("Exception reading CSR")
        return 0xdeadbeefdeadbeef

def csr_write(address, value):
    try:
        if (device() != thread(10,0,0)):
            print("pc write")
            csr_write_pc(address, value)
        else:
            csr_write_sbp(address)
    except:
        print("Exception writing CSR", sys.exc_info()[0])
        return None
    
def sbp():
    device(thread(10,0,0))

def pc(cluster):
    device(thread(cluster,0,0))
    
def cc():
    pc(9)

    
UART_CTRL   =0x0
UART_MODE   =0x4
UART_IER    =0x8
UART_BRGR   =0x18
UART_BDIVR  =0x34
UART_MSR    =0x28
UART_CSR    =0x2c
UART_CISR   =0x14
UART_RFIFO  =0x30
UART_TFIFO  =0x30
UART_REMPTY =0x1
UART_TEMPTY =0x3
UART_TFUL   =0x4
UART_IRDA   =0xb
UART_PARE   =0x7
APB0_BRIDGE_UART0_ADDR           = 0xb800000400

def _uart_rd64(regoffset):
    return csr_read(APB0_BRIDGE_UART0_ADDR + regoffset*2)

def _uart_wr64(regoffset, val):
    csr_write(APB0_BRIDGE_UART0_ADDR + regoffset * 2, val)

def uart_write_char(c):
    _uart_wr64(UART_TFIFO, ord(c))

def uart_print(s):
    for c in s:
        uart_write_char(c)

MCR_FCM_EN   = (1<<5)
FCDR_DEFAULT = (1<<4)
MODE_WSIZE_ONE  = (1<<12)
MODE_PAR_NONE   = (1<<5)
MODE_NBSTOP_ONE = (0)
MODE_CHRL_EIGHT = (0)

UART_MCR  = (0x24)
UART_FCDR = (0x38)

MODE_DEFAULT = (MODE_WSIZE_ONE | MODE_PAR_NONE | MODE_NBSTOP_ONE | MODE_CHRL_EIGHT)


def hbm_read(addr):
    csr_write(MUH_SNA_EXT_MEM_RW_CMD_ADDR, 0x8002000000000000 | addr)
    for i in range(0, 8):
        r = csr_read(MUH_SNA_EXT_MEM_RW_DATA_0_ADDR + i * 8)
        print("[%d] 0x%0.16x" % (i, r))

# addr >>= 6
# muh = addr & 3
# base = MUHS[muh] + rw_cmd_addr_offset
        
MUH_SNA_EXT_MEM_RW_CMD_ADDR_OFF     = 0x00f0
MUH_SNA_EXT_MEM_RW_DATA_0_ADDR_OFF  = 0x0100
MUHS = [0x9000190000, 0x90001a0000, 0x9800190000, 0x98001a0000]

def hbm_read_sbp(addr, clear=False):
    cache_addr = addr >> 6
    muh_id = cache_addr & 3
    muh_addr = cache_addr >> 2
    muh_base = MUHS[muh_id]
    muh_cmd = muh_base + MUH_SNA_EXT_MEM_RW_CMD_ADDR_OFF
    muh_data = muh_base + MUH_SNA_EXT_MEM_RW_DATA_0_ADDR_OFF
    if (clear):
        print("clearing registers...")
        for i in range(0, 8):
            # print "clearing data CSR at 0x%x" % (muh_data + i * 8)
            csr_write_sbp(muh_data + i * 8, 0xce9ce9ce9ce9ce9c)
    else:
        print("not clearing registers...")
    print("issuing command to 0x%x" % muh_cmd)
    csr_write_sbp(muh_cmd, 0x8000000000000000 | (muh_addr <<37))
    for i in range(0, 8):
        # print "reading data CSR at 0x%x" % (muh_data + i * 8)
        r = csr_read_sbp(muh_data + i * 8)
        print("[0x%0.16x] 0x%0.16x" % ((cache_addr << 6) + i * 8, r))



def print_stack(sp):
    stack_top = (sp | 0xfff) + 1
    while (stack_top >= sp):
        stack_top -= 8
        print("0x%0.16x: 0x%0.16x" % (stack_top, doubleword(stack_top)))



CCU_CMD_TYPE_MSK=	(0x0f)
CCU_CMD_TYPE_SHF=	(60)
CCU_CMD_SIZE_MSK=	(0x3f)
CCU_CMD_SIZE_SHF=	(54)
CCU_CMD_RING_MSK=	(0x1f)
CCU_CMD_RING_SHF=	(49)
CCU_CMD_INIT_MSK=	(0x01)
CCU_CMD_INIT_SHF=	(48)
CCU_CMD_CRSV_MSK=	(0x03)
CCU_CMD_CRSV_SHF=	(45)
CCU_CMD_TAG_MSK=	(0x1f)
CCU_CMD_TAG_SHF=	(40)
CCU_CMD_BUSY_MSK=	(0x01)
CCU_CMD_BUSY_SHF=	(47)
CCU_CMD_SRSV_MSK=	(0x03)
CCU_CMD_SRSV_SHF=	(44)
CCU_CMD_CLM_MSK=	(0x01)
CCU_CMD_CLM_SHF=	(43)
CCU_CMD_RSP_MSK=	(0x07)
CCU_CMD_RSP_SHF=	(40)
CCU_CMD_ADDR_MSK =	(0x0ffffffffff)
CCU_CMD_ADDR_SHF =	(0)

CCU_CMD_TYPE_REQ= 0
CCU_CMD_TYPE_GRANT= 1
CCU_CMD_TYPE_RD_T= 2
CCU_CMD_TYPE_WR_T= 3
CCU_CMD_TYPE_RD_RSP= 4
CCU_CMD_TYPE_WR_RSP= 5
CCU_CMD_SIZE_64= 0
CCU_CMD_SIZE_1= 1
CCU_CMD_SIZE_2= 2
CCU_CMD_SIZE_3= 3
CCU_CMD_SIZE_4= 4
CCU_CMD_SIZE_5= 5
CCU_CMD_SIZE_6= 6
CCU_CMD_INIT_DIS= 0
CCU_CMD_INIT_ENB= 1
CCU_RING_SHF	=(35)
CCU_RING_MSK	=(0x1f)

def CCU_CMD(ty, sz, rn, init, tag, adr):
    v = ((((ty)   & CCU_CMD_TYPE_MSK) << CCU_CMD_TYPE_SHF) | (((sz)   & CCU_CMD_SIZE_MSK) << CCU_CMD_SIZE_SHF) | (((rn)   & CCU_CMD_RING_MSK) << CCU_CMD_RING_SHF) | (((init) & CCU_CMD_INIT_MSK) << CCU_CMD_INIT_SHF) | (((tag)  & CCU_CMD_TAG_MSK)  << CCU_CMD_TAG_SHF) | (((adr)  & CCU_CMD_ADDR_MSK) << CCU_CMD_ADDR_SHF))
    return v

def csr_wide_read_cmd(addr, nwords):
    if (nwords <= 0):
        print("bad nwords")
        return None
    cmd_sz = nwords - 1
    rng_sel = ((addr >> CCU_RING_SHF) & CCU_RING_MSK)
    cmd = CCU_CMD(CCU_CMD_TYPE_RD_T, cmd_sz, rng_sel, CCU_CMD_INIT_DIS, 0, addr)
    return cmd

def csr_wide_write_cmd(addr, nwords):
    if (nwords <= 0):
        print("bad nwords")
        return None
    cmd_sz = nwords - 1
    rng_sel = ((addr >> CCU_RING_SHF) & CCU_RING_MSK)
    cmd = CCU_CMD(CCU_CMD_TYPE_WR_T, cmd_sz, rng_sel, CCU_CMD_INIT_DIS, 0, addr)
    return cmd

def resettron(fname = "/tmp/reset-device.now"):
    print("Polling on %s" % fname)
    while (1):
        if (os.path.isfile(fname)):
            try:
                os.remove(fname)
            except:
                raise RuntimeError("Failed to remove signal file, barf")
            print("Restting device due to existence of %s" % fname)
            try:
                reset(hard_run)
            except:
                print("NOTE: exception during reset. Not entirely unexpected")
            print("Returning to poll on %s" % fname)
        time.sleep(1)


# almost 1152000 (not 115200!)
UART_1152000 = (3, 28)
UART_500KBIT = (40, 4)
UART_1MBIT = (20, 4)
UART_2MBIT = (10, 4)
UART_4MBIT = (5, 4)

def reprogram_uart0(params):
    brgr = params[0]
    bdivr = params[1]
    _uart_wr64(UART_CTRL, 0x28);
    _uart_wr64(UART_BRGR, brgr);
    _uart_wr64(UART_BDIVR, bdivr);
    _uart_wr64(UART_CTRL, 0x3);
    _uart_wr64(UART_MODE, MODE_DEFAULT);
    _uart_wr64(UART_MCR,  MCR_FCM_EN);
    _uart_wr64(UART_FCDR, FCDR_DEFAULT);
    _uart_wr64(UART_CTRL, 0x14);
    _uart_wr64(UART_IER, (1<<UART_TEMPTY) | (1<<UART_REMPTY));




CC_EFI_QSTATE_MEM_BASE_BASE_ADR_LSB =   28
CC_EFI_QSTATE_MEM_BASE_CC = 0x4883000208
CC_EFI_MEM_INIT_LEN_LEN_LSB = 48
CC_EFI_MEM_INIT_LEN_CC = 0x48830001c8
CC_EFI_MEM_INIT_START_CC = 0x48830001d0
CC_EFI_MEM_INIT_DONE_CC = 0x48830001D8
CC_EFI_STATS_ADDR_CC = 0x4883901800

def hbm_init_sbp(base, size):
    sbp()
    magic = 1<<36
    #data64_rb[0] = 0;
    #data64_fb[0] = qstate_base_adr;
    if (base & 0x3f):
        print("base must be 64B aligned")
        return
    if (size & 0x3f):
        print("size must be 64B aligned")
    base = base | magic
    base = base >> 6
    size = size >> 6
    if (size > 65535):
        print("size must be  <= 65535 lines")
        return
    #CC_EFI_QSTATE_MEM_BASE_BASE_ADR_WRITE(data64_rb, data64_fb);
    val = base << CC_EFI_QSTATE_MEM_BASE_BASE_ADR_LSB
    #CC_EFI_QSTATE_MEM_BASE_WRITE(get_unit_base_addr(8,PCC_CSR_UNIT_TYPE_EQM),
    #      data64_rb);
    csr_write_sbp(CC_EFI_QSTATE_MEM_BASE_CC, val)
    # write the length of the init, max is 32768:
    # CC_EFI_MEM_INIT_LEN_LEN_WRITE(data64_rb, data64_fb);
    val = size << CC_EFI_MEM_INIT_LEN_LEN_LSB
    # CC_EFI_MEM_INIT_LEN_WRITE(get_unit_base_addr(8,PCC_CSR_UNIT_TYPE_EQM),data64_rb);
    csr_write_sbp(CC_EFI_MEM_INIT_LEN_CC, val)
    # then start the engine:
    #data64_rb[0] = 0;
    #data64_fb[0] = 1;
    # CC_EFI_MEM_INIT_START_START_WRITE(data64_rb, data64_fb);
    # CC_EFI_MEM_INIT_START_WRITE(get_unit_base_addr(8,PCC_CSR_UNIT_TYPE_EQM),data64_rb);
    csr_write_sbp(CC_EFI_MEM_INIT_START_CC, 0)
    csr_write_sbp(CC_EFI_MEM_INIT_START_CC, 1<<63)
    # print stop
    print("done: 0x%x" % csr_read_sbp(CC_EFI_MEM_INIT_DONE_CC))
    print("stats: 0x%x" % csr_read_sbp(CC_EFI_STATS_ADDR_CC))

def zd():
    cc()
    for i in range (0,8):
        print(hex(xkd(i*64)))

PROBES = { "sb-01": ("sp55e", "10.1.40.82"),
           "sb-02": ("sp0491", "10.1.40.83"),
           "sb-04": ("sp55e", "10.1.40.85"),
           }
def connect_to_sb_probe(sbid, no_detect=False):
    if (sbid not in list(PROBES.keys())):
        raise RuntimeError("unknown probe %s (known ids %s)" % (sbid, list(PROBES.keys())))

    p = probe(PROBES[sbid][0], ip_address=PROBES[sbid][1])

    if (no_detect):
        return

    # do the sequence
    print("handshaking...")
    reset(probe)
    tckrate(25000000)
    autodetect()

