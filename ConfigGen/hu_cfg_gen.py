#!/usr/bin/env python2.7

# -*- coding: utf-8 -*-
"""Utilities for C code generation from JSON config

This module generates C struct from JSON config.

Todo:
    * add compile test
    *

.. _Google Python Style Guide:
   http://google.github.io/styleguide/pyguide.html

"""

import glob, os, sys, re, datetime
from string import Template
import logging, sys
import json
import jsonutils
import tempfile
from itertools import chain

from pprint import pprint

logger = logging.getLogger("hu_cfg_gen")
logger.setLevel(logging.INFO)

class HUCfgGen():
    """ HU Code generation class

    This class creates merged hu config and generates c struct from JSON configuration

    Args:
        config_dict (dict): configuration dict from JSON
        schema_dict (dict): schema dictionary

    Attributes:
        config_dict (dict): configuration dict from JSON
        schema_dict (dict): schema dictionary
        struct_def (dict): struct definition, dimension and index sizes
        output_dir (str): output dir
    """

    def __init__(self, input_dir, output_dir):
        self.config_dict = dict()
        self.schema_dict = dict()
        self.struct_defs = {}
        self.output_dir = output_dir
        self.input_dir = input_dir

    def _get_array_dim_info(self, struct_obj, k, _args_v):
        """ parse array dim information and populate dict

        parse array dimension information

        :param struct_obj:
        :param v: array values to parse
        :return:
        """

        items = _args_v['items']

        assert isinstance(items, list)

        struct_obj["name"] = k
        struct_obj["dim"] = len(items)

        for i, v_items in enumerate(items):
            assert 'oneOf' in list(v_items.keys())
            oneof_list = v_items['oneOf']

            for l in oneof_list:
                if l["type"] != "integer":
                    continue

                if l["maximum"] == 0 and l["minimum"] == 0:
                    # if max and min both 0, then create array of 2
                    # this is for hu _args based indexing on 'all' or 0
                    struct_obj["index_"+str(i)] = 1 + 1 # maximum and minimum was inclusive, so +1 to get the size
                else:
                    struct_obj["index_"+str(i)] = l["maximum"] + 1


    def _gets_array_dim_size(self, struct_def, terminal_char):
        """" return array dimension string for struct

        Args:
            struct_def(dict): struct_def dict holds dimension and array index
            terminal_char: terminal chars

        return:
            terminal strings
        """

        if struct_def['dim'] == 0:
            trail_str = "%s\n" % terminal_char
        else:
            dim = struct_def['dim']

            trail_str = ""
            for i in range(dim):
                trail_str += "[%d]" % struct_def['index_' + str(i)]

            trail_str += "%s\n" % terminal_char

        return trail_str

    def _gets_struct_def_field(self, k, v, obj_key, struct_def, int_field, enum_field, bool_field, int_array_field,
                               enum):
        """ generate string for struct entries for header

        :param k:
        :param v:
        :param obj_key:
        :param struct_def: struct def dict
        :param str_field:
        :param int_field:
        :param enum_field:
        :param bool_field:
        :param int_array_field:
        :param enum:
        :return:
        """

        str_field = ""
        enum_def_str = ""

        v_type = v['type']

        if v_type == "integer":
            str_field = int_field.substitute(fname=k)
            struct_def[k] = 'int'
        elif (v_type == "string") and ('enum' in v):
            v_enum = v['enum']
            assert isinstance(v_enum, list)
            struct_def[k] = 'enum ' + obj_key + "_" + k
            enum_def_field_str = ""
            for l in v_enum:
                enum_def_field_str += "\t" + l + ",\n"
            # enum field
            str_field = enum_field.substitute(ename=obj_key + "_" + k, fname=k)
            # enum definition
            enum_def_str += enum.substitute(ename=obj_key + "_" + k, field=enum_def_field_str)
            logger.debug("ENUM")
            logger.debug(enum_def_str)
        elif v_type == "boolean":
            struct_def[k] = 'bool'
            str_field = bool_field.substitute(fname=k, value=v["type"])
        elif v_type == "array":
            struct_def[k] = 'int[]'
            array_type = v["items"]["type"]
            assert array_type == "integer"
            array_max = v["maxItems"]
            str_field = int_array_field.substitute(fname=k, max=array_max)
        else:
            logger.error('unknown type: {}'.format(v_type))
            assert False

        return str_field, enum_def_str

    def _parse_schema(self, obj_key, obj_properties, maxItem, struct_def):
        """ parse schema

        Args:
            obj_key:
            obj_properties: object property value
            maxItem: array size
            struct_def: dict for struct object generation

        Return:
            struct definition string

        """

        # enum definition
        enum = Template('enum $ename {\n$field};\n\n')
        # struct definition
        struct_tmpl = Template('$enum_def\n\nstruct $sname {\n$fields\n};\n\n$extern\n')

        # extern definition
        extern_tmpl = Template("extern struct $sname $name$trail")

        # struct int field
        int_field = Template('\t' + 'int $fname;\n')
        # struct enum field
        bool_field = Template('\t' + 'bool $fname;\n')
        # struct int array field
        int_array_field = Template('\t' + 'int $fname[$max];\n')
        # struct enum field
        enum_field = Template('\t' + 'enum $ename $fname;\n')

        # temporary string, struct def string, enum def string, extern def string
        str_field, struct_def_str, enum_def_str, extern_str = "", "", "", ""

        struct_name = obj_key
        struct_def["dim"] = 0

        for k, v in list(obj_properties.items()):
            if k == "_args":
                # _args is used in FunOS internal indexing, so skip generating this field
                self._get_array_dim_info(struct_def, k, v)
                continue

            (s_field, e_def_str) = self._gets_struct_def_field(k, v, obj_key, struct_def, int_field,
                                        enum_field, bool_field, int_array_field, enum)
            str_field += s_field
            enum_def_str += e_def_str
            logger.debug(enum_def_str)

        trail_str = self._gets_array_dim_size(struct_def, ";")

        extern_str += extern_tmpl.substitute(sname=struct_name + "_cfg",
                                        name=struct_name, trail=trail_str)

        struct_def_str += struct_tmpl.substitute(sname=struct_name + "_cfg",
                                        fields=str_field, enum_def=enum_def_str,
                                        extern=extern_str)

        return struct_def_str

    def _generate_header(self, cfg_name, key_to_gen):
        """ generate header file

        Args:
            cfg_name (string): string name for config object used for comment and file name
            key_to_gen (list): json configuraiton objects to generate code
            output_dir (string): dir for output .h .c files
        """
        struct_defs_str = ""
        obj_maxitems = 0

        schema_properties = self.schema_dict["properties"]['HuInterface']

        logger.debug('Generating config data header file: {}'.format(cfg_name))
        file_tmpl = Template('// Source file auto generated by ' + __file__ + ' at $date \n'\
                              '// DO NOT change this file\n\n'\
                              '#pragma once\n\n\n#include <stdbool.h>\n$data\n')

        header_file = cfg_name + ".h"
        f = open(os.path.join(self.output_dir, header_file), 'w')

        # go through type entry to generate struct
        for k, v in list(schema_properties.items()):
            if k not in key_to_gen:
                logger.info('NOT found: {}'.format(k))
                continue

            obj_type = v['type']

            if obj_type == 'object':
                assert "properties" in v
                obj_properties = v['properties']

            elif obj_type == 'array':
                assert "items" in v
                assert "maxItems" in v
                obj_items = v['items']

                assert "properties" in obj_items
                obj_properties = obj_items['properties']
                obj_maxitems = v['maxItems']

            else:
                logger.error('ERROR: unsupported type: {}'.format(obj_type))
                assert False

            self.struct_defs[k] = {}
            struct_def = self.struct_defs[k]
            struct_defs_str += self._parse_schema(k, obj_properties, int(obj_maxitems), struct_def)

            if 'dim' in list(struct_def.keys()):
                logger.debug(k, " obj dim len %d" % struct_def['dim'])
            else:
                logger.error("NO dim len %k", k)
                assert False

        f.write(file_tmpl.substitute(data=struct_defs_str,
                    date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
        f.close()

    def _set_parse_dict(self, parse_dict, name, is_exist, start, end):
        """  set parse_dict
        :param parse_dict: set
        :param name:
        :param is_exist:
        :param start:
        :param end:
        :return:
        """
        parse_dict[name] = is_exist
        parse_dict["%s_start" % name] = start
        parse_dict["%s_end" % name] = end

    def _init_parse_dict(self, parse_dict):
        """ init parse_dict

        :param parse_dict:
        :return:
        """
        parse_dict["huid"] = False
        parse_dict["ctrl"] = False
        parse_dict["pf"] = False
        parse_dict["vf"] = False

    def _parse_args(self, _args, parse_dict, struct_def):
       """ parse "_args index"

       Args:
           _arrgs: list of indexes
           parse_dict: dict to store parse
           struct_def: struct definitions

       """
       assert isinstance(_args, list)

       self._init_parse_dict(parse_dict)

       for i, l in enumerate(_args):
            _arg = l
            logger.debug('_args {} type {}'.format(_args, type(_args)))
            if not isinstance(_arg, int):
                if _arg != "all":
                    logger.error('only allowed _arg is [all], but found: {}'.format(_arg))
                    assert False

                if i == 0:
                    assert "index_0" in list(struct_def.keys())
                    self._set_parse_dict(parse_dict, "huid", True, 0, struct_def["index_0"])
                elif i == 1:
                    assert "index_1" in list(struct_def.keys())
                    self._set_parse_dict(parse_dict, "ctrl", True, 0, struct_def["index_1"])
                elif i == 2:
                    assert "index_2" in list(struct_def.keys())
                    self._set_parse_dict(parse_dict, "pf", True, 0, struct_def["index_2"])
                elif i == 3:
                    assert "index_3" in list(struct_def.keys())
                    self._set_parse_dict(parse_dict, "vf", True, 0, struct_def["index_3"])
                else:
                    logger.error("too many nested index, %d", i)
                    assert False

            else:
                if i == 0:
                    self._set_parse_dict(parse_dict, "huid", True, _arg, _arg + 1)
                elif i == 1:
                    self._set_parse_dict(parse_dict, "ctrl", True, _arg, _arg + 1)
                elif i == 2:
                    self._set_parse_dict(parse_dict, "pf", True, _arg, _arg + 1)
                elif i == 3:
                    self._set_parse_dict(parse_dict, "vf", True, _arg, _arg + 1)
                else:
                    assert False


    def _get_start_end_index(self, _args_dict, name):
        """ get start and end index

        Args:
            _args_dict: _args dict
            name: start and end name
        return:
            start and end
        """

        if _args_dict[name]:
            start = _args_dict["%s_start" % name]
            end = _args_dict["%s_end" % name]
        else:
            start = 0
            end = 1

        return start, end

    def _gets_list_string(self, v):
        """ generate string for list

        :param v: list
        :returns list string
        """

        val = "{"
        for l1 in v:
            val += "%d, " % l1
        val += "}"

        return val

    def _gets_array_index(self, _args_dict, huid, ctrl, pf, vf):
        """ generate string for array index

        :param _args_dict : argument dict
        :param huid
        :param ctrl
        :param pf
        :param vf

        :return array index string
        """

        index_str = ""
        if _args_dict["huid"]:
            index_str += "[%d]" % huid
        if _args_dict["ctrl"]:
            index_str += "[%d]" % ctrl
        if _args_dict["pf"]:
            index_str += "[%d]" % pf
        if _args_dict["vf"]:
            index_str += "[%d]" % vf

        return index_str

    def _gets_entry_val(self, k, v, struct_def):
        """ get string of struct entry
        :param k : key
        :param v : value
        :param struct_def (dict): struct definition dict

        :return converted string
        """

        v_type = struct_def[k]

        if v_type == "int":
            val = "0x%x" % v
        elif v_type.startswith("enum"):
            val = v
        elif v_type == "bool":
            val = str(v).lower()
        elif v_type == "int[]":
            assert isinstance(v, list)
            val = self._gets_list_string(v)
        else:
            logger.error('no matching: {}'.format(v_type))
            assert False

        return val

    def _populate_struct(self, struct_key, struct_val):
        """" generate array of HostUnit contents
        Args:
            struct_key: struct name in string
            struct_val (list): struct contents

        return: struct array string
        """

        struct_def = self.struct_defs[struct_key]
        struct_dict = {}

        # struct head definition
        struct_contents_tmpl = Template("\n\t$index = {\n$content\n\t},")

        for l in struct_val:
            # _args_parse
            _args_dict = {}
            _args = l["_args"]
            self._parse_args(_args, _args_dict, struct_def)
            huid_start, huid_end = self._get_start_end_index(_args_dict, "huid")

            for huid in range(huid_start, huid_end):
                ctrl_start, ctrl_end = self._get_start_end_index(_args_dict, "ctrl")

                for ctrl in range(ctrl_start, ctrl_end):
                    pf_start, pf_end = self._get_start_end_index(_args_dict, "pf")

                    for pf in range(pf_start, pf_end):
                        vf_start, vf_end = self._get_start_end_index(_args_dict, "vf")

                        for vf in range(vf_start, vf_end):
                            struct_content_str = ""
                            """
                            # TODO dafault value handle
                            hw_instance_set = False
                            """

                            for k, v in list(l.items()):
                                # _args are already taken care of as array index
                                if k == "_args":
                                    continue

                                if k not in list(struct_def.keys()):
                                    logger.debug('No matching key: {}'.format(k))
                                    continue

                                # default value update
                                """
                                if k == "hw_instance":
                                    hw_instance_set = True
                                    logger.info('({} {} {} {}) hw_instance: {}'.format(huid, ctrl, pf, vf, v))
                                """

                                val = self._gets_entry_val(k, v, struct_def)
                                struct_content_str += "\t\t.%s = %s,\n" % (k, val)

                            """
                            # by default hw_instance is true
                            if not hw_instance_set:
                                struct_content_str += "\t\t.%s = %s,\n" % ("hw_instance", "true")
                            """

                            index_str = self._gets_array_index(_args_dict, huid, ctrl, pf, vf)
                            struct_dict["%s" % index_str] = struct_content_str

        tmpstr = ""

        for k, v in list(struct_dict.items()):
            tmpstr += struct_contents_tmpl.substitute(index=k, content=v)

        return tmpstr

    def _gets_struct_array(self, struct_key, struct_val):
        """" generate array of struct contents
        Args:
            struct_key: struct name in string
            struct_val (list): struct contents

        return: struct array string
        """

        struct_array = ""

        if struct_key == "HostUnit" or struct_key == "HostUnitController" or struct_key == "HostUnitFunction":
            struct_array += self._populate_struct(struct_key, struct_val)
            return struct_array

        logger.error('Unknown struct_key: {}'.format(struct_key))
        assert False

    def _gets_c_struct_head(self, k, v, struct_head_tmpl):
        """ return string for struct head for c file

        :param k:
        :param v:
        :param struct_head_tmpl:
        :return:
        """

        struct_def = self.struct_defs[k]
        # dim = struct_def['dim']

        trail_str = self._gets_array_dim_size(struct_def, " = {")
        struct_head_str = struct_head_tmpl.substitute(sname=k + "_cfg", name=k, trail=trail_str)
        # struct_objs_str += struct_head_str

        return struct_head_str


    def _generate_struct_entry(self, v, struct_def):
        """ populate string for struct entries in C file

        :param v:
        :param struct_def:
        :return:
        """

        struct_objs_str = ""
        for k_e, v_e in list(v.items()):
            if struct_def[k_e] == 'int':
                struct_objs_str += "\t.%s = 0x%x,\n" % (k_e, v_e)

        return struct_objs_str


    def generate_config(self):
        """ Generate merged hu config from all global hu configs"""

        logger.debug('Generating merged hu config from all global configs')
        hu_cfg = dict()
        file_pattern_list = ['hu_config/*.cfg']

        for file_pattern in file_pattern_list:
            for cfg in glob.glob(os.path.join(self.input_dir, file_pattern)):
                logger.debug('Processing {}'.format(cfg))
                cfg_json = jsonutils.load_fungible_json(cfg)
                hu_cfg = jsonutils.merge_dicts(hu_cfg, cfg_json)
        logger.debug("DONE: Generating HU C code: generate_hu_cfg")
        return hu_cfg

    def generate_code(self):
        """ Generate c header and source"""

        logger.debug("Generating HU header code: generate_hu_cfg")
        hu_cfg = dict()
        file_pattern_list = ['hu_config/*.schema']

        for file_pattern in file_pattern_list:
            for cfg in glob.glob(os.path.join(self.input_dir, file_pattern)):
                logger.debug('Processing {}'.format(cfg))
                cfg_json = jsonutils.load_fungible_json(cfg)
                hu_cfg = jsonutils.merge_dicts(hu_cfg, cfg_json)

        # get the schema dict
        self.schema_dict = hu_cfg["Schema"]

        # keys to generate HU CONFIG C code
        key_to_gen = [
            'HostUnits',
            'HostUnit',
            'HostUnitController',
            'HostUnitFunction',
        ]

        # generate C code
        cfg_name = "hu_cfg"
        self._generate_header(cfg_name, key_to_gen)

