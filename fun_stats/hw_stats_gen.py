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
import pprint

#logger = logging.getLogger("stats")

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

# Process each CSR entry node
class CSRNode(object):
    def __init__(self, name, cfg):
        self.name = name
        logging.debug("Processing CSR entry:{}".format(name))
        self.__process_entry(cfg)
        logging.debug("CSR Entry node {} added!".format(name))

    def __process_entry(self, cfg):
        valid_bool_inputs = ["TRUE", "FALSE"]
        self.props_name = cfg.get("name", self.name)

        self.gen_objs = collections.OrderedDict()
        self.ring_class = None
        self.ring_inst = None
        rnode = cfg.get("ring", None)
        if rnode is not None:
            rclass = rnode.get("class", None)
            if rclass is not None:
                if type(rclass) is not unicode:
                    logging.error(("CSR:{} ring class must"
                                   " be a string").format(self.name))
                    sys.exit(1)
            self.ring_class = rclass

            rinst = rnode.get("inst", None)
            if rinst is not None:
                if type(rinst) is not int:
                    logging.error(("CSR:{} RING:{} must"
                                   " be a string").format(self.name,
                                                          self.ring_class))
                    sys.exit(1)
            self.ring_inst = rinst

        self.an = None
        self.an_path = None
        anode = cfg.get("anode", None)
        if anode is not None:
            self.an = anode.get("an", None)
            self.an_path = anode.get("an_path", None)

            """
            self.an_inst_list = list()
            an_inst_range = anode.get("inst", None)
            if an_inst_range is not None:
                if type(an_inst_range) is str:
                    min, max = range_min_max(an_inst_range)
                    self.an_inst_list = range(min, max)
                elif type(an_inst_range) is int:
                    self.an_inst_list.append(an_inst_range)
                else:
                    logging.error(("CSR:{} ANODE:{}"
                            "\'inst\' must be a range string or a unsigned"
                            " integer").format(self.name, self.an)
                    sys.exit(1)
            """
        self.clear_on_read = cfg.get("clear_on_read", None)
        if self.clear_on_read is not None:
            if self.clear_on_read.upper() not in valid_bool_inputs:
                logging.error(("CSR:{} clear_on_read property value is invalid!"
                               " Expected values are \"true/false\"").format(self.name))
                sys.exit(1)
        else:
            self.clear_on_read = "false"

        self.on_demand = cfg.get("on_demand", None);
        if self.on_demand is not None:
            if not self.on_demand.upper() in valid_bool_inputs:
                logging.error(("CSR:{} on_demand property value is invalid!"
                               " Expected values are \"true/false\"").format(self.name))
                sys.exit(1)
        else:
            self.on_demand = "false"

        self.poll_interval = cfg.get("poll_interval", None);
        if self.poll_interval is not None:
            if type(self.poll_interval) is not int:
                logging.error(("CSR:{} poll_interval property should be"
                               " integer").format(self.poll_interval))
                sys.exit(1)
        else:
            self.poll_interval = 0

        self.csr_defs = csr_metadata().get_csr_def(self.name,
                                                   self.ring_class,
                                                   self.ring_inst,
                                                   self.an_path,
                                                   self.an)

        if not self.csr_defs:
            logging.error(("**No csr metadata matching CSR:{}"
                           " RING:{} {} AN:{} {}").format(
                            self.name, self.ring_class,
			    self.ring_inst,
                            self.an, self.an_path))
            sys.exit(1)
        self.csr_type = cfg.get("csr_type", None)
        self.ring_dict = collections.OrderedDict()
        self.csr_def_flds = None
        self.csr_n_entries = None
        cfg_fields = cfg.get("fields", None)
        for csr in self.csr_defs:
            if self.csr_type is None:
                self.csr_type = csr.get("csr_type", None)

            if self.csr_n_entries is not None:
                if csr.get("csr_n_entries", None) != self.csr_n_entries:
                    logging.error(("CSR:{} has different different number "
                                   "entries in different instances!").format(
                                   self.name))
                    sys.exit(1)
            else:
                self.csr_n_entries = csr.get("csr_n_entries", None)

            if self.csr_def_flds is not None:
                if self.csr_def_flds != csr.get("fld_lst", None):
                    logging.error(("CSR:{} has different fields in different"
                                " instances!").format(self.name))
                    sys.exit(1)
            else:
                self.csr_def_flds = csr.get("fld_lst", None)
            if self.csr_def_flds is None:
                logging.error(("CSR:{} has no fields").format(self.name))
                sys.exit(1)
            ring_name = csr.get("ring_name", None)
            ring_inst = csr.get("ring_inst", None)
            an_name = csr.get("an", None)
            an_inst_cnt = csr.get("an_inst_cnt", None)

            ring = self.gen_objs.get(ring_name, None)
            if ring is None:
                ring = collections.OrderedDict()
                ring["ring_addr"] = csr.get("ring_addr", None)
                self.gen_objs[ring_name] = ring

            rinst_lst = ring.get("ring_inst", None)
            if rinst_lst is None:
                rinst_lst = collections.OrderedDict()
                ring["ring_inst"] = rinst_lst

            rinst = rinst_lst.get(ring_inst, None)
            if rinst is None:
                rinst = collections.OrderedDict()
                rinst["ring_inst_addr"] = csr.get("ring_inst_addr", None)
                rinst_lst[ring_inst] = rinst

            anode_lst = rinst.get("anode", None)
            if anode_lst is None:
                anode_lst = collections.OrderedDict()
                rinst["anode"] = anode_lst

            anode = anode_lst.get(an_name, None)
            if anode is None:
                anode = collections.OrderedDict()
                anode["an_inst_cnt"] = an_inst_cnt
                anode["an_addr"] = csr.get("an_addr", None)
                anode["skip_addr"] = csr.get("an_skip_addr", None)
                anode_lst[an_name] = anode

            csr_lst = anode.get("csr", None)
            if csr_lst is None:
                csr_lst = collections.OrderedDict()
                anode["csr"] = csr_lst

            csr_node = csr_lst.get(self.name, None)
            if csr_node is None:
                csr_node = collections.OrderedDict()
                if self.poll_interval is None:
                    csr_node["period_usec"] = 0
                else:
                    csr_node["period_usec"] = self.poll_interval
                csr_node["on_demand"] = self.on_demand
                csr_node["clear_on_read"] = self.clear_on_read
                csr_node["type"] = csr.get("csr_type", None)
                csr_node["n_instances"] = csr.get("csr_count", None)
                csr_node["addr"] = csr.get("csr_addr", None)
                csr_width_64bit = csr.get("csr_width", None)
                csr_node["width_64bit"] = csr_width_64bit
                csr_width = self.__get_csr_width(csr.get("fld_lst", None))
                csr_node["width"] = csr_width
                csr_node["n_entries"] = csr.get("csr_n_entries", None)
                fld_list = self.__get_field_objs(cfg_fields,
							csr.get("fld_lst", None), csr_width_64bit)
                csr_node["num_fields"] = len(fld_list)
                csr_node["fld_list"] = fld_list
                csr_lst[self.name] = csr_node

    def get_gen_objs(self):
        return self.gen_objs;

    def __get_csr_width(self, csr_def_flds):
		csr_fld_width = 0
		for csr_fld in csr_def_flds:
			csr_field_name = csr_fld["fld_name"]
			if csr_field_name == "__rsvd":
				continue
			csr_fld_width += csr_fld["fld_width"]
		return csr_fld_width

    def __get_field_objs(self, fields, csr_def_flds, csr_width_64bit):
        if csr_def_flds is None:
            logging.error(("CSR: {} metadata field list empty!").format(self.name))
            sys.exit(1)
        fld_objs = collections.OrderedDict()
        if fields is not None:
            for k,v in fields.iteritems():
                csr_index = None
                if self.csr_type == "TBL_REG_LIST":
                    if type(v) is not collections.OrderedDict:
                        logging.error(("CSR: {} TBL_REG_LIST expetcts "
				                       "index-field map dictionary!").format(
                                       self.name))
                        sys.exit(1)
                    csr_field_name = v.get("field", None)
                    if csr_field_name is None:
                        logging.error(("CSR: {} TBL_REG_LIST expetcts "
                                       "field property inside value "
                                       "dictionary!").format(self.name))
                        sys.exit(1)
                    csr_index = v.get("index", None)
                    if csr_index is None or type(csr_index) is not int:
                        logging.error(("CSR: {} TBL_REG_LIST expetcts "
                                       "index in the field map"
                                       " dictionary!").format(self.name))
                        sys.exit(1)
                else:
                    csr_field_name = v
                if type(csr_field_name) is not unicode:
            	    logging.error("CSR:{} field:{} value data type "
                                  "should be string!".format(
                                  self.name, k))
                    sys.exit(1)
                fld = None
                offset = 0;
                for csr_fld in csr_def_flds:
                    csr_fld_width = csr_fld["fld_width"]
                    offset += csr_fld_width
                    if csr_fld.get("fld_name", None) == csr_field_name:
                        fld = dict()
                        fld["csr_fld_name"] = csr_fld["fld_name"]
                        fld["csr_fld_width"] = csr_fld_width
                        if csr_index is not None:
                            fld["csr_tbl_index"] = csr_index
                        fld["csr_fld_offset"] = csr_width_64bit - offset
                if fld is None:
                    logging.error("CSR:{} field:{} not found "
                                  "in csr definition!".format(
                                  self.name, csr_field_name))
                    sys.exit(1)
                else:
                    fld_objs[k] = fld
        else:
            logging.debug("{} ".format(self.name))
            offset = 0;
            for csr_fld in csr_def_flds:
                fld = dict()
                offset += csr_fld["fld_width"]
                csr_field_name = csr_fld["fld_name"]
                if csr_field_name == "__rsvd":
                    continue
                fld["csr_fld_name"] = csr_field_name
                fld["csr_fld_width"] = csr_fld["fld_width"]
                fld["csr_fld_offset"] = csr_width_64bit - offset
                fld_objs[csr_field_name] = fld
        return fld_objs
        #self.fld_objs = fld_objs

    def print_csr_node(self):
        logging.debug(("CSR:{} RING:{}.{} AN:{}.{}").format(
                    self.name, self.ring_class, self.ring_inst,
                    self.an, self.an_path))
        logging.debug(("csr type: {} n_entries: {}").format(
                    self.csr_type,
                    self.csr_n_entries));
        logging.debug(("csr def: {}").format(self.gen_objs))


    def get_an_list(self):
        an_set = set()
        for i in self.subnodes:
            an_set |= i.get_an_list()
        return an_set


