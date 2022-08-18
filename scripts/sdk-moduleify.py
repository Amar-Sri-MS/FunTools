#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generic python command-line boilerplate with mypy annotations
 
static check:
% mypy myfile.py
 
format:
% python3 -m black myfile.py
"""

from typing import List, Optional, Type, Dict, Any, Tuple
import argparse
from comby import Comby
 
# global comby object
comby = Comby(language=".c")

###
##  processing file contents
#

MOD_BEGIN: str = "MODULE_DEFINITION_BEGIN(:[modname])"
MOD_END: str = "MODULE_DEFINITION_END()"

REF_MATCH: str = "MODULE_REFERENCE(:[modname])"

NEW_MOD_BEGIN  = "MODULE_DEF_BEGIN("
NEW_DEP_INDENT = " " * len(NEW_MOD_BEGIN)

# make sure to include a trailing semi
DEP_MATCH: str = "MODULE_DECLARE_DEPENDENCY(:[depname]):[semi~;?]"
DEP_REWRITE: str = NEW_DEP_INDENT + ", MODULE_DEP(:[depname])"

# list of (MATCH, REWRITE, prototype) for other properties
PROPS = [
    ("MODULE_DECLARE_COMMANDER_INIT(:[fn]):[semi~;?]",
     "MODULE_DEC_COMMANDER_INIT(:[fn])",
     "void {}(void);"),

    ("MODULE_DECLARE_DIRECT_INIT(:[fn]):[semi~;?]",
     "MODULE_DEC_DIRECT_INIT(:[fn])",
     "void {}(const struct fun_json *config_json);"),

    ("MODULE_DECLARE_METAFLOW_RESOURCE_TYPE(:[fn]):[semi~;?]",
     "MODULE_DEC_METAFLOW_RESOURCE_TYPE(:[fn])",
     "void {}(const struct hu_fn_params *params, OUT struct metaflow_resource_params *res_params);"),

    ("MODULE_DECLARE_PROPS_BRIDGE_INIT(:[fn]):[semi~;?]",
     "MODULE_DEC_PROPS_BRIDGE_INIT(:[fn])",
     "void {}(void);"),

    ("MODULE_DECLARE_CONFIG_JSON_UPDATED(:[fn]):[semi~;?]",
     "MODULE_DEC_CONFIG_JSON_UPDATED(:[fn])",
     "void {}(struct module *);"),

    ("MODULE_DECLARE_ISSU_DRAIN(:[fn]):[semi~;?]",
     "MODULE_DEC_ISSU_DRAIN(:[fn])",
     "enum fun_ret {}(void);"),

    ("MODULE_DECLARE_ISSU_QUIESCE(:[fn]):[semi~;?]",
     "MODULE_DEC_ISSU_QUIESCE(:[fn])",
     "enum fun_ret {}(void);"),

    ("MODULE_DECLARE_ISSU_SAVE_STATE(:[fn]):[semi~;?]",
     "MODULE_DEC_ISSU_SAVE_STATE(:[fn])",
     "void {}(struct fun_json *);"),

    ("MODULE_DECLARE_UNLOAD(:[fn]):[semi~;?]",
     "MODULE_DEC_UNLOAD(:[fn])",
     "void {}(void);"),

    ("MODULE_DECLARE_TERMINATE(:[fn]):[semi~;?]",
     "MODULE_DEC_TERMINATE(:[fn])",
     "void {}(void);"),

]

def is_preproc_line(line: str) -> bool:
    if (line.strip()[:1]  == "#"):
        return True

    return False

def is_ref_line(line: str) -> bool:
    return len(list(comby.matches(line, REF_MATCH))) > 0

def is_dep_line(line: str) -> bool:
    deps = list(comby.matches(line, DEP_MATCH))

    # no match
    if (len(deps) == 0):
        return False

    assert(len(deps) == 1)

    depname = deps[0].environment["depname"].fragment
    print("\t\tFound dependency on '%s'" % depname )

    return True

def rewrite_dep_line(line: str) -> str:
    return comby.rewrite(line, DEP_MATCH, DEP_REWRITE)

def rewrite_other_line(line: str) -> str:
    
    for (match, rewrite, pline) in PROPS:
        ms = list(comby.matches(line, match))
        if (len(ms) == 0):
            # no match
            continue

        proto = None
        m = ms[0]
        newline = comby.rewrite(line, match, rewrite)
        print("\t\tRewrite '%s' -> '%s'" % (m.matched, newline.rstrip()))
        if (pline is not None):
            funcname = m.environment["fn"].fragment
            proto = pline.format(funcname) + "\n"
        return (newline, proto)

    # make sure there's no stray module definitions
    assert(len(list(comby.matches(line, "MODULE_"))) == 0)

    return (line, None)



def rewrite_defn(comby, modname:str, defn: str) -> str:

    protos = ""
    deps = ""
    body = "\n"
    foot = ""

    # process the definition line-by-line
    lines = defn.split("\n")

    for line in lines:
        # restore the \n
        line += "\n"
        if (is_preproc_line(line)):
            if (deps == ""):
                deps = "\n"
            deps += line
            body += line
        elif (is_ref_line(line)):
            # badly placed module references
            if (foot == ""):
                foot = "\n"
            foot += line
        elif (is_dep_line(line)):
            if (deps == ""):
                deps = "\n"
            deps += rewrite_dep_line(line)
        else:
            (b, p) = rewrite_other_line(line)
            body += b
            if (p is not None):
                protos += p


    if (protos != ""):
        protos = "/* auto-generated module declaration function prototypes */\n" + protos + "\n\n"

    print("protos: '%s'" % protos)
    print("deps: '%s'" % deps)
    print("body: '%s'" % body)

    new_defn = protos
    new_defn += NEW_MOD_BEGIN + modname + deps + ")"
    new_defn += body.rstrip()
    new_defn += "\nMODULE_DEF_END()"
    new_defn += foot
    new_defn += "\n"

    return new_defn

def process_file(source: str) -> Optional[str]:

    # find if there's a module definition
    begins = list(comby.matches(source, MOD_BEGIN))
    ends = list(comby.matches(source, MOD_END))

    if ((len(begins) == 0) and (len(ends) == 0)):
        print("\tFile lacks module definition")
        return None

    if ((len(begins) != 1) or (len(ends) != 1)):
        print("\tFile has multiple/corrupt module definitions")
        return None

    # the span
    begin = begins[0]
    end = ends[0]

    # extract the module name
    #print("env: %s" % begin.environment)
    modname = begin.environment["modname"].fragment
    print("\tFound module %s" % modname)

    # split the file into three
    pre = source[:begin.location.start.offset-1]
    defn = source[begin.location.stop.offset:end.location.start.offset-1]
    post = source[end.location.stop.offset:]

    if ("MODULE_WU_DEF_INCLUDE" in defn):
        print("\tXXX: File has MODULE_WU_DEF_INCLUDE, cannot process")
        return None

    # print it
    #print("pre: '%s'" % pre[-100:])
    #print("defn: '%s'" % defn)
    #print("post: '%s'" % post[:100])

    # re-write the definition
    new_defn = rewrite_defn(comby, modname, defn)

    # print("new defn: '%s'" % new_defn)

    # return it
    return pre + new_defn + post

###
##  parse_args
#
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
 
    # Files
    parser.add_argument("files", nargs="+", help="Files to process")
 
    # Whether to update files
    parser.add_argument("-s", "--sure", action="store_true", default=False)
 
    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Verbosity (-v, -vv, etc)")
 
    args: argparse.Namespace = parser.parse_args()
    return args
 
###
##  main
#
def main() -> int:
    args: argparse.Namespace = parse_args()

    for fname in args.files:
        print("Processing file '%s'" % fname)

        input = open(fname).read()
        output = process_file(input)

        if (output) is None:
            print("\tNo legacy module declaration, ignoring")
            continue

        if (args.sure):
            print("\tUpdating file...")
            open(fname, "w").write(output)
            print("\tDone")
        else:
            print("\tSkipping file update")

    return 0
 
###
##  entrypoint
#
if __name__ == "__main__":
    main()
