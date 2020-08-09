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

    with open(args.cfg, 'r') as f:
        cfg = json.load(f)

    env = {}
    env['logdir'] = args.dir

    pipeline = Pipeline(cfg, env)
    pipeline.process()


class BlockFactory(object):
    """ A factory for blocks """

    def __init__(self):
        self.plugins = {}
        self._register_block_types()

    def _register_block_types(self):
        """
        Utterly lame, but I'm scared of exec. Should figure out something
        better.
        """
        self.plugins['FunOSInput'] = file_input.FunOSInput
        self.plugins['HumanDateTime'] = display_time.HumanDateTime
        self.plugins['Merge'] = merge.Merge
        self.plugins['StdOutput'] = stdout_output.StdOutput

    def create_block(self, block_name):
        """ Create an instance of the block """
        cls = self.plugins[block_name]
        return cls()


class Pipeline(object):

    def __init__(self, cfg, env):
        self.block_factory = BlockFactory()
        self.cfg = cfg
        self.env = env

    def process(self):
        blocks_by_id = self.get_block_mapping()
        block_order = topsort(blocks_by_id)

        input_iters_by_uid = collections.defaultdict(list)

        for id in block_order:
            block = blocks_by_id[id]
            out = block.get('out')
            obj = self.block_factory.create_block(block['block'])

            cfg = block.get('cfg', dict())
            cfg['env'] = self.env
            cfg['uid'] = id
            obj.set_config(cfg)

            input_inters = input_iters_by_uid[id]
            out_iter = obj.process(input_inters)
            if out_iter is not None:
                input_iters_by_uid[out].append(out_iter)

    def get_block_mapping(self):
        blocks_by_id = {}
        for item in self.cfg['pipeline']:
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


if __name__ == '__main__':
    main()