#
#  artifacts.py
#
#  Created by Hariharan Thantry on 2018-02-22
#
#  Copyright 2018 Fungible Inc. All rights reserved.
#
# Process the address map

import collections
import jinja2
import logging
import os
import pdb
import re
import sys

class ANUtils(object):
    def __init__(self, logger=None):
        pass
    def get_an(self, an_path):
        an_arr = an_path.split('.')
        prefix_path = None
        if len(an_arr) > 1:
            prefix_path = '.'.join(elem for elem in an_arr[:-1])
            an_name = an_arr[-1]
        else:
            an_name = an_path
        return prefix_path, an_name

class TmplMgr(object):
    def __init__(self, tpl_path):
        path, filename = os.path.split(tpl_path)
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(path or './'))
        self.tmpl = env.get_template(filename)

    def write_cfg(self, out_file, obj):
        with open (out_file, 'w') as fh:
            fh.write(self.tmpl.render(gen_obj=obj))
        fh.close()

# For every top level ring, one RingNode object
class RingNode(object):
    def __init__(self, name, is_dummy=False):
        self.name = name
        self.is_dummy = is_dummy
        self.instances = collections.OrderedDict()

    def add_instance(self, inst_num, addr):
        assert inst_num not in self.instances
        self.instances[inst_num] = RingProps(self.name, inst_num, addr)

    def add_an_path(self, inst_num, an_path, n_inst, start_addr, skip_addr):
        r_props = self.instances.get(inst_num, None)
        assert r_props != None
        r_props.add_an_path(an_path, n_inst, start_addr, skip_addr)

    def get_an_path(self, inst_num, an_path):
        r_props = self.instances.get(inst_num, None)
        assert r_props != None
        return r_props.get_an_path(an_path)


    def add_an(self, inst_num, an, an_addr, csr_map):
        assert inst_num in self.instances
        self.instances[inst_num].add_an(an, an_addr, csr_map)

    def add_csr(self, inst_num, csr_name, csr_addr, csr_range=None):
        assert inst_num in self.instances
        self.instances[inst_num].add_csr(csr_name, csr_addr, csr_range)

    def add_64_w(self, inst_num, an_name, num_64_w):
        assert inst_num in self.instances
        if not self.is_dummy:
            self.instances[inst_num].add_64_w(an_name, num_64_w)

    def get_instances(self):
        return self.instances

    def __str__(self):
        r_str = "ring_coll_t {}_rng;\n".format(self.name)
        for m_id, m_node in self.instances.items():
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
                format(self.addr, self.addr_range)
        return r_str
    __repr__ = __str__

