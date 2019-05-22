#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
#    gdbserver.py - Control OllyDBG2 with GDB over the network! (for fun)
#    Copyright (C) 2013 Axel "0vercl0k" Souchet - http://www.twitter.com/0vercl0k
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# from ollyapi import *
import sys
import socket
import logging
import struct
import optparse

GDB_SIGNAL_TRAP = 5

###
##  File Corpse
#

class FileCorpse:

    def __init__(self, fname):
        self.fname = fname
        self.fl = open(fname)
        self.memoffset = 0 # FIXME: remove
        self.threadid = 0
        self.threadcount = 0
        self.thread_list = []
        self.thread_enumerator = 0
        self.vpnumtab = {}
        self.symbollist = [
            "_vplocal_arr",
            "_topo_vp",
            "exception_stack_memory",
            "PLATFORM_DEBUG_CONSTANT_vplocal_stride",
            "PLATFORM_DEBUG_CONSTANT_debug_context_offset",
            "PLATFORM_DEBUG_CONSTANT_ccv_state_invalid",
            "PLATFORM_DEBUG_CONSTANT_ccv_state_offline",
            "PLATFORM_DEBUG_CONSTANT_ccv_state_online",
            "PLATFORM_DEBUG_CONSTANT_topo_vp_stride",
        ]
        self.symbols = None

    def badread(self, n):
        return "\xde\xad\xbe\xef\xde\xad\xbe\xef"[:n]

    def virt2phys(self, addr):

        # check the top bit for TLB VA
        kseg = addr >> 56
        if (kseg == 0xc0):
            # magic expander section
            if (addr & (1<<47)):
                raise RuntimeError("double guard page!")
            else:
                offset = addr & 0xfff
                addr &= 0xfffffffff000
                addr >>= 1
                addr |= offset
        elif (kseg == 0xff):
            addr = addr & 0x1fffffff

        # truncate remaining bits to 8gb
        addr &= (8<<30)-1
        if (addr < self.memoffset):
            return None

        return addr

    def readbytes(self, addr, n):
        addr = self.virt2phys(addr)
        if (addr is None):
            print "zero read"
            return self.badread(n)

        regaddr = addr - self.memoffset
        # print "read at addr: 0x%x" % regaddr
        self.fl.seek(regaddr)
        bytes = self.fl.read(n)
        if (len(bytes) < n):
            # can't seek
            print "short read at 0x%x" % regaddr
            return self.badread(n)
        return bytes


    def find_exception_base(self):
        if (self.symbols is None):
            return None

        vpnum = self.vpnumtab[self.threadid]

        if (False):
            b = self.symbols["exception_stack_memory"]
            o = (vpnum + 1) * 4096 - (32*8)
            return b + o
        else:
            p = self.symbols["_vplocal_arr"]
            n = self.ReadMemory64(self.symbols["PLATFORM_DEBUG_CONSTANT_vplocal_stride"], host=True)
            o = self.ReadMemory64(self.symbols["PLATFORM_DEBUG_CONSTANT_debug_context_offset"], host=True)

            ptr = p + vpnum * n + o
            base = self.ReadMemory64(ptr, host=True)

            # print "exception base = 0x%x + %d * %d + 0x%x = 0x%x -> 0x%x" % (p, vpnum, n, o, ptr, base)

        return base

    def ReadMemory8(self, addr):
        bytes = self.readbytes(addr, 1)
        value = struct.unpack("<B", bytes)[0]
        # print "value is 0x%0.2x" % value
        return value

    def ReadMemory16(self, addr):
        bytes = self.readbytes(addr, 2)
        value = struct.unpack("<H", bytes)[0]
        # print "value is 0x%0.4x" % value
        return value

    def ReadMemory32(self, addr, host=False):
        bytes = self.readbytes(addr, 4)
        if (host):
            value = struct.unpack(">I", bytes)[0]
        else:
            value = struct.unpack("<I", bytes)[0]
        # print "value is 0x%0.8x" % value
        return value

    def ReadMemory64(self, addr, host=False):
        bytes = self.readbytes(addr, 8)
        if (host):
            value = struct.unpack(">Q", bytes)[0]
        else:
            value = struct.unpack("<Q", bytes)[0]

        # print "value is 0x%0.16x" % value
        return value

    def GetThreadCount(self):
        return self.threadcount

    def SetThreadId(self, newid):
        if (newid not in self.thread_list):
            raise RuntimeError("FIXME: attempt to select bad thread ID %s" % newid)
        self.threadid = newid

    def GetThreadId(self):
        return self.threadid

    def ReadReg(self, name):

        if (name[0] == 'r'):
            regnum = int(name[1:])
            offset = regnum * 8
        elif (name == "status"):
            offset = -0x8
        elif (name == "pc"):
            offset = -0x10
        elif (name == "cause"):
            offset = -0x18
        elif (name == "bad"):
            offset = -0x20
        else:
            return 0x0

        base = self.find_exception_base()
        if (base is None):
            return 0xdeadbeefdeadbeef

        regaddr = base + offset

        value = self.ReadMemory64(regaddr)
        # print "thread %d reg %s: at 0x%x value 0x%x\n" % (self.threadid, name, regaddr, value)

        return value


    def GetNextThreadId(self):
        if (self.thread_enumerator >= self.threadcount):
            return None
        tid = self.thread_list[self.thread_enumerator]
        self.thread_enumerator += 1
        return tid

    def GetFirstThreadId(self):
        if (len(self.thread_list) > 0):
            self.thread_enumerator = 0
            return self.GetNextThreadId()
        else:
            return 0

    def vpnum_IsRunning(self, tid):
        p = self.symbols["_topo_vp"]
        n = self.ReadMemory64(self.symbols["PLATFORM_DEBUG_CONSTANT_topo_vp_stride"], host=True)
        online = self.ReadMemory64(self.symbols["PLATFORM_DEBUG_CONSTANT_ccv_state_online"], host=True)

        ptr = p + tid * n + 0 # FIXME: offset
        state = self.ReadMemory32(ptr, host=True)

        # print "thread %s state = 0x%x + %d * %d = 0x%x -> 0x%x" % (tid, p, n, tid, ptr, state)

        if (state == online):
            return True
        else:
            return False

    def IsRunning(self, tid):
        return (tid != 0)

    def ccv_vpnum(self, cl, co, vp):
        return cl * 24 + co * 4 + vp

    def ccv_is_running(self, cl, co, vp):
        return self.vpnum_IsRunning(self.ccv_vpnum(cl, co, vp))

    def setup_threadlist(self):
        for cl in range(9):
            for co in range(6):
                for vp in range(4):
                    if (self.ccv_is_running(cl, co, vp)):
                        tid = cl * 100 + co * 10 + vp
                        self.thread_list.append(tid)
                        self.vpnumtab[tid] = self.ccv_vpnum(cl, co, vp)
        self.threadcount = len(self.thread_list)

    def GetThreadInfo(self, tid):
        cl = int(tid / 100)
        co = int((tid % 100) / 10)
        vp = tid % 10
        return "ccv %d.%d.%d" % (cl, co, vp)

    def GetSymbolsNeeded(self):
        return self.symbollist

    def SymbolsLoaded(self, d):
        self.symbols = d

        self.setup_threadlist()



