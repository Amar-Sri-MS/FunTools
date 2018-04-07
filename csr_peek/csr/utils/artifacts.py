#
#  artifacts.py
#
#  Created by Hariharan Thantry on 2018-02-22
#
#  Copyright 2018 Fungible Inc. All rights reserved.
#
# Process the address map

import collections
import os
import jinja2
import pdb
import re

class TmplMgr(object):
    def __init__(self, tpl_path):
        path, filename = os.path.split(tpl_path)
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(path or './'))
        self.tmpl = env.get_template(filename)
        print filename
    def write_cfg(self, out_file, obj):
        print out_file
        #print obj
        with open (out_file, 'w') as fh:
            #fh.write(self.tmpl.render(gen_obj=obj))
            fh.write(obj.__str__())
        fh.close()

# For every top level ring, one RingNode object
class RingNode(object):
    def __init__(self, name):
        self.name = name
        self.instances = collections.OrderedDict()

    def add_instance(self, inst_num, addr):
        assert inst_num not in self.instances
        self.instances[inst_num] = RingProps(self.name, inst_num, addr)

    def add_an_path(self, inst_num, an_path, n_inst, start_addr, skip_addr):
        r_props = self.instances.get(inst_num, None)
        assert r_props != None
        r_props.add_an_path(an_path, n_inst, start_addr, skip_addr)

    def add_an(self, inst_num, an, an_addr, csr_map):
        assert inst_num in self.instances
        self.instances[inst_num].add_an(an, an_addr, csr_map)

    def add_csr(self, inst_num, csr_name, csr_addr, csr_range=None):
        assert inst_num in self.instances
        self.instances[inst_num].add_csr(csr_name, csr_addr, csr_range)

    def get_instances(self):
        return self.instances

    def __str__(self):
        r_str = "ring_coll_t {}_rng;\n".format(self.name)
        for m_id, m_node in self.instances.iteritems():
            r_str += "{}_rng.add_ring({}, 0x{:01X});\n".\
                    format(self.name, m_id, m_node.get_addr())
            r_str += "{}".format(m_node)
        return r_str
    __repr__ = __str__

class CSRNode(object):
    def __init__(self, addr, addr_range=0):
        self.addr = addr
        self.addr_range = addr_range

    def get_addr(self):
        return self.addr

    def get_addr_range(self):
        return self.addr_range

    def __str__(self):
        r_str = ""
        r_str += "{} {}".\
                format(hex(self.addr), hex(self.addr_range))
        return r_str
    __repr__ = __str__

class ANode(object):
    def __init__(self, path, start_addr, n_inst=1, skip_addr=0):
        self.path = path
        self.start_addr = start_addr
        self.n_inst = n_inst
        self.skip_addr = skip_addr
        self.csrs = collections.OrderedDict()

    def add_csr(self, csr_name, addr, addr_range=None):
        csr_arr = re.split(r'_', csr_name)
        if csr_arr[-1].isdigit():
            csr_name = '_'.join(elem for elem in csr_arr[:-1])
        csr_lst = self.csrs.get(csr_name, None)
        addr -= self.start_addr
        p = CSRNode(addr, addr_range)
        if not csr_lst:
            csr_lst = [p, 1]
        else:
            csr_lst[1] += 1;
        #print "NAG ANode ADD_CSR:{}:NAG{}".format(self.path, csr_name)
        self.csrs[csr_name] = csr_lst

    def get_csr(self, csr_name):
        return self.csrs[csr_name]

    def get_start_addr(self):
        return self.start_addr

    def get_n_inst(self):
        return self.n_inst

    def get_skip_addr(self):
        return self.skip_addr

    def get_num_csr(self, csr_name):
        csr_arr = re.split(r'_', csr_name)
        if csr_arr[-1].isdigit():
            csr_name = '_'.join(elem for elem in csr_arr[:-1])
        p = self.csrs.get(csr_name, None)
        if p == None:
            print "WARNING: ADDR_FOR:{} not found in {}".format(csr_name, self.path)
            return 1
        return p[1]
    def get_csr_addr(self, csr_name):
        csr_arr = re.split(r'_', csr_name)
        if csr_arr[-1].isdigit():
            csr_name = '_'.join(elem for elem in csr_arr[:-1])

        p = self.csrs.get(csr_name, None)
        if p == None:
            print "WARNING: ADDR_FOR:{} not found in {}".format(csr_name, self.path)
            return 0

        return p[0].addr


    def get_path_str(self):
        path_arr = self.path.split('.')
        r_str = ""

        for elem in path_arr[:-1]:
            r_str += "\"{}\",".format(elem)

        r_str += "\"{}\"".format(path_arr[-1])
        return r_str
        return ','.join(str(elem) for elem in path_arr)

    def __str__(self):
        r_str = ""
        r_str += "{}, 0x{:02X}, {}, 0x{:02X}".format(self.path,
                self.start_addr, self.n_inst, self.skip_addr)
        return r_str
    __repr__ = __str__