class ANode(object):
    def __init__(self, path, start_addr, csr_map, n_inst=1, skip_addr=0, logger=None):
        self.path = path
        self.start_addr = start_addr
        self.n_inst = n_inst
        self.skip_addr = skip_addr
        self.csr_map = csr_map
        self.csrs = collections.OrderedDict()
        self.logger = logger or logging.getLogger(__name__)

    def add_csr(self, csr_name, addr, addr_range=None):
        csr_lst = self.csrs.get(csr_name, None)
        if csr_lst:
            return
        addr -= self.start_addr
        csr_attr = self.csr_map.get().get(csr_name, None)
        if not csr_attr:
            # This could be because of the exclusion filters
            return
        n_entries  = (csr_attr.n_entries * csr_attr.count)
        p = CSRNode(addr, addr_range)
        csr_lst = [p, n_entries]
        self.csrs[csr_name] = csr_lst
        self.logger.debug("ANode AN_PATH:{}: CSR_NAME{}".format(self.path, csr_name))

    def get_csr(self, csr_name):
        return self.csrs[csr_name]

    def get_start_addr(self):
        return self.start_addr

    def get_n_inst(self):
        return self.n_inst

    def get_skip_addr(self):
        return self.skip_addr

    def get_num_csr(self, csr_name):
        p = self.csrs.get(csr_name, None)
        if p == None:
            for k, v in self.csrs.items():
                self.logger.debug("{}:{}".format(k, v))
            self.logger.warning("NINSTANCE_NOT_FOUND_FOR:{} not found in {}".format(csr_name, self.path))
            return 1
        return p[1]
    def get_csr_addr(self, csr_name):

        p = self.csrs.get(csr_name, None)
        if p == None:
            self.logger.warning("ADDR_FOR:{} not found in {}".format(csr_name, self.path))
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
    Total64w = 0
    def __init__(self, r_name, i_num, addr, logger=None):
        self.r_name = r_name
        self.i_num = i_num
        self.addr = addr;
        self.last_aname = None
        self.root_paths = collections.OrderedDict()
        self.anodes = collections.OrderedDict()
        self.logger = logger or logging.getLogger(__name__)

    def get_addr(self):
        return self.addr

    def add_an_path(self, path, n_inst, start_addr, skip_addr):
        assert path not in self.root_paths
        self.logger.debug("RingProps ADD an_path {} n_inst:{}"
               "start_addr:{}".format(path, n_inst, start_addr))
        self.root_paths[path] = [n_inst, start_addr, skip_addr]

    def get_an_path(self, path):
        return self.root_paths.get(path, None)

    def get_an(self, an_name):
        return self.anodes[an_name]

    # Get the properties of CSR from csr_map
    def get_csr_prop(self, an_name, csr_name):
        an_csrs = self.csr_map.get(an_name, None)
        self.logger.debug("AN: {} csr_name: {} CSRs".format(an_name, csr_name))
        csr_prop = an_csrs.get().get(csr_name, None)
        if csr_prop == None:
            self.logger.warning("!WARNING! Could not find CSR in csr_map.")


        return csr_prop

    # The CSR attribute map is for csrs local to this anode
    def add_an(self, an_node, addr, csr_map):
        # First determine if this is a root node AN
        r_attr = self.root_paths.get(an_node, None)
        prefix_path, an_name = ANUtils().get_an(an_node)

        anode = None
        addr -= self.addr
        if r_attr != None:
            anode = ANode(an_node, addr, csr_map, r_attr[0], r_attr[2])
        elif prefix_path:
            r_attr = self.root_paths.get(prefix_path, None)
            if (r_attr != None):
                anode = ANode(an_node, addr, csr_map, r_attr[0], r_attr[2])
            else:
                anode = ANode(an_node, addr, csr_map)
        else:
            anode = ANode(an_node, addr, csr_map)

        an_lst = self.anodes.get(an_name, [])
        an_lst.append(anode)

        self.logger.debug("AN_CREATE:{}:{}".format(an_name, anode))
        self.anodes[an_name] = an_lst
        self.last_anode = anode
    def add_64_w(self, an_node, num_64_w):
        r_attr = self.root_paths.get(an_node, None)
        an_arr = an_node.split('.')
        prefix_path = None
        if len(an_arr) > 1:
            prefix_path = '.'.join(elem for elem in an_arr[:-1])
            an_name = an_arr[-1]
        else:
            an_name = an_node
        if r_attr != None:
            RingProps.Total64w = RingProps.Total64w + (r_attr[0] * num_64_w)
        elif prefix_path:
            r_attr = self.root_paths.get(prefix_path, None)
            if r_attr != None:
                RingProps.Total64w = RingProps.Total64w + (r_attr[0] * num_64_w)
            else:
                RingProps.Total64w = RingProps.Total64w + num_64_w
        else:
            RingProps.Total64w = RingProps.Total64w + num_64_w

        self.logger.debug("0x{:02X}".format(RingProps.Total64w))


    def add_csr(self, csr_name, csr_addr, addr_range=None):
        assert self.last_anode != None, "No address node to add CSR to"
        csr_addr -= self.addr

        self.last_anode.add_csr(csr_name, csr_addr, addr_range)

    def __str__(self):
        r_str = ""
        for an_name, an_lst in self.anodes.items():
            for idx, elem in enumerate(an_lst):

                an_csrs = elem.csr_map
                if an_csrs != None:
                    if len(list(an_csrs.get().keys())) == 0:
                        continue
                    r_str += "#pragma message \"Compiling: AN: {}\"\n".format(an_name)
                    r_str += "{{\n // BEGIN {} \n".format(an_name)
                    r_str += "addr_node_t* {}_{} = {}_rng[{}].add_an({{{}}}, 0x{:01X}, {}, 0x{:01X});\n".\
                        format(an_name, idx, self.r_name, self.i_num,
                                elem.get_path_str(), elem.start_addr, elem.n_inst, elem.skip_addr);
                    colls = {}
                    for csr_name, csr_val in an_csrs.get().items():
                        if csr_val.name in colls:
                            continue
                        r_str += "fld_map_t {};\n".format(csr_val.name)
                        off = 0
                        for fldd in csr_val.fld_lst:
                            r_str += "ADD_ENTRY({}, \"{}\", {}, {});\n".\
                                    format(csr_val.name, fldd.fld_name, off, fldd.width)
                            off += fldd.width
                        r_str += "auto {}_sp = new csr_s({});\n".\
                                format(csr_val.name, csr_val.name)
                        r_str += "csr_prop_t {}_prop {{\n".format(csr_val.name)
                        r_str += "{}_sp,\n".format(csr_val.name)
                        r_str += "0x{:01X},\n".format(elem.get_csr_addr(csr_name))
                        #r_str += "{},\n".format(csr_val.type)
                        r_str += "{}}};\n".format(elem.get_num_csr(csr_name))
                        r_str += "add_csr({}_{}, \"{}\", {}_prop);\n".\
                                 format(an_name, idx, csr_val.name, csr_val.name)
                        colls[csr_val.name] = True

                    r_str += " // END {} \n}}\n".format(an_name)
        return r_str

    __repr__ = __str__


