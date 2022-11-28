#!/usr/bin/env python3
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

import os
import sys
import uuid
import excat
import struct
import select
import socket
import logging
import argparse
import binascii
import platform
import traceback
import subprocess
import uuid_extract
import signal

try:
    import idzip
    have_idzip = True
except:
    print("Failed to import idzip decompressor, doing without")
    have_idzip = False


try:
    import elftools
    from elftools.elf.elffile import ELFFile
    have_elftools = True
except:
    print("Failed to import pyelftools, will not handle ELF core dumps")
    have_elftools = False


GDB_SIGNAL_TRAP = 5

opts = None

###
##  Logging
#

log_file = sys.stderr

def LOG(msg, suffix = "\n"):
    log_file.write(msg + suffix)
    if (opts.verbose >= 2):
        # flush if we're doing serious debug
        log_file.flush()

def LOG_ALWAYS(msg):
    msg += "\n"
    prefix = ""
    if (not opts.server_only):
        prefix = "fungdbserver: "
    fl = sys.stderr
    if (opts.crashlog):
        fl = sys.stdout
    fl.write(prefix + msg)
    if (log_file != sys.stderr):
        # echo it to the log
        LOG(msg, "")

def DEBUG(msg):
    if (opts.verbose >= 2):
        LOG(msg)

def ERROR(msg):
    LOG_ALWAYS(msg)

###
##  platform details
#

def get_default_gdb():
    current_os = platform.system()
    if current_os == 'Darwin':
        gdbs = ['/Users/Shared/cross-py3/bin/mipsel-unknown-linux-gnu-gdb',
                '/Users/Shared/cross/mips64/bin/mips64-unknown-elf-gdb',
                '/Users/Shared/cross-el/bin/mips64-gdb']
    else:
        gdbs = ['/opt/cross/mips64/bin/mips64-unknown-elf-gdb']

    for gdb in gdbs:
        if (os.path.exists(gdb)):
            return gdb

    # return something so the user can override it
    return "mips64-gdb"

def get_default_dir():

    if (os.environ.get("FUNOS_SRC") is not None):
        return os.environ.get("FUNOS_SRC")

    if (os.environ.get("WORKSPACE") is not None):
        return os.path.join(os.environ.get("WORKSPACE"), "FunOS")

    return None

def get_sdkdir():

    sdk = os.environ.get("SDKDIR")
    if (sdk is not None):
        return sdk

    workspace = os.environ.get("WORKSPACE")
    if (workspace is not None):
        sdk = os.path.join(workspace, "FunSDK")
        return sdk

    # try relative to the script - a few levels of "../"
    for i in range (1,6):
        workspace = os.path.dirname(os.path.realpath(__file__))
        for j in range(i):
            workspace = os.path.dirname(workspace)
        DEBUG("workspace search: %s" % workspace)
        sdk = os.path.join(workspace, "FunSDK")
        sdk2 = os.path.join(sdk, "FunSDK")
        print("Trying %s" % sdk)
        if (os.path.exists(sdk) and os.path.exists(sdk2)):
            return sdk

    # try relative to the dir - ".."
    if (opts.dir is not None):
        workspace = os.path.dirname(opts.dir)
        sdk = os.path.join(workspace, "FunSDK")
        if (os.path.exists(sdk)):
            return sdk

    # no idea -- assume CWD
    return "."



def get_script():

    # handle user input
    if (opts.script is not None):
        if (os.path.isfile(opts.script)):
            LOG_ALWAYS("using specified script %s" % opts.script)
            return opts.script
        else:
            # they want/get nothing
            LOG_ALWAYS("specified script %s invalid, ignoring" % opts.script)
            return None

    # default logic: get a file from FunSDK
    # since it's hopefully the most recent
    # otherwise, scrape FunOS which could be older
    LOG_ALWAYS("sdkdir is %s" % get_sdkdir())
    script = os.path.join(get_sdkdir(), "bin/scripts/funos_gdb.py")
    if (os.path.isfile(script)):
        LOG_ALWAYS("using script from FunSDK %s" % get_sdkdir())
        return script

    if (opts.dir is not None):
        script = os.path.join(opts.dir, "scripts/funos_gdb.py")
        if (os.path.isfile(script)):
            LOG_ALWAYS("using script from --dir")
            return script

    # no idea
    LOG_ALWAYS("could not find a script file")
    return None

###
##  File Corpse
#

def open_idzip(fname, use_http):

    if (not have_idzip):
        print("cannot open this file without idzip package")
        print("% pip3 install python-idzip")
        sys.exit(1)

    idzip.decompressor.SELECTED_CACHE = idzip.caching.LuckyCache
    if (use_http):
        # just hand over the file directly
        fl = httpfile.HttpFile(fname)
        dzfile = idzip.decompressor.IdzipFile(None, fl)

        # default if the not specified
        if (opts.gdb_timeout is None):
            opts.gdb_timeout = 20
    else:
        dzfile = idzip.decompressor.IdzipFile(fname)
    return dzfile

