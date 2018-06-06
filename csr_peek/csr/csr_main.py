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
import os
from module_path import module_locator
from csr.utils.yml import YML_Reader, CSR_YML_Reader
from csr.utils.artifacts import CSRRoot, Walker, RingUtil, TmplMgr
from csr.utils.utilities import Filer, Compiler

class Slurper(object):
    def __init__(self, cwd):
        self.cwd = cwd
        self.cmd_parser = argparse.ArgumentParser(description="CSR Slurper utility for F1")
        self.other_args = {}
        self.__arg_process(self.cmd_parser, self.other_args)

    def __arg_process(self, cmd_parser, other_args):
        ml_dir = module_locator().module_path()
        cmd_parser.add_argument("-d", "--csr-defs", help="CSR definitions", required=True, type=str)
        cmd_parser.add_argument("-g", "--gen-lib", help="Generate the CSR library", action='store_true')

        cmd_parser.add_argument("-l", "--lib-dir", help="Output directory for generated lib & include",
                required=False, default=self.cwd, type=str)

        cmd_parser.add_argument("-i", "--inc-dir", help="Output directory for generated lib & include",
                required=False, default=self.cwd, type=str)

        cmd_parser.add_argument("-c", "--cfg-dir", help="Output directory for JSONs", required=False,
                default=self.cwd, type=str)

        cmd_parser.add_argument("-t", "--temp-dir", required=False,
                help="Output directory for generated temporaries",type=str)

        cmd_parser.add_argument("-k", "--keep-temps", required=False,
                help="Keep generated artifacts", action='store_true')

        def_filter = os.path.join(ml_dir, "template", "csr_filter.yaml")
        cmd_parser.add_argument("-f", "--filter-file", help="Filter YAML file, usually required for compiles to pass",
                default=def_filter, required=False, type=str)

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

        #print "{}".format(self.schema)
        # First populate the top level root
        # Only populates the address attribute
        p = YML_Reader()
        csr_def = p.read_file(self.other_args['csr_defs'])
        print "Filter file: {}".format(args.filter_file)
        filter_def = p.read_file(args.filter_file)

        # Pass to CSR Yaml reader, a list of included & excluded CSRs
        # If a CSR is included by name, ignore the attribute

        schema = CSR_YML_Reader(yml_dir, filter_def, csr_def)

        self.csr_root = CSRRoot(amap_file, schema.get(), filter_def)
        file_mkr = Filer()
        file_mkr.mkdir(args.cfg_dir)
        o_file = os.path.join(args.cfg_dir, 'csr_metadata.json')
        with open(o_file, "w") as fp:
            fp.write(json.dumps(self.csr_root.get_csr_metadata(), indent=4))

        self.args = args
        print "[Written Config]: {}".format(o_file)

        # Next, get the ring structure
        #p = YML_Reader()
        #yml_stream = p.read_file(ring_file)
        #w = Walker(yml_stream)
        #print "{}".format(w)

    def __get_files(self, dirname, ext):
        f_lst = []
        for m_file in os.listdir(dirname):
            if m_file.endswith(ext):
                f_lst.append(os.path.join(dirname, m_file))
        return f_lst
    def __create_dirs(self, args):
        args.lib_dir = self.__update_loc(args.lib_dir)
        args.inc_dir = self.__update_loc(args.inc_dir)
        if not args.temp_dir:
            args.temp_dir = "/tmp/csr.{}".format(os.getpid())
        else:
            args.temp_dir=self.__update_loc(args.temp_dir)
        file_mkr = Filer()

        file_mkr.mkdir(args.lib_dir)
        file_mkr.mkdir(args.inc_dir)
        file_mkr.mkdir(args.temp_dir)
    def __compile(self, tmp_files):

        base_dir = os.path.join(self.ml_dir, "libcsr")
        src_dir = os.path.join(base_dir, "src")
        src_files = self.__get_files(src_dir, ".cpp")
        lst = [m_file for m_file in tmp_files if m_file.endswith(".cpp")]
        src_files.extend(lst)

        inc_dir = [os.path.join(base_dir, "include")]
        tmp_dir = []
        for m_file in tmp_files:
            if not m_file.endswith(".h"):
                continue
            dir_name = os.path.dirname(m_file)
            if dir_name not in tmp_dir:
                tmp_dir.append(dir_name)
        inc_dir.extend(tmp_dir)

        m_cpp = Compiler()
        m_cpp.clean_files(tmp_files)
        m_cpp.build_lib("libcsr", "static",
                src_files, inc_dir, self.args.lib_dir, self.args.inc_dir)

    def __clean(self, tmp_files):
        dirs = []
        for m_file in tmp_files:
            basedir = os.path.dirname(m_file)
            if basedir == self.args.lib_dir or \
                    basedir == self.args.inc_dir:
                        continue
            if os.path.exists(m_file):
                print "Removing tmp: {}".format(m_file)
                os.remove(m_file)
            if not basedir in dirs:
                dirs.append(basedir)
        for dirname in dirs:
            if os.listdir(dirname):
                continue
            print "Removing directory: {}".format(dirname)
            os.rmdir(dirname)

    def compile(self):

        if not self.args.gen_lib:
            print "Not generating CSR lib"
            return
        self.__create_dirs(self.args)

        cc_file = os.path.join(self.args.temp_dir, 'csr_gen.cpp')
        tmpl = TmplMgr(self.other_args['tmpl_file'])
        tmpl.write_cfg(cc_file, self.csr_root)
        self.__compile([cc_file])
        if self.args.keep_temps:
            return
        self.__clean([cc_file])

    def __str__(self):
        r_str = "{}".format(self.schema)
        return r_str

    __repr__ = __str__

