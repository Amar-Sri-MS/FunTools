import argparse
import collections
import json
import os

# Input blocks
from blocks import file_input

# Filters
from blocks import display_time
from blocks import merge

# Output blocks
from blocks import stdout_output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dir", help="Log directory")
    parser.add_argument("cfg", help="Config file")
    args = parser.parse_args()

    plugins = register_plugins()

    with open(args.cfg, 'r') as f:
        cfg = json.load(f)

    env = {}
    env['logdir'] = args.dir

    blocks_by_id = get_block_mapping(cfg)
    order = topsort(blocks_by_id)

    process(blocks_by_id, plugins, order, env)


def register_plugins():
    """
    Utterly lame, but I'm scared of exec. Should figure out something
    better.
    """
    plugins = {}
    plugins['FunOSInput'] = file_input.FunOSInput
    plugins['HumanDateTime'] = display_time.HumanDateTime
    plugins['Merge'] = merge.Merge
    plugins['StdOutput'] = stdout_output.StdOutput

    return plugins


def get_block_mapping(cfg):
    blocks_by_id = {}
    for item in cfg['pipeline']:
        uid = item['id']
        blocks_by_id[uid] = item

    return blocks_by_id


def topsort(blocks_by_id):
    visited = {}
    completed = []

    for id in blocks_by_id:
        dfs(id, blocks_by_id, visited, completed)

    completed.reverse()
    return completed


def dfs(curr, blocks_by_id, visited, completed):
    if curr in visited:
        return

    visited[curr] = True

    # our blocks only have one output (or none for the output block)
    block = blocks_by_id[curr]
    next = block.get('out')

    # recursion... okay for this purpose as the graph shouldn't be deep
    # and this is the easiest way to get a topsort
    if next is not None:
        dfs(next, blocks_by_id, visited, completed)

    completed.append(curr)


def process(blocks_by_uid, plugins, order, env):
    input_iters_by_uid = collections.defaultdict(list)

    for id in order:
        block = blocks_by_uid[id]
        out = block.get('out')
        cls = plugins[block['block']]
        obj = cls()

        cfg = block.get('cfg', dict())
        cfg['env'] = env
        cfg['uid'] = id
        obj.set_config(cfg)

        input_inters = input_iters_by_uid[id]
        out_iter = obj.process(input_inters)
        if out_iter is not None:
            input_iters_by_uid[out].append(out_iter)


if __name__ == '__main__':
    main()