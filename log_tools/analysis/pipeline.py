#!/usr/bin/env python3

#
# Log analysis pipeline.
#

import argparse
import collections
import json
import os

# Input blocks
from .blocks import file_input

# Filters
from .blocks import display_time
from .blocks import log_parsers
from .blocks import merge
from .blocks import log_filter

# Output blocks
from .blocks import analytics_output
from .blocks import elastic_output
from .blocks import html_output
from .blocks import stdout_output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('build_id', help='Unique build ID')
    parser.add_argument("dir", help="Log directory")
    parser.add_argument("cfg", help="Pipeline config file")
    args = parser.parse_args()

    block_factory = BlockFactory()

    with open(args.cfg, 'r') as f:
        cfg = json.load(f)

    env = {}
    env['logdir'] = args.dir
    env['build_id'] = args.build_id

    pipeline = Pipeline(block_factory, cfg, env)
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
        self.plugins['TextFileInput'] = file_input.TextFileInput
        self.plugins['FunOSInput'] = log_parsers.FunOSInput
        self.plugins['ISOFormatInput'] = log_parsers.ISOFormatInput
        self.plugins['GenericInput'] = log_parsers.GenericInput
        self.plugins['KeyValueInput'] = log_parsers.KeyValueInput
        self.plugins['JSONInput'] = log_parsers.JSONInput
        self.plugins['HumanDateTime'] = display_time.HumanDateTime
        self.plugins['Merge'] = merge.Merge
        self.plugins['Filter'] = log_filter.LogFilter
        self.plugins['AnalyticsOutput'] = analytics_output.AnalyticsOutput
        self.plugins['HTMLOutput'] = html_output.HTMLOutput
        self.plugins['ElasticOutput'] = elastic_output.ElasticsearchOutput
        self.plugins['StdOutput'] = stdout_output.StdOutput

    def create_block(self, block_name):
        """ Create an instance of the block """
        cls = self.plugins[block_name]
        return cls()


class Pipeline(object):
    """ A processing pipeline for logs. """

    def __init__(self, block_factory, pipeline_cfg, env):
        """
        Creates a pipeline.

        block_factory is a factory that can return instances of processing
        blocks.
        pipeline_cfg describes the processing pipeline structure (assumed to be
        a DAG)
        env contains our "version" of environment variables that can be
        used in the pipeline_cfg.
        """
        self.block_factory = block_factory
        self.pipeline_cfg = pipeline_cfg
        self.env = env

    def process(self):
        """ Runs the pipeline """
        pipeline_node_by_id = self._get_pipeline_nodes()

        processing_order = _topsort(pipeline_node_by_id)

        input_iters_by_uid = collections.defaultdict(list)

        for id in processing_order:
            pipeline_node = pipeline_node_by_id[id]
            block = self.block_factory.create_block(pipeline_node['block'])

            cfg = pipeline_node.get('cfg', dict())
            cfg['env'] = self.env
            cfg['uid'] = cfg.get('src', id)
            block.set_config(cfg)

            input_inters = input_iters_by_uid[id]
            out_iter = block.process(input_inters)

            if out_iter is not None:
                out = pipeline_node.get('out')
                input_iters_by_uid[out].append(out_iter)

    def _get_pipeline_nodes(self):
        """
        Extracts all entries (nodes in the graph) from the pipeline
        config.
        """
        entries_by_id = {}
        for entry in self.pipeline_cfg['pipeline']:
            uid = entry['id']
            entries_by_id[uid] = entry

        return entries_by_id


def _topsort(pipeline_node_by_id):
    """ Standard topsort based on recursive dfs """
    visited = {}
    completed = []

    for id in pipeline_node_by_id:
        _dfs(id, pipeline_node_by_id, visited, completed)

    completed.reverse()
    return completed

def _dfs(curr, pipeline_node_by_id, visited, completed):
    if curr in visited:
        return

    visited[curr] = True

    # our blocks only have one output (or none for the output block)
    block = pipeline_node_by_id[curr]
    next = block.get('out')

    # recursion... okay for this purpose as the graph shouldn't be deep
    # and this is the easiest way to get a topsort
    if next is not None:
        _dfs(next, pipeline_node_by_id, visited, completed)

    completed.append(curr)


if __name__ == '__main__':
    main()