class RingProps(object):
    def __init__(self, r_name, i_num, addr):
        self.r_name = r_name
        self.i_num = i_num
        self.addr = addr;
        self.last_aname = None
        self.root_paths = collections.OrderedDict()
        self.anodes = collections.OrderedDict()
        # From an aname to csr signature
        self.csr_map = collections.OrderedDict()
    def get_addr(self):
        return self.addr

    def add_an_path(self, path, n_inst, start_addr, skip_addr):
        assert path not in self.root_paths
        print "RingProps.add_an_path {} n_inst:{} start_addr:{}".format(path, n_inst, start_addr)
        self.root_paths[path] = [n_inst, start_addr, skip_addr]

    def get_an_paths(self, path):
        return self.root_paths[path]

    def get_an(self, an_name):
        print an_name
        #print self.anodes.keys()
        return self.anodes[an_name]

    def get_csr_prop(self, an_name, csr_name):
        an_csrs = self.csr_map.get(an_name, None)
        print "AN: {} csr_name: {} CSRs".format(an_name, csr_name)
        #print type(an_csrs)
        #for key, val in an_csrs.get().iteritems():
        #    print key
        csr_prop = an_csrs.get()[csr_name]
        if csr_prop == None:
            sys.exit(1)
        return csr_prop

    def add_an(self, an_node, addr, csr_map):
        # First determine if this is a root node AN
        r_attr = self.root_paths.get(an_node, None)

        an_arr = an_node.split('.')
        prefix_path = None
        if len(an_arr) > 1:
            prefix_path = '.'.join(elem for elem in an_arr[:-1])
            an_name = an_arr[-1]
        else:
            an_name = an_node

        print an_name
        self.csr_map[an_name] = csr_map.get(an_name, collections.OrderedDict())

        anode = None
        addr -= self.addr
        if r_attr != None:
            anode = ANode(an_node, addr, r_attr[0], r_attr[2])
        elif prefix_path:
            r_attr = self.root_paths.get(prefix_path, None)
            if (r_attr != None):
                anode = ANode(an_node, addr, r_attr[0], r_attr[2])
            else:
                anode = ANode(an_node, addr)
        else:
            anode = ANode(an_node, addr)

        an_lst = self.anodes.get(an_name, [])
        an_lst.append(anode)

        print "AN_CREATE:{}:{}".format(an_name, anode)
        self.anodes[an_name] = an_lst
        self.last_anode = anode

    def add_csr(self, csr_name, csr_addr, addr_range=None):
        assert self.last_anode != None, "No address node to add CSR to"
        csr_addr -= self.addr
        self.last_anode.add_csr(csr_name, csr_addr, addr_range)

    def __str__(self):
        r_str = ""
        for an_name, an_lst in self.anodes.iteritems():
            for idx, elem in enumerate(an_lst):
                #print "PATH={}".format(elem.get_path_str())
                #print "SA={}".format(elem.start_addr)
                #print "NINST={}".format(elem.n_inst)
                #print "SKIP_ADDR={}".format(elem.skip_addr)

                print "AN: {}".format(an_name)
                an_csrs = self.csr_map.get(an_name, None)
                if an_csrs != None:
                    r_str += "{{\n // BEGIN {} \n".format(an_name)
                    r_str += "auto {}_{} = {}_rng[{}].add_an({{{}}}, 0x{:01X}, {}, 0x{:01X});\n".\
                        format(an_name, idx, self.r_name, self.i_num,
                                elem.get_path_str(), elem.start_addr, elem.n_inst, elem.skip_addr);
                    for csr_name, csr_val in an_csrs.get().iteritems():
                        r_str += "fld_map_t {} {{\n".format(csr_name)
                        off = 0
                        for fldd in csr_val.fld_lst[:-1]:
                            r_str += "CREATE_ENTRY(\"{}\", {}, {}),\n".\
                                    format(fldd.fld_name, off, fldd.width)
                            off += fldd.width
                        fldd = csr_val.fld_lst[-1]
                        r_str += "CREATE_ENTRY(\"{}\", {}, {})\n".\
                                format(fldd.fld_name, off, fldd.width)

                        r_str += "};"
                        r_str += "auto {}_prop = csr_prop_t(\n".format(csr_name)
                        r_str += "std::make_shared<csr_s>({}),\n".format(csr_name)
                        r_str += "0x{:01X},\n".format(elem.get_csr_addr(csr_name))
                        r_str += "{},\n".format(csr_val.type)
                        r_str += "{});\n".format(elem.get_num_csr(csr_name))
                        r_str += "add_csr({}_{}, \"{}\", {}_prop);\n".\
                                 format(an_name, idx, csr_name, csr_name)

                    r_str += " // END {} \n}}\n".format(an_name)
        return r_str

    __repr__ = __str__