class FileCorpse:

    def __init__(self, fname, use_idzip = False, use_http = False):
        self.fname = fname
        self.idzip = use_idzip
        self.memoffset = 0
        self.threadid = 0
        self.threadcount = 0
        self.thread_list = []
        self.thread_enumerator = 0
        self.vpnumtab = {}
        self.symbollist = [
            "_vplocal_arr",
            "_topo_vp",
            "exception_stack_memory",
            "stack_memory",
            "tls_mem_block",
            "tls_stride",
            "tls_mem_block_size",
            "PLATFORM_DEBUG_CONSTANT_vplocal_stride",
            "PLATFORM_DEBUG_CONSTANT_debug_context_offset",
            "PLATFORM_DEBUG_CONSTANT_ccv_state_invalid",
            "PLATFORM_DEBUG_CONSTANT_ccv_state_offline",
            "PLATFORM_DEBUG_CONSTANT_ccv_state_online",
            "PLATFORM_DEBUG_CONSTANT_topo_vp_stride",
            "PLATFORM_DEBUG_CONSTANT_DISPATCH_STACK_TOKEN_SHIFT",
            "PLATFORM_DEBUG_CONSTANT_DISPATCH_STACK_CLUSTER_SHIFT",
            "PLATFORM_DEBUG_CONSTANT_DISPATCH_STACK_CORE_SHIFT",
            "PLATFORM_DEBUG_CONSTANT_DISPATCH_STACK_VP_SHIFT",
            "PLATFORM_DEBUG_CONSTANT_DISPATCH_STACK_SIZE",
            "PLATFORM_DEBUG_CONSTANT_DISPATCH_STACK_BAD_MASK",
        ]
        self.symbols = None

        self.fl = self.open_file(use_idzip, use_http)

        # ELFFile object or None if this is not elf
        self.elf = None
        if self.is_elf_corpse():
            if not have_elftools:
                raise RuntimeError("need pyelftools to open ELF file: "
                                   "try pip3 install pyelftools")
            print("Opening file as ELF corpse...")
            fh = self.open_file(use_idzip, use_http)
            actual_size = self.get_file_size(fh, use_idzip)

            self.elf = ELFFile(fh)
            if not opts.skip_dump_size_check:
                self.verify_dump_size(actual_size)

        # ELF segment headers in memory, faster than reading from file
        self.elf_phdrs = []

    def open_file(self, use_idzip, use_http):
        if (use_idzip):
            return open_idzip(self.fname, use_http)
        else:
            return open(self.fname, "rb")

    def is_elf_corpse(self):
        """ Whether this corpse is an ELF core file """
        magic_len = 4
        magic = self.fl.read(magic_len)
        if len(magic) == magic_len:
            # binary mode means the type should be bytes, so look for 0x7'ELF'
            return (magic[0] == 0x7f and magic[1] == 0x45 and
                    magic[2] == 0x4c and magic[3] == 0x46)
        return False

    def verify_dump_size(self, actual_size):
        """ Check actual file size against ELF note and bail out on mismatch """
        edn = ELFDumpNote(self.elf)
        note = edn.get_note()

        if note:
            expected_size = note.get("dump_size")
            if expected_size != actual_size:
                raise RuntimeError("bad dump size (corrupt ELF?):"
                                   " expected %d bytes got %d bytes" % (expected_size, actual_size))

    def get_file_size(self, fh, is_idzip):
        if is_idzip:
            return self.get_idzip_size_binary_search(fh)
        else:
            fh.seek(0, os.SEEK_END)
            size = fh.tell()
            fh.seek(0)
            return size

    def get_idzip_size_binary_search(self, fh):
        """
        Find the uncompressed size via binary search.

        idzip does not support relative seeking from the end of file, and does
        not have a public way to obtain the uncompressed file size. Summing
        the file sizes of the internal members does the trick, but that's
        internal.

        Note that looking at the final 4 bytes only reveals the last member's
        file size so that's not an option as well.
        """
        first = 0
        last = 64 << 30  # 64GB, bigger than any hbm dump

        # find the first point at which read(1) returns EOF
        while first < last:
            pos = first + (last - first) // 2
            fh.seek(pos)
            b = fh.read(1)

            if b:
                first = pos + 1
            else:
                # Traditional is pos - 1, but we want last to always be EOF.
                # This modification should still terminate because we take
                # the floor of (first + last) / 2.
                last = pos

        fh.seek(0)  # just be nice and undo
        return first

    def badread(self, n):
        return b"\xde\xad\xbe\xef\xde\xad\xbe\xef"[:n]

    def va_clean(self, addr):
        # truncate remaining bits to the physical address
        addr &= (1<<42)-1
        if (addr < self.memoffset):
            return None

        return addr

    def decode_dispatch_stack_addr(self, addr):

        # filter out bogus
        if (addr & self.rdsym("PLATFORM_DEBUG_CONSTANT_DISPATCH_STACK_BAD_MASK")):
            return None

        cluster = (addr >> self.rdsym("PLATFORM_DEBUG_CONSTANT_DISPATCH_STACK_CLUSTER_SHIFT")) & 0xf
        core = (addr >> self.rdsym("PLATFORM_DEBUG_CONSTANT_DISPATCH_STACK_CORE_SHIFT")) & 0xf
        vp = (addr >> self.rdsym("PLATFORM_DEBUG_CONSTANT_DISPATCH_STACK_VP_SHIFT")) & 0xf

        vpnum = self.ccv_vpnum(cluster, core, vp)

        ss = self.rdsym("PLATFORM_DEBUG_CONSTANT_DISPATCH_STACK_SIZE")

        va = self.symbols["stack_memory"]
        va += vpnum * ss
        va += addr & (ss-1)

        return self.va_clean(va)

    def virt2phys(self, addr):

        # check the top bit for TLB VA
        kseg = addr >> 56
        if (kseg == 0xc0):
            ## dispatch stack
            if (((addr >> self.rdsym("PLATFORM_DEBUG_CONSTANT_DISPATCH_STACK_TOKEN_SHIFT")) & 0xf) >= 0xe):
                return self.decode_dispatch_stack_addr(addr)

            ## guard page
            # magic expander section
            if (addr & (1<<47)):
                addr &= ~(1<<47);

            offset = addr & 0xfff
            addr &= 0xfffffffff000
            addr >>= 1
            addr |= offset
        elif (kseg == 0xff):
            addr = addr & 0x1fffffff

        addr = self.va_clean(addr)

        return addr

    def elf_load_phdrs(self):
        for seg in self.elf.iter_segments():
            if seg['p_type'] == 'PT_LOAD':
                self.elf_phdrs.append(seg)

    def elf_offset(self, addr):
        phys = self.virt2phys(addr)

        if (phys is None):
            return None

        if not self.elf_phdrs:
            self.elf_load_phdrs()

        # Look up the file offset in the ELF segments
        # We can do better than this linear search, really
        for seg in self.elf_phdrs:
            seg_paddr = seg["p_paddr"]
            if (phys >= seg_paddr and phys < seg_paddr + seg["p_filesz"]):
                return seg["p_offset"] + phys - seg_paddr

        # Houston, we have a problem
        return None

    def readbytes(self, addr, n):
        if self.elf is None:
            addr = self.virt2phys(addr)
        else:
            addr = self.elf_offset(addr)

        if (addr is None):
            DEBUG("zero read")
            return self.badread(n)

        regaddr = addr - self.memoffset
        DEBUG("read at addr: 0x%x" % regaddr)
        self.fl.seek(regaddr)
        bytes = self.fl.read(n)
        if (len(bytes) < n):
            # can't seek
            DEBUG("Short read at offset 0x%x. Expected %d bytes, got %d" % (regaddr, n, len(bytes)))
            return self.badread(n)
        return bytes


    def find_context_from_stack(self):
        vpnum = self.vpnumtab[self.threadid]
        b = self.symbols["exception_stack_memory"]
        o = (vpnum + 1) * 4096 - (32*8)
        return b + o


    def find_exception_base(self):
        if (self.symbols is None):
            return None

        vpnum = self.vpnumtab[self.threadid]

        if (False):
            return self.find_context_from_stack()
        else:
            p = self.symbols["_vplocal_arr"]
            n = self.rdsym("PLATFORM_DEBUG_CONSTANT_vplocal_stride")
            o = self.rdsym("PLATFORM_DEBUG_CONSTANT_debug_context_offset")

            ptr = p + vpnum * n + o
            base = self.ReadMemory64(ptr, host=True)

            DEBUG("exception base = 0x%x + %d * %d + 0x%x = 0x%x -> 0x%x" % (p, vpnum, n, o, ptr, base))

        if (base == 0):
            DEBUG("NULL exception base, going straight to stack memory")
            return self.find_context_from_stack()

        return base

    def ReadMemory8(self, addr):
        bytes = self.readbytes(addr, 1)
        value = struct.unpack("<B", bytes)[0]
        DEBUG("value is 0x%0.2x" % value)
        return value

    def ReadMemory16(self, addr):
        bytes = self.readbytes(addr, 2)
        value = struct.unpack("<H", bytes)[0]
        DEBUG("value is 0x%0.4x" % value)
        return value

    def ReadMemory32(self, addr, host=False):
        bytes = self.readbytes(addr, 4)
        if (host):
            value = struct.unpack(">I", bytes)[0]
        else:
            value = struct.unpack("<I", bytes)[0]
        DEBUG("value is 0x%0.8x" % value)
        return value

    def ReadMemory64(self, addr, host=False):
        bytes = self.readbytes(addr, 8)
        if (host):
            value = struct.unpack(">Q", bytes)[0]
        else:
            value = struct.unpack("<Q", bytes)[0]

        DEBUG("value is 0x%0.16x" % value)
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
        DEBUG("thread %d reg %s: at 0x%x value 0x%x\n" % (self.threadid, name, regaddr, value))

        return value


    def GetNextThreadId(self):
        if (len(self.thread_list) == 0):
            return None
        if (self.thread_enumerator >= self.threadcount):
            return None
        tid = self.thread_list[self.thread_enumerator]
        self.thread_enumerator += 1
        return tid

    def GetFirstThreadId(self):
        if (len(self.thread_list) > 0):
            self.thread_enumerator = 0
            return self.thread_list[0]
        else:
            return None

    def rdsym(self, symname):

        p = self.symbols[symname]
        if (p < 0x10000):
            # XXX: temp hack for defaults
            return p
        else:
            return self.ReadMemory64(self.symbols[symname], host=True)

    def vpnum_IsRunning(self, tid):
        p = self.symbols["_topo_vp"]
        n = self.rdsym("PLATFORM_DEBUG_CONSTANT_topo_vp_stride")
        online = self.rdsym("PLATFORM_DEBUG_CONSTANT_ccv_state_online")

        ptr = p + tid * n + 0 # FIXME: offset
        state = self.ReadMemory32(ptr, host=True)

        LOG("thread %s state = 0x%x + %d * %d = 0x%x -> 0x%x" % (tid, p, n, tid, ptr, state))

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
                    tid = cl * 100 + co * 10 + vp
                    if (self.ccv_is_running(cl, co, vp)):
                        DEBUG(f"Adding vpnumtab {tid}")
                        self.thread_list.append(tid)
                        self.vpnumtab[tid] = self.ccv_vpnum(cl, co, vp)
                    else:
                        DEBUG(f"Thread {cl}.{co}.{vp} ({tid}) is not running")
        self.threadcount = len(self.thread_list)
        LOG("FunOS has %d online threads" % self.threadcount)

        if (self.threadcount == 0):
            print("WARNING: No online threads!")
        elif (self.threadid not in self.thread_list):
            tid = self.thread_list[0]
            DEBUG(f"Default thread {self.threadid} not running / " +
                  "does not exist. Setting to thread {tid}")
            self.SetThreadId(tid)

    def GetThreadInfo(self, tid):
        cl = int(tid / 100)
        co = int((tid % 100) / 10)
        vp = tid % 10
        return "ccv %d.%d.%d" % (cl, co, vp)

    def GetTLSBase(self, tid):
        cl = int(tid / 100) % 10
        co = int(tid / 10) % 10
        vp = tid % 10
        vpnum = self.ccv_vpnum(cl, co, vp)
        tls_mem_block_va = self.symbols["tls_mem_block"]
        tls_stride_va = self.symbols["tls_stride"]
        tls_mem_block_size_va = self.symbols["tls_mem_block_size"]
        if (tls_mem_block_va == 0 or tls_stride_va == 0 or tls_mem_block_size_va == 0):
            ERROR("No tls_mem_block in image")
            return 0
        tls_mem_block = self.ReadMemory64(self.virt2phys(tls_mem_block_va), True)
        tls_stride = self.ReadMemory32(self.virt2phys(tls_stride_va), True)
        tls_mem_block_size = self.ReadMemory32(self.virt2phys(tls_mem_block_size_va), True)

        if (tls_stride * vpnum >= tls_mem_block_size):
            ERROR("Thread out of range of tls_mem_block in image")
            return 0
        return tls_mem_block + (tls_stride * vpnum)

    def GetSymbolsNeeded(self):
        return self.symbollist

    def SymbolsLoaded(self, d):
        self.symbols = d

        self.setup_threadlist()


