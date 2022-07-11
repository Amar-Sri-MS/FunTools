#
#  csr_main.py
#
#  Created by Hariharan Thantry on 2018-02-21
#
#  Copyright 2018 Fungible Inc. All rights reserved.
#
# Top level main python package

import argparse
import json
import logging
import os

from .module_path import module_locator
from csr.utils.yml import YML_Reader, CSR_YML_Reader
from csr.utils.artifacts import CSRRoot, Walker, RingUtil, TmplMgr
from csr.utils.utilities import Filer

class Slurper(object):
    def __init__(self, cwd, logger=None):
        logging.basicConfig(level=logging.INFO)
        self.logger = logger or logging.getLogger(__name__)

        self.cwd = cwd
        self.cmd_parser = argparse.ArgumentParser(description="CSR Slurper utility for F1")
        self.other_args = {}
        self.__arg_process(self.cmd_parser, self.other_args)

    def __arg_process(self, cmd_parser, other_args):
        ml_dir = module_locator().module_path()
        cmd_parser.add_argument("-d", "--csr-defs", help="CSR definitions", required=True, type=str)
        cmd_parser.add_argument("-g", "--gen-cc", help="Generate the CC file", action='store_true')
        cmd_parser.add_argument("-c", "--cfg-dir", help="Output directory for JSON/DB", required=False,
                default=self.cwd, type=str)
        def_filter = os.path.join(ml_dir, "template", "csr_filter.yaml")
        cmd_parser.add_argument("-f", "--filter-file", help="Filter YAML file to reduce the size of the executable",
                default=None, required=False, type=str)
        cmd_parser.add_argument("-l", "--log-level", required=False, default='INFO', help="Set the logging output level")

        self.other_args['gen_cc_dir'] = os.path.join(self.cwd, "csr", "libcsr", "src")

        self.other_args['tmpl_file'] = os.path.join(ml_dir, "template", "csr_rt.j2")
        self.other_args['csr_defs']  = os.path.join(ml_dir, "template", "csr_defs.yaml")
        self.ml_dir = ml_dir


    def __update_loc(self, loc):
        if not os.path.isabs(loc):
            loc = os.path.join(self.cwd, loc)
        return loc

    def __check_yml_dir(self, y_dir):
        yml_dir = os.path.join(y_dir, "csr")
        if not os.path.exists(yml_dir):
            assert False, "Yaml directory: {} does not exist".format(yml_dir)

        if not os.path.isdir(yml_dir):
            assert False, "Yaml: {} not a directory".format(yml_dir)
        if not os.path.exists(os.path.join(y_dir, "AMAP")):
            assert False, "AMAP file does not exist"

    def run(self):
        args = self.cmd_parser.parse_args()
        args.csr_defs = self.__update_loc(args.csr_defs)
        args.cfg_dir = self.__update_loc(args.cfg_dir)

        self.__check_yml_dir(args.csr_defs)
        yml_dir = os.path.join(args.csr_defs, "csr")
        amap_file = os.path.join(args.csr_defs, "AMAP")

        if args.log_level == "DEBUG":
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)


        # First populate the top level root
        # Only populates the address attribute
        p = YML_Reader(self.logger)
        csr_def = p.read_file(self.other_args['csr_defs'])

        filter_def = None
        if args.filter_file:
            self.logger.info("Filter file: {}".format(args.filter_file))
            filter_def = p.read_file(args.filter_file)


        # Pass to CSR Yaml reader, a list of included & excluded CSRs
        # If a CSR is included by name, ignore the attribute

        schema = CSR_YML_Reader(yml_dir, csr_def, filter_def, self.logger)
        self.logger.debug("{}".format(schema))

        self.csr_root = CSRRoot(amap_file, schema.get(), filter_def, self.logger)
        file_mkr = Filer()
        file_mkr.mkdir(args.cfg_dir)
        o_file = os.path.join(args.cfg_dir, 'csr_metadata.json')
        csr_meta = self.csr_root.csr_metadata
        self.logger.debug("{}".format(csr_meta))
        with open(o_file, "w") as fp:
            fp.write(json.dumps(self.csr_root.get_csr_metadata(), indent=4))

        self.args = args
        self.logger.info("[Written Config]: {}".format(o_file))

        # Next, get the ring structure
        #p = YML_Reader()
        #yml_stream = p.read_file(ring_file)
        #w = Walker(yml_stream)
        #print "{}".format(w)

    def gen_cc(self):
        if not self.args.gen_cc:
            self.logger.info("Not generating CC file")
            return
        if not self.args.filter_file:
            self.logger.info("\n\n\n!!!!  WARNING   !!! Entire CSR database being generated in-memory. May NOT COMPILE\n\n\n")

        cc_file = os.path.join(self.other_args['gen_cc_dir'], 'csr_gen.cpp')
        tmpl = TmplMgr(self.other_args['tmpl_file'])
        tmpl.write_cfg(cc_file, self.csr_root)

    def __str__(self):
        r_str = "{}".format(self.schema)
        return r_str

    __repr__ = __str__