###
##  corpse management
#

corpse = None

def setup_corpse(opts, args):

    if (opts.hbmfile is None):
        raise RuntimeError("Expected: -F /path/to/hbmdump.bin")

    global corpse
    corpse = FileCorpse(opts.hbmfile)

###
##  helpers
#

done_sym = False

def hexstr(sym):
    s = ""

    for c in sym:
        n = ord(c)
        s += "%0.2x" % n

    return s

###
##  Machine hooks
#

def jtag_ReadMemory(size, addr):
    if (size == 1):
        r = struct.pack('<B', corpse.ReadMemory8(addr))
    elif (size == 2):
        r = struct.pack('<H', corpse.ReadMemory16(addr))
    elif (size == 4):
        r = struct.pack('<I', corpse.ReadMemory32(addr))
    elif (size == 8):
        r = struct.pack('<Q', corpse.ReadMemory64(addr))
    else:
        # else make a byte-by-byte read
        r = ""
        for i in range(size):
            r += struct.pack('<B', corpse.ReadMemory8(addr + i))


    return r

def jtag_SetCpuThreadId(obj, tid):
    if (tid > 0):
        tid -= 1000
        corpse.SetThreadId(tid)
    obj.send("OK")

def jtag_GetCpuThreadId():
    return 1000 + corpse.GetThreadId()

def jtag_ReadReg(name):
    return corpse.ReadReg(name)

def jtag_GetFirstThreadId():
    tid = corpse.GetFirstThreadId()
    if (tid != 0):
        tid += 1000
    return tid

def jtag_GetNextThreadId():
    tid = corpse.GetNextThreadId()
    if (tid is None):
        return tid
    return 1000 + tid

def jtag_IsRunning(tid):
    if (tid == 0):
        return False
    tid -= 1000
    return corpse.IsRunning(tid)

def jtag_GetThreadInfo(tid):
    if (tid == 0):
        return False
    tid -= 1000
    return corpse.GetThreadInfo(tid)