class ELFDumpNote:
    """
    Pulls Fungible-specific notes out of the ELF dump.
    """

    def __init__(self, elf_file):
        """
        elf_file should be an ELFFile.

        There are no guarantees about correctness if the header is incomplete,
        so it's wise to at least have ~10kB of the file before invoking this.
        """
        self.elf = elf_file

    def get_note(self):
        """
        Returns the note information as a dict.

        Expect { version: 0, num_shards: N, dump_size: Z }
        """
        for seg in self.elf.iter_segments():
            if seg['p_type'] != 'PT_NOTE':
                continue

            note = self._find_note_in_segment(seg)
            if note is not None:
                return note

    def _find_note_in_segment(self, seg):
        """ Returns the fungible note from this segment, or None """

        for note in seg.iter_notes():
            if note['n_name'] == 'Fungible' and note['n_type'] == 0:
                desc = note['n_desc']
                if float(elftools.__version__) < 0.28 and isinstance(desc, str):
                    # reverse the less-than-helpful string conversion done
                    # by the pyelftools module prior to v0.28. Newer versions
                    # keep the notes as bytes.
                    desc = desc.encode('latin-1')
                t = struct.unpack('>LLQ', desc)

                ret = {}
                ret['version'] = t[0]
                ret['num_shards'] = t[1]
                ret['dump_size'] = t[2]
                return ret
        return None


