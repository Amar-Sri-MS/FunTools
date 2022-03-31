#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract FunVisor core file from enclosing HBM dump.

For a given HBM dump file, we also need the corresponding FunOS image
so that we can find the location of several values needed to create
the FunVisor (ccLinux) core file.

The general approach is:

* Find the location of the "funvisor" memory region and the Funvisor
  vCPU register states in the HBM dump.

* Copy the funvisor memory region into the new core file

* Write ELF core file notes with register contents of all FunVisor vCPUs

Resulting core (call it vmlinux.core) file can be used like this:

 mips64-unknown-elf-gdb vmlinux vmlinux.core


static check:
% mypy fv-core.py

format:
% python3 -m black fv-core.py

"""
from typing import List, Optional, Type, Dict, Any, Union, Tuple, BinaryIO, ClassVar
import argparse
import os
import struct
import subprocess
import tempfile

class Phdr:
    """
    Phdr encapsulates an ELF Program Header
    """
    PT_NULL:    ClassVar[int] = 0
    PT_LOAD:    ClassVar[int] = 1
    PT_DYNAMIC: ClassVar[int] = 2
    PT_INTERP:  ClassVar[int] = 3
    PT_NOTE:    ClassVar[int] = 4

    PF_R:       ClassVar[int] = 4
    PF_W:       ClassVar[int] = 2
    PF_X:       ClassVar[int] = 1

    ENT_SIZE:   ClassVar[int] = 56

    ph_pack: ClassVar[struct.Struct] = struct.Struct('>II6Q')
    ph_type: int
    ph_flags: int
    ph_offset: int
    ph_vaddr: int
    ph_paddr: int
    ph_filesz: int
    ph_memsz: int
    ph_align: int

    def __init__(self, arg0: Union[bytes, int], flags: int = 0, offset: int = 0, vaddr: int = 0, paddr: int = 0, filesz: int = 0, memsz: int = 0, align: int = 0):
        """
        Construct a new 'Phdr' object.

        :param arg0: If it is an instance of bytes, unpack into an new Phdr, otherwise create the Phdr from all the rest of the parameters
        """
        if isinstance(arg0, bytes):
            (self.ph_type,
             self.ph_flags,
             self.ph_offset,
             self.ph_vaddr,
             self.ph_paddr,
             self.ph_filesz,
             self.ph_memsz,
             self.ph_align) = Phdr.ph_pack.unpack(arg0)
        elif isinstance(arg0, int):
            self.ph_type = arg0
            self.ph_flags = flags
            self.ph_offset = offset
            self.ph_vaddr = vaddr
            self.ph_paddr = paddr
            self.ph_filesz = filesz
            self.ph_memsz = memsz
            self.ph_align = align
        else:
            assert(False)

    def to_bytes(self) -> bytes:
        """
        Convert the 'Phdr' object back to a bytes object that can be writtin to an ELF file.

        :return: return the bytes.
        """
        v = Phdr.ph_pack.pack(self.ph_type, self.ph_flags, self.ph_offset, self.ph_vaddr, self.ph_paddr, self.ph_filesz, self.ph_memsz, self.ph_align)
        assert(len(v) == Phdr.ENT_SIZE)
        return v;

    @staticmethod
    def to_type(t: int) -> str:
        if t == Phdr.PT_NULL:
            return 'NULL   '
        elif t == Phdr.PT_LOAD:
            return 'LOAD   '
        elif t == Phdr.PT_DYNAMIC:
            return 'DYNAMIC'
        elif t == Phdr.PT_INTERP:
            return 'INTERP '
        elif t == Phdr.PT_NOTE:
            return 'NOTE   '
        return hex(t)

    def print(self) -> None:
        print("%s %d %s %s" % (Phdr.to_type(self.ph_type), self.ph_offset, hex(self.ph_vaddr), hex(self.ph_memsz)))

    def is_load(self) -> bool:
        return self.ph_type == Phdr.PT_LOAD

class ELFNote:
    """
    ELFNote encapsulates an ELF file note
    """
    NT_PRSTATUS: ClassVar[int] = 1
    NT_PRPSINFO: ClassVar[int] = 3
    header_pack: ClassVar[struct.Struct] = struct.Struct('>III')
    n_name: str
    n_type: int
    content: bytes

    def __init__(self, n_name: str, n_type: int, content: bytes):
        self.n_name = n_name
        self.n_type = n_type
        self.content = content
        assert(len(content) % 4 == 0)

    def to_bytes(self) -> bytes:
        name = self.n_name.encode(encoding='ascii')
        padded_len = (len(name) + 4) & ~3
        pad = bytes(padded_len - len(name))
        header = ELFNote.header_pack.pack(len(name) + 1, len(self.content), self.n_type)
        return header + name + pad + self.content

    @staticmethod
    def prsinfo(sname: str, fname: str, cmdline: str) -> 'ELFNote':
        """
        Generate a NT_PRPSINFO note

        :param sname: The value for the pr_sname field
        :param fname: The value for the pr_fname field
        :param cmdline: The value of the pr_psargs field

        :return: The NT_PRPSINFO note.
        """
        sname_blob = sname.encode('ascii')[0:1]
        fname_blob = (fname.encode('ascii') + bytes(16))[0:16]
        cmdline_blob = (cmdline.encode('ascii') + bytes(80))[0:80]

        content = bytes(1) + sname_blob + bytes(38) + fname_blob + cmdline_blob
        return ELFNote('CORE', ELFNote.NT_PRPSINFO, content)

class ELFFile:
    """
    ELFFile wraps access to an ELF file

    ELFFile is in one of two modes: read-only or write-only
    """
    EI_MAG0: ClassVar[int] = 0x7f
    EI_MAG1: ClassVar[int] = ord("E")
    EI_MAG2: ClassVar[int] = ord("L")
    EI_MAG3: ClassVar[int] = ord("F")

    ELFCLASS32: ClassVar[int] = 1
    ELFCLASS64: ClassVar[int] = 2

    ELFDATA2LSB: ClassVar[int] = 1
    ELFDATA2MSB: ClassVar[int] = 2

    EV_CURRENT: ClassVar[int] = 1

    ELFOSABI_NONE: ClassVar[int] = 0

    ET_CORE: ClassVar[int] = 4

    EM_MIPS: ClassVar[int] = 8

    ELF64_HEADER_SIZE: ClassVar[int] = 64

    INITIAL_WRITE_POS: ClassVar[int] = 0x10000

    header_pack: ClassVar[struct.Struct] = struct.Struct('>8BQHHI3QI6H')
    elf_file: BinaryIO
    ph_off: int
    ph_size: int
    ph_num: int
    for_output: bool
    write_pos: int
    e_flags: int

    phdrs: List[Phdr]

    def __init__(self, elf_file: BinaryIO, for_output: bool = False, def_e_flags: int = 0xa0000401):
        """
        Construct a new ELFFile object

        :param elf_file: The underlying file
        :param for_output: If true the ELFFile is in write-only mode.
        :param def_e_flags: E_FLAGS value to use when writing.
        """
        self.elf_file = elf_file
        self.for_output = for_output
        self.phdrs = []

        if for_output:
            self.e_flags = def_e_flags
            self.ph_size = 64
            self.write_pos = ELFFile.INITIAL_WRITE_POS
            return

        elf_file.seek(0)
        ehdr = elf_file.read(64)
        (ei_mag0, ei_mag1, ei_mag2, ei_mag3, ei_class, ei_data, ei_version, ei_osabi, ei_pad,
         e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, self.e_flags, e_ehsize,
         e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx) =  ELFFile.header_pack.unpack(ehdr)
        if (
                ei_mag0 != ELFFile.EI_MAG0
                or ei_mag1 != ELFFile.EI_MAG1
                or ei_mag2 != ELFFile.EI_MAG2
                or ei_mag3 != ELFFile.EI_MAG3
                or ei_pad  != 0
                or ei_class != ELFFile.ELFCLASS64
                or ei_data != ELFFile.ELFDATA2MSB # big-endian
        ):
            raise Exception("Not BE ELF64")
        self.ph_off = e_phoff
        self.ph_size = e_phentsize
        self.ph_num = e_phnum;

        idx = 0
        while idx < self.ph_num:
            self.elf_file.seek(self.ph_off + (self.ph_size * idx))
            raw_ph = self.elf_file.read(self.ph_size)
            ph = Phdr(raw_ph)
            self.phdrs.append(ph)
            idx += 1

    def print_phdrs(self) -> None:
        """
        Print out all the Program Headers in the ELFFile
        """
        for ph in self.phdrs :
            ph.print()

    def write_phdr(self, ph: Phdr, out_elf: 'ELFFile') -> Tuple[int, int]:
        """
        Copy the contents of one Program Header into another ELFFile

        :param ph" The Phdr to copy
        :param out_elf: The ELFFile to copy into

        :return: A tuple of the position and size of the contents in *out_elf*
        """
        assert(out_elf.for_output)

        out_elf.elf_file.seek(out_elf.write_pos)
        self.elf_file.seek(ph.ph_offset)
        to_copy = ph.ph_filesz
        rv_size = to_copy
        rv_pos = out_elf.write_pos
        while to_copy > 0:
            nr = max(0x100000, to_copy)
            to_copy -= nr
            d = self.elf_file.read(nr)
            out_elf.elf_file.write(d)
        out_elf.write_pos += rv_size
        return (rv_pos, rv_size)

    def write_bytes(self, payload: bytes) -> Tuple[int, int]:
        """
        Copy data into the ELFFile

        :param payload: The data to copy.
        :return: A tuple of the position and size of the *payload* in this ELFFile
        """
        assert(self.for_output)

        self.elf_file.seek(self.write_pos)
        rv_size = len(payload)
        rv_pos = self.write_pos
        self.elf_file.write(payload)
        self.write_pos += rv_size
        return (rv_pos, rv_size)

    def find_load_phdr(self, pa: int) -> Optional[Phdr]:
        """
        Find a Program Header tha contains the specified address

        :param pa: The physical address to find

        :return: The Phdr or None if not found.
        """
        for ph in self.phdrs:
            if ph.is_load() and ph.ph_paddr <= pa and pa < ph.ph_paddr + ph.ph_filesz:
                return ph
        return None

    def close(self) -> None:
        self.elf_file.close()

    def add_phdr(self, ph: Phdr) -> None:
        """
        Add a Program Header to this ELFFile

        :param ph: The Program Header to add
        """
        self.phdrs.append(ph)

    def emit_headers(self) -> None:
        """
        Write all the ELF headers and Program Headers to the underlying file.
        """
        hdr = ELFFile.header_pack.pack(ELFFile.EI_MAG0, ELFFile.EI_MAG1, ELFFile.EI_MAG2, ELFFile.EI_MAG3,
                                       ELFFile.ELFCLASS64, ELFFile.ELFDATA2MSB, ELFFile.EV_CURRENT, ELFFile.ELFOSABI_NONE, 0,
                                       ELFFile.ET_CORE, ELFFile.EM_MIPS, 1, 0, ELFFile.ELF64_HEADER_SIZE, 0, self.e_flags, ELFFile.ELF64_HEADER_SIZE,
                                       Phdr.ENT_SIZE, len(self.phdrs), 0, 0, 0)
        assert(len(hdr) == ELFFile.ELF64_HEADER_SIZE)
        assert(len(hdr) + len(self.phdrs) * Phdr.ENT_SIZE <= ELFFile.INITIAL_WRITE_POS)

        self.elf_file.seek(0)
        self.elf_file.write(hdr)
        for ph in self.phdrs:
            self.elf_file.write(ph.to_bytes())

    def read_from_phdr(self, ph: Phdr, addr: int, count: int) -> bytes:
        """
        Read data from the ELFFile corresponding the the supplied address

        :param ph: The Program Header containing the address
        :param addr: The address
        :param count: The number of bytes to read.
        """
        assert(ph.ph_paddr <= addr and addr + count <= ph.ph_paddr + ph.ph_filesz)
        self.elf_file.seek(ph.ph_offset + (addr - ph.ph_paddr))
        content = self.elf_file.read(count)
        return content


###
##  parse_args
#
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument("hbm", help="HBM file")

    # Required positional argument
    parser.add_argument("core", help="Output core file")

    parser.add_argument("--gdb", default="/opt/cross/mips64/bin/mips64-unknown-elf-gdb", help="Path to gdb executable")

    parser.add_argument("--funos", required=True, help="Path to funos executable")

    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Verbosity (-v, -vv, etc)"
    )

    args: argparse.Namespace = parser.parse_args()
    return args

def xkphys_to_pys(va: int) -> int:
    """
    Convert a MIPS64 xhphys address to a physical address

    :param va: The xkphys virtual address

    :return: The corresponding physical address.
    """
    return va & 0xfffffffffffff

def get_reg_offsets(gdb: str, funos_path: str) -> Tuple[int, int, int, int, int, int]:
    """
    Use gdb to determine the address and offsets of objects in a FunOS image.
    :param gdb: PATH to the gdb executable
    :param funos_path: The FunOS object to examine

    :return: Tuple of values extracted.
    """
    gdb_cmds = tempfile.NamedTemporaryFile(mode='w', encoding='ascii', delete=False)
    gdb_cmds_filename=gdb_cmds.name
    try:
        print('p/x (long)&fv_gbl_ctx', file=gdb_cmds)
        print('p/x (long)&((struct vm_ctx *)0)->vcpus', file=gdb_cmds)
        print('p/x (long)&((struct vcpu_ctx *)0)->cpu_ctx.guest_gpr', file=gdb_cmds)
        print('p/x (long)&((struct vcpu_ctx *)0)->cpu_ctx.epc', file=gdb_cmds)
        print('p/x (long)&((struct vcpu_ctx *)0)->cpu_ctx.guest_status', file=gdb_cmds)
        print('p/x &regions[MEM_REGION_FUNVISOR].start', file=gdb_cmds)
        print('quit', file=gdb_cmds)
        gdb_cmds.close()
        gdb_proc = subprocess.Popen([gdb, '-x', gdb_cmds_filename, funos_path], stdout=subprocess.PIPE, encoding='utf8')

        assert(gdb_proc.stdout)
        for line in gdb_proc.stdout:
            if line.startswith('$1 = '):
                fv_gbl_ctx = xkphys_to_pys(int(line.strip()[5:], 0))
            elif line.startswith('$2 = '):
                vcpus_offset = int(line.strip()[5:], 0)
            elif line.startswith('$3 = '):
                guest_gpr_offset = int(line.strip()[5:], 0)
            elif line.startswith('$4 = '):
                epc_offset = int(line.strip()[5:], 0)
            elif line.startswith('$5 = '):
                status_offset = int(line.strip()[5:], 0)
            elif line.startswith('$6 = '):
                fv_region_start = xkphys_to_pys(int(line.strip()[5:], 0))
    finally:
        os.remove(gdb_cmds_filename)

    print("fv_gbl_ctx: " + hex(fv_gbl_ctx))
    print("vcpus_offset: " + hex(vcpus_offset))
    print("guest_gpr_offset: " + hex(guest_gpr_offset))
    print("epc_offset: " + hex(epc_offset))
    print("status_offset: " + hex(status_offset))
    print("fv_region_start: " + hex(fv_region_start))

    return (fv_gbl_ctx, vcpus_offset, guest_gpr_offset, epc_offset, status_offset, fv_region_start)


###
##  main
#
def main() -> int:
    args: argparse.Namespace = parse_args()
    elf_notes: bytes = bytes(0)

    print("HBM filename: " + args.hbm)

    # Get address and offset of a bunch of things.
    (fv_gbl_ctx, vcpus_offset, guest_gpr_offset, epc_offset, status_offset, fv_region_start) = get_reg_offsets(args.gdb, args.funos)

    # Open and wrap in ELFFile the HBM dump.
    hbm_file = open(args.hbm, 'rb')
    hbm: ELFFile = ELFFile(hbm_file)

    # Why not see which Program Headers are present in the HBM dump?
    hbm.print_phdrs()

    # Get the array of vcpu pointers from the HBM dump
    funos_phdr = hbm.find_load_phdr(fv_gbl_ctx)
    assert(funos_phdr)

    vcpus = struct.unpack('>8Q', hbm.read_from_phdr(funos_phdr, fv_gbl_ctx + vcpus_offset, 8*8))

    # Generate a concatenation of all the ELF Notes.
    did_prsinfo = False
    vcpu_index = -1
    for vcpu in vcpus:
        vcpu_index += 1
        print("vcpu %d: " % vcpu_index + hex(vcpu))
        if vcpu == 0:
            continue
        # Synthesize some faux id values so gdb thinks each vCPU is a thread.
        # PID, PPID, PGRP, SID : 100+VCPU, 10, 100, 10
        pid_blob = struct.pack('>4I', 100 + vcpu_index, 10, 100, 10)

        # Get the register contents for the vCPU
        regs_phdr = hbm.find_load_phdr(xkphys_to_pys(vcpu))
        assert(regs_phdr)
        regs_blob = hbm.read_from_phdr(regs_phdr, xkphys_to_pys(vcpu) + guest_gpr_offset, 32*8)
        epc_blob = hbm.read_from_phdr(regs_phdr, xkphys_to_pys(vcpu) + epc_offset, 8)
        status_blob = hbm.read_from_phdr(regs_phdr, xkphys_to_pys(vcpu) + status_offset, 4)
        cause_blob = bytes(8)
        badvaddr_blob = bytes(8)
        regs = struct.unpack('>32Q', regs_blob)
        # struct elf_prstatus has size 0x1e0, registers are at offset 0x70
        lohi_blob = bytes(0x10)
        # Pack it all up in a NT_PRSTATUS object
        prstatus_blob = bytes(0x20) + pid_blob + bytes(0x40) + regs_blob + lohi_blob + epc_blob + badvaddr_blob + bytes(4) + status_blob + cause_blob + bytes(0x40)
        reg_note = ELFNote('CORE', ELFNote.NT_PRSTATUS, prstatus_blob)
        elf_notes += reg_note.to_bytes()
        if not did_prsinfo:
            # The first one also gets a NT_PRSINFO to say what program it is.
            prsinfo = ELFNote.prsinfo('R', 'vmlinux', 'vmlinux')
            elf_notes += prsinfo.to_bytes()
            did_prsinfo = True
        for reg in regs:
            print("   reg: " + hex(reg))
        print("   epc: " + hex(struct.unpack('>Q', epc_blob)[0]))

    # Find out where the "funvisor" memory region is.
    funos_phdr = hbm.find_load_phdr(fv_region_start)
    assert(funos_phdr)
    funvisor_address = struct.unpack('>Q', hbm.read_from_phdr(funos_phdr, fv_region_start, 8))[0]
    funvisor_address = xkphys_to_pys(funvisor_address)
    print("FunVisor region address: " + hex(funvisor_address))

    xkphys_base = 0xa800000000000000
    kseg0_base  = 0xffffffff80000000
    kseg0_size  = 0x0000000020000000

    fv_phdr = hbm.find_load_phdr(funvisor_address)
    if fv_phdr is None:
        print("No FunVisor region found")
        return 1

    core_file = open(args.core, 'wb')
    core: ELFFile = ELFFile(core_file, True)

    # Copy over the "funvisor" memory region to the new core file
    (blob_pos, blob_size) = hbm.write_phdr(fv_phdr, core)
    # Program Header for xkphys view of memory.
    blob_ph = Phdr(Phdr.PT_LOAD, Phdr.PF_R | Phdr.PF_W | Phdr.PF_X, blob_pos, xkphys_base, 0, blob_size, blob_size, 0)
    core.add_phdr(blob_ph)
    # Program Header for KSEG0 view of memory.
    kseg0_view_size = min(blob_size, kseg0_size)
    kseg0_ph = Phdr(Phdr.PT_LOAD, Phdr.PF_R | Phdr.PF_W | Phdr.PF_X, blob_pos, kseg0_base, 0, kseg0_view_size, kseg0_view_size, 0)
    core.add_phdr(kseg0_ph)

    # NOTE Program Header and contents.
    (note_pos, note_size) = core.write_bytes(elf_notes)
    note_ph = Phdr(Phdr.PT_NOTE, 0, note_pos, 0, 0, note_size, 0, 0)
    core.add_phdr(note_ph)
    core.emit_headers()
    core.close()
    # Done!

    return 0


###
##  entrypoint
#
if __name__ == "__main__":
    main()
