#!/usr/bin/env python3
#
# hw_stats_gen.py
#
# Created by Nag Ponugoti March 28 2018
# Copyright Fungible Inc. 2018

import os, sys
import string, json, collections
import logging
import pdb, argparse
from json_reader import CFG_Reader
from itertools import chain
import re

#logger = logging.getLogger("stats")

#Groups the range strings
def group_to_range(group):
    group = ''.join(group.split())
    sign, g = ('-', group[1:]) if group.startswith('-') else ('', group)
    r = g.split('-', 1)
    r[0] = sign + r[0]
    r = sorted(int(__) for __ in r)
    return list(range(r[0], 1 + r[-1]))

#Groups and expands range strings
def rangeexpand(txt):
    ranges = chain.from_iterable(group_to_range(__) for __ in txt.split(','))
    return sorted(set(ranges))

# Process each CSR entry node
class CSRNode(object):
    def __init__(self, name, cfg):
        self.name = name
        logging.debug("Processing CSR entry:{}".format(name))
        self.__process_entry(cfg)
        logging.debug("CSR Entry node {} added!".format(name))

    def __process_entry(self, cfg):
        self.cfg_objs = collections.OrderedDict()
        self.ring_class = None
        self.ring_inst = None
        rnode = cfg.get("ring", None)
        if rnode is not None:
            rclass = rnode.get("class", None)
            if rclass is not None:
                if type(rclass) is not str:
                    logging.error(("CSR:{} ring class must"
                                   " be a string").format(self.name))
                    sys.exit(1)
            self.ring_class = rclass

            rinst = rnode.get("inst", None)
            if rinst is not None:
                if type(rinst) is str:
                    self.ring_inst = rangeexpand(rinst)
                elif type(rinst) is int:
                    self.ring_inst = [rinst]
                else:
                    logging.error(("CSR:{} RING:{} inst must"
                                   " be a integer or comma"
                                   " separated range string").format(self.name,
                                   self.ring_class))
                    sys.exit(1)

        self.an = None
        self.an_path = None
        anode = cfg.get("anode", None)
        if anode is not None:
            self.an = anode.get("an", None)
            self.an_path = anode.get("an_path", None)

        self.poll_interval = cfg.get("poll_interval", None);
        if self.poll_interval is None:
            logging.error(("CSR:{} Missing poll_interval property").format(self.name))
            sys.exit(1)

        if self.ring_inst is None:
            self.ring_inst = list()
            self.ring_inst.append(None)

        for i in self.ring_inst :
            logging.debug(('csr: {} ring_class: {} ring_inst: {}').format(
                self.name, self.ring_class, i))
            self.csr_defs = csr_metadata().get_csr_def(self.name,
                                                       self.ring_class,
                                                       i,
                                                       self.an_path,
                                                       self.an)

            if not self.csr_defs:
                logging.error(("**No csr metadata matching CSR:{}"
                               " RING:{} {} AN:{} {}").format(
                                self.name, self.ring_class,
                                i,
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

                ring = self.cfg_objs.get(ring_name, None)
                if ring is None:
                    ring = collections.OrderedDict()
                    ring["ring_addr"] = csr.get("ring_addr", None)
                    self.cfg_objs[ring_name] = ring

                rinst_lst = ring.get("ring_inst", None)
                if rinst_lst is None:
                    rinst_lst = collections.OrderedDict()
                    ring["ring_inst"] = rinst_lst

                rinst = rinst_lst.get(ring_inst, None)
                if rinst is None:
                    rinst = collections.OrderedDict()
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
                        csr_node["period_msec"] = 0
                    else:
                        csr_node["period_msec"] = self.poll_interval
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

    def get_cfg_objs(self):
        return self.cfg_objs;

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
        field_list = list()
        if fields is not None:
            if type(fields) is str:
                field_list.append(fields);
            elif  type(fields) is list:
                field_list = fields
            else:
                logging.error(("CSR: {} fields property must be a string or"
                               " list").format(self.name))
                sys.exit(1)

        offset = 0;
        for csr_fld in csr_def_flds:
            fld = dict()
            offset += csr_fld["fld_width"]
            csr_field_name = csr_fld["fld_name"]
            if csr_field_name == "__rsvd":
                continue
            if field_list:
                if csr_field_name not in field_list:
                    continue
                else:
                    field_list.remove(csr_field_name)
            fld["csr_fld_name"] = csr_field_name
            fld["csr_fld_width"] = csr_fld["fld_width"]
            fld["csr_fld_offset"] = csr_width_64bit - offset
            fld_objs[csr_field_name] = fld
        if field_list:
            logging.error(("CSR: {} Invalid fields: {}").format(self.name,
                                                                field_list))
            sys.exit(1)
        return fld_objs

class StatsGen(object):
    def __init__(self, cwd):
        logging.info("Stats Code Generate")
        self.cwd = cwd
        self.cmd_parser = argparse.ArgumentParser(description="Stats Code Generatation")
        self.other_args = {}
        self.__arg_process(self.cmd_parser, self.other_args)
        self.csr_cfg_obj = list()
        #self.cfg_objs = collections.OrderedDict()
        self.props_groups = collections.OrderedDict()
        #self.cfg_objs = dict()

    def __arg_process(self, cmd_parser, other_args):
        def_dir = os.path.join(self.cwd, "configs/stats_config")
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

        cfg = CFG_Reader(args.cfg_dir)
        csr_metadata_file = os.path.join(args.csr_metadata_dir, "csr_metadata.json")
        csr_metadata().set_metadata(json.load(open(csr_metadata_file)))

        inc_path = None
        code_str = None
        block_lst = list()

        logging.info("Generate the funos source code!")
        stats_cfg = collections.OrderedDict()
        file_name = "stats_cache.cfg"
        logging.info("Creating file {}".format(file_name))
        f = open(os.path.join(args.out_dir, file_name), "w")
        for name,cfg in cfg.get().items():
            cfg_objs = collections.OrderedDict()
            for k,v in cfg.items():
                csr_obj = CSRNode(k,v)
                dict_merge(cfg_objs, csr_obj.get_cfg_objs())
            stats_cfg[name] = self.get_cfg_gen_objs(cfg_objs)
            self.print_cfg_objs(cfg_objs)
        f.write(json.dumps(stats_cfg, indent=4))
        f.close()

    def __print_fld_objs(self, fld_list):
        for k,v in fld_list.items():
            logging.debug(("\t\t\t\tFIELD:{} NAME:{}, WIDTH:{}, OFFSET:{}").format(
                k, v.get("csr_fld_name", None), v.get("csr_fld_width", None),
                v.get("csr_fld_offset", None)))

    def __print_csr_objs(self, csr_list):
        for k,v in csr_list.items():
            logging.debug(("\t\t\tCSR:{}, ADDR:{}, WIDTH:{}, N_INST:{}, N_ENTRIES:{}").format(
                k, v.get("addr", None), v.get("width", None), v.get("n_instances", None),
                v.get("n_entries", None), v.get("type", None)))
            self.__print_fld_objs(v.get("fld_list", None))

    def __print_anode_objs(self, an_list):
        for k,v in an_list.items():
            logging.debug(("\t\tANODE:{} N_INST:{} ADDR: {} SKIP_ADDR:{}").format(
                k, v.get("an_inst_cnt", None), v.get("an_addr", None),
                 v.get("skip_addr", None)))
            self.__print_csr_objs(v.get("csr", None))

    def __print_ring_inst_objs(self, rinst_list):
        for k,v in rinst_list.items():
            self.__print_anode_objs(v.get("anode", None))

    def print_cfg_objs(self, cfg_objs):
        for k,v in cfg_objs.items():
            logging.debug("RING: {} ADDR:{}".format(k, v.get("ring_addr", None)))
            self.__print_ring_inst_objs(v.get("ring_inst", None))

    def __get_csr_objs(self, base_addr, csr_list):
        gen_obj_list = list()
        for k,v in csr_list.items():
            csr_addr = v.get("addr", None)
            if csr_addr is None:
                logging.error("CSR:{} Invalid address!".format(k))
                sys.exit(1)
            csr_addr = self.__hexlify(csr_addr)

            csr_width = v.get("width", None)
            if csr_width == 0 or csr_width is None:
                logging.error("CSR:{} Invalid width!".format(k))
                sys.exit(1)

            fld_list = v.get("fld_list", None)
            if fld_list is None:
                logging.error("CSR:{} Empty field list!".format(k))
                sys.exit(1)

            n_instances = v.get("n_instances", None)
            if n_instances is None:
                logging.error("CSR:{} Invalid number of instances!".format(k))
                sys.exit(1)

            n_entries = v.get("n_entries", None)
            if n_entries is None:
                logging.error("CSR:{} Invalid number of entries!".format(k))
                sys.exit(1)
            csr_width_64bit = v.get("width_64bit", None)
            if csr_width_64bit is None:
                logging.error("CSR:{} Invalid width_64bit !".format(k))
                sys.exit(1)
            csr_width_bytes = csr_width_64bit/8

            for i in range(n_instances):
                for e in range(n_entries):
                    addr = base_addr + csr_addr \
                            + ((i * n_entries) * csr_width_bytes) \
                            + (e * csr_width_bytes)
                    for f,d in fld_list.items():
                        fld_obj = collections.OrderedDict()
                        fld_obj["csr_addr"] = hex(addr)
                        fld_obj["csr_width"] = csr_width
                        fld_obj["period_msec"] = v.get("period_msec", 0)
                        field_offset = d.get("csr_fld_offset", None)
                        if field_offset is None:
                            logging.error(("CSR:{} field:{} Invalid field"
                                    " offset!").format(k, d.get("csr_fld_name",
                                        None)))
                            sys.exit(1)
                        fld_obj["field_offset"] = field_offset
                        field_width = d.get("csr_fld_width", None)
                        if field_width is None:
                            logging.error(("CSR:{} field:{} Invalid field"
                                    " width!").format(k, d.get("csr_fld_name",
                                                             None)))
                            sys.exit(1)
                        fld_obj["field_width"] = field_width
                        gen_obj_list.append(fld_obj)

        return gen_obj_list

    def __get_anode_objs(self, an_list):
        gen_obj_list = list()
        for k,v in an_list.items():
            inst_cnt = v.get("an_inst_cnt", 1)
            an_addr = v.get("an_addr", None)
            if an_addr is None:
                logging.error("Invalid anode:{} address!".format(k))
                sys.exit(1)
	    an_addr = self.__hexlify(an_addr)
	    skip_addr = v.get("skip_addr", None)
	    if skip_addr is None:
		logging.error("Invalid skip_addr for anode:{}!".format(k))
		sys.exit(1)
	    skip_addr = self.__hexlify(skip_addr)
            for i in range(inst_cnt):
                base_addr = an_addr + (i * skip_addr)
                objs = self.__get_csr_objs(base_addr, v.get("csr", None))
                gen_obj_list += objs
        return gen_obj_list

    def __get_ring_inst_objs(self, rinst_list):
        gen_obj_list = list()
        for k,v in rinst_list.items():
            objs = self.__get_anode_objs(v.get("anode", None))
            gen_obj_list += objs
        return gen_obj_list

    def get_cfg_gen_objs(self, cfg_objs):
        gen_obj_list = list()
        for k,v in cfg_objs.items():
            objs = self.__get_ring_inst_objs(v.get("ring_inst", None))
            gen_obj_list += objs
        return gen_obj_list

    def __hexlify(self, entry):
        entry = re.sub(r'0x', '', entry)
        entry = re.sub(r'_', '', entry)
        val = int(entry, 16)
        return val



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
        if rn_inst is not None:
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
    for k, v in merge_dct.items():
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