###
## gdb crc
## GPL implemenation from gdb itself
#

CRCTAB = [
  0x00000000, 0x04c11db7, 0x09823b6e, 0x0d4326d9,
  0x130476dc, 0x17c56b6b, 0x1a864db2, 0x1e475005,
  0x2608edb8, 0x22c9f00f, 0x2f8ad6d6, 0x2b4bcb61,
  0x350c9b64, 0x31cd86d3, 0x3c8ea00a, 0x384fbdbd,
  0x4c11db70, 0x48d0c6c7, 0x4593e01e, 0x4152fda9,
  0x5f15adac, 0x5bd4b01b, 0x569796c2, 0x52568b75,
  0x6a1936c8, 0x6ed82b7f, 0x639b0da6, 0x675a1011,
  0x791d4014, 0x7ddc5da3, 0x709f7b7a, 0x745e66cd,
  0x9823b6e0, 0x9ce2ab57, 0x91a18d8e, 0x95609039,
  0x8b27c03c, 0x8fe6dd8b, 0x82a5fb52, 0x8664e6e5,
  0xbe2b5b58, 0xbaea46ef, 0xb7a96036, 0xb3687d81,
  0xad2f2d84, 0xa9ee3033, 0xa4ad16ea, 0xa06c0b5d,
  0xd4326d90, 0xd0f37027, 0xddb056fe, 0xd9714b49,
  0xc7361b4c, 0xc3f706fb, 0xceb42022, 0xca753d95,
  0xf23a8028, 0xf6fb9d9f, 0xfbb8bb46, 0xff79a6f1,
  0xe13ef6f4, 0xe5ffeb43, 0xe8bccd9a, 0xec7dd02d,
  0x34867077, 0x30476dc0, 0x3d044b19, 0x39c556ae,
  0x278206ab, 0x23431b1c, 0x2e003dc5, 0x2ac12072,
  0x128e9dcf, 0x164f8078, 0x1b0ca6a1, 0x1fcdbb16,
  0x018aeb13, 0x054bf6a4, 0x0808d07d, 0x0cc9cdca,
  0x7897ab07, 0x7c56b6b0, 0x71159069, 0x75d48dde,
  0x6b93dddb, 0x6f52c06c, 0x6211e6b5, 0x66d0fb02,
  0x5e9f46bf, 0x5a5e5b08, 0x571d7dd1, 0x53dc6066,
  0x4d9b3063, 0x495a2dd4, 0x44190b0d, 0x40d816ba,
  0xaca5c697, 0xa864db20, 0xa527fdf9, 0xa1e6e04e,
  0xbfa1b04b, 0xbb60adfc, 0xb6238b25, 0xb2e29692,
  0x8aad2b2f, 0x8e6c3698, 0x832f1041, 0x87ee0df6,
  0x99a95df3, 0x9d684044, 0x902b669d, 0x94ea7b2a,
  0xe0b41de7, 0xe4750050, 0xe9362689, 0xedf73b3e,
  0xf3b06b3b, 0xf771768c, 0xfa325055, 0xfef34de2,
  0xc6bcf05f, 0xc27dede8, 0xcf3ecb31, 0xcbffd686,
  0xd5b88683, 0xd1799b34, 0xdc3abded, 0xd8fba05a,
  0x690ce0ee, 0x6dcdfd59, 0x608edb80, 0x644fc637,
  0x7a089632, 0x7ec98b85, 0x738aad5c, 0x774bb0eb,
  0x4f040d56, 0x4bc510e1, 0x46863638, 0x42472b8f,
  0x5c007b8a, 0x58c1663d, 0x558240e4, 0x51435d53,
  0x251d3b9e, 0x21dc2629, 0x2c9f00f0, 0x285e1d47,
  0x36194d42, 0x32d850f5, 0x3f9b762c, 0x3b5a6b9b,
  0x0315d626, 0x07d4cb91, 0x0a97ed48, 0x0e56f0ff,
  0x1011a0fa, 0x14d0bd4d, 0x19939b94, 0x1d528623,
  0xf12f560e, 0xf5ee4bb9, 0xf8ad6d60, 0xfc6c70d7,
  0xe22b20d2, 0xe6ea3d65, 0xeba91bbc, 0xef68060b,
  0xd727bbb6, 0xd3e6a601, 0xdea580d8, 0xda649d6f,
  0xc423cd6a, 0xc0e2d0dd, 0xcda1f604, 0xc960ebb3,
  0xbd3e8d7e, 0xb9ff90c9, 0xb4bcb610, 0xb07daba7,
  0xae3afba2, 0xaafbe615, 0xa7b8c0cc, 0xa379dd7b,
  0x9b3660c6, 0x9ff77d71, 0x92b45ba8, 0x9675461f,
  0x8832161a, 0x8cf30bad, 0x81b02d74, 0x857130c3,
  0x5d8a9099, 0x594b8d2e, 0x5408abf7, 0x50c9b640,
  0x4e8ee645, 0x4a4ffbf2, 0x470cdd2b, 0x43cdc09c,
  0x7b827d21, 0x7f436096, 0x7200464f, 0x76c15bf8,
  0x68860bfd, 0x6c47164a, 0x61043093, 0x65c52d24,
  0x119b4be9, 0x155a565e, 0x18197087, 0x1cd86d30,
  0x029f3d35, 0x065e2082, 0x0b1d065b, 0x0fdc1bec,
  0x3793a651, 0x3352bbe6, 0x3e119d3f, 0x3ad08088,
  0x2497d08d, 0x2056cd3a, 0x2d15ebe3, 0x29d4f654,
  0xc5a92679, 0xc1683bce, 0xcc2b1d17, 0xc8ea00a0,
  0xd6ad50a5, 0xd26c4d12, 0xdf2f6bcb, 0xdbee767c,
  0xe3a1cbc1, 0xe760d676, 0xea23f0af, 0xeee2ed18,
  0xf0a5bd1d, 0xf464a0aa, 0xf9278673, 0xfde69bc4,
  0x89b8fd09, 0x8d79e0be, 0x803ac667, 0x84fbdbd0,
  0x9abc8bd5, 0x9e7d9662, 0x933eb0bb, 0x97ffad0c,
  0xafb010b1, 0xab710d06, 0xa6322bdf, 0xa2f33668,
  0xbcb4666d, 0xb8757bda, 0xb5365d03, 0xb1f740b4
]


