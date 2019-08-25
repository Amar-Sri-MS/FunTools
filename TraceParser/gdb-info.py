#!/usr/bin/python

## read a deduped file and translate all the addresses into something
## interesting via gdb

import os
import sys
import json
import time
import platform

# try and import gdb
try:
    import gdb
    in_gdb = True
except:
    in_gdb = False

IN_FILE = "miss-counts.js"
OUT_FILE = "gdbdb.js"
FUNOS_BINARY = "funos-f1.stripped"

###
##  We need gdb to import us...
#

def restart_in_gdb():

    current_os = platform.system()
    if current_os == 'Darwin':
        gdb = '/Users/Shared/cross-el/bin/mips64-gdb'
    else:
        gdb = ('/opt/cross/mips64/bin/'
               'mips64-unknown-elf-gdb')

    cmd = "%s -ex 'source %s' %s -ex quit" % (gdb, os.path.realpath(__file__),
                                               FUNOS_BINARY)
    print cmd
    
    r = os.system(cmd)
    if (r != 0):
        print "gdb failed: %s" % cmd
        sys.exit(1)
    sys.exit(0)
    
###
##  use addr2line
#

def struct_type_walk(name, type, offset, is_union):

    # compute the field:
    names = []
    for field in type.fields():
        base = field.bitpos / 8
        max = base + field.type.sizeof
        if ((offset >= base) and (offset < max)):
            fname = field.name
            if (fname is None):
                fname = "[anon]"
            newname = "%s.%s" % (name, fname)
            offset = offset - base
            newname = nested_type_walk(newname, field.type, offset)
            if (not is_union):
                return newname
            names.append(newname)

    if (len(names) > 0):
        return "\n".join(names)
            
    return  "%s.?? (%s + 0x%x)" % (name, name, offset)


def nested_type_walk(name, type, offset):

    if (type.code == gdb.TYPE_CODE_ARRAY):
        # FIXME
        per = type.target().sizeof
        idx = int(offset/per)
        offset = offset - idx * per
        return nested_type_walk("%s[%d]" % (name, idx), type.target(), offset)
    elif (type.code == gdb.TYPE_CODE_STRUCT):
        return struct_type_walk(name, type, offset, False)
    elif (type.code == gdb.TYPE_CODE_UNION):
        # FIXME: use union?
        return struct_type_walk(name, type, offset, False)
    else:
        if (offset == 0):
            return name
        else:
            return "%s + 0x%x" % (name, offset)


def sym2str(va, sym):

    assert(va >= sym[0])
    assert(va < sym[1])
    
    name = sym[2]
    type = sym[3]
    offset = va - sym[0]

    return nested_type_walk(name, type, offset)
    
def printsym(sym):
    print "(0x%x, 0x%x, %s, %s)" % sym

def debug_find_closest(va, syms):

    for i in range(len(syms)):
        sym = syms[i]
        if (sym[0] > va):
            print i
            printsym(syms[i-1])
            printsym(syms[i])
            printsym(syms[i+1])
            return

def get_syminfo(va, syms):

    n0 = 0
    n1 = len(syms)-1

    debug = False
    if (va == 0xa800000003bdf240):
        print "magic sym"
        debug = True

    if (debug):
        debug_find_closest(va, syms)
    
    while (n0 <= n1):
        i = (n0 + n1) / 2

        sym = syms[i]
        if ((va >= sym[0]) and (va < sym[1])):
            if (debug):
                print "found: %s" % printsym(sym)
            return sym2str(va, sym)
        
        if (va >= sym[1]):
            n0 = i + 1
        elif (va < sym[0]):
            n1 = i - 1

        if (debug):
            print n0, i, n1, "0x%x" % va
            printsym(sym)

    if (debug):
        print "not found?"
    return None
    
    
###
##  add a VA and its line info to the full list
#

def mkaddrinfo(va, syms):
    # look up all the info for a line
    info = {}

    info["line_va"] = va - (va % 64) # round to cache line
    
    # find the gdb symbol info
    info["syminfo"] = get_syminfo(va, syms)

    return info
    
def check_add(addrinfo, va, syms):
    sva = "0x%016x" % va
    if (sva not in addrinfo):
        info = mkaddrinfo(va, syms)
        addrinfo[sva] = info
        if (info["line_va"] not in addrinfo):
            va = info["line_va"]
            info = mkaddrinfo(va, syms)
            sva = "0x%016x" % va
            addrinfo[sva] = info

###
##  Get all the symbols
#

LOCTAB = None