class CSRMetaData(object):
    def __init__(self, rname, rinst, ring_addr, an, an_addr, reg_addr, reg_n_inst, reg_data):
        self.ring_name = rname
        self.ring_inst = rinst
        self.ring_addr = ring_addr
        self.an = an
        self.an_addr = an_addr
        self.reg_addr = reg_addr
        self.reg_n_inst = reg_n_inst
        self.reg_data = reg_data

    def get_an_base_addr(self):
        return self.ring_addr + self.an_addr

    def get_csr_data(self):
        return self.reg_data

    def get_reg_n_inst(self):
        return self.reg_n_inst

    def __str__(self):
        str = "RING: {}, RING_INST: {}, RING_ADDR: {} ".format(
                self.ring_name, self.ring_inst, hex(self.ring_addr))
        str += "AN: {} AN_ADDR: {} ".format(self.an, hex(self.an_addr))
        str += "REG_ADDR: {} REG_N_INST: {}, REG_DATA: {}".format(
                hex(self.reg_addr), self.reg_n_inst, self.reg_data)
        return str
    __repr__ = __str__

class CSRRoot(object):
    START_RING = r'START_RING'
    END_RING = r'END_RING'
    IGNORE = [r'^ROOT:', r'^ROR:', r'^ActSize:', r'^LEAF:', r'^##-INFO-:', r'^AN:', r'New EA:', r'INST\[']
    RING_DONE = 0
    RING_PROCESS = 1
    IN_RING = 2
    IN_ANODE = 3
    CSR_FLAG =4
    MAX_FLAGS=5

    def __init__(self, amap_file, csr_map, ring_match=None):
        self.flags = [False]*CSRRoot.MAX_FLAGS
        self.r_util = RingUtil()
        #self.curr_an_path = None
        #self.curr_an = None
        #self.csr_metadata  = collections.OrderedDict()
        self.csr_map = csr_map
        print "Print csr_map start"
        #print self.csr_map
        print "Print csr_map end"
        self.ring_map = collections.OrderedDict()
        print "Print ring_map start"
        #print self.ring_map
        print "Print ring_map done"
        self.__read_update(amap_file, ring_match)

    def get_map(self):
        return self.ring_map

    def __read_update(self, m_file, ring_match):
        f = open(m_file, "r")
        for line in f:
            line = line.lstrip()
            #print "LINE:{}".format(line)
            if self.__ignore(line):
                #print "IGNORE: {}".format(line)
                continue
            if self.__process_ring(line, ring_match):
                #print ("RING " + line)
                continue
            if self.__process_root(line, ring_match):
                #print ("ROOT " + line)
                continue
            if self.__process_anode(line, ring_match):
                #print ("ANODE " + line)
                continue
            self.__process_csr(line)
        #print "Print ring_map after read"
        #print self.ring_map

    def __ignore(self, line):
        for rep in CSRRoot.IGNORE:
            if re.search(rep, line):
                return True
        return False

    def __process_ring(self, line, ring_match):
        if self.flags[CSRRoot.RING_DONE]:
            return False
        if not self.flags[CSRRoot.IN_RING]:
            if re.search(CSRRoot.START_RING, line):
                self.flags[CSRRoot.IN_RING] = True
                return True
        if re.search(CSRRoot.END_RING, line):
            self.flags[CSRRoot.RING_DONE] = True
            return True

        l_arr = line.split(':')
        if len(l_arr) < 2:
            return True

        #print l_arr
        ring_class, ring_inst = self.r_util.get_info(l_arr[0])
        print ring_class
        print ring_inst
        if not re.search(ring_match.lower(), ring_class.lower()):
            return True

        self.__add_ring_instance(ring_class, ring_inst, self.__hexlify(l_arr[1]))
        print "RING_ACCEPT: {}".format(line)
        return True
    def __add_ring_instance(self, ring_class, ring_inst, addr):
        ring_node = self.ring_map.get(ring_class, RingNode(ring_class))
        ring_node.add_instance(ring_inst, addr)
        self.ring_map[ring_class] = ring_node
        return ring_node

    def __process_root(self, line, ring_match):
        if not re.search('^COUNT', line):
            return False
        print "Processing ROOT {}".format(line)
        coll = line.split(':')
        print coll
        m_arr = coll[1].split('.')
        print m_arr
        ring_class, ring_inst = self.r_util.get_info(m_arr[0])
        print ring_class
        print ring_inst

        k = self.__clean_name(m_arr[1:])
        print k
        if not re.search(ring_match.lower(), ring_class.lower()):
            self.flags[CSRRoot.RING_PROCESS] = False
            return True
        else:
            self.flags[CSRRoot.RING_PROCESS] = True
        print "NAG ROOT_ACCEPT:{}".format(line)
        rn = self.ring_map.get(ring_class, None)
        if rn == None:
           print "Adding dummy ring class: {}".format(ring_class)
           rn = self.__add_ring_instance(ring_class, ring_inst, 0)

        self.flags[CSRRoot.IN_ANODE] = False
        print ring_inst
        print "K.{}".format(k)
        print coll[2]
        print coll[3]
        print coll[4]
        rn.add_an_path(ring_inst, k, int(coll[2]),
                self.__hexlify(coll[3]), self.__hexlify(coll[4]))
        return True

    def __process_anode(self, line, ring_match):
        if not re.search('^START_ANODE', line):
            return False
        line = line.lower()

        coll = line.split(':')
        m_arr = coll[1].split('.')
        ring_class, ring_inst = self.r_util.get_info(m_arr[0])
        if not re.search(ring_match.lower(), ring_class.lower()):
            self.flags[CSRRoot.RING_PROCESS] = False
            return True
        else:
            self.flags[CSRRoot.RING_PROCESS] = True
        print "ANODE_ACCEPT:{}".format(line)
        k = self.__clean_name(m_arr[1:])
        rn = self.ring_map.get(ring_class, None)
        if rn == None:
           print "Adding dummy ring class: {}".format(ring_class)
           rn = self.__add_ring_instance(ring_class, ring_inst, 0)

        assert rn != None, "Unknown ring class"
        self.flags[CSRRoot.IN_ANODE] = True
        #self.curr_rn_class = ring_class
        self.curr_rn = rn
        self.curr_ri = ring_inst
        #self.curr_an = k

        addr = self.__hexlify(coll[2])
        print "ADD_AN: {}:***{}***:0x{:02X}".format(ring_inst, k, addr)

        rn.add_an(ring_inst, k, addr, self.csr_map)
        return True

    def __process_csr(self, line):
        if not self.flags[CSRRoot.IN_ANODE]:
            return
        if not self.flags[CSRRoot.RING_PROCESS]:
            return
        if not line:
            return
        coll  = line.split(':')
        if len(coll) < 2:
            return

        ex_coll = coll[1].split()
        if len(ex_coll) > 2:
            return

        #print "CSR_ACCEPT: {}".format(line)
        cname =  coll[0].strip()
        addr = 0
        addr_range = 0
        if len(ex_coll) > 1:
            addr = self.__hexlify(ex_coll[0].strip())
            addr_range = self.__hexlify(ex_coll[1].strip())
        else:
            addr = self.__hexlify(coll[1].strip())
        self.curr_rn.add_csr(self.curr_ri, cname, addr, addr_range)
        #self.__add_csr_metadata(cname, addr, addr_range)

    """
    def __add_csr_metadata(self, name, addr, addr_range):
        mdata = self.csr_metadata.get(name, [])
        if not mdata:
            self.csr_metadata[name] = mdata
        mdata.append(CSRMetaData(self.curr_rn_class, self.curr_ri,
                                         self.curr_an))
    """

    def __clean_name(self, m_arr):
        for idx, _ in enumerate(m_arr):
            m_arr[idx] = re.sub('(_an)|(_AN)', '', m_arr[idx])

        k = ".".join(elem for elem in m_arr)
        return k

    def __hexlify(self, entry):
        entry = re.sub(r'0x', '', entry)
        entry = re.sub(r'_', '', entry)
        val = int(entry, 16)
        return val

    def csr_metadata_print(self):
        for k,v in self.csr_metadata.iteritems():
            str = ""
            for c in v:
                str += "\t" + c.print_metadata() + "\n"
            print "KEY: {}\n{}\n\n".format(k, str)

    def get_csr_metadata(self, csr_name, rn_class, rn_inst, an_path, an, an_inst):
        #v = self.csr_metadata[csr_name]
        #str = ""
        #for c in v:
        #    str += "\t" + c.print_metadata() + "\n"

        rn = self.ring_map.get(rn_class, None)
        rn_props = rn.get_instances()
        if len(rn_props) > 1:
            if rn_inst == None:
                print "There are {} instances of {}! Add inst info!".format(len(rn_props), rn_class)
                #print rn_props.keys()
                sys.exit(1)
            else:
                rn_prop = rn_props[rn_inst]
                #print rn_prop
        else:
            rn_prop = rn_props[0]
            #print rn_prop

        print "CSR: {} RN:{} INST:{} AN_PATH: {} AN: {} AN_INST:{}".format(csr_name, rn_class, rn_inst, an_path, an, an_inst)
        an_lst = rn_prop.get_an(an)
        if len(an_lst) > 1:
            if an_inst != None:
                anode = an_lst[an_inst]
            else:
                print "There are {} instances of {}! Add an inst info!".format(len(an_lst), anode)
                print an_lst
                sys.exit(1)
        else:
            anode = an_lst[0]

        ring_addr = rn_prop.get_addr()
        start_addr = anode.get_start_addr()
        inst_cnt = anode.get_n_inst()
        skip_addr = anode.get_skip_addr()

        print "AN: {} RING ADDR: {} AN_ADDR: 0x{} INST_CNT: {} SKIP_ADDR: 0x{}".format(an, hex(ring_addr), hex(start_addr), inst_cnt, hex(skip_addr))

        n_inst = anode.get_n_inst()
        if n_inst > 1:
            if an_inst == None:
                print "There are {} instances of {}! Add AN inst info!".format(n_inst, an)
            else:
                rn_prop = rn_props[rn_inst]
        else:
            rn_prop = rn_props[0]

        csr_addr = anode.get_csr_addr(csr_name)
        num_csr = anode.get_num_csr(csr_name)

        csr_data = rn_prop.get_csr_prop(an, csr_name)
        off = 0
        for fldd in csr_data.fld_lst[:-1]:
            print "Field: {} Width: {} offset: {}".format(fldd.fld_name, off, fldd.width)
            off += fldd.width

        return CSRMetaData(rn_class, rn_inst, ring_addr,
                           an, start_addr, csr_addr, num_csr, csr_data)


    def __str__(self):
        r_str = ""
        for name, node in self.ring_map.iteritems():
            r_str += "{}".format(node)
            r_str += "sys_rings[\"{}\"] = {}_rng;\n".format(name.upper(), name)
        return r_str


    __repr__ = __str__