def gnu_debuglink_crc32(crc, buf):
    for b in buf:
        crc = (crc << 8) ^ CRCTAB[((crc >> 24) ^ b) & 255]
        crc &= 0xffffffff
    return crc


###
##  corpse classification
#

UUID_LOCATOR = b"ELFSHA1E"
UUID_STRIDE = 8
UUID_OFFSET = 32
UUID_LEN = 16
MAX_LOCATE = (32*1024*1024)
def find_corpse_uuid(corpse):

    if (opts.force_uuid is not None):
        try:
            uu = uuid.UUID(opts.force_uuid)
        except:
            uu = None

        if (uu is None):
            raise RuntimeError("invalid forced UUID: %s" % opts.force_uuid)
        LOG_ALWAYS("FunOS UUID forced to %s" % str(uu))
        return uu

    LOG_ALWAYS("Searching for FunOS UUID")

    # search for the locator token
    offset = 0
    found = None
    while (offset < MAX_LOCATE):
        s = corpse.readbytes(offset, len(UUID_LOCATOR))
        if (s == UUID_LOCATOR):
            found = offset
            break
        offset += UUID_STRIDE

    if (found is None):
        LOG_ALWAYS("No FunOS UUID indicator found. Invalid hbmdump")
        return None

    LOG_ALWAYS("Found FunOS UUID indicator at offset %s" % found)
    buuid = corpse.readbytes(found - UUID_OFFSET, UUID_LEN)
    u = uuid.UUID(bytes=buuid)

    if (u is None):
        raise RuntimeError("Could not locate FunOS UUID")

    return u


def auto_corpse_offset(corpse):

    n0mb = corpse.ReadMemory64(0)
    n1mb = corpse.ReadMemory64(1024*1024)

    # ELF files have no offset
    if corpse.elf is not None:
        return 0

    if (n0mb != 0):
        LOG("Detected 1mb memory offset")
        return 1024 * 1024

    if (n1mb == 0):
        raise RuntimeError("Cannot find FunOS boot vector at 1mb")

    LOG("detected corpse offset 0")
    return 0


def find_corpse_offset(corpse):

    if (opts.offset == "0"):
        LOG("corpse offset 0mb")
        return 0
    elif (opts.offset == "1"):
        LOG("corpse offset 1mb")
        return 1024 * 1024
    elif (opts.offset == "auto"):
        return auto_corpse_offset(corpse)
    else:
        raise RuntimeError("unknown offset '%s'" % opts.offset)

###
##  auto file unpacking
#

def filetype(fname):
    cmd = ["file", "-0z", fname]
    output = uuid_extract.output4command(cmd)
    toks = output.split("\0")
    s = toks[-1]
    if (s[0] == ":"):
        s = s[1:]
    return s.strip()

def file_is_bzip(hbmdump):
    stype = filetype(hbmdump)
    if (stype.startswith("bzip2 compressed data")):
        return True

    if (stype.startswith("data (bzip2 compressed data")):
        return True

    return stype.startswith("ELF") and "bzip2 compressed data" in stype

def file_is_data(hbmdump):
    stype = filetype(hbmdump)
    if (stype == "data"):
        return True

    return False

def file_is_gzip(hbmdump):
    stype = filetype(hbmdump)
    if (stype.startswith("gzip compressed data")):
        return True

    if (stype.startswith("data (gzip compressed data")):
        return True

    return stype.startswith("ELF") and "gzip compressed data" in stype

def file_is_tar(hbmdump):
    stype = filetype(hbmdump)
    if (stype.startswith("POSIX tar archive")):
        return True

    return False

def file_is_tgz(hbmdump):
    stype = filetype(hbmdump)
    if ((stype.startswith("POSIX tar archive") and
         ("gzip compressed data" in stype))):
        return True

    return False

def file_is_tbz(hbmdump):
    stype = filetype(hbmdump)
    if ((stype.startswith("POSIX tar archive") and
         ("bzip2 compressed data" in stype))):
        return True

    return False

# indexed gzip (idzip)
def file_is_idgz(hbmdump):
    # ignore it if we don't have/want the library
    if (not have_idzip):
        return False

    stype = filetype(hbmdump)
    if ("(gzip compressed data, extra field" in stype):
        return True

    return False

# http remote indexed gzip
def file_is_http(hbmdump):

    # just check the name
    if ((not hbmdump.startswith("http://"))
        and (not hbmdump.startswith("https://"))):
        return False

    # try to load the http file module on demand
    SCRIPTDIR = os.path.dirname(sys.argv[0])
    sys.path.append(os.path.join(SCRIPTDIR, "../scripts"))
    sys.path.append(os.path.join(get_sdkdir(), "bin/scripts"))

    # blow up if we can't
    global httpfile
    import httpfile

    return True

def file_is_elf(hbmdump):
    stype = filetype(hbmdump)
    return stype.startswith("ELF")

def transform_file(xform, cmd, inname, outname=None):

    if (outname is None):
        # so you can rm *.fungdb_out*
        outname = "%s.fungdb_out" % inname

    if (not os.path.exists(outname)):
        # transform the args
        y = {}
        y["inname"] = inname
        y["outname"] = outname
        cmd = [x.format(**y) for x in cmd]
        cmd = " ".join(cmd)
        LOG_ALWAYS("%s %s -> %s" % (xform, inname, outname))
        DEBUG(cmd)
        os.system(cmd)
    else:
        LOG_ALWAYS("%s files exists: %s" % (xform, outname))

    return outname


def extract_bzip(bzname):
    return transform_file("bunzip2",
                          ["bunzip2", "-c", "{inname}", ">", "{outname}"],
                          bzname)

def extract_gzip(gzname):
    return transform_file("gunzip",
                          ["gunzip", "-c", "{inname}", ">", "{outname}"],
                          gzname)

