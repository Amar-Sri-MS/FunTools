#!/usr/bin/env python3

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

IN_FILE = "addr-list.js"
OUT_FILE = "gdb-ident.js"
FUNOS_BINARY = "funos-f1.stripped"

###
##  We need gdb to import us...
#

def restart_in_gdb(binname, exit=True):

    current_os = platform.system()
    if current_os == 'Darwin':
        gdb = '/Users/Shared/cross-el/bin/mips64-gdb'
        if not os.path.exists(gdb):
            gdb = '/Users/Shared/cross/mips64/bin/mips64-unknown-elf-gdb'
    else:
        gdb = ('/opt/cross/mips64/bin/'
               'mips64-unknown-elf-gdb')

    # XXX: if we're compiled, strip back to the real script name for gdb
    scriptname = os.path.realpath(__file__)
    print(scriptname, scriptname[:-4])
    if (scriptname[-4:] == ".pyc"):
        print("fixup")
        scriptname = scriptname[:-1]
        
    print(scriptname)
    
    cmd = "%s -ex 'source %s' %s -ex quit" % (gdb, scriptname,
                                              binname)
    print(cmd)
    
    r = os.system(cmd)
    if (r != 0):
        print("gdb failed: %s" % cmd)
        sys.exit(1)
    if (exit):
        sys.exit(0)
    
###
##  use addr2line
#

def struct_type_walk(name, type, offset, is_union, vague):

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
            newname = nested_type_walk(newname, field.type, offset, vague)
            if (not is_union):
                return newname
            names.append(newname)

    if (len(names) > 0):
        return "\n".join(names)
            
    return  "%s.?? (%s + 0x%x)" % (name, name, offset)


def nested_type_walk(name, type, offset, vague):

    if (type.code == gdb.TYPE_CODE_ARRAY):
        # FIXME
        per = type.target().sizeof
        idx = int(offset/per)
        offset = offset - idx * per
        if (not vague):
            vidx = str(idx)
        else:
            vidx = "i"
        return nested_type_walk("%s[%s]" % (name, vidx),
                                type.target(), offset, vague)
    elif (type.code == gdb.TYPE_CODE_STRUCT):
        return struct_type_walk(name, type, offset, False, vague)
    elif (type.code == gdb.TYPE_CODE_UNION):
        # FIXME: use union?
        return struct_type_walk(name, type, offset, False, vague)
    else:
        if (offset == 0):
            return name
        else:
            return "%s + 0x%x" % (name, offset)


def sym2str(va, sym, vague):

    assert(va >= sym[0])
    assert(va < sym[1])
    
    name = sym[2]
    type = sym[3]
    offset = va - sym[0]

    return nested_type_walk(name, type, offset, vague)
    
def printsym(sym):
    print("(0x%x, 0x%x, %s, %s)" % sym)

def debug_find_closest(va, syms):

    for i in range(len(syms)):
        sym = syms[i]
        if (sym[0] > va):
            print(i)
            printsym(syms[i-1])
            printsym(syms[i])
            printsym(syms[i+1])
            return

