#!/usr/bin/python

#
# TODO (jimmy): this is throwaway code, duplicated from FunHW,
#               and will be replaced with the new csr2api layer
#

import glob
import os
import json

import codegen


###
##  for which chip are we building?
#

F1GEN = False

###
##  reference by name
#

NODETAB = {}

def publish_node(node):

    pkg = find_package_name(node)
    nodename = "%s::%s" % (pkg, node.name)

    if (node.name is None):
        return

    #if (NODETAB.get(nodename) is not None):
    #    raise RuntimeError("overwriting published node %s" % nodename)

    NODETAB[nodename] = node

def find_node(nodename):
    node = NODETAB.get(nodename)

    if (node is None):
        raise RuntimeError("Could not find node %s" % nodename)

    return node

###
##  consume csr2 json files
#
class Node:
    def __init__(self, parent, jdict, silent=False):
        self.jdict = jdict

        self.parent = parent

        if (jdict is None):
            return

        self.name = jdict.get("name")
        self.kind = jdict.get("kind")
        self.deps = jdict.get("deps")
        self.is_indirect = False
        self.is_silent = silent
        self.altname = None


        # print "%s - %s" % (self.name, self.kind)

        # Everyone has these fields
        self.align = jdict.get("align")
        self.size = jdict.get("size")
        self.offset = jdict.get("offset")
        self.irq_offset = jdict.get("irq_offset")
        self.lsb = jdict.get("lsb")
        self.msb = jdict.get("msb")
        if ("irq" in jdict):
            self.irq = jdict.get("irq")

        # put ourself in the namespace
        if (self.kind == "typedef"):
            publish_node(self)

        # some more useful feelds
        self.attributes = jdict.get("attributes")
        self.count = jdict.get("count")
        self.stride = jdict.get("stride", 0)
        self.bounds = jdict.get("bounds", [])

        if ("codepoints" in jdict):
            self.codepoints = jdict.get("codepoints")

        # make 1d arrays consistent with csr2lint-generated multi-dimensional arrays
        if len(self.bounds) == 2 and all(isinstance(bound, int) for bound in self.bounds):
            self.bounds = [self.bounds]
        # convert each bound back to a tuple
        self.bounds = [tuple(bound) for bound in self.bounds]

        self.intervals = jdict.get("intervals")
        self.irq_count = jdict.get("irq_count")
        self.irq_stride = jdict.get("irq_stride")

        if (self.kind == "package"):
            self.children = walk_nodelist(self, jdict.get("defs"))
        elif (self.kind == "typedef"):
            self.children = [mknode(self, jdict.get("type"))]
        elif (self.kind == "portal"):
            self.children = [mknode(self, jdict.get("type"))]
        elif (self.kind == "reg"):
            self.children = [mknode(self, jdict.get("type"))]
        elif (self.kind == "struct"):
            self.children = walk_nodelist(self, jdict.get("fields"))
            # print "%s has %d field children" % (self.name, len(self.children))
        elif (self.kind == "regfile"):
            self.children = walk_nodelist(self, jdict.get("fields"))
        elif (self.kind == "override"):
            self.children = [mknode(self, jdict.get("type"))]
            self.overrides = jdict["overrides"]
        elif (self.kind == "logic"):
            self.children = []
        elif (self.kind == "array"):
            self.children = [mknode(self, jdict.get("type"))]
        elif (self.kind == "repeat"):
            self.children = [mknode(self, jdict.get("type"))]
        elif (self.kind == "union"):
            self.children = walk_nodelist(self, jdict.get("fields"))
        elif (self.kind == None):
            # FIXME: "fla_cfg" has no kind?
            self.children = [mknode(self, jdict.get("type"))]
        else:
            print "don't know how to make children on %s" % self.kind
            self.children = []


    def dump_tree(self, fp, indent=""):
        # bug catcher
        if (len(indent) > 80):
            # raise RuntimeError("too deeply nested: %s" % self.name)
            fp.write("XXX: too deeply nested: %s\n" % self.name)
            return

        fp.write(indent)

        if (self.jdict is None):
            fp.write("{none}\n")
        else:
            fp.write("%s: %s" % (self.name, self.kind))

            if (self.is_indirect):
                fp.write(" (indirect)")
            if (self.is_silent):
                fp.write(" (silent)")
            if (self.offset is not None):
                fp.write(" (offset=0x%x)" % (self.offset / 8))
            if (self.align is not None):
                fp.write(" (align=0x%x)" % (self.align / 8))
            if (self.size is not None):
                fp.write(" (size=0x%x)" % (self.size / 8))
            fp.write("\n")

            for child in self.children:
                child.dump_tree(fp, indent + "\t")