def extract_tar(tarname):
    return transform_file("untar",
                          ["tar", "Oxf", "{inname}", ">", "{outname}"],
                          tarname)

def extract_tgz(tarname):
    return transform_file("untgz",
                          ["tar", "Ozxf", "{inname}", ">", "{outname}"],
                          tarname)

def extract_tbz(tarname):
    return transform_file("untbz",
                          ["tar", "Ojxf", "{inname}", ">", "{outname}"],
                          tarname)

###
##  corpse management
#

corpse = None

def setup_corpse(hbmdump):

    global corpse
    use_idzip = False

    # work out what kind of file it is
    if (file_is_http(hbmdump)):
        # remote compressed file
        print("File is http, using remote")

        # setup the file object
        corpse = FileCorpse(hbmdump, True, True)
    elif (file_is_idgz(hbmdump)):
        # same file, different file object
        print("File is indexed gzip, using in-place")

        # setup the file object
        corpse = FileCorpse(hbmdump, True)
    else:
        print("Regular old file")
        if (file_is_tgz(hbmdump)):
            hbmdump = extract_tgz(hbmdump)

        if (file_is_tbz(hbmdump)):
            hbmdump = extract_tbz(hbmdump)

        if (file_is_bzip(hbmdump)):
            hbmdump = extract_bzip(hbmdump)

        if (file_is_gzip(hbmdump)):
            hbmdump = extract_gzip(hbmdump)

        if (file_is_tar(hbmdump)):
            hbmdump = extract_tar(hbmdump)

        if (not file_is_data(hbmdump) and not file_is_elf(hbmdump)):
            raise RuntimeError("hbmdump file is still not raw data or elf")

        # setup the file object
        corpse = FileCorpse(hbmdump, False)

    # make sure it's FunOS
    uuid = find_corpse_uuid(corpse)

    # work out its offset
    corpse.memoffset = find_corpse_offset(corpse)

    return uuid

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
        r = b""
        for i in range(size):
            r += struct.pack('<B', corpse.ReadMemory8(addr + i))


    return r

def jtag_SetCpuThreadId(obj, tid):
    if (tid >= 1000):
        tid -= 1000
        corpse.SetThreadId(tid)
    obj.send("OK")

def jtag_GetCpuThreadId():
    if (corpse.symbols is None):
        return 0 # nonsense
    return 1000 + corpse.GetThreadId()

def jtag_ReadReg(name):
    return corpse.ReadReg(name)

def jtag_GetFirstThreadId():
    tid = corpse.GetFirstThreadId()
    if (tid != None):
        tid += 1000
    else:
        tid = 0
    return tid

def jtag_GetNextThreadId():
    tid = corpse.GetNextThreadId()
    if (tid is None):
        return tid
    return 1000 + tid

def jtag_IsRunning(tid):
    if (tid < 1000):
        return False
    tid -= 1000
    return corpse.IsRunning(tid)

def jtag_GetThreadInfo(tid):
    if (tid < 1000):
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
    if (regno >= len(REGS)):
        return 0xdeadbeef
    r = REGS[regno]
    DEBUG("reading %s" % r)
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


DEF_SYMS = {
    "tls_mem_block": 0,
    "tls_stride": 0,
    "tls_mem_block_size": 0,
    "PLATFORM_DEBUG_CONSTANT_vplocal_stride": 4160,
    "PLATFORM_DEBUG_CONSTANT_debug_context_offset": 376,
    "PLATFORM_DEBUG_CONSTANT_ccv_state_invalid": 0,
    "PLATFORM_DEBUG_CONSTANT_ccv_state_offline": 1,
    "PLATFORM_DEBUG_CONSTANT_ccv_state_online": 2,
    "PLATFORM_DEBUG_CONSTANT_topo_vp_stride": 24,
    "PLATFORM_DEBUG_CONSTANT_DISPATCH_STACK_TOKEN_SHIFT": 44,
    "PLATFORM_DEBUG_CONSTANT_DISPATCH_STACK_CLUSTER_SHIFT": 40,
    "PLATFORM_DEBUG_CONSTANT_DISPATCH_STACK_CORE_SHIFT": 36,
    "PLATFORM_DEBUG_CONSTANT_DISPATCH_STACK_VP_SHIFT": 32,
    "PLATFORM_DEBUG_CONSTANT_DISPATCH_STACK_SIZE": 4096,
    "PLATFORM_DEBUG_CONSTANT_DISPATCH_STACK_BAD_MASK": ~0,
    }

def _default_sym(symname):

    if (symname in DEF_SYMS.keys()):
        ERROR("WARNING: gdb failed to return symbol %s, using default" % symname)
        return DEF_SYMS[symname]

    # barf
    ERROR("Failed to find symbol '%s' in binary or defaults. Exiting" % symname)
    sys.exit(1)


def deal_withCRC(obj, cmd):

    LOG("crc subcmd: %s" % cmd)
    cmd = cmd[4:]
    toks = cmd.split(",")

    addr = int(toks[0], 16)
    leng = int(toks[1], 16)

    LOG("%s, %s" % (addr, leng))

    # send a reply
    data = jtag_ReadMemory(leng, addr)
    data = data[::-1] # reverse it
    s = gnu_debuglink_crc32(0xffffffff, reversed(data))
    s = "c%x" % s
    LOG(s)
    obj.send(s)


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
        LOG(reply)
        toks = reply.split(":")
        if (toks[1] == ''):
            v = _default_sym(SYMLIST[0])
        else:
            v = int(toks[1], 16)
        SYMTAB[SYMLIST.pop(0)] = v


    if (len(SYMLIST) == 0):
        corpse.SymbolsLoaded(SYMTAB)
        SYMTAB = None
        SYMLIST = None
        obj.send("OK")
        return

    s = "qSymbol:%s" % hexstr(SYMLIST[0])
    LOG("asking for symbol: %s [%s]" % (SYMLIST[0], s))
    obj.send(s)

def deal_withTLSAddr(obj, cmd):
    toks = cmd.split(":")
    args = toks[1].split(",")
    tid = int(args[0], 16)
    cmd_offset = int(args[1], 16)

    tls_base = corpse.GetTLSBase(tid)
    if (tls_base == 0):
        obj.send("E42")
        return
    tls_offset = tls_base + cmd_offset
    obj.send("%X" % tls_offset)

IGNORE_Q = ["TfV", "TfP"]