class CSRMetaData(object):
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.metadata = collections.OrderedDict()

    def add_csr_metadata(self, ring_name, ring_inst, ring_addr,
                        an, an_path, an_inst_cnt, an_skip_addr,
                        an_addr, csr_name, csr_addr,
                        csr_addr_range, csr_prop):
        if csr_prop.type == "CSR_TYPE::REG_LST":
            m_name = csr_name.split('_')
            inst_str = m_name[-1]
            if inst_str.isdigit():
                if int(inst_str) > 0:
                    self.logger.debug("Skipping {}".format(csr_name))
                    return
                lst = m_name[:-1]
            else:
                self.logger.warning("ERROR!!! CSR:{} REG_LST should end with a"
                      "digit!".format(csr_name))
                sys.exit(1)
            csr_name = '_'.join(elem for elem in lst)
        self.logger.debug("ADD csr {}".format(csr_name))
        csr_metadata_lst = self.metadata.get(csr_name, [])

        csr_metadata = dict()
        csr_metadata["ring_name"] = ring_name
        csr_metadata["ring_inst"] = ring_inst
        csr_metadata["ring_addr"] = hex(ring_addr)
        csr_metadata["an"] = an
        csr_metadata["an_path"] = an_path
        csr_metadata["an_inst_cnt"] = an_inst_cnt
        csr_metadata["an_skip_addr"] = hex(an_skip_addr)
        csr_metadata["an_addr"] = hex(an_addr)
        csr_metadata["csr_addr"] = hex(csr_addr)
        csr_metadata["csr_count"] = csr_prop.count
        csr_metadata["csr_addr_range"] = csr_addr_range
        csr_metadata["csr_type"] = csr_prop.type
        csr_metadata["csr_n_entries"] = csr_prop.n_entries
        csr_metadata["csr_width"] = csr_prop.width
        csr_metadata["csr_stride_width"] = csr_prop.stride_width
        csr_metadata["csr_inst_size"] = csr_prop.inst_size

        fld_lst = list()
        offset = 0;
        csr_width_64bit = (csr_prop.width + 63) & ~0x3f
        for fld in csr_prop.fld_lst:
            offset += fld.width
            fld_prop = {"fld_name": fld.fld_name,
                        "fld_width": fld.width,
                        "fld_offset": csr_width_64bit - offset}
            fld_lst.append(fld_prop)
        csr_metadata["fld_lst"] = fld_lst
        csr_metadata_lst.append(csr_metadata)
        self.metadata[csr_name] = csr_metadata_lst

    def get_csr_metadata(self):
        return self.metadata


    def __str__(self):
        r_str = ""
        for csr_name, csr_lst in self.metadata.items():
            r_str += "NAME:{}\n".format(csr_name)
            for idx, csr_prop in enumerate(csr_lst):
                r_str += "[{}]: {}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}\n".\
                        format(idx,
                                csr_prop["ring_name"],
                                csr_prop["ring_inst"],
                                csr_prop["ring_addr"],
                                csr_prop["an_path"],
                                csr_prop["an_inst_cnt"],
                                csr_prop["an_addr"],
                                csr_prop["an_skip_addr"],
                                csr_prop["csr_addr"],
                                csr_prop["csr_count"],
                                csr_prop["csr_addr_range"],
                                csr_prop["csr_type"],
                                csr_prop["csr_n_entries"],
                                csr_prop["csr_width"],
                                csr_prop["csr_stride_width"],
                                csr_prop["csr_inst_size"]
                              )
                for r_idx, fldd in enumerate(csr_prop["fld_lst"]):
                    r_str += "    [{}]:{}:{}\n".format(r_idx, fldd["fld_name"], fldd["fld_width"])
            r_str += "\n"
        return r_str






