#
#  schema.py
#
#  Created by Hariharan Thantry on 2018-02-22
#
#  Copyright 2018 Fungible Inc. All rights reserved.
#

# Creates the entity schema

import collections

# Top level record for YAML entity
# In this case, the Entity is a CSR Register

class Entity():
    def __init__(self):
        self.addr = 0
        self.attr = 0
        self.fld_lst = []
        self.width = 0
    def __str__(self):
        r_str = ""
        r_str += "    attr: {}\n".format(self.attr)
        r_str += "    w: {}\n".format(self.width)
        r_str += "    flds: {}\n".format(self.fld_lst)
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

    ALLOW_LST = ['REGLST', 'WIDTH', 'ATTR', 'FLDLST', 'NAME']
    ALLOW_ATTR = [0x4, 0x8]
    def __init__(self, yml_stream):
        self.schema = collections.OrderedDict()
        yml_stream = self.__sanitize(yml_stream)
        self.entities = self.__create_schema(yml_stream)
        #self.__dump(yml_stream)

    def __create_schema(self, yml_stream):
        m_hash = collections.OrderedDict()
        if not 'REGLST' in yml_stream:
            return
        p_stream = yml_stream['REGLST']
        for reg_rec in p_stream:
            assert reg_rec['NAME'] not in m_hash, "Duplicate CSR Names"
            e = Entity()
            e.attr = reg_rec.get('ATTR', 0)
            e.width = reg_rec.get('WIDTH', 0)
            lst = reg_rec.get('FLDLST', [])
            for fld_elem in lst:
                e.fld_lst.append(Field(fld_elem['NAME'], fld_elem['WIDTH']))
            store = False
            for elem in Schema.ALLOW_ATTR:
                if int(e.attr) & elem:
                    store = True
            if store:
                m_hash[reg_rec['NAME']] = e
        return m_hash

    def __dump(self, yml_stream):
        for key, val in yml_stream.iteritems():
            print "{}".format(key)

    def __sanitize(self, yml_stream):
        lst = []
        for key, val in yml_stream.iteritems():
            if key not in Schema.ALLOW_LST:
                 lst.append(key)
        for key in lst:
            yml_stream.pop(key, None)
        lst = []
        for key, val in yml_stream.iteritems():
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
        for key, val in self.entities.iteritems():
            r_str += "  {}:\n{}".format(key, val)
        return r_str
    __repr__ = __str__



