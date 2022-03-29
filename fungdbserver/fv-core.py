#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract FunVisor core file from enclosing HBM dump.

static check:
% mypy fv-core.py

format:
% python3 -m black fv-core.py
"""
from typing import List, Optional, Type, Dict, Any, Union, Tuple, BinaryIO, ClassVar
import argparse
import struct

class Phdr:
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
    NT_PRSTATUS: ClassVar[int] = 1
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
        pad_len = ((4 - (len(name) + 1) % 4) & 3) + 1
        pad = bytes(pad_len)
        header = ELFNote.header_pack.pack(len(name) + 1, len(self.content), self.n_type)
        return header + name + pad + self.content

class ELFFile:
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
        for ph in self.phdrs :
            ph.print()

    def write_phdr(self, ph: Phdr, out_elf: 'ELFFile') -> Tuple[int, int]:
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
        assert(self.for_output)

        self.elf_file.seek(self.write_pos)
        rv_size = len(payload)
        rv_pos = self.write_pos
        self.elf_file.write(payload)
        self.write_pos += rv_size
        return (rv_pos, rv_size)

    def find_load_phdr(self, pa: int) -> Optional[Phdr]:
        for ph in self.phdrs:
            if ph.is_load() and ph.ph_paddr == pa:
                return ph
        return None

    def close(self) -> None:
        self.elf_file.close()

    def add_phdr(self, ph: Phdr) -> None:
        self.phdrs.append(ph)

    def emit_headers(self) -> None:
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


###
##  parse_args
#
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument("hbm", type=argparse.FileType("rb"), help="HBM file")

    # Required positional argument
    parser.add_argument("core", type=argparse.FileType("wb"), help="Output core file")

    parser.add_argument("-a", "--funvisor-address", type=int, default=0x28000000000, help="physical address of FunVisor region")

    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Verbosity (-v, -vv, etc)"
    )

    args: argparse.Namespace = parser.parse_args()
    return args


###
##  main
#
def main() -> int:
    args: argparse.Namespace = parse_args()

    hbm: ELFFile = ELFFile(args.hbm)
    core: ELFFile = ELFFile(args.core, True)
    hbm.print_phdrs()

    xkphys_base = 0xa800000000000000
    kseg0_base  = 0xffffffff80000000
    kseg0_size  = 0x0000000020000000

    fv_phdr = hbm.find_load_phdr(args.funvisor_address)
    if fv_phdr:
        (blob_pos, blob_size) = hbm.write_phdr(fv_phdr, core)
        blob_ph = Phdr(Phdr.PT_LOAD, Phdr.PF_R | Phdr.PF_W | Phdr.PF_X, blob_pos, xkphys_base, 0, blob_size, blob_size, 0)
        core.add_phdr(blob_ph)
        kseg0_view_size = min(blob_size, kseg0_size)
        kseg0_ph = Phdr(Phdr.PT_LOAD, Phdr.PF_R | Phdr.PF_W | Phdr.PF_X, blob_pos, kseg0_base, 0, kseg0_view_size, kseg0_view_size, 0)
        core.add_phdr(kseg0_ph)
        # Dummy register set of all zeros
        note = ELFNote('CORE', ELFNote.NT_PRSTATUS, bytes(480))
        (note_pos, note_size) = core.write_bytes(note.to_bytes())
        note_ph = Phdr(Phdr.PT_NOTE, 0, note_pos, 0, 0, note_size, 0, 0)
        core.add_phdr(note_ph)
        core.emit_headers()
        core.close()
    else:
        print("No FunVisor region found")

    return 0


###
##  entrypoint
#
if __name__ == "__main__":
    main()