# All registers are transferred as 64 bit quantities in
# the order: 32 general-purpose; sr; lo; hi; bad; cause; pc; 32
# floating-point registers; fsr; fir; fp.
gprs = [ "r%s" % n for n in range(32) ]
sprs = [ "status", "lo", "hi", "bad", "cause", "pc" ]
fprs = [ "f%s" % n for n in range(32) ]
fsps = [ "fsr", "fir", "fp" ]

REGS = gprs + sprs + fprs + fsps

def jtag_GetReg(regno):
    r = REGS[regno]
    # print "reading %s" % r
    return jtag_ReadReg(r)

def jtag_GetRegList():
    l = []
    # GPR + FP regs
    count = len(REGS)
    for i in range(0,count):
        l.append(jtag_GetReg(i))

    return l

###
##  Original Code
#
def checksum(data):
    checksum = 0
    for c in data:
        checksum += ord(c)
    return checksum & 0xff


SYMLIST = None
SYMTAB = None
def deal_withsymbols(obj, reply):

    global SYMTAB
    global SYMLIST

    # first pass, load the symbol list
    if (reply is None):
        SYMLIST = corpse.GetSymbolsNeeded()

        if (SYMLIST is not None):
            SYMTAB = {}
    else:
        print reply
        toks = reply.split(":")
        SYMTAB[SYMLIST.pop(0)] = int(toks[1], 16)


    if (len(SYMLIST) == 0):
        corpse.SymbolsLoaded(SYMTAB)
        SYMTAB = None
        SYMLIST = None
        obj.send("OK")
        return

    s = "qSymbol:%s" % hexstr(SYMLIST[0])
    print "asking for symbol: %s" % s
    obj.send(s)