class RingUtil(object):
    RING_ENC = r'([\w]+)_([\d])+'
    ALT_RING_ENC = r'([\w]+)([\d]+)'
    def __init__(self):
        pass

    def get_info(self, nodename):
        r_grp = re.match(RingUtil.RING_ENC, nodename)
        if not r_grp:
            r_grp = re.match(RingUtil.ALT_RING_ENC, nodename)
        if r_grp:
           ring_class = r_grp.group(1)
           ring_inst = int(r_grp.group(2))
        else:
           ring_class = nodename
           ring_inst = 0
        return ring_class, ring_inst


class Walker(object):
    def __init__(self, ring_tree):
        self.m_lst = []
        for val in self.__flatten(ring_tree):
            self.m_lst.append(val)

    def __flatten(self, yml_obj, pre=None):
        pre = pre[:] if pre else []
        if isinstance(yml_obj, dict):
            for key, val in yml_obj.items():
                if isinstance(val, dict):
                    for d in self.__flatten(val, pre + [key]):
                        yield d
                elif isinstance(val, list) or isinstance(val, tuple):
                    for v in val:
                        for d in self.__flatten(v, pre + [key]):
                            yield d
                else:
                    yield pre + [key, val]
        else:
            yield pre + [yml_obj]

    def get_ans(self):
        return self.m_lst

    def __str__(self):
        r_str = ""
        for elem in self.m_lst:
            r_str += "{}\n".format(elem)
        return r_str
    __repr__ = __str__


