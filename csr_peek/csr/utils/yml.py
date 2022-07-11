#
#  yml.py
#
#  Created by Hariharan Thantry on 2017-07-06
#
#  Copyright  2017 Fungible Inc. All rights reserved.
#
import collections
import copy
import glob
import logging
import os
import pdb
import re
import yaml

from csr.utils.schema import Schema


def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=collections.OrderedDict):
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            construct_mapping)
    return yaml.load(stream, OrderedLoader)

class CSR_YML_Reader(object):
    ALLOW_LST = ['REGLST', 'WIDTH', 'ATTR', 'FLDLST']
    def __init__(self, dirname, filter_yml, csr_def, logger=None):
        self.logger = logger or logging.getlogger(__name__)
        self.__read_dir(dirname, filter_yml, csr_def)

    def __read_dir(self, dirname, filter_yml, csr_def):
        self.csr_schema = collections.OrderedDict()
        for yml_file in glob.glob(os.path.join(dirname, '*.yaml')):
            f_name = os.path.splitext(os.path.basename(yml_file))[0]
            self.logger.info("Processing \'{}\'".format(f_name))
            yml_stream = self.__read_file(yml_file)
            f_name = re.sub('(_an)|(_AN)', '', f_name)
            self.csr_schema[f_name.lower()] = Schema(yml_stream, filter_yml, csr_def)

    def __dump(self, yml_stream):
        lst = []
        for key, val in yml_stream.items():
            self.logger.debug("{}:".format(key))
            if isinstance(val, dict):
                self.__dump(val)
            elif isinstance(val, list):
                self.__dump_lst(val)
            else:
                self.logger.debug("{}:{}\n".format(key, val))
    def __dump_lst(self, lst):
        for elem in lst:
            if isinstance(elem, list):
                self.__dump_lst(elem)
            if isinstance(elem, dict):
                self.__dump(elem)
            else:
                self.logger.debug("{}\n".format(elem))

    def __remove_symbols(self, m_dict, allow_lst):
        m_lst = []
        for key, val in m_dict.items():
            if key not in allow_lst:
                m_lst.append(key)

        for key in m_lst:
            m_dict.pop(key, None)

        for key, val in m_dict.items():
            if isinstance(val, dict):
                m_dict = self.__remove_symbols(val, allow_lst)
        return m_dict

    def __read_file(self, f_name):
        yml_stream = None
        p = YML_Reader()
        yml_stream = p.read_file(f_name)
        assert yml_stream != None, "YAML Load issues for file: {}".format(f_name)
        yml_stream = self.__remove_symbols(yml_stream, CSR_YML_Reader.ALLOW_LST)
        return yml_stream

    def get(self):
        return self.csr_schema

    def __str__(self):
        r_str = ""
        for key, val in self.csr_schema.items():
            r_str += "{}:\n{}".format(key, val)
        return r_str
    __repr__ = __str__


class YML_Reader(object):
    def __init__(self, logger=None):
        pass
    def read_file(self, f_name):
        yml_stream = None
        with open(f_name, 'r') as r_stream:
            yml_stream = ordered_load(r_stream)
        return yml_stream