# Code a bit inspired from http://mspgcc.cvs.sourceforge.net/viewvc/mspgcc/msp430simu/gdbserver.py?revision=1.3&content-type=text%2Fplain
class GDBClientHandler(object):
    def __init__(self, clientsocket):
        self.clientsocket = clientsocket
        # need binary input since gdb may send extended ascii (incorrectly?)
        self.netin = clientsocket.makefile('rb', buffering=0)
        self.netout = clientsocket.makefile('w')
        self.last_pkt = None

    def close(self):
        '''End of story!'''
        self.netin.close()
        self.netout.close()
        self.clientsocket.close()
        LOG('closed')

    def run(self):
        '''Some doc about the available commands here:
            * http://www.embecosm.com/appnotes/ean4/embecosm-howto-rsp-server-ean4-issue-2.html#id3081722
            * http://git.qemu.org/?p=qemu.git;a=blob_plain;f=gdbstub.c;h=2b7f22b2d2b8c70af89954294fa069ebf23a5c54;hb=HEAD +
             http://git.qemu.org/?p=qemu.git;a=blob_plain;f=target-i386/gdbstub.c;hb=HEAD'''
        LOG('client loop ready...')
        while self.receive() == 'Good':
            pkt = self.last_pkt
            DEBUG('receive(%r)' % pkt)
            # Each packet should be acknowledged with a single character. '+' to indicate satisfactory receipt
            self.send_raw('+')

            def handle_q(subcmd):
                '''
                subcmd Supported: https://sourceware.org/gdb/onlinedocs/gdb/General-Query-Packets.html#qSupported
                Report the features supported by the RSP server. As a minimum, just the packet size can be reported.
                '''
                if subcmd.startswith('Supported'):
                    LOG('Received qSupported command')
                    self.send('PacketSize=%x' % 4096)
                elif subcmd.startswith('Attached'):
                    LOG('Received qAttached command')
                    # https://sourceware.org/gdb/onlinedocs/gdb/General-Query-Packets.html
                    self.send('1')
                elif (subcmd.startswith('CRC')):
                    deal_withCRC(self, subcmd)
                elif subcmd.startswith('C'):
                    self.send('T%.2x;' % jtag_GetCpuThreadId())
                elif (subcmd == "fThreadInfo"):
                    # FIXME: make a thread list
                    tid = jtag_GetFirstThreadId()
                    s = "m%x" % tid
                    LOG("sending first thread (%s)" % s)
                    self.send(s)
                elif (subcmd == "sThreadInfo"):
                    # FIXME: make a thread list
                    tid = jtag_GetNextThreadId()
                    if (tid is not None):
                        s = "m%x" % tid
                        DEBUG("sending next thread (%s)" % s)
                        self.send(s)
                    else:
                        LOG("done sending threads")
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
                    DEBUG(subcmd)
                    tid = int(subcmd.split(",")[1], 16)
                    info = jtag_GetThreadInfo(tid)
                    self.send(hexstr(info))
                elif (subcmd.startswith("GetTLSAddr:")):
                    deal_withTLSAddr(self, subcmd)
                elif (subcmd in IGNORE_Q):
                    DEBUG('This subcommand %r is ignored in q' % subcmd)
                    self.send('')
                else:
                    ERROR('This subcommand %r is not implemented in q' % subcmd)
                    self.send('')

            def handle_h(subcmd):
                DEBUG(subcmd)
                op = subcmd[0]
                tid = int(subcmd[1:],16)
                jtag_SetCpuThreadId(self, tid)

            def handle_v(subcmd):
                DEBUG("v command %s" % subcmd)
                self.send('')

            def handle_qmark(subcmd):
                self.send('S%.2x' % GDB_SIGNAL_TRAP)

            def handle_g(subcmd):
                if subcmd == '':
                    tid = jtag_GetCpuThreadId()
                    DEBUG("register read request on %d" % tid)
                    # make all the registers
                    registers = jtag_GetRegList()
                    s = ''
                    for r in registers:
                        s += struct.pack('<Q', r).hex()
                    DEBUG("regfile: %s" % s)
                    self.send(s)
                else:
                    ERROR("unknown 'g' subcommand?")

            def handle_p(subcmd):
                regno = int(subcmd, 16)
                r = jtag_GetReg(regno)
                s = struct.pack('<I', r).hex()
                DEBUG("reg %s: %s" % (regno, s))
                self.send(s)

            def handle_m(subcmd):
                addr, size = subcmd.split(',')
                addr = int(addr, 16)
                size = int(size, 16)
                DEBUG('Received a "read memory" command (@%#.8x : %d bytes)' % (addr, size))
                self.send(jtag_ReadMemory(size, addr).hex())

            def handle_s(subcmd):
                LOG('Received a "single step" command')
                jtag_StepInto()
                self.send('T%.2x' % GDB_SIGNAL_TRAP)

            def handle_T(subcmd):
                n = int(subcmd, 16)
                DEBUG("checking thread %d" % n)
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
                LOG('%r command not handled' % pkt)
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
            # read a binary character (b'c')
            c = self.netin.read(1)

            # EOF checks first
            if len(c) != 1:
                return 'Error: EOF'

            # translate it to internal string. some gdb commands
            # get messed up bytes. decode() fails on them. but you
            # can do this. python fail.
            c = chr(ord(c))

            if c == '\x03':
                return 'Error: CTRL+C'

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
        DEBUG('send(%r)' % msg)
        self.send_raw('$%s#%.2x' % (msg, checksum(msg)))

    def send_raw(self, r):
        self.netout.write(r)
        self.netout.flush()

###
##  gdb server managemnt
#

def setup_server():
    port = opts.port
    if (opts.server_only and (port == 0)):
        port = 1234
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # GDB does a lot of very small socket IO.
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    sock.bind(('', port))
    return sock

def poll_sock_and_gdb(sock):

    DEBUG("going to select loop")
    while True:

        # check gdb is still alive
        gdb_status = gdb_proc.poll()
        if (gdb_status is not None):
            ERROR("gdb terminated before connecting to TCP socket: %s" % gdb_status)
            sys.exit(1)

        # wait a short while for a connection
        DEBUG("selecting")
        r, w, x = select.select([sock], [], [sock], 0.1)
        if (len(r) > 0):
            break

        DEBUG("select timeout")


def wait_for_connect(sock):

    # wait for gdb to connect
    # lest gdb barf on startup
    if (opts.server_only):
        return

    poll_sock_and_gdb(sock)