def mkloctab():
    global LOCTAB
    if (LOCTAB is None):
        LOCTAB =  {gdb.SYMBOL_LOC_UNDEF:	"gdb.SYMBOL_LOC_UNDEF",
                   gdb.SYMBOL_LOC_CONST:	"gdb.SYMBOL_LOC_CONST",
                   gdb.SYMBOL_LOC_STATIC:	"gdb.SYMBOL_LOC_STATIC",
                   gdb.SYMBOL_LOC_REGISTER:	"gdb.SYMBOL_LOC_REGISTER",
                   gdb.SYMBOL_LOC_ARG: 	 	"gdb.SYMBOL_LOC_ARG",
                   gdb.SYMBOL_LOC_REF_ARG:	"gdb.SYMBOL_LOC_REF_ARG",
                   gdb.SYMBOL_LOC_REGPARM_ADDR: "gdb.SYMBOL_LOC_REGPARM_ADDR",
                   gdb.SYMBOL_LOC_LOCAL: 	"gdb.SYMBOL_LOC_LOCAL",
                   gdb.SYMBOL_LOC_TYPEDEF:	"gdb.SYMBOL_LOC_TYPEDEF",
                   gdb.SYMBOL_LOC_BLOCK: 	"gdb.SYMBOL_LOC_BLOCK",
                   gdb.SYMBOL_LOC_CONST_BYTES:	"gdb.SYMBOL_LOC_CONST_BYTES",
                   gdb.SYMBOL_LOC_UNRESOLVED:  	"gdb.SYMBOL_LOC_UNRESOLVED",
                   gdb.SYMBOL_LOC_OPTIMIZED_OUT:"gdb.SYMBOL_LOC_OPTIMIZED_OUT",
                   gdb.SYMBOL_LOC_COMPUTED:     "gdb.SYMBOL_LOC_COMPUTED",
                   gdb.SYMBOL_LOC_COMPUTED: 	"gdb.SYMBOL_LOC_COMPUTED",
        }


def mksymlist(block):

    print "block start: 0x%x" % block.start
    print "block end: 0x%x" % block.end
    
    mkloctab()
    
    l = []
    for sym in block:
        name = sym.name
        if (name == "running_cluster_count"):
            debug = True
        else:
            debug = False
        if (debug):
            print "sym %s" % sym.name
            print "%d: %s" % (sym.addr_class, LOCTAB[sym.addr_class])
            print "type: %s, %d" % (sym.type, sym.type.sizeof)
            print sym.line
            print sym.is_valid()
            print dir(sym)
            print sym.symtab

        if (sym.needs_frame):
            if (debug):
                print "needs frame!"
            continue
        
        if (sym.addr_class == gdb.SYMBOL_LOC_UNRESOLVED):
            if (debug):
                print "unresolved!"
            continue

        if (sym.addr_class == gdb.SYMBOL_LOC_TYPEDEF):
            if (debug):
                print "typedef!"
            continue

        if (sym.addr_class == gdb.SYMBOL_LOC_OPTIMIZED_OUT):
            if (debug):
                print "optimised out!"
            continue

        if (sym.addr_class == gdb.SYMBOL_LOC_CONST):
            if (debug):
                print "const!"
            continue
        
        if (debug):
            print sym, sym.value()
            print sym.value().address
        if (sym.value().address is not None):
            address = sym.value().address.cast(gdb.lookup_type("uintptr_t"))
        else:
            address = sym.value().cast(gdb.lookup_type("uintptr_t"))
            
        start = int(address) & 0xffffffffffffffff # sigh python
        end = start + sym.type.sizeof
        tup = (start, end, name, sym.type)
        if (debug):
            printsym(tup)
        
        l.append(tup)

    return l

def find_all_symbols():

    syms = []

    symtab = gdb.lookup_global_symbol("kernel_start").symtab

    syms += mksymlist(symtab.global_block())
    syms += mksymlist(symtab.static_block())

    print "Found %d symbols" % len(syms)
    syms.sort()

    return syms
            
###
##  main in gdb
#

def gdb_main():
    print "starting in gdb..."
    fl = open(IN_FILE)

    misslist = json.loads(fl.read())
    addrinfo = {}

    syms = find_all_symbols()
    
    n = len(misslist)
    t0 = time.time()
    for i in range(0, n):
        miss = misslist[i]
        pc = miss["pc"]
        va = miss["vaddr"]

        t1 = time.time()
        if ((t1 - t0) > 10):
            print "complete: %f%%" % ((i * 100.0) / n)
            t0 = t1
        check_add(addrinfo, int(pc, 16), syms)
        check_add(addrinfo, int(va, 16), syms)
                

    # write it out
    fl = open(OUT_FILE, "w")
    fl.write(json.dumps(addrinfo, indent=4))
    print "done"

        

### 
##  XXX: UI hack
#
if (__name__ == "__main__"):
    if (not in_gdb):
        restart_in_gdb()
    else:
        gdb_main() # run out in-gdb code


