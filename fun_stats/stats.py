#!/usr/bin/python
#
# stats.py
#
# Created by Nag Ponugoti March 28 2018
# Copyright Fungible Inc. 2018

import os, sys
import string, json, collections
import logging
import pdb, argparse
from jinja2 import Environment, FileSystemLoader
from json_reader import CFG_Reader

logger = logging.getLogger("stats")

#Groups the range strings
def group_to_range(group):
  group = ''.join(group.split())
  sign, g = ('-', group[1:]) if group.startswith('-') else ('', group)
  r = g.split('-', 1)
  r[0] = sign + r[0]
  r = sorted(int(__) for __ in r)

#Groups the range strings
def range_min_max(group):
  group = ''.join(group.split())
  sign, g = ('-', group[1:]) if group.startswith('-') else ('', group)
  r = g.split('-', 1)
  r[0] = sign + r[0]
  r = sorted(int(__) for __ in r)
  return r[0], 1 + r[-1]

# Endpoint input range node
class RangeNode(object):
    def __init__(self, name, info):
        self.name = name
        self.range_min = 0
        self.range_max = 0
        self.incr = 0
        logging.debug("INPUT NODE:{}".format(name))
        self.__process_input(info)
        logging.debug("Range Node:{} min:{} max:{} incr:{}".format(name,
                            self.range_min, self.range_max, self.incr))

    def __process_input(self, info):
        if info["range"] != None:
            min, max = range_min_max(info["range"])
            self.__set_range(min, max)
            self.__set_incr(info.get("index_incr", 1))

    def __set_range(self, min, max):
        self.range_min = min
        self.range_max = max

    def __set_incr(self, incr=0):
        self.incr = incr

