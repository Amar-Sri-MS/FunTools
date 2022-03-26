#
#  schema.py
#
#  Created by Hariharan Thantry on 2018-02-22
#
#  Copyright 2018 Fungible Inc. All rights reserved.


# Creates the entity schema

import collections
import logging
import re

from csr.utils.lex import Lexer, LexTok

# Top level record for YAML entity
# In this case, the Entity is a CSR Register

class Entity():
    def __init__(self):
        self.name = None
        self.addr = 0
        self.attr = 0
        self.type = "CSR_TYPE::REG"
        self.n_entries = 0
        self.stride_width = 0
        self.inst_size = 0
        self.fld_lst = []
        self.width = 0

    def __str__(self):
        r_str = ""
        r_str += "name:{}\n".format(self.name)
        r_str += "width: {}\n".format(self.width)
        r_str += "stride_width: {}\n".format(self.stride_width)
        r_str += "inst_size: {}\n".format(self.inst_size)
        r_str += "count: {}\n".format(self.count)
        r_str += "entries: {}\n".format(self.n_entries)
        r_str += "type: {}\n".format(self.type)
        r_str += " flds: {}\n".format(self.fld_lst)
        return r_str
    __repr__ = __str__


class Field():
    def __init__(self, fld_name, width):
        self.fld_name = fld_name
        self.width = width

    def __str__(self):
        r_str = ""
        r_str += "{}:{}".format(self.fld_name, self.width)
        return r_str

    __repr__ = __str__

class Schema():

    ALLOW_LST = ['REGLST', 'WIDTH', 'ATTR', 'COUNT', 'FLDLST', 'NAME',
                 'ENTRIES', 'ARRAY_BYTE_STRIDE', 'REPEAT_BYTE_STRIDE']
    #ALLOW_ATTR = [0x4, 0x8]
    ALLOW_ATTR = [0x4]
    MIN_WIDTH = 64
    def __init__(self, yml_stream, csr_def, csr_filter, logger=None):
        yml_stream = self.__sanitize(yml_stream)
        self.logger = logger or logging.getLogger(__name__)
        def_map = self.__create_map(csr_def)
        lexer = Lexer(def_map)
        lexer.build()

        self.entities = self.__create_schema(yml_stream, csr_filter, lexer)
        #self.__dump(yml_stream)
    def get(self):
        return self.entities

    def __create_map(self, csr_def_yml):
        m_coll = collections.OrderedDict()
        for key, val in csr_def_yml['ATTR'].items():
            m_coll[key] = LexTok(val)
        return m_coll

    def __match(self, regex_arr, m_elem):
        for elem in regex_arr:
            if re.match(elem, m_elem):
                return True
    def __should_store(self, m_elem, csr_filter, lexer):
        if not csr_filter:
            return True
        include_attr = csr_filter.get('include_attr', [])
        for elem in include_attr:
            v = lexer.eval(elem)
            if v ==  m_elem.attr:
                return True
        return False

    def __get_name(self, reg_rec):
        m_name = reg_rec['NAME'].split('_')
        if m_name[-1].isdigit():
            e_count = reg_rec.get('COUNT', 1)
            if e_count > 1:
                lst = m_name[:-1]
            else:
                lst = m_name
            m_name = '_'.join(elem for elem in lst)
        else:
            m_name = reg_rec['NAME']
        return m_name


    def __create_schema(self, yml_stream, csr_filter, lexer):
        m_hash = collections.OrderedDict()
        p_stream = yml_stream.get('REGLST', None)
        if not p_stream:
            p_stream = yml_stream.get('FLDLST', None)
        if not p_stream:
            return m_hash
        for reg_rec in p_stream:
            store = True
            base_name = reg_rec['NAME']
            if base_name in m_hash:
                self.logger.warning("Same CSR Name, {} appears multiple times".format(base_name))
                continue
            e = Entity()
            e.name = self.__get_name(reg_rec)
            e.attr = reg_rec.get('ATTR', 0)
            e.width = reg_rec.get('WIDTH', 0)
            e.n_entries = reg_rec.get('ENTRIES', 1)
            if (e.n_entries > 1):
                e.type = "CSR_TYPE::TBL"
            e.count = reg_rec.get('COUNT', 1)
            if not isinstance(e.count, int):
                self.logger.warning("CSR count is not integral. Ignoring {} CSR".format(e.name))
                store = False
            if (e.count > 1):
                e.type = "CSR_TYPE::REG_LST"

            lst = reg_rec.get('FLDLST', [])
            lst, e.width = self.__update_width(lst)
            for fld_elem in lst:
                e.fld_lst.append(Field(fld_elem['NAME'], fld_elem['WIDTH']))
            e.stride_width = reg_rec.get('ARRAY_BYTE_STRIDE', e.width/8)
            e.inst_size = reg_rec.get('REPEAT_BYTE_STRIDE', (e.stride_width * e.n_entries))
            store = store & self.__should_store(e, csr_filter, lexer)
            if store:
                m_hash[base_name] = e

        return m_hash

    def __update_width(self, lst):
        w = 0
        for fld in lst:
            w += fld['WIDTH']
        extra_w = 0
        if w%Schema.MIN_WIDTH:
            extra_w = Schema.MIN_WIDTH - w%Schema.MIN_WIDTH
        if extra_w:
            m_fld = collections.OrderedDict()
            m_fld['NAME'] = "__rsvd"
            m_fld['WIDTH'] = extra_w
            lst.append(m_fld)
        return lst, (w+extra_w)

    def __dump(self, yml_stream):
        for key, val in yml_stream.items():
            self.logger.debug("{}".format(key))

    def __sanitize(self, yml_stream):
        lst = []
        for key, val in yml_stream.items():
            if key not in Schema.ALLOW_LST:
                 lst.append(key)
        for key in lst:
            yml_stream.pop(key, None)
        lst = []
        for key, val in yml_stream.items():
            if isinstance(val, dict):
                return self.__sanitize(val)
            elif isinstance(val, list):
                m_val = self.__expand_list(val)
                lst.append([key, m_val])
        for rec in lst:
            yml_stream[rec[0]] = rec[1]

        return yml_stream

    def __expand_list(self, lst):
        m_lst = []
        r_idx = []
        for idx, elem in enumerate(lst):
            if isinstance(elem, dict):
                m_elem = self.__sanitize(elem)
                m_lst.append(m_elem)
                r_idx.append(idx)
            elif isinstance(elem, list):
                lst = self.__expand_list(self, lst)
        for idx, elem in enumerate(r_idx):
            lst[elem] = m_lst[idx]
        return lst

    def __str__(self):
        r_str = ""
        for val in self.entities.values():
            r_str += "{}".format(val)
        return r_str
    __repr__ = __str__