def server_listen(sock):
    port = sock.getsockname()[1]
    LOG_ALWAYS('listening on :%d' % port)
    sock.listen(1)
    wait_for_connect(sock)
    conn, addr = sock.accept()
    LOG_ALWAYS('gdb connected')

    GDBClientHandler(conn).run()
    return 1


###
##  Clean elf files downloaded from excat
#

def clean_elf_files(elffile):
    try:
        # delete the .excat elf file
        os.remove(elffile)
        # delete the .bz file
        os.remove(elffile.replace('excat','bz'))
    except:
        ERROR("failed to remove elf files.")
        sys.exit(1)



###
##  running a gdb client
#

gdb_proc = None

def run_gdb_async(port, elffile):

    global gdb_proc
    cmd = [opts.gdb]

    if (opts.dir is not None):
        cmd += ["-ex", "dir %s" % opts.dir]

    if (opts.debug_exit_gdb):
        cmd += ["-ex", "quit"]

    if (not opts.confirm):
        cmd += ["-ex", "set confirm off"]

    script = get_script()
    if (script is not None):
        cmd += ["-ex", "source %s" % script]

    if (opts.gdb_debug):
        cmd += ["-ex", "set debug remote 1"]

    if (opts.gdb_timeout is not None):
        # avoid gdb packet timeout errors due to
        # wire latency
        cmd += ["-ex", "set remotetimeout %s" % opts.gdb_timeout]

    cmd += ["-ex", "target remote :%s" % port,
            "-ex", "compare-sections .note.gnu.build-id"]

    # make sure we discard gdb's bootstrap register state
    cmd += ["-ex", "flushregs"]

    if (opts.crashlog):
        cmd += ["-ex", "crashlog",
                "-ex", "quit"]

    for command in opts.ex:
        cmd += ["-ex", command]

    cmd += [elffile]

    LOG_ALWAYS("Running GDB: %s" % " ".join(cmd))
    try:
        gdb_proc = subprocess.Popen(cmd)
    except:
        ERROR("failed to execute GDB, exiting")
        sys.exit(1)


###
##  entry & argument parsing
#

def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("-v", "--verbose", action="count",
                        default=0)
    parser.add_argument("-P", "--port", action="store",
                        default=0, type=int,
                        help="TCP port to listen on. 0=pick a random port, or 1234 for server-only mode")
    parser.add_argument("--offset", action="store",
                        default="auto",
                        help="hbmdump file offset (default=auto, other values 0 or 1)")
    parser.add_argument("--server-only", action="store_true",
                        default=False)
    parser.add_argument("-O", "--output", action="store",
                        default="fungdbserver.log",
                        help="filename to log to")
    parser.add_argument("-A", "--always-log", action="store_true",
                        default=False,
                        help="force logging in server-only mode")
    parser.add_argument("-G", "--gdb", action="store",
                        default=get_default_gdb(),
                        help="specify a specific GDB to execute")
    parser.add_argument("-X", "--debug-exit-gdb", action="store_true",
                        default=False,
                        help="DEBUG: exit gdb before it connects")
    parser.add_argument("-U", "--force-uuid", action="store",
                        default=None,
                        help="Force a specific FunOS UUID instead of discovering it")
    parser.add_argument("-D", "--dir", action="store",
                        default=get_default_dir(),
                        metavar="dirname",
                        help=("specify a FunOS source path\n"
                              "(defaults to $FUNOS_SRC or $WORKSPACE/FunOS"))
    parser.add_argument("-S", "--script", action="store",
                        default=None,
                        help=("specify a python gdb script to load\n"
                              "(defaults to standard FunSDK or FunOS/scripts version"))
    parser.add_argument("--confirm", action="store_true",
                        default=False,
                        help="Require gdb to confirm exit")
    parser.add_argument("--crashlog", action="store_true",
                        default=False,
                        help="Just execute the script to generate a crashlog and exit")
    parser.add_argument("--skip-dump-size-check", action="store_true",
                        default=False,
                        help="Skip dump size verification")
    parser.add_argument("--gdb-debug", action="store_true",
                        default=False,
                        help="Enable gdb packet debugging")
    parser.add_argument("--gdb-timeout", action="store",
                        default=None, type=int,
                        help="Set gdb packet timeout")
    parser.add_argument("--ex", action="append", metavar="command", default=[],
                        help="GDB ex command to run")
    parser.add_argument("--elf", help="Use provided elf file instead of downloading from excat")
    parser.add_argument("--clean-excat-files", action="store_true",
                        default=False,
                        help="Delete the elf file(s) which is downloaded from excat")

    # final arg is the dump file
    parser.add_argument("hbmdump", help="hbmdump file")

    args = parser.parse_args()

    return args

def main():
    # In the parent process, we want to ignore SIGINT, this will get sent to
    # GDB and GDB will stop executing whatever is currently consuming the main
    # thread.
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    # parse the arge
    global opts
    opts = parse_args()
    force_exit = False
    # setup logging
    if ((not opts.server_only) or opts.always_log):
        global log_file
        LOG_ALWAYS("fungdbserver logging to %s" % opts.output)
        log_file = open(opts.output, "w")

    try:
        # setup the file
        uuid = setup_corpse(opts.hbmdump)

        LOG_ALWAYS("uuid of FunOS is %s" % str(uuid))

        # setup the server
        sock = setup_server()

        # start gdb and give it control of the stdin/stdout
        if (not opts.server_only):
            # find us a binary
            if opts.elf:
                elffile = opts.elf
            else:
                excat.parse_args(True)
                elffile = excat.get_action(str(uuid))

            if (elffile is None):
                LOG_ALWAYS("Cannot continue without symbols")
                sys.exit(1)

            # run gdb
            port = sock.getsockname()[1]
            run_gdb_async(port, elffile)
        # listen
        server_listen(sock)
    except Exception as e:
        LOG_ALWAYS(f"Exception while running fungdbserver.py: \"{e}\", exiting")
        if (opts.verbose >= 1):
            traceback.print_exc()
        force_exit = True
    finally:
        # clean downloaded excat files and then raise exception.
        if opts.clean_excat_files and (not opts.elf):
            clean_elf_files(elffile)
        if force_exit:
            sys.exit(1)

    LOG_ALWAYS("exiting")

if __name__ == '__main__':
    main()
