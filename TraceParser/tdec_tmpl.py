#!/usr/bin/env python2.7

#external libs
import jinja2
import json
from optparse import OptionParser
import os
import sys

def RenderTemplate(template_name, page_dict):
    """Renders a Jinja template into HTML.

    template_name is the filename for the template.
    page_dict is a dictionary containing values used during rendering.
    """
    this_dir = os.path.dirname(os.path.abspath(__file__))
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(this_dir))
    
    template = env.get_template(template_name)
    return template.render(page_dict, env=env)

# Functions that should be drawn collapsed, either because they generate
# too big a call graph or are uninteresting during performance analysis.
functions_to_collapse = ['syslog',
             'printf', 'snprintf', 'fprintf',
             'malloc', 'calloc', 'realloc', 'free',
             'fun_calloc_threaded', 'fun_realloc_threaded',
             'fun_malloc_threaded', 'fun_free']

def AddLevels(tree, height, show_node):
    """Preprocesses a call tree in JSON form.

    Marks uninteresting functions as collapsed.
    """
    
    tree['level'] = height
    # Collapse on a node prevents it from being displayed at all.
    tree['collapse'] = not show_node
    show_children = tree['name'] not in functions_to_collapse
    # collapse_children  on a node changes the +/- on that line to
    # hint that the line can be expanded.
    tree['children_collapse'] = not show_children
    
    if 'calls' in tree:
        # Validation
        for c in tree['calls']:
            AddLevels(c, height + 1, show_children)
  
def PrepareTrees(roots, nodes):
    """Preprocess trees to be rendered in HTML.

    Convert numbered references to children into pointers to the
    actual objects.  We numbered the nodes to make them easier to
    render and process, but need the recursive structures to draw.

    Also add a level number on each node so we can indent nodes,
    and collapse certain uninteresting nodes.

    roots: list of indices for the nodes that are roots to the call
    trees.
    nodes: list of call tree nodes, as dictionaries.  The "id" field
    gives the number of the element, which is referenced by roots and
    in the "calls" field.
    """
    # Implement with a worklist so that deep trees don't crash Python.
    nodes_by_id = {}

    for node in nodes:
        nodes_by_id[node["id"]] = node

    for node in nodes:
        if "calls" in node:
            node["calls"] = [nodes_by_id[n] for n in node["calls"]]
    roots = [nodes_by_id[root_id] for root_id in roots]

    for root in roots:
        AddLevels(root, 0, True)

    return roots

if __name__ == "__main__":
    parser = OptionParser()

    parser.add_option("-t", "--trace", dest="trace_file",
              help="JSON trace data", metavar="FILE")
    parser.add_option('-d', '--dir', dest='dest_dir',
              help='Destination for HTML files')
    parser.add_option('-c', '--core', dest='core', default='',
              help='Core number.  Used for output filenames')
    (options, args) = parser.parse_args()

    if options.trace_file is None:
        print "Need to specify a fungible option trace file"
        sys.exit(1)

    dest_dir = ''
    if options.dest_dir != None:
        dest_dir = os.path.abspath(options.dest_dir)

    # suffix on each generated file.
    core = 0
    if options.core:
        core = int(options.core)

    if not os.path.isfile(options.trace_file):
        sys.stderr.write('No such file: %s\n' % options.trace_file)
        sys.exit(1)
    f = open(options.trace_file, 'r')
    try:
        trace_json = json.load(f)
    except Exception as e:
        sys.stderr.write('Problems loading JSON trace: %s\n' % e)
        sys.exit(1)
    f.close()

    #roots = ParseTraceFile(trace_json)

    trace_json['root_nodes']= PrepareTrees(trace_json['roots'],
                           trace_json['call_nodes'])

    trace_json['function_names'] = sorted(trace_json['function_stats'])
    # print RenderTemplate('fn_table.tmpl', trace_json)

    out = RenderTemplate('template/call_tree.html', trace_json)
    f = open(os.path.join(dest_dir, 'c%d.html' % core), 'w')
    f.write(out)
    f.close()

    out = RenderTemplate('template/function_list.html', trace_json)
    f = open(os.path.join(dest_dir, 'function_list_%d.html' % core),
         'w')
    f.write(out)
    f.close()
    
    sys.stderr.write('Generated call tree and function summary.\n')
    sys.exit(1)