# Code a bit inspired from http://mspgcc.cvs.sourceforge.net/viewvc/mspgcc/msp430simu/gdbserver.py?revision=1.3&content-type=text%2Fplain
class GDBClientHandler(object):
    def __init__(self, clientsocket):
        self.clientsocket = clientsocket
        self.netin = clientsocket.makefile('r')
        self.netout = clientsocket.makefile('w')
        self.log = logging.getLogger('gdbclienthandler')
        self.last_pkt = None

    def close(self):
        '''End of story!'''
        self.netin.close()
        self.netout.close()
        self.clientsocket.close()
        self.log.info('closed')

    def run(self):
        '''Some doc about the available commands here:
            * http://www.embecosm.com/appnotes/ean4/embecosm-howto-rsp-server-ean4-issue-2.html#id3081722
            * http://git.qemu.org/?p=qemu.git;a=blob_plain;f=gdbstub.c;h=2b7f22b2d2b8c70af89954294fa069ebf23a5c54;hb=HEAD +
             http://git.qemu.org/?p=qemu.git;a=blob_plain;f=target-i386/gdbstub.c;hb=HEAD'''
        self.log.info('client loop ready...')
        while self.receive() == 'Good':
            pkt = self.last_pkt
            self.log.debug('receive(%r)' % pkt)
            # Each packet should be acknowledged with a single character. '+' to indicate satisfactory receipt
            self.send_raw('+')

            def handle_q(subcmd):
                '''
                subcmd Supported: https://sourceware.org/gdb/onlinedocs/gdb/General-Query-Packets.html#qSupported
                Report the features supported by the RSP server. As a minimum, just the packet size can be reported.
                '''
                if subcmd.startswith('Supported'):
                    self.log.info('Received qSupported command')
                    self.send('PacketSize=%x' % 4096)
                elif subcmd.startswith('Attached'):
                    self.log.info('Received qAttached command')
                    # https://sourceware.org/gdb/onlinedocs/gdb/General-Query-Packets.html
                    self.send('1')
                elif subcmd.startswith('C'):
                    self.send('T%.2x;' % jtag_GetCpuThreadId())
                elif (subcmd == "fThreadInfo"):
                    # FIXME: make a thread list
                    tid = jtag_GetFirstThreadId()
                    s = "m%x" % tid
                    print "sending first thread (%s)" % s
                    print s
                    self.send(s)
                elif (subcmd == "sThreadInfo"):
                    # FIXME: make a thread list
                    tid = jtag_GetNextThreadId()
                    if (tid is not None):
                        s = "m%x" % tid
                        print "sending next thread (%s)" % s
                        self.send(s)
                    else:
                        print "done sending threads"
                        self.send("l")
                elif (subcmd == "TStatus"):
                    # just a stub
                    self.send("T0")
                elif (subcmd == "Offsets"):
                    # no relocation (FIXME: need for u-boot?)
                    self.send("Text=00;Data=00;Bss=00")
                elif (subcmd == "Symbol::"):
                    # no symbols?
                    deal_withsymbols(self, None)
                elif (subcmd.startswith("Symbol:")):
                    deal_withsymbols(self, subcmd)
                elif (subcmd.startswith("ThreadExtraInfo")):
                    print subcmd
                    tid = int(subcmd.split(",")[1], 16)
                    info = jtag_GetThreadInfo(tid)
                    self.send(hexstr(info))
                else:
                    self.log.error('This subcommand %r is not implemented in q' % subcmd)
                    self.send('')

            def handle_h(subcmd):
                print subcmd
                op = subcmd[0]
                tid = int(subcmd[1:],16)
                jtag_SetCpuThreadId(self, tid)

            def handle_v(subcmd):
                print "v command %s" % subcmd
                self.send('')

            def handle_qmark(subcmd):
                self.send('S%.2x' % GDB_SIGNAL_TRAP)

            def handle_g(subcmd):
                if subcmd == '':
                    tid = jtag_GetCpuThreadId()
                    if (tid == 0):
                        self.send('E 37')
                    print "register read request on %d" % tid
                    # make all the registers
                    registers = jtag_GetRegList()
                    s = ''
                    for r in registers:
                        s += struct.pack('<Q', r).encode('hex')
                    print "regfile: %s" % s
                    self.send(s)
                else:
                    print "unknown 'g' subcommand?"

            def handle_p(subcmd):
                regno = int(subcmd)
                r = jtag_GetReg(regno)
                s = struct.pack('<I', r).encode('hex')
                print "reg %s: %s" % (regno, s)
                self.send(s)

            def handle_m(subcmd):
                addr, size = subcmd.split(',')
                addr = int(addr, 16)
                size = int(size, 16)
                self.log.info('Received a "read memory" command (@%#.8x : %d bytes)' % (addr, size))
                self.send(jtag_ReadMemory(size, addr).encode('hex'))

            def handle_s(subcmd):
                self.log.info('Received a "single step" command')
                jtag_StepInto()
                self.send('T%.2x' % GDB_SIGNAL_TRAP)

            def handle_T(subcmd):
                n = int(subcmd, 16)
                # print "checking thread %d" % n
                if (jtag_IsRunning(n)):
                    self.send('OK')
                else:
                    self.send('E 37')

            dispatchers = {
                'q' : handle_q,
                'H' : handle_h,
                '?' : handle_qmark,
                'g' : handle_g,
                'm' : handle_m,
                's' : handle_s,
                'v' : handle_v,
                'p' : handle_p,
                'T' : handle_T
            }

            cmd, subcmd = pkt[0], pkt[1 :]
            if cmd == 'k':
                break

            if cmd not in dispatchers:
                self.log.info('%r command not handled' % pkt)
                self.send('')
                continue

            dispatchers[cmd](subcmd)

        self.close()

    def receive(self):
        '''Receive a packet from a GDB client'''
        # XXX: handle the escaping stuff '}' & (n^0x0)
        csum = 0
        state = 'Finding SOP'
        packet = ''
        while True:
            c = self.netin.read(1)
            if c == '\x03':
                return 'Error: CTRL+C'

            if len(c) != 1:
                return 'Error: EOF'

            if state == 'Finding SOP':
                if c == '$':
                    state = 'Finding EOP'
            elif state == 'Finding EOP':
                if c == '#':
                    if csum != int(self.netin.read(2), 16):
                        raise Exception('invalid checksum')
                    self.last_pkt = packet
                    return 'Good'
                else:
                    packet += c
                    csum = (csum + ord(c)) & 0xff
            else:
                raise Exception('should not be here')

    def send(self, msg):
        '''Send a packet to the GDB client'''
        self.log.debug('send(%r)' % msg)
        self.send_raw('$%s#%.2x' % (msg, checksum(msg)))

    def send_raw(self, r):
        self.netout.write(r)
        self.netout.flush()

def main():
    parser = optparse.OptionParser(usage="usage: %prog [options] ")
    parser.add_option("-F", "--hbmfile", action="store", default=None)
    parser.add_option("-P", "--port", action="store", type="int", default=1234)

    (opts, args) = parser.parse_args()
    setup_corpse(opts, args)

    logging.basicConfig(level = logging.WARN)
    for logger in 'gdbclienthandler runner main'.split(' '):
        logging.getLogger(logger).setLevel(level = logging.INFO)

    log = logging.getLogger('main')
    port = opts.port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', port))
    log.info('listening on :%d' % port)
    sock.listen(1)
    conn, addr = sock.accept()
    log.info('connected')

    GDBClientHandler(conn).run()
    return 1

if __name__ == '__main__':
    main()