# Process list element of leaf stats node
class EntrySubNode(object):
    def __init__(self, e, input):
        self.csr_defs = csr_metadata()
        self.input_map = collections.OrderedDict()
        self.reg = None
        self.fields = collections.OrderedDict()
        self.offset = None
        self.an_path = None
        self.an = None
        self.an_inst = None
        self.rn_class = None
        self.rn_inst = None
        self.width = None
        self.reg_inst = None
        self.poll_interval = 0
        self.clear_on_read = False
        self.__process_entry_subnode(e, input)
        logging.debug("Entry sub-node for reg: {} is added!".format(self.reg))

    def __process_entry_subnode(self, e, input):
        if input:
            for i in input:
                if e[i] == None:
                    logging.error("Valid input range is not provided for \'{}:"
                              "{}\'".format(self.reg, i))
                    sys.exit(1)
                if self.input_map.get(i, None) != None:
                    logging.error("Duplicate input range for \'{}:"
                              "{}\'".format(self.reg, i))
                    sys.exit(1)
                self.input_map[i] = RangeNode(i, e[i])

        if e["reg"] is None:
            logging.error("Valid csr name should be passed!")
            sys.exit(1)
        if not bool(e["fields"]):
            logging.error("Valid fields should be passed for"
                      "reg: {} fields: {}".format(e["reg"], e["fields"]))
            sys.exit(1)
        self.reg = e["reg"]
        self.fields = e["fields"]
        self.reg_inst = e.get("reg_inst", None)
        self.offset = e.get("offset", None)
        self.poll_interval = e.get("poll_interval", 0)
        self.clear_on_read = e.get("clear_on_read", False)
        self.on_demand = e.get("on_demand", "false")
        ring = e.get("ring", None)
        if ring != None:
            self.rn_class = ring.get("class", None)
            self.rn_inst = ring.get("inst", None)
        anode = e.get("anode", None)
        if anode != None:
            self.an_path = anode.get("root", None)
            self.an = anode.get("an", None)
            self.an_inst = anode.get("inst", 0)
        self.__process_fields()

    def get_fields(self):
        return self.fields

    def get_on_demand(self):
        if self.on_demand == "true":
            return True
        else:
            return False

    def get_poll_interval(self):
        if self.poll_interval == "auto":
            return 5000 #TODO(@nponugoti)
        else:
            return self.poll_interval

    def get_an_list(self):
        an_set = set()
        an_set.add(self.an)
        logging.debug("AN_SET.{}".format(an_set))
        return an_set

    def get_csr_width(self):
        return self.csr_width

    def get_num_fields(self):
        return len(self.fields)

    def get_num_cntrs(self):
        return self.num_cntrs

    def __process_fields(self):
        logging.debug("Processing fields of CSR:".format(self.reg))
        csr_def = self.csr_defs.get_csr_def(self.reg, self.rn_class,
                self.rn_inst, self.an_path, self.an, self.an_inst)
        logging.debug("csr_def: {}".format(csr_def))
        csr_flds = csr_def["fld_lst"]
        fld_objs = None
        idx_offset =0
        self.csr_type = csr_def["csr_type"]
        self.csr_width = csr_def["csr_width"]
        if type(self.fields) == list:
            if self.csr_type != "CSR_TYPE::TBL":
                logging.error("If input is list of heterogenious field groups,"
                          "CSR type should be table!")
                sys.exit(1)
            self.csr_type = "CSR_TYPE::TBL_HETERO"
            fld_objs = collections.OrderedDict()
            for field in self.fields:
                fobj = collections.OrderedDict()
                for csr_fld in csr_flds:
                    for k,v in field["field_map"].iteritems():
                        if csr_fld["fld_name"] == v:
                            fld = dict()
                            fld["csr_fld_name"] = csr_fld["fld_name"]
                            fld["csr_fld_width"] = csr_fld["fld_width"]
                            fld["cntr_idx_offset"] = idx_offset
                            fobj[k] = fld
                            idx_offset +=1
                fld_objs[field["index"]] = fobj
            logging.debug("fld_objs: {}".format(fld_objs))

        else:
            fld_objs = collections.OrderedDict()
            logging.debug("csr_flds: {}".format(csr_flds))
            logging.debug("self.fields: {}".format(self.fields))
            for csr_fld in csr_flds:
                for k,v in self.fields.iteritems():
                    if csr_fld["fld_name"] == v:
                        fld = dict()
                        fld["csr_fld_name"] = csr_fld["fld_name"]
                        fld["csr_fld_width"] = csr_fld["fld_width"]
                        fld["cntr_idx_offset"] = idx_offset
                        fld_objs[k] = fld
                        idx_offset +=1

        if self.csr_type == "CSR_TYPE::REG_LST":
            min, max = range_min_max(self.reg_inst["range"])
            reg_inst = dict()
            reg_inst["range_min"] = min
            reg_inst["range_max"] = max
            reg_inst["name"] = self.reg_inst["name"]
            self.reg_inst = reg_inst
            self.num_cntrs = idx_offset*(max-min)
        else:
            self.num_cntrs = idx_offset

        self.fld_objs = fld_objs
        self.num_fields = idx_offset
        logging.debug(("num_fields: {}, num_cntrs: {}, fld_objs:"
                  "{}").format(self.num_fields, self.num_cntrs, self.fld_objs))
        logging.debug("input_map: {}".format(self.input_map))
        for k,v in self.input_map.iteritems():
            rmin = v.range_min
            rmax = v.range_max
            self.num_cntrs *= (rmax - rmin)
        logging.debug("input_map: {} self.num_cntrs: {}".format(self.input_map,
                                                            self.num_cntrs))

    def get_gen_objs(self):
        csr_def = self.csr_defs.get_csr_def(self.reg, self.rn_class,
                self.rn_inst, self.an_path, self.an, self.an_inst)

        subnode = dict()
        subnode["csr"] = self.reg
        an_base_addr = csr_def["an_addr"]
        an_skip_addr = 0
        an_inst_cnt = csr_def.get("an_inst_cnt", 1)
        if an_inst_cnt > 1 and self.an_inst > 0:
            an_skip_addr = csr_def.get("an_skip_addr", None)
            if not an_skip_addr:
                logging.error(("Invalid ANODE skip addr! CSR: {}, RN:{}, AN:{},"
                              "AN_INST:{}").format(self.reg, self.rn_class,
                                                  self.an_path, self.an_inst))
                sys.exit(1)
            an_skip_addr = int(an_skip_addr, 16) * self.an_inst

        subnode["base_addr"] = int(an_base_addr, 16) + an_skip_addr
        subnode["csr_width"] = (csr_def["csr_width"]+63)/64
        subnode["fields"] = self.fld_objs
        subnode["num_fields"] = self.num_fields
        subnode["csr_offset"] = self.offset
        subnode["input"] = self.input_map
        subnode["csr_type"] = self.csr_type
        subnode["reg_inst"] = self.reg_inst
        subnode["clear_on_read"] = self.clear_on_read
        return subnode

# Process leaf stats entry node
class EntryNode(object):
    def __init__(self, name, input, info):
        self.name = name
        self.subnodes = list()
        logging.debug("Processing entry:{}".format(name))
        self.__process_entry(input, info)
        logging.debug("Entry node added!:{}\n".format(name))

    def __process_entry(self, input, info):
        for e in info:
            self.subnodes.append(EntrySubNode(e, input))

    def get_gen_objs(self):
        num_cntrs = 0
        rbuf_size = 0;
        on_demand = False
        poll_interval = sys.maxsize;
        subnodes = list()

        for i in self.subnodes:
            subnode = i.get_gen_objs()
            subnode["cntr_base"] = num_cntrs
            subnodes.append(subnode)
            num_cntrs += i.get_num_cntrs()
            if subnode["csr_width"] > rbuf_size:
                rbuf_size = subnode["csr_width"]
            if i.get_poll_interval() < poll_interval:
                poll_interval = i.get_poll_interval()
            if i.get_on_demand() == True:
                on_demand = True

        gen_objs = dict()
        gen_objs["rbuf_size"] = rbuf_size
        gen_objs["num_cntrs"] = num_cntrs
        gen_objs["subnodes"] = subnodes
        gen_objs["on_demand"] = on_demand
        if poll_interval == sys.maxsize:
            poll_interval = 0
        gen_objs["poll_interval"] = poll_interval
        if on_demand == False and poll_interval == 0:
            logging.error("Either poll_interval attribute or on_demand attribute"
                      "are needed for entry {}".format(self.name))
            sys.exit(1)
        return gen_objs

    def get_an_list(self):
        an_set = set()
        for i in self.subnodes:
            an_set |= i.get_an_list()
        return an_set

