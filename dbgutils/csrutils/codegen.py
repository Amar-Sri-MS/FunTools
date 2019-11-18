#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# TODO (jimmy): this is throwaway code, duplicated from FunHW,
#               and will be replaced with the new csr2api layer
#

from copy import copy


## class definitions
class SubDimension():
    def __init__(self, name, left, right):
        self.name = name
        self.left = left
        self.right = right

    @property
    def arity(self):
        return 1 + abs(self.left - self.right)


# Interval node
# body nodes have non-empty children and value is the cut point
# intervals less than the cut point are under children[0], and
# intervals not less than the cut point are under children[1]
# leaf nodes have empty children and value is base offset
class Interval():
    def __init__(self, value, children=None):
        self.value = value
        self.children = children

    @classmethod
    def from_list(cls, intervals):
        def go(lo, hi, default):
            if lo < hi:
                i = (lo + hi) // 2
                # body node
                return cls(intervals[i]['index'], (go(lo, i, default), go(i+1, hi, intervals[i])))
            else:
                # leaf node
                return cls(default['base'] // 8)
        return go(1, len(intervals), intervals[0])

    
class Dimension():
    def __init__(self, name, rep):
        self.name = name
        self.stride = rep.stride // 8
        self.count = rep.count
        # append index to name if multiple subdims
        mkname = lambda i: name if len(rep.bounds) == 1 else "%s%d" % (name, i)
        self.subdims = [SubDimension(mkname(i), left, right) for i, (left, right) in enumerate(rep.bounds)]
        self.nsubdims = len(self.subdims)
        if rep.intervals:
            self.intervals = Interval.from_list(rep.intervals)
        else:
            self.intervals = None


REPNAMES = ["i", "j", "k", "l", "m"]


class Register():
    def __init__(self, context, node):
        self.context = context
        self.node = node
        self.name = context["path"]
        self.devtype = context["devtype"]

        # XXX: just eat any copies of the prefix while we transition to
        # csr2. We can clean this up later
        while(self.name.startswith(context["prefix"])):
            self.name = self.name[len(context["prefix"]):]
        self.name = context["prefix"] + self.name
        self.short_name = self.name[len(context["prefix"]):]

        self.fields = None
        self.is_wide = (node.size > 64)
        self.msb = node.msb
        self.size = node.lsb - node.msb + 1
        self.padded_size = node.size
        self.stride = node.stride
        self.count = node.parent.count

        # compute the address of the register relative to the dev
        self.offset = node.offset
        if (len(context["offset"]) > 0):
            self.addr_comp = "offset calc %s (local=%s)" % ([ hex(x/8) for x in context["offset"]], node.offset)
            self.address = hex(sum(context["offset"]) / 8)
        else:
            self.address = "CSR2_BADVALUE"

        # make a list of the "repeat" argument variables
        reps = context["repeats"]
        self.nrep = len(reps)
        assert self.nrep <= len(REPNAMES), "Insufficient REPNAMES"
        self.is_repeat = self.nrep > 0
        self.rpt_dims = [Dimension(name, rep) for name, rep in zip(REPNAMES, reps)]
        self.rpt_args = [subdim.name for dim in self.rpt_dims for subdim in dim.subdims]

        # go and fish out any attributes
        self.attrs = []
        self.is_irq = 0
        self.irq_node = None
        if (node.parent is not None):
            self.attrs = node.parent.jdict.get("attributes")

class Irq():
    def __init__(self, context, node):
        self.context = context
        self.node = node
        self.name = context["path"]
        self.devtype = context["devtype"]
        inode = getattr(node,'irq')
        category = inode['category']
        self.is_fatal = (category == "fatal")
        self.reg_status = None
        self.reg_mask = None
        self.reg_diag = None
        self.index = 0
        self.repeated = 0
        self.irq_address = 0
        self.wiq_number = 0
        self.hw_hole = 0
        self.inst = None
        if (len(context["irq_offset"]) > 0):
            self.irq_offset = context["irq_offset"][-1]

        # XXX: just eat any copies of the prefix while we transition to
        # csr2. We can clean this up later
        while(self.name.startswith(context["prefix"])):
            self.name = self.name[len(context["prefix"]):]
        self.name = context["prefix"] + self.name

        if (len(context["irq_offset"]) > 0):
            self.irq_addr_comp = "offset calc %s (local=%s)" % ([ hex(x) for x in context["irq_offset"]], node.irq_offset)
            self.irq_address = hex(sum(context["irq_offset"]))
        else:
            self.irq_address = "CSR2_BADVALUE"


class DevInstance():
    def __init__(self, address, irq_address, name, pname, dname):
        self.id = -1
        self.address = address
        self.irq_address = irq_address
        self.name = name
        self.pname = pname
        self.dname = dname

    def get_address(self):
        return self.address

    def get_irq_address(self):
        return self.irq_address

    def get_name(self):
        return self.name

    def get_dpath(self):
        return self.dname


class Field():
    def __init__(self, context, node):
        self.node = node
        self.name = node.name
        self.size = node.children[0].size # xxx?
        self.msb = context["reg"].padded_size - node.offset - 1 - context["reg"].msb
        self.lsb = self.msb - self.size + 1
        self.count = node.count
        self.fld_type = self.name
        self.attrs = node.jdict.get("attributes")
        self.is_wide = self.size > 64

    def enum(self):
        return [self]


class UnnamedField(Field):
    def __init__(self, context, node):
        self.node = node
        self.name = "<implicit>"
        self.size = node.size
        self.msb = context["reg"].padded_size - 1 - context["reg"].msb
        self.lsb = self.msb - self.size + 1
        self.count = 1
        self.fld_type = "unnamed"
        self.attrs = node.jdict.get("attributes")
        self.is_wide = self.size > 64

    def get_type_flags(self):
        # is_implicit, is_array, is_composite
        return (True, False, False)


class ArrayField(Field):
    def __init__(self, context, node):
        self.node = node
        self.field = mkfield(context, node.children[0])
        self.name = "array"
        self.lsb = None # fixme
        self.size = node.size
        self.count = node.children[0].count
        self.rpt_args = REPNAMES[:1]
        self.fld_type = "<array[%s]>" % self.field.fld_type
        self.attrs = self.field.attrs

    def get_type_flags(self):
        # is_implicit, is_array, is_composite
        return (False, True, False)


class ListField(Field):
    def __init__(self, context, node, is_union):
        self.node = node
        self.field_list = []
        self.name = "<composite>"
        for field in node.children[0].children:
            # self.field_list.append(mkfield(context, field))
            self.field_list.append(Field(context, field))
        self.count = len(self.field_list)
        self.size = node.size
        self.fld_type = "composite"
        self.attrs = None # OK?
        self.is_union = is_union

    def get_type_flags(self):
        # is_implicit, is_array, is_composite
        return (False, False, True)

    def enum(self):
        return self.field_list


# factory for properly typed fields
def mkfield(context, node):

    typ = node.children[0]
    kind = typ.kind
    if (kind == "logic"):
        field = UnnamedField(context, typ)
    elif (kind == "array"):
        field = ArrayField(context, node)
    elif (kind == "union"):
        field = ListField(context, node, is_union=True)
    elif (kind == "struct"):
        field = ListField(context, node, is_union=False)
    elif (kind == "elastic"):
        field = Field(context, node)
    elif  (kind == "typedef"):
        field = mkfield(context, typ)
    else:
        raise RuntimeError("unknown field node '%s'" % kind)

    return field

## Recurse the context copying as necessary
def update_path(context, rnode):

    context = context.copy()
    curpath = context["path"]
    curindexpath = context["indexpath"]
    curdotpath = context["dotted_path"]

    if (rnode.altname is None):
        name = rnode.name
    else:
        name = rnode.altname
        # print "altname is %s" % name

    if (not rnode.is_silent):
        if (name is not None):
            if (curpath != ""):
                curpath += "_"
            curpath += name
            if (curindexpath != ""):
                curindexpath += "_"
            curindexpath += name
            if (curdotpath != ""):
                curdotpath += "."
            curdotpath += name

    if (rnode.kind == "repeat"):
        if curindexpath.endswith("%d"):
            curindexpath += "_"
        if curdotpath.endswith("%d"):
            curdotpath += "_"
        curindexpath += "%d"
        curdotpath += "%d"

    context["path"] = curpath
    context["indexpath"] = curindexpath
    context["dotted_path"] = curdotpath
    context["repeats"] = list(context["repeats"])

    return context

def build_field_list(context, rnode):

    fldcontext = context.copy()
    fields = mkfield(context, rnode)

    return fields

def build_register(context, rnode, is_irq):

    assert(rnode.kind == "reg")
    assert((rnode.size % 64) == 0)

    regcontext = context.copy()
    reg = Register(context, rnode)
    reg.is_irq = is_irq
    regcontext['reg'] = reg
    reg.fields = build_field_list(regcontext, rnode)
    (reg.is_implicit, reg.is_array, reg.is_composite) = reg.fields.get_type_flags()
    # link irq to access registers
    if is_irq and len(context["dev"]["irqs"]) > 0:
        if 'status' in reg.name:
            context["dev"]["irqs"][-1].reg_status = reg
            if len(context["tmp_irqs"]):
                context["tmp_irqs"][-1].reg_status = reg
        elif 'mask' in reg.name:
            context["dev"]["irqs"][-1].reg_mask = reg
            if len(context["tmp_irqs"]):
                context["tmp_irqs"][-1].reg_mask = reg
        elif 'diag' in reg.name:
            context["dev"]["irqs"][-1].reg_diag = reg
            if len(context["tmp_irqs"]):
                context["tmp_irqs"][-1].reg_diag = reg
        else:
            print ( "Unknown irq reg name %s" % reg.name )

        # back link to irq
        reg.irq_node = context["dev"]["irqs"][-1]

    return reg

def build_irq(context, rnode):
    irq = Irq(context, rnode)
    return irq

###
##  strip "_csr" from csr2package names
#
def fixname(stem):
    if (stem.endswith("_csr")):
        stem = stem[:-4]

    return stem

###
##  generics
#

generic_reglist = {}
generic_pkglist = []

chip_devlist = []

full_irqs = []

def generics_add_package(pkginfo):

    # so we know which header
    generic_pkglist.append(pkginfo["devname"])

    # build a register list by short name
    for reg in pkginfo["regs"]:
            l = generic_reglist.setdefault(reg.short_name, [])
            l.append(reg)

###
##  top-level tree walkers
#


def generate_indices(repeats, dim=0):
    if dim < len(repeats):
        rep = repeats[dim]
        assert not rep.intervals, "Cannot handle non-linear repeated devnodes"
        for i in range(rep.count):
            for indices in generate_indices(repeats, dim+1):
                yield [i] + indices
    else:
        yield []

# if we've hit a devnode, update the context as necessary to
# keep recursing
def update_devnode_context(context, rnode, devtab):

    # there's 2 things to do here:
    # (1) if this is an unseen device, add it to the devtab and reset
    # key context details so parsing makes sense
    #
    # (2) add the instance to the devtab

    pname = fixname(rnode.name)
    rnode.altname = pname

    # grab a copy in case we change it
    address = list(context["address"])
    repeats = list(context["repeats"])
    irq_address = list(context["irq_address"])
    path = context["path"]

    if (pname not in devtab):
        # create the dev
        # XXX: tracking a device with a dict instead of a class because
        # jinja is happier that way. can probably just __dict__ tho?
        dev = {}
        dev["devtype"] = "csr2dev_%s" % pname
        dev["devname"] = pname
        dev["instances"] = []
        dev["regs"] = []
        dev["irqs"] = []
        dev["full_irqs"] = []
        devtab[pname] = dev

        # tweak the context naming & reset the address and repeats for children
        context = context.copy()
        context["dev"] = dev
        context["devtype"] = "csr2dev_%s" % pname
        context["path"] = pname
        context["prefix"] = "%s_" % pname
        context["offset"] = []
        context["repeats"] = []
        context["irq_offset"] = []

    # either way, this is now an instance of an existing device so add
    # it
    base_address = sum(address)
    base_irq_address = sum(irq_address)

    for indices in generate_indices(repeats):
        offset = sum(rep.stride * i for rep, i in zip(repeats, indices))
        irq_offset = sum(rep.irq_stride * i for rep, i in zip(repeats, indices))
        indexpath = context["indexpath"] % tuple(indices)
        dottedpath = context["dotted_path"] % tuple(indices)
        devtab[pname]["instances"].append(
                DevInstance((base_address + offset) // 8,
                            base_irq_address + irq_offset,
                            indexpath, pname, dottedpath))
        chip_devlist.append(  devtab[pname]["instances"][-1] ) # accumurate all instances within the chip
    return context


def do_build_devtab(context, rnode, devtab, is_irq):
    global Tracing
    my_irq = is_irq
    # dud nodes
    if (rnode.jdict is None):
        return

    # if this is an irq regfile
    if (hasattr(rnode,'irq')):
        my_irq = 1
        # ignore registers for which we're not looking at a device
        if (context["dev"] is not None):
            context["dev"]["irqs"].append(build_irq(context, rnode))
            context["tmp_irqs"].append(context["dev"]["irqs"][-1])
            context["dev"]["full_irqs"].append(context["dev"]["irqs"][-1])
            context["dev"]["is_irq"] = 1

    if (context["dev"] is not None):
        context["dev"]["is_irq"] = my_irq

    # if this is a register, add it to the current device
    if (rnode.kind == "reg"):
        # ignore registers for which we're not looking at a device
        if (context["dev"] is not None):
            context["dev"]["regs"].append(build_register(context, rnode, my_irq))
            return

        # just ignore the tree under registers otherwise
        return

    # children
    context = update_path(context, rnode)

    # if we've hit a devnode we care about, process it
    # FIXME: use interims
    if ((rnode.name in context["devnodes"])
        and (rnode.kind == context["nodetype"])):
        if (rnode.name == "mud_top"):
            print "found a mud top"
        context = update_devnode_context(context, rnode, devtab)
    elif (rnode.name == "mud_top"):
        print "skipped a mud top (%s) %d %s %s" % (rnode.kind, rnode.kind == context["nodetype"], rnode.name in context["devnodes"], context["devnodes"])

    # manage repeat
    if (rnode.kind == "repeat"):
        context["repeats"].append(rnode)
        # collecting irq under repeat to create repeated instances for wiq table
        # currently only one dimension is supported. may extend to support multi-dimension if needed.
        if( context["irq_pop_repeat"] is None):
            context["tmp_irqs"] = []
            context["irq_pop_repeat"] = rnode

    # manage offsets
    if (rnode.offset is not None):
        # skip any offset for the root
        context["address"] = context["address"] + [rnode.offset]
        context["offset"] = context["offset"] + [rnode.offset]

    # manage offsets
    if (rnode.irq_offset is not None):
        # skip any offset for the root
        context["irq_address"] = context["irq_address"] + [rnode.irq_offset]
        context["irq_offset"] = context["irq_offset"] + [rnode.irq_offset]

    for child in rnode.children:
        do_build_devtab(context, child, devtab, my_irq)

    if ( rnode.kind == "repeat" ):
        if( context["irq_pop_repeat"] == rnode ):
            context["irq_pop_repeat"] = None
            if ( context["dev"] is not None and len(context["tmp_irqs"]) > 0 ):
                # create repeated irq in collected order
                # first set is already in full_irqs
                for i in range(rnode.count - 1):
                    for irq in context["tmp_irqs"]:
                        print( "repeating %s on %d" % (irq.name, i+1) )
                        irq_copy = copy(irq)
                        irq_copy.index = i + 1
                        irq_copy.repeated = 1
                        context["dev"]["full_irqs"].append(irq_copy)

# Some IRQ csrs are no-hw, and should avoid read access
#  Note: Holes are hard-coded here, which is not proper way. 
#  JSON file shold tell where the holes are. 
hw_holes = [  
  (230, 232),   # sdif placeholder
  (357, 365)    # hsu h1 shared block with h0
]

def do_update_full_irq(context,devtab):
    irq_num = 0
    l = chip_devlist
    l.sort(key=DevInstance.get_irq_address)
    mismatch = 0
    # for i, inst in enumerate(l):
    #     inst.id = i    
    for inst in l:
        dev = devtab[inst.pname]
        base_irq_addr = inst.irq_address
        if( base_irq_addr - irq_num > mismatch ):
            mismatch = base_irq_addr - irq_num - mismatch
            print( "ERROR!! IRQ wiq_number mismatch %d p_dev %s p_inst %s  dev %s inst %s base %d current %d" %( mismatch, p_inst.pname, p_inst.name, inst.pname, inst.name, inst.irq_address, irq_num) )
        irq_n = 0
        p_inst = inst
        for irq in dev["full_irqs"]:
            c_irq = copy(irq)
            c_irq.inst = inst
            c_irq.wiq_number = irq_num
            for ( hole_start, hole_end) in hw_holes:
                if (irq_num >= hole_start) and (irq_num <= hole_end):
                    print( "HW hole detected on wiq_number %d " % irq_num )
                    c_irq.hw_hole = 1
            # print( "inst %s %s irq %s irq_address %d wiq_number %d" % (inst.pname, inst.name, c_irq.name, base_irq_addr + irq_n, c_irq.wiq_number ) )
            irq_num += 1
            irq_n += 1
            full_irqs.append(c_irq)


def build_devtab(rnode, devnodes, nodetype):

    # initial parsing context
    context = {}
    context["repeats"] = []
    context["prefix"] = ""
    context["path"] = ""
    context["indexpath"] = ""
    context["dotted_path"] = ""
    context["address"] = [] # offsets from root
    context["offset"] = [] # offsets from closest dev ancestor (or root)
    context["irq_address"] = [] # irq_offsets from root
    context["irq_offset"] = [] # irq_offsets from closest dev ancestor (or root)
    context["dev"] = None
    context["devnodes"] = devnodes
    context["nodetype"] = nodetype

    context["is_irq"] = 0
    context["irqs"] = []
    context["tmp_irqs"] = []
    context["irq_pop_repeat"] = None
    context["full_irqs"] = []

    devtab = {}
    do_build_devtab(context, rnode, devtab, 0)

    do_update_full_irq(context, devtab)

    return devtab

###
##  external APIs
#


def process_root(root, devnodes, nodetype):

    # process the whole tree
    devtab = build_devtab(root, devnodes, nodetype)
    return devtab