class IndirectNode(Node):

    def __init__(self, child, name):
        #self.name = None # name
        #self.kind = "indirect"
        #self.deps = None
        #self.jdict = name
        self.indirection = child
        self.is_indirect = True
        self.is_silent = True

    def __getattr__(self, name):
        return getattr(self.indirection, name)


###
##  indirection aware factory
#

def mknode(parent, jdict):
    silent = False

    if (isinstance(jdict, basestring)):
        # print "indirect on %s" % jdict
        return IndirectNode(find_node(jdict), jdict)

    # For F1, patch parent names, too
    if (F1GEN):
        if (jdict is not None):
            kind = jdict.get("kind")
        if (kind == "typedef"):
            silent = True

        if (kind == "portal"):
            silent = True
        if (kind == "regfile"):
            silent = True

        # patch our parent if we're a silent type
        if silent and parent.kind:
            parent.is_silent = True

    # silence the root node, it appears in all contexts
    if not parent:
        silent = True

    return Node(parent, jdict, silent)


###
##  tree walks
#

def walk_nodelist(parent, jdict):

    nodes = []
    for d in jdict:
        node = mknode(parent, d)
        nodes.append(node)

    return nodes


def find_package_name(node):

    while (node.kind != "package"):
        node = node.parent

        if (node is None):
            raise RuntimeError("node without parent: %s" % node.name)

    return node.name

def find_specific_node(root, name, kind):

    if (root.jdict is None):
        return None

    # don't span imports for s1
    #if (root.is_indirect):
    #    return None

    if ((root.name == name)
        and (root.kind == kind)):
        return root

    for child in root.children:
        ret = find_specific_node(child, name, kind)
        if (ret is not None):
            return ret

    return None


###
##  make sure we parse files in dependency order
#
def find_usable_json(jsons, deps, doneset):

    # print "Checking %s" % jsons.keys()
    for jsname in jsons.keys():

        # print "Checking json %s" % jsname
        d = deps[jsname]

        # if everything we need is done, ship it
        if d.issubset(doneset):
            # print "%s it a subset of %s" % (d, doneset)
            return jsname
        else:
            # print "%s it not a subset of %s" % (d, doneset)
            pass

    # nothign OK
    return None

###
##  consume csr2 json files
#


def get_device_table():
    global F1GEN

    # TODO (jimmy): find a better way to get the csr2 json files?
    ws = os.environ.get('WORKSPACE')
    if not ws:
        print 'Error: Must set WORKSPACE environment variable'
        return None
    chip = 's1'
    if F1GEN:
        chip = 'f1'

    funhw = os.path.join(ws, 'FunHW')
    if not os.path.exists(funhw):
        print 'Error: Must have FunHW repo in WORKSPACE'
        return None

    devfile = '%s/FunHW/csr2api/%s-devlist.txt' % (ws, chip)
    json_files = glob.glob('%s/FunHW/chip/%s/csr2/*.json' % (ws, chip))

    lines = open(devfile).readlines()
    devnodes = [ l.strip() for l in lines ]

    if F1GEN:
        nodetype = None
        args_root = 'chip_f1::root'
    else:
        # compatabilty
        devnodes += [ "%s_csr" % l for l in devnodes ]
        nodetype = "typedef"
        args_root = 'chip_s1::root'

    print "Looking for device nodes %s" % ", ".join(devnodes)

    # start by reading all the jsons and extracting their dependencies
    jsons = {}
    deps = {}
    load_json_and_build_deps(json_files, deps, jsons)

    build_nodes(jsons, deps)

    # find all of the typedef'd enums and group them by package
    packages = {}
    for node in NODETAB.values():
        if node.children[0].kind == "enum":
            package_name = find_package_name(node)
            packages.setdefault(package_name, []).append(node)

    # find the root node and process it
    root = find_node(args_root)
    return codegen.process_root(root, devnodes, nodetype)


def build_nodes(jsons, deps):
    doneset = set()
    while len(jsons) > 0:

        # find a fulfillable json
        jsname = find_usable_json(jsons, deps, doneset)

        if jsname is None:
            raise RuntimeError("Failed to satisfy all dependencies")

        print "Parsing %s" % jsname

        # move it from todo to done
        js = jsons[jsname]
        del jsons[jsname]
        doneset.add(js["name"])

        # make a root node without a parent
        root = mknode(None, js)


def load_json_and_build_deps(json_files, deps, jsons):
    for arg in json_files:
        with open(arg) as fp:
            js = json.load(fp)
        jsons[arg] = js
        ds = set([l[0] for l in js["deps"]])  # first of each dep list
        deps[arg] = ds


if __name__ == "__main__":
    get_device_table()