# Process endpoint stats node
class EndPoint(object):
    EXCLUDE = ["input"]
    def __init__(self, name, info):
        self.name = name
        self.input = list()
        self.entry_map = collections.OrderedDict()
        logging.debug("Endpoint:{}".format(name))
        self.__process_endpoint(info)

    def __process_endpoint(self, info):
        if 'input' in info:
            self.__process_input(info["input"]);
        else:
            self.__process_input();

        for k,v in info.iteritems():
            if k not in EndPoint.EXCLUDE:
                self.__add_entry_instance(k, v)

    def __process_input(self, valid_inputs=None):
        self.input = valid_inputs

    def __add_entry_instance(self, entry, data):
        node = self.entry_map.get(entry, EntryNode(entry, self.input, data))
        self.entry_map[entry] = node

    def get_gen_objs(self):
        modules = collections.OrderedDict()
        modules["input"] = self.input
        nodes = collections.OrderedDict()
        for k,v in self.entry_map.iteritems():
            nodes[k] = v.get_gen_objs()
        modules["nodes"] = nodes
        return modules

    def get_an_list(self):
        an_set = set()
        for k,v in self.entry_map.iteritems():
            an_set |= v.get_an_list()
        return an_set

# Process module stats node
class ModuleNode(object):
    def __init__(self, name, info):
        logging.debug("Module: {}".format(name))
        self.name = name
        self.endpoint_map = collections.OrderedDict()
        self.__process_module(info)

    def __process_module(self, info):
        for k,v in info.iteritems():
            self.__add_endpoint_instance(k, v)

    def __add_endpoint_instance(self, endpoint, data):
        node = self.endpoint_map.get(endpoint, EndPoint(endpoint, data))
        self.endpoint_map[endpoint] = node

    def get_gen_objs(self):
        endpoints = collections.OrderedDict()
        for k,v in self.endpoint_map.iteritems():
            endpoints[k] = v.get_gen_objs()
        return endpoints

    def get_an_list(self):
        an_set = set()
        for k,v in self.endpoint_map.iteritems():
            an_set |= v.get_an_list()
        return an_set

# Process block stats node
class BlockRoot(object):
    def __init__(self, block, data):
        self.module_map = collections.OrderedDict()
        self.name = block
        self.__block_process(data)

    def __block_process(self, data):
        for k,v in data.iteritems():
            self.__add_module_instance(k, v)

    def __add_module_instance(self, k, v):
        module = self.module_map.get(k, ModuleNode(k, v))
        self.module_map[k] = module

    def get_gen_objs(self):
        modules = dict()
        for k,v in self.module_map.iteritems():
            logging.debug("BlockRoot {}".format(k))
            modules[k] = v.get_gen_objs()
        return modules

    def get_an_list(self):
        an_set = set()
        for k,v in self.module_map.iteritems():
            an_set |= v.get_an_list()
        return an_set