def get_syminfo(va, syms, vague=False):

    n0 = 0
    n1 = len(syms)-1

    debug = False
    if (va == 0xa800000003bdf240):
        print("magic sym")
        debug = True

    if (debug):
        debug_find_closest(va, syms)
    
    while (n0 <= n1):
        i = (n0 + n1) / 2

        sym = syms[i]
        if ((va >= sym[0]) and (va < sym[1])):
            if (debug):
                print("found: %s" % printsym(sym))
            return sym2str(va, sym, vague)
        
        if (va >= sym[1]):
            n0 = i + 1
        elif (va < sym[0]):
            n1 = i - 1

        if (debug):
            print(n0, i, n1, "0x%x" % va)
            printsym(sym)

    if (debug):
        print("not found?")
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
    info["symvague"] = get_syminfo(va, syms, True)

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

    print("block start: 0x%x" % block.start)
    print("block end: 0x%x" % block.end)
    
    mkloctab()
    
    l = []
    for sym in block:
        name = sym.name
        if (name == "running_cluster_count"):
            debug = True
        else:
            debug = False
        if (debug):
            print("sym %s" % sym.name)
            print("%d: %s" % (sym.addr_class, LOCTAB[sym.addr_class]))
            print("type: %s, %d" % (sym.type, sym.type.sizeof))
            print(sym.line)
            print(sym.is_valid())
            print(dir(sym))
            print(sym.symtab)

        if (sym.needs_frame):
            if (debug):
                print("needs frame!")
            continue
        
        if (sym.addr_class == gdb.SYMBOL_LOC_UNRESOLVED):
            if (debug):
                print("unresolved!")
            continue

        if (sym.addr_class == gdb.SYMBOL_LOC_TYPEDEF):
            if (debug):
                print("typedef!")
            continue

        if (sym.addr_class == gdb.SYMBOL_LOC_OPTIMIZED_OUT):
            if (debug):
                print("optimised out!")
            continue

        if (sym.addr_class == gdb.SYMBOL_LOC_CONST):
            if (debug):
                print("const!")
            continue

        if (sym.addr_class == gdb.SYMBOL_LOC_CONST_BYTES):
            if (debug):
                print("const bytes!")
            continue

        if (debug):
            print(sym, sym.value())
            print(sym.value().address)

        # Work around the thread-local variables in FunOS because gdb won't
        # handle them without register context.
        try:
            v = sym.value()
        except gdb.error as e:
            if "without registers" in str(e):
                continue

        if (v.address is not None):
            address = v.address.cast(gdb.lookup_type("uintptr_t"))
        else:
            address = v.cast(gdb.lookup_type("uintptr_t"))
            
        start = int(address) & 0xffffffffffffffff # sigh python
        end = start + sym.type.sizeof
        tup = (start, end, name, sym.type)
        if (debug):
            printsym(tup)
        
        l.append(tup)

    return l


class FakeGdbType:
    """
    Faux gdb type object.

    May be extended in future to mimic a proper gdb type so we can walk into
    structs and arrays in thread-local.
    """
    def __init__(self):
        self.code = None


def add_thread_locals():
    """
    Work around the fact that gdb chokes on the thread-local variables.

    A previous stage may have generated thread-local information via other
    means. This function converts that information into the symbol tuples
    used by the other portions of gdb_ident.
    """
    syms = []
    fname = "thread-local-ident.js"

    if not os.path.exists(fname):
        return syms

    with open(fname, "r") as f:
        vars = json.load(f)
        for var in vars:
            start = var[1]
            size = var[2]

            # Hokey... mangle the variable name to include the c.c.v so we know
            # which VP the thread-local belongs to.
            #
            # An alternative for the future: treat the per-vp stride
            # as a struct, and the thread-local region as an array of those
            # structs. This will require conjuring faux gdb data structures,
            # but gives the best insight when folks start adding structs and
            # arrays into thread-local.
            mangled_name = var[0] + " (%s)" % ccv(var[3])
            sym = (start, start + size, mangled_name, FakeGdbType())
            syms.append(sym)

    return syms


MAX_VPS_PER_CLUSTER = 24
MAX_VPS_PER_CORE = 4

def ccv(vpnum):
    cl = vpnum // MAX_VPS_PER_CLUSTER
    co = (vpnum % MAX_VPS_PER_CLUSTER) // MAX_VPS_PER_CORE
    vp = vpnum % MAX_VPS_PER_CORE
    return "%d.%d.%d" % (cl, co, vp)


def find_all_symbols():

    syms = []

    symtab = gdb.lookup_global_symbol("kernel_start").symtab

    syms += mksymlist(symtab.global_block())
    syms += mksymlist(symtab.static_block())
    syms += add_thread_locals()

    print("Found %d symbols" % len(syms))
    syms.sort()

    return syms

###
##  main in gdb
#

def gdb_main():
    print("starting in gdb...")
    fl = open(IN_FILE)

    addrlist = json.loads(fl.read())
    addrident = {}

    syms = find_all_symbols()
    
    n = len(addrlist)
    t0 = time.time()
    for i in range(0, n):
        va = addrlist[i]

        t1 = time.time()
        if ((t1 - t0) > 10):
            print("complete: %f%%" % ((i * 100.0) / n))
            t0 = t1
        check_add(addrident, int(va, 16), syms)


    # write it out
    fl = open(OUT_FILE, "w")
    fl.write(json.dumps(addrident, indent=4))
    print("done")

        

### 
##  XXX: UI hack
#
if (__name__ == "__main__"):
    if (not in_gdb):
        restart_in_gdb(FUNOS_BINARY)
    else:
        gdb_main() # run out in-gdb code

