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
import re

from blocks.block import Block


class TextFileInput(Block):
    """ Reads input from text files matching a specified pattern """

    def __init__(self):
        self.file_pattern = None
        self.env = {}
        self.uid = None
        self.cfg = {}

    def set_config(self, cfg):
        self.env = cfg['env']
        self.file_pattern = cfg['file_pattern']
        self.uid = cfg['uid']
        self.pattern = cfg.get('pattern', None)
        self.cfg = cfg

    def process(self, iters):
        pattern = self._replace_file_vars()

        input_files = glob.glob(pattern)

        # Assume that sorting files in timestamp order provides
        # input in sorted order. We might enforce lexicographic order
        # if it proves too difficult to enforce copying files with their
        # original timestamp.
        input_files.sort(key=os.path.getmtime)
        file_size = 0

        for file in input_files:
            print('INFO: Parsing', file)
            if file.endswith('.gz'):
                with gzip.open(file, mode='rt', encoding='ascii', errors='replace') as f:
                    yield from self.read_logs(f)
                    f.seek(0,2)
                    file_size += f.tell()
            else:
                with open(file, 'r', encoding='ascii', errors='replace') as f:
                    yield from self.read_logs(f)
                    f.seek(0,2)
                    file_size += f.tell()
        print('INFO: Uncompressed file size (in bytes):', file_size)

    def read_logs(self, f):
        multiline_logs = []
        for line in f:
            # No need to parse if the log line is empty
            if not line: continue

            # If the multiline pattern is not present
            if not self.pattern:
                yield from self._format_iters(line)
                continue

            # Check if the current line is start of a new log and there are lines from
            # previous logs to parse
            if multiline_logs and self._check_for_match(line):
                yield from self._format_iters(''.join(multiline_logs))
                multiline_logs = []
            multiline_logs.append(line)
        yield from self._format_iters(''.join(multiline_logs))

    def _format_iters(self, log):
        yield (None,
               None,
               self.cfg.get('system_type'),
               self.cfg.get('system_id'),
               self.uid,
               None,
               None,
               log)

    def _check_for_match(self, line):
        m = re.match(self.pattern, line)
        return True if m else False

    def _replace_file_vars(self):
        logdir = self.env['logdir']
        return self.file_pattern.replace('${logdir}', logdir)