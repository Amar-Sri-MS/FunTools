#!/usr/bin/env python3

#
# ETW manifest to FunOS structured log generator.
#
# Emits a FunOS logging function for each event in
# an ETW manifest to stdout.
#

import argparse
import json
import os
import xml.etree.ElementTree as ET


import jinja2


class Event:
    """An ETW event"""

    def __init__(self, symbol, value, template_id, level, keywords):
        self.symbol = symbol
        self.value = value
        self.template_id = template_id
        self.keywords = keywords.split()
        self.level = level

    def __str__(self):
        return "sym: {} val: {} tid: {}".format(
            self.symbol, self.value, self.template_id
        )


class Template:
    """An ETW template"""

    def __init__(self, template_id):
        self.template_id = template_id
        self.items = []

    def add_data(self, data):
        self.items.append(data)

    def __str__(self):
        return "id: {} data: {}".format(self.template_id, str(self.items))


class Data:
    """Data item in an ETW template"""

    def __init__(self, name, intype, outtype):
        self.name = name
        self.intype = intype
        self.outtype = outtype

    def __str__(self):
        return "name: {} in: {} out: {}".format(self.name, self.intype, self.outtype)


class LogGen:

    def __init__(self, template_basename, typemap_basename, templates_by_id, keywords):
        self.templates_by_id = templates_by_id
        self.mask_by_keywords = keywords

        script_dir = os.path.dirname(__file__)
        self.jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(script_dir))
        self.jinja_tmpl = self.jinja_env.get_template(template_basename)
        self.type_map = self.create_type_mapping(typemap_basename)
        self.level_map = self.create_level_mapping()

    def create_type_mapping(self, typemap_basename):
        """ETW data types to FunOS log data types"""
        with open(typemap_basename, "r") as f:
            type_map = json.load(f)
            return type_map

    def create_level_mapping(self):
        """ETW levels to FunOS log severity"""
        return {
            "win:Critical": "CRIT",
            "win:Error": "ERR",
            "win:Warning": "WARNING",
            "win:Informational": "INFO",
            "win:Verbose": "DEBUG",
        }

    def generate(self, event):
        event_tid = event.template_id
        event_tmpl = None
        if event_tid and event_tid in self.templates_by_id:
            event_tmpl = self.templates_by_id[event_tid]
        tmpl_dict = {
            "evt": event,
            "evt_tmpl": event_tmpl,
            "evt_tmpl_size_empty": True if event_tmpl is None else False,
            "type_map": self.type_map,
            "keyword_map": self.mask_by_keywords,
            "level_map": self.level_map,
        }

        return self.jinja_tmpl.render(tmpl_dict, env=self.jinja_env)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", help="ETW (input) manifest")
    parser.add_argument(
        "--template", default="default_log.tmpl", help="output log template (jinja2)"
    )
    parser.add_argument(
        "--type-map", default="default_typemap.json", help="ETW to FunOS type mapping"
    )
    args = parser.parse_args()

    tree = ET.parse(args.manifest)
    root = tree.getroot()

    namespace = {"evt": "http://schemas.microsoft.com/win/2004/08/events"}
    provider = find_provider(tree, namespace)

    events = build_events(provider, namespace)
    templates_by_id = build_templates_by_id(provider, namespace)
    mask_by_keywords = build_keywords(provider, namespace)

    gen = LogGen(args.template, args.type_map, templates_by_id, mask_by_keywords)
    for event in events:
        print(gen.generate(event))


def find_provider(tree, namespace):
    """
    Find the provider element from the root of the manifest.
    Assumes only one provider (TODO needs to be fixed).
    """
    root = tree.getroot()
    ins = root.find("evt:instrumentation", namespace)
    evts = ins.find("evt:events", namespace)
    provider = evts.find("evt:provider", namespace)
    return provider


def build_events(provider, namespace):
    events = []
    events_elem = provider.find("evt:events", namespace)
    for event_elem in events_elem.findall("evt:event", namespace):
        attrs = event_elem.attrib
        keywords = attrs.get("keywords", "")
        tmpl = attrs.get("template", None)
        ev = Event(attrs["symbol"], attrs["value"], tmpl, attrs["level"], keywords)
        events.append(ev)
    return events


def build_templates_by_id(provider, namespace):
    templates_by_id = {}

    templates_elem = provider.find("evt:templates", namespace)
    for template_elem in templates_elem.findall("evt:template", namespace):
        attrs = template_elem.attrib
        if "tid" in attrs:
            tid = attrs["tid"]
            template = Template(tid)
            templates_by_id[tid] = template

            for data_elem in template_elem.findall("evt:data", namespace):
                d_attrs = data_elem.attrib
                data = Data(d_attrs["name"], d_attrs["inType"], d_attrs.get("outType"))
                template.add_data(data)

    return templates_by_id


def build_keywords(provider, namespace):
    keywords = {}
    keywords_elem = provider.find("evt:keywords", namespace)
    if keywords_elem is None:
        return keywords

    for kw_elem in keywords_elem.findall("evt:keyword", namespace):
        attrs = kw_elem.attrib
        keywords[attrs["name"]] = attrs["mask"]
    return keywords


if __name__ == "__main__":
    main()