class StatsGen(object):
    def __init__(self, cwd):
        logging.info("Stats Code Generate")
        self.cwd = cwd
        self.cmd_parser = argparse.ArgumentParser(description="Stats Code Generatation")
        self.other_args = {}
        self.__arg_process(self.cmd_parser, self.other_args)

    def __arg_process(self, cmd_parser, other_args):
        def_dir = os.path.join(self.cwd, "Configfiles/stats")
        cmd_parser.add_argument("-c", "--cfg-dir", help="Dir for config files",
                default=def_dir, required=False, type=str)

        cmd_parser.add_argument("-o", "--out-dir", help="Dir for generated files",
                required=True, type=str)

        sdk_dir = os.path.join(self.cwd, "../FunSDK")
        csr_metadata_dir =  os.path.join(sdk_dir, "FunSDK/config/csr")
        cmd_parser.add_argument("-m", "--csr-metadata-dir", help="CSR metadata directory",
                default=csr_metadata_dir, required=False, type=str)
        my_path = os.path.dirname(os.path.abspath(__file__))
        self.other_args['tmpl_dir'] = os.path.join(my_path, "templates")

    def __update_loc(self, loc):
        if not os.path.isabs(loc):
            loc = os.path.join(self.cwd, loc)

        assert os.path.exists(loc), "{}: directory does not exist!".format(loc)
        return loc

    def run(self):
        args = self.cmd_parser.parse_args()
        args.cfg_dir = self.__update_loc(args.cfg_dir)
        out_dir = args.out_dir
        args.out_dir = self.__update_loc(args.out_dir)
        args.csr_metadata_dir = self.__update_loc(args.csr_metadata_dir)
        tmpl_dir = self.__update_loc(self.other_args['tmpl_dir'])

        cfg = CFG_Reader(args.cfg_dir)
        csr_metadata_file = os.path.join(args.csr_metadata_dir, "csr_metadata.json")
        csr_metadata().set_metadata(json.load(open(csr_metadata_file)))

        ENVIRONMENT = Environment( autoescape=False,
            loader=FileSystemLoader(tmpl_dir), trim_blocks=False)
        source_tmpl = ENVIRONMENT.get_template("source.j2")
        props_h_tmpl = ENVIRONMENT.get_template("props_h.j2")
        props_c_tmpl = ENVIRONMENT.get_template("props_c.j2")

        inc_path = None
        code_str = None
        block_lst = list()
        logging.info("Generate the funos source code!")
        for i, (k,v) in enumerate(cfg.get().iteritems()):
            logging.debug("Generating source code for {}!".format(k))
            block = BlockRoot(k, v)
            headers= block.get_an_list()
            gen_objs = dict()
            gen_objs["modules"] = block.get_gen_objs()
            gen_objs["dyn_headers"] = headers
            gen_objs["block"] = k
            block_lst.append(k)

            file = "fun_{}_stats.c".format(k)
            gen_objs["file"] = file
            logging.info("Creating file {}".format(file))
            with open(os.path.join(args.out_dir, file), 'w') as f:
                f.write(source_tmpl.render(gen_objs))
            f.close()
            stats_gen_indent(os.path.join(args.out_dir, file))

        props_gen_objs = dict()
        props_gen_objs["blocks"] = block_lst
        props_gen_objs["header_path"] = out_dir

        h_file = "fun_stats_bridge.h"
        props_gen_objs["header_file"] = h_file
        props_gen_objs["file"] = h_file
        h_file = os.path.join(args.out_dir, h_file)
        with open(os.path.join(args.out_dir, h_file), 'w') as f:
            f.write(props_h_tmpl.render(props_gen_objs))
        f.close()
        stats_gen_indent(h_file)

        c_file = "fun_stats_bridge.c"
        props_gen_objs["file"] = c_file
        c_file = os.path.join(args.out_dir, c_file)
        with open(os.path.join(args.out_dir, c_file), 'w') as f:
            f.write(props_c_tmpl.render(props_gen_objs))
        f.close()
        #stats_gen_indent(c_file)

def stats_gen_indent(gen_file):
    cmd = "indent -br -npsl -l120 -i4 -nut " + gen_file
    os.system(cmd)

def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

@singleton
class csr_metadata:
    def set_metadata(self, metadata):
        self.metadata = metadata

    def csr_equal(self, x, rn_class, rn_inst, an_path, an, an_inst):
        if rn_class:
            if x["ring_name"] != rn_class:
                return False
        if rn_inst:
            if x["ring_inst"] != rn_inst:
                return False
        if an:
            if x["an"] != an:
                return False

        if an_inst:
            if x["an_inst_cnt"] < an_inst:
                return False

        return True

    def get_csr_def(self, csr_name, rn_class, rn_inst, an_path, an, an_inst):
        csr_defs_lst = self.metadata.get(csr_name, [])
        if not csr_defs_lst:
            return None
        else:
            csr_defs_lst = [x for x in csr_defs_lst        \
                            if self.csr_equal(x, rn_class, \
                            rn_inst, an_path, an, an_inst)]

        if len(csr_defs_lst) > 1:
            logging.error("There are more than one instance"
                      "register defintion. Be more specific!!!")
            logging.info(json.dumps(csr_defs_lst, indent=1))
            sys.exit(1)
        if not csr_defs_lst:
            sys.exit(1)
        csr_def = csr_defs_lst[0]
        if csr_def["an_inst_cnt"] <= an_inst:
            logging.error(("ANODE instane number({}) for CSR:{} RN:{} AN:{} is "
                          "out of range!").format(an_inst, csr_name, rn_class, an))
            sys.exit(1)
        return csr_def

logger = logging.getLogger()
def logger_init(level):
    logger.setLevel(level)

if __name__ == "__main__":
    logger_init(logging.DEBUG)
    stats_gen = StatsGen(os.getcwd())
    stats_gen.run()



