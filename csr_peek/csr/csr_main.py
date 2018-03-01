#
#  csr_main.py
#
#  Created by Hariharan Thantry on 2018-02-21
#
#  Copyright 2018 Fungible Inc. All rights reserved.
#
# Top level main python package

import argparse
import os
from module_path import module_locator
from csr.utils.yml import YML_Reader, CSR_YML_Reader
from csr.utils.artifacts import CSRRoot, Walker
#from csr.schema.csr_tree import CSRTree

class Slurper(object):
    def __init__(self, cwd):
        self.cwd = cwd
        self.cmd_parser = argparse.ArgumentParser(description="CSR Slurper utility for F1")
        self.other_args = {}
        self.__arg_process(self.cmd_parser, self.other_args)

    def __arg_process(self, cmd_parser, other_args):
        ml = module_locator()
        def_dir = os.path.join(ml.module_path(), "csr_cfg")
        cmd_parser.add_argument("-i", "--csr-defs", help="CSR definitions", 
                default=def_dir, required=False, type=str)

        cmd_parser.add_argument("-o", "--gen-cc", help="Dir for the C++ files.", 
                required=True, type=str)

    def __update_loc(self, loc):
        if not os.path.isabs(loc):
            loc = os.path.join(self.cwd, loc)
        assert os.path.exists(loc), "{}: directory does not exist".format(loc)    
        return loc
    def __check_yml_dir(self, y_dir):
        yml_dir = os.path.join(y_dir, "yaml")
        if not os.path.exists(yml_dir):
            assert False, "Yaml directory: {} does not exist".format(yml_dir)
        
        if not os.path.isdir(yml_dir):
            assert False, "Yaml: {} not a directory".format(yml_dir)
        if not os.path.exists(os.path.join(y_dir, "AMAP")):
            assert False, "AMAP file does not exist"
        if not os.path.exists(os.path.join(y_dir, "ring_an.yaml")):
            assert False, "Ring file does not exist"

    def run(self):
        args = self.cmd_parser.parse_args()
        args.csr_defs = self.__update_loc(args.csr_defs)
        args.gen_cc = self.__update_loc(args.gen_cc)

        self.__check_yml_dir(args.csr_defs) 
        yml_dir = os.path.join(args.csr_defs, "yaml")
        amap_file = os.path.join(args.csr_defs, "AMAP")
        ring_file = os.path.join(args.csr_defs, "ring_an.yaml")
        self.root = None

        # First populate the top level root
        # Only populates the address attribute
        csr_rings = CSRRoot(amap_file)

        # Next, get the ring structure
        p = YML_Reader()
        yml_stream = p.read_file(ring_file)
        w = Walker(yml_stream)
        print "{}".format(w)
       
        # Next, setup the collection such that for every


        #self.__get_csrs(self.root, yml_dir)


        #self.schema = CSR_YML_Reader(yml_dir)
        #p = AMAP(amap_file, self.schema)


    def __str__(self):
        r_str = "{}".format(self.schema)
        return r_str
    
    __repr__ = __str__