class CSRRoot(object):
    START_RING = 'START_RING'
    END_RING = 'END_RING'
    IGNORE = ['ROOT:', 'ROR:', 'ActSize:', 'LEAF:', '##-INFO-:', 'AN:']
    IGNORE_REGEX = ['New EA:', 'INST\[']
    RING_DONE = 0
    RING_PROCESS = 1
    IN_RING = 2
    IN_ANODE = 3
    CSR_FLAG =4
    MAX_FLAGS=5

    def __init__(self, amap_file, csr_map, filter_yml, logger=None):
        self.flags = [False]*CSRRoot.MAX_FLAGS
        self.logger = logger or logging.getlogger(__name__)
        self.r_util = RingUtil(self.logger)
        curr_ring = None
        curr_inst = None
        self.curr_an_name = None
        self.csr_map = csr_map
        self.csr_metadata = CSRMetaData(self.logger)
        self.ring_map = collections.OrderedDict()
        self.start_addr = 0xFFFFFFFFFF
        self.end_addr = 0
        self.__read_update(amap_file, filter_yml)
        self.ring_exclude = collections.OrderedDict()

    def get_map(self):
        return self.ring_map

    def __read_update(self, m_file, filter_yml):
        f = open(m_file, "r")
        skip = False
        for line in f:
            line = line.lstrip()
            self.logger.debug("LINE:{}".format(line))
            if self.__ignore(line):
                self.logger.debug("IGNORE: {}".format(line))
                if line.startswith('##-INFO-:'):
                    skip = True
                continue
            if self.__process_ring(line):
                continue
            if self.__process_root(line):
                continue
            if self.__process_anode(line):
                do_process = self.__filter(line, filter_yml)
                self.an_added = False
                skip = False
                continue
            if skip:
                self.logger.debug("IGNORE: {}".format(line))
                continue
            self.__process_csr(line, do_process, filter_yml)

        self.logger.info("ADDR_RANGE: 0x{:02X}->0x{:02X}".format(self.start_addr, self.end_addr))
        self.logger.info("Total64w: 0x{:02X}".format(RingProps.Total64w))

    def __ignore(self, line):
        for rep in CSRRoot.IGNORE:
            if line.startswith(rep):
                return True
        for rep in CSRRoot.IGNORE_REGEX:
            if re.search(rep, line):
                return True
        return False

    def __match(self, regex_arr, m_elem):
        for elem in regex_arr:
            if re.match(elem, m_elem):
                return True

    def __filter(self, line, filter_yml):

        if not filter_yml:
            return True
        line = line.lower()
        coll = line.split(':')
        tree = coll[1].split('.')
        anode = tree[-1]
        process = False

        include_anodes = filter_yml.get('include_an', [])
        if self.__match(include_anodes, anode):
            self.logger.debug("ANODE_ACCEPT: {}".format(line))
            return True

        exclude_anodes = filter_yml.get('exclude_an', [])
        if self.__match(exclude_anodes, anode):
            self.logger.debug("ANODE_REJECT: {}".format(line))
            return False

        # The first element is always the ring
        interior = []
        if len(tree) > 2:
            interior = tree[1:-1]
        exclude_interior = filter_yml.get('exclude_interior', [])
        include_interior = filter_yml.get('include_interior', [])
        for s_elem in reversed(interior):
            if self.__match(include_interior, s_elem):
                self.logger.debug("INTERIOR_ACCEPT: {}".format(line))
                return True
            if self.__match(exclude_interior, s_elem):
                self.logger.debug("INTERIOR_REJECT: {}".format(line))
                return False

        include_ring = filter_yml.get('include_ring', [])
        if self.__match(include_ring, tree[0]):
            self.logger.debug("RING_ACCEPT: {}".format(line))
            return True

        exclude_ring = filter_yml.get('exclude_ring', [])
        if self.__match(exclude_ring, tree[0]):
            self.logger.debug("RING_REJECT: {}".format(line))
            return False

        self.logger.debug("DEFAULT_REJECT: {}".format(line))
        return False

    def __process_ring(self, line):

        if self.flags[CSRRoot.RING_DONE]:
            return False
        if not self.flags[CSRRoot.IN_RING]:
            if line.startswith(CSRRoot.START_RING):
                self.flags[CSRRoot.IN_RING] = True
                return True
        if line.startswith(CSRRoot.END_RING):
            self.flags[CSRRoot.RING_DONE] = True
            return True

        l_arr = line.split(':')
        if len(l_arr) < 2:
            return True

        ring_class, ring_inst = self.r_util.get_info(l_arr[0])
        self.__add_ring_instance(ring_class, ring_inst, self.__hexlify(l_arr[1]))
        self.logger.debug("RING_ACCEPT: {}".format(line))
        return True
    def __add_ring_instance(self, ring_class, ring_inst, addr, is_dummy=False):
        ring_node = self.ring_map.get(ring_class, RingNode(ring_class, is_dummy))
        ring_node.add_instance(ring_inst, addr)
        self.ring_map[ring_class] = ring_node
        return ring_node

    def __process_root(self, line):
        if not line.startswith('COUNT'):
            return False
        coll = line.split(':')
        m_arr = coll[1].split('.')
        ring_class, ring_inst = self.r_util.get_info(m_arr[0])

        k = self.__clean_name(m_arr[1:])
        self.logger.debug("ROOT_ACCEPT:{}".format(line))

        rn = self.ring_map.get(ring_class, None)
        if rn == None:
           self.logger.info("Adding dummy ring class: {}".format(ring_class))
           rn = self.__add_ring_instance(ring_class, ring_inst, 0, True)

        st_addr = self.__hexlify(coll[3])
        skip_val = self.__hexlify(coll[4])
        num_inst = int(coll[2])
        end_addr = st_addr + (num_inst - 1)*skip_val
        if st_addr < self.start_addr and not rn.is_dummy:
            self.logger.debug("NEW START: 0x{:02X}->0x{:02X}".format(self.start_addr, st_addr))
            self.start_addr = st_addr

        if end_addr > self.end_addr and not rn.is_dummy:
            self.logger.debug("NEW END: 0x{:02X}->0x{:02X}".format(self.end_addr, end_addr))
            self.end_addr = end_addr
        self.flags[CSRRoot.IN_ANODE] = False
        rn.add_an_path(ring_inst, k, num_inst,
                st_addr, skip_val)
        return True
    def __filter_csr(self, csr_name, do_process, filter_yml):
        if not filter_yml:
            return True
        include_csr = filter_yml.get('include_csr', [])
        if self.__match(include_csr, csr_name):
            self.logger.debug("CSR_ACCEPT: {}".format(csr_name))
            return True
        exclude_csr = filter_yml.get('exclude_csr', [])
        if self.__match(exclude_csr, csr_name):
            self.logger.debug("CSR_REJECT: {}".format(csr_name))
            return False
        return do_process

    def __process_anode(self, line):
        if not line.startswith('START_ANODE'):
            return False
        line = line.lower()
        coll = line.split(':')
        m_arr = coll[1].split('.')
        ring_class, ring_inst = self.r_util.get_info(m_arr[0])
        self.logger.debug("ANODE_ACCEPT:{}".format(line))
        k = self.__clean_name(m_arr[1:])
        an_name = k.split('.')[-1]
        rn = self.ring_map.get(ring_class, None)
        if rn == None:
           self.logger.info("Adding dummy ring class: {}".format(ring_class))
           rn = self.__add_ring_instance(ring_class, ring_inst, 0, True)

        assert rn != None, "Unknown ring class"
        self.flags[CSRRoot.IN_ANODE] = True
        self.curr_rn = rn
        self.curr_rc = ring_class
        self.curr_ri = ring_inst
        self.curr_path = k
        self.curr_an_name = an_name
        st_addr = self.__hexlify(coll[2])
        num_64_w = self.__hexlify(coll[3])
        end_addr = st_addr + num_64_w

        self.curr_addr = st_addr


        if st_addr < self.start_addr and not rn.is_dummy:
            self.logger.debug("NEW START: 0x{:02X}->0x{:02X}".format(self.start_addr, st_addr))
            self.start_addr = st_addr
        if end_addr > self.end_addr and not rn.is_dummy:
            self.logger.debug("NEW END: 0x{:02X}->0x{:02X}".format(self.end_addr, end_addr))
            self.end_addr = end_addr

        self.logger.debug("ADD_AN: {}:{}:0x{:02X}".format(ring_inst, k, st_addr))
        # Add number of 64w being added
        rn.add_64_w(ring_inst, k, num_64_w)
        return True

    def __process_csr(self, line, do_process, filter_yml):
        if not self.flags[CSRRoot.IN_ANODE]:
            return
        if not line:
            return
        coll  = line.split(':')
        if len(coll) < 2:
            return

        ex_coll = coll[1].split()
        if len(ex_coll) > 2:
            return

        csr_name = coll[0].strip()
        do_process = self.__filter_csr(csr_name,
                do_process,
                filter_yml)

        if not do_process:
            self.logger.debug("CSR_REJECT: {}".format(line))
            return
        # Accept CSRs by name, except for the attribute
        # specific stuff that will be removed elsewhere
        if not self.an_added:
            prefix_path, an_name = ANUtils(self.logger).get_an(self.curr_path)
            if not an_name in self.csr_map:
                self.logger.warning("ANode: {} not found in csr_map!".format(an_name))
                sys.exit(1)
            self.curr_rn.add_an(self.curr_ri, self.curr_path,\
                        self.curr_addr, self.csr_map.get(an_name, None))
            self.an_added = True
        self.logger.debug("CSR_ACCEPT: {}".format(line))
        csr_addr = None
        csr_addr_range = None
        self.logger.debug("AN_NAME: {} PATH: {}".\
                format(self.curr_an_name, self.curr_path))

        an_csrs = self.csr_map.get(self.curr_an_name, None)
        if not an_csrs:
            self.logger.warning("Could not get CSRs for AN:{}".format(self.curr_an_name))
            return
        csr_prop = an_csrs.get().get(csr_name, None)
        if csr_prop == None:
            self.logger.warning("Could not get info for CSR: {}".format(csr_name))
            return

        if len(ex_coll) > 1:
            csr_addr = self.__hexlify(ex_coll[0].strip())
            csr_addr_range = self.__hexlify(ex_coll[1].strip())
            self.curr_rn.add_csr(self.curr_ri,
                    csr_name,
                    csr_addr,
                    csr_addr_range)
        else:
            csr_addr = self.__hexlify(coll[1].strip())
            csr_addr_range = ((csr_prop.width + 63) & ~(0x3f)) >> 3
            self.curr_rn.add_csr(self.curr_ri,
                    csr_name,
                    csr_addr)
        self.__add_csr_metadata_inst(csr_name, csr_addr, csr_addr_range, csr_prop)

    def __clean_name(self, m_arr):
        for idx, _ in enumerate(m_arr):
            m_arr[idx] = re.sub('(_an)|(_AN)', '', m_arr[idx])

        k = ".".join(elem for elem in m_arr)
        return k.lower()

    def __hexlify(self, entry):
        entry = re.sub(r'0x', '', entry)
        entry = re.sub(r'_', '', entry)
        val = int(entry, 16)
        return val

    def __add_csr_metadata_inst(self, csr_name, csr_addr, csr_addr_range, csr_prop):
        rn = self.ring_map.get(self.curr_rc, None)
        rn_props = rn.get_instances()
        rn_prop = rn_props[self.curr_ri]
        ring_addr = rn_prop.get_addr()

        an_inst_cnt = 1
        an_skip_addr = 0
        an_attr = rn.get_an_path(self.curr_ri, self.curr_path)
        if an_attr == None:
            prefix_path, an_name = ANUtils().get_an(self.curr_path)
            an_attr = rn.get_an_path(self.curr_ri, prefix_path)
        if an_attr != None:
            an_inst_cnt = an_attr[0]
            an_skip_addr = an_attr[2]

        self.csr_metadata.add_csr_metadata(self.curr_rc, self.curr_ri, ring_addr,
            self.curr_an_name, self.curr_path, an_inst_cnt, an_skip_addr,
            self.curr_addr, csr_name, csr_addr - self.curr_addr, csr_addr_range, csr_prop)
        # AMAP file does not capture PC1-PC7 instance details
        # So, workaround by adding them
        # http://jira.fungible.local/browse/F1-4083
        if self.curr_rc == "pc" and self.curr_ri == 0:
            for i in range(1, 8):
                self.csr_metadata.add_csr_metadata(self.curr_rc, self.curr_ri + i,
                    (i + 1) * ring_addr, self.curr_an_name, self.curr_path,
                    an_inst_cnt, an_skip_addr, self.curr_addr + (i * ring_addr),
                    csr_name, csr_addr - self.curr_addr, csr_addr_range, csr_prop)

    def get_csr_metadata(self):
        return self.csr_metadata.get_csr_metadata()

    def __str__(self):
        r_str = ""
        for name, node in self.ring_map.items():
            r_str += "{}".format(node)
            r_str += "sys_rings[\"{}\"] = {}_rng;\n".format(name.upper(), name)
        return r_str


    __repr__ = __str__


class RingUtil(object):
    RING_ENC = r'([\w]+)_([\d])+'
    ALT_RING_ENC = r'([\w]+)([\d]+)'
    def __init__(self, logger=None):
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
            for key, val in list(yml_obj.items()):
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


