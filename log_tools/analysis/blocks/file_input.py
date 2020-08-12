#
# Various file input blocks.
#
# The hope is that at some point, once we have a real log ingestion scheme
# that uses flume, syslog-ng, the ELK stack or something else, that this
# will simplify into reading the structured output data (or maybe even a
# search query) from that ingestion scheme.
#
# But till then... we have to play its role.
#

import glob
import gzip
import io
import os

from blocks.block import Block


class TextFileInput(Block):
    """ Reads input from text files matching a specified pattern """

    def __init__(self):
        self.file_pattern = None
        self.env = {}
        self.uid = None

    def set_config(self, cfg):
        self.env = cfg['env']
        self.file_pattern = cfg['file_pattern']
        self.uid = cfg['uid']

    def process(self, iters):
        pattern = self._replace_file_vars()

        input_files = glob.glob(pattern)

        # Assume that sorting files in timestamp order provides
        # input in sorted order. We might enforce lexicographic order
        # if it proves too difficult to enforce copying files with their
        # original timestamp.
        input_files.sort(key=os.path.getmtime)

        for file in input_files:
            if file.endswith('.gz'):
                with gzip.open(file, mode='rt', encoding='ascii', errors='replace') as f:
                    for line in f:
                        yield (None, None, self.uid, None, line)
            else:
                with open(file, 'r', encoding='ascii', errors='replace') as f:
                    for line in f:
                        yield (None, None, self.uid, None, line)

    def _replace_file_vars(self):
        logdir = self.env['logdir']
        return self.file_pattern.replace('${logdir}', logdir)