class StatsGen(object):
    def __init__(self, cwd):
        logging.info("Stats Code Generate")
        self.cwd = cwd
        self.cmd_parser = argparse.ArgumentParser(description="Stats Code Generatation")
        self.other_args = {}
        self.__arg_process(self.cmd_parser, self.other_args)
        self.csr_cfg_obj = list()
        self.gen_objs = collections.OrderedDict()
        self.props_groups = collections.OrderedDict()
        #self.gen_objs = dict()

    def __arg_process(self, cmd_parser, other_args):
        def_dir = os.path.join(self.cwd, "Configfiles/stats")
        cmd_parser.add_argument("-c", "--cfg-dir", help="Dir for config files",
                default=def_dir, required=False, type=str)

        cmd_parser.add_argument("-o", "--out-dir", help="Dir for generated files",
                required=True, type=str)
        cmd_parser.add_argument('--log-level',
                        required=False,
                        default='INFO',
                        dest='log_level',
                        help='Set the logging output level.')

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
        log_level = args.log_level
        if log_level == "DEBUG":
	        logger_init(logging.DEBUG)
        else:
            logger_init(logging.INFO)
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
        #header_tmpl = ENVIRONMENT.get_template("header.j2")

        inc_path = None
        code_str = None
        block_lst = list()

        logging.info("Generate the funos source code!")
        stats_cfg = collections.OrderedDict()
        for k,v in cfg.get().iteritems():
            stats_cfg = cfg.merge_dicts(stats_cfg, v)

        csr_list = stats_cfg.get("csr", None)
        for k,v in csr_list.iteritems():
            cfg_obj = CSRNode(k,v)
            dict_merge(self.gen_objs, cfg_obj.get_gen_objs())

        #props_alias_list = stats_cfg.get("props_groups", None)
        #for k,v in props_alias_list.iteritems():
        #    self.__process_props_group(k, v)

        self.print_gen_objs()
        file = "fun_hw_stats_gen.c"
        logging.info("Creating file {}".format(file))
        with open(os.path.join(args.out_dir, file), 'w') as f:
            f.write(source_tmpl.render({"gen_objs":self.gen_objs,
                                        "file": file}))
        f.close()

    def __process_props_group(self, group_name, group_info):
        p_group = self.props_groups.get(group_name, None)
        if p_group is not None:
            logging.error("Props group: {} defined twice!".format(group_name))
            sys.exit(1)
        p_group =  collections.OrderedDict()
        self.props_groups[group_name] = p_group
        if type(group_info) == list:
            for gnode in group_info:
                self.__add_props_group_gen_obj(group_name, gnode)
                path = gnode.get("path", None)
                hier_nodes = path.split("/")
                if len(hier_nodes) is not 5:
                    logging.error("Invalid props path: {}".format(path))
                    sys.exit(1)

        else:
            self.__add_props_group_gen_obj(group_name, group_info)
            path = group_info.get("path", None)
            hier_nodes = path.split("/")
            print hier_nodes

    def __get_positive_int(str):
        try:
            number = int(str)
            assert(number > 0), 'Number must be bigger than 0'
        except:
            logging.error("Must be positive Integer!")



    def __print_gen_fld_objs(self, fld_list):
        for k,v in fld_list.iteritems():
            logging.debug(("\t\t\t\tFIELD:{} NAME:{}, WIDTH:{}, OFFSET:{}").format(
                k, v.get("csr_fld_name", None), v.get("csr_fld_width", None),
                v.get("csr_fld_offset", None)))

    def __print_gen_csr_objs(self, csr_list):
        for k,v in csr_list.iteritems():
            logging.debug(("\t\t\tCSR:{}, ADDR:{}, WIDTH:{}, N_INST:{}, N_ENTRIES:{}").format(
                k, v.get("addr", None), v.get("width", None), v.get("n_instances", None),
                v.get("n_entries", None), v.get("type", None)))
            self.__print_gen_fld_objs(v.get("fld_list", None))

    def __print_gen_anode_objs(self, an_list):
        for k,v in an_list.iteritems():
            logging.debug(("\t\tANODE:{} N_INST:{} ADDR: {} SKIP_ADDR:{}").format(
                k, v.get("an_inst_cnt", None), v.get("an_addr", None),
                 v.get("skip_addr", None)))
            self.__print_gen_csr_objs(v.get("csr", None))

    def __print_gen_ring_inst_objs(self, rinst_list):
        for k,v in rinst_list.iteritems():
            logging.debug("\tRING_INST: {} ADDR: {}".format(
                    k, v.get("ring_inst_addr", None)))
            self.__print_gen_anode_objs(v.get("anode", None))

    def print_gen_objs(self):
        for k,v in self.gen_objs.iteritems():
            logging.debug("RING: {} ADDR:{}".format(k, v.get("ring_addr", None)))
            self.__print_gen_ring_inst_objs(v.get("ring_inst", None))

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

    def csr_equal(self, x, rn_class, rn_inst, an_path, an):
        if rn_class:
            if x["ring_name"] != rn_class:
                return False
        if rn_inst:
            if x["ring_inst"] != rn_inst:
                return False
        if an:
            if x["an"] != an:
                return False

        return True

    def get_csr_def(self, csr_name, rn_class, rn_inst, an_path, an):
        csr_defs_lst = self.metadata.get(csr_name, [])
        if not csr_defs_lst:
            return None
        else:
            csr_defs_lst = [x for x in csr_defs_lst        \
                            if self.csr_equal(x, rn_class, \
                            rn_inst, an_path, an)]

        #print csr_defs_lst
        return csr_defs_lst

def dict_merge(dct, merge_dct):
    for k, v in merge_dct.iteritems():
		if (k in dct and isinstance(dct[k], dict)
				and isinstance(merge_dct[k], collections.Mapping)):
			dict_merge(dct[k], merge_dct[k])
		else:
			dct[k] = merge_dct[k]

logger = logging.getLogger()
def logger_init(level):
    formatter = logging.Formatter('[%(filename)s:%(lineno)d] %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(handler)
    logger.setLevel(level)

if __name__ == "__main__":
    stats_gen = StatsGen(os.getcwd())
    stats_gen.run()

