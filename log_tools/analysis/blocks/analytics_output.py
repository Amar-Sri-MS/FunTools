#
# Analytics Output Block
# Perform analysis on the logs
#
import hashlib
import heapq
import json
import logging
import os
import re
import requests

from elasticsearch7 import Elasticsearch
from elasticsearch7.helpers import parallel_bulk
from urllib.parse import quote

from blocks.block import Block
import config_loader
from utils.lossycounting import LossyCounting
from utils import timeline

class AnchorMatch:
    """ Anchor Match to hold data required for a match """

    def __init__(self, anchor, match, msg_dict):
        """Construct a new AnchorMatch instance.

        Args:
            anchor (dict): The JSON dictionary that represents the anchor that
                           the line matched. Expected to have the key "short".
            match (RE match): The match object.
            msg_dict (dict): The message block which is convereted to dict. Expected
                        to have the key "datetime"
        """
        self.anchor = anchor
        self.msg_dict = msg_dict

        # If this is a regular expression anchor, fill all the values in the
        # short representation with the matchgroups.
        short_desc = anchor.get('short', '')
        if 'rematch' in anchor:
            for key, value in list(match.groupdict().items()):
                short_desc = re.sub(f'<{key}>', value, short_desc)
        self.short_desc = short_desc

    # Need this to sort match objects based on their timestamp.
    def __lt__(self, other):
        return self.msg_dict['datetime'] < other.msg_dict['datetime']


class AnchorMatcher:
    def __init__(self, anchor_files, anchor_keys, timestamped_only=False):
        """Construct an AnchorMatcher object. This provides an interface that
        can return AnchorMatch objects given a filename for a log.

        Args:
            anchor_files (str list): List of strings that represent filenames
                                     of files that contain JSON anchors.
            anchor_keys (set):       List of keys to use from anchors file.
            timestamped_only (bool): Limit to only matches that have a
                                     timestamp associated with them.
        """

        self.timestamped_only = timestamped_only
        anchors = self._load_anchors(anchor_files, anchor_keys)
        self.compiled, self.uber_compiled = self._generate_matchers(anchors)

    def _load_anchors(self, anchor_files, anchor_keys):
        """Generate a list of dictionaries representing the anchors in the
        given files. Each line in the anchor file will be treated as a separate
        valid JSON anchor. If the line starts with a '#' character, it will be
        skipped.
        """

        anchors = []
        for anchor_file in anchor_files:
            logging.info(f'Reading Anchor file from: {anchor_file}')

            with open(os.path.expandvars(anchor_file)) as f:
                for line in f:
                    line = line.strip()

                    # Each anchor is it's own valid piece of JSON. The anchors
                    # file as a whole is not valid JSON.
                    if line and not line.startswith('#'):
                        anchor = json.loads(line)
                        if anchor_keys == None or anchor['key'] in anchor_keys:
                            anchors.append(anchor)

        return anchors

    def _generate_matchers(self, anchors):
        """ Generate the two regular expression matchers. This returns a tuple
        of (compiled, uber_compiled).

        The compiled list is a list of (anchor, regular expression). This will
        be used later to narrow down a match after the uber regex has matched.

        The uber_compiled is a single regular expression that is comprised of
        all of the regular expressions in the compiled list.
        """

        compiled = []
        uber_matchers = []
        for anchor in anchors:
            if 'rematch' in anchor:
                pattern = anchor['rematch']

                # Remove the grouping tags of the form ?P<KEY>
                uber_pattern = re.sub(r'\(\?P<[^>]+>', '(', pattern)
            else:
                pattern = anchor['match']
                pattern = re.escape(pattern)
                uber_pattern = pattern

            uber_matchers.append(uber_pattern)
            compiled.append((anchor, re.compile(pattern)))

        uber_re = '|'.join(uber_matchers)
        uber_compiled = re.compile(uber_re)

        return compiled, uber_compiled

    def _generate_match_entry(self, msg_dict):
        """
        Find the anchor that generated the match, and create a new AnchorMatch
        object with the associated message dict.
        """

        line = msg_dict['line']
        for anchor, matcher in self.compiled:
            match = matcher.search(line)
            if match:
                return AnchorMatch(anchor, match, msg_dict)

        return None

    def _filter_entry(self, entry):
        """
        We have a match entry, now do we want it?
        """

        return not self.timestamped_only or entry.msg_dict['datetime']

    def generate_match(self, msg_dict):
        """
        Given a message block, search for match against the given anchors.
        """
        line = msg_dict['line']
        if self.uber_compiled.search(line):
            entry = self._generate_match_entry(msg_dict)
            if entry and self._filter_entry(entry):
                return entry

        return None


class AnalyticsOutput(Block):
    """ Perform analysis on the logs """

    def __init__(self):
        self.cfg = None
        self.config = config_loader.get_config()

        # Window size of 100k to check for duplicates.
        self.duplicate_counter = LossyCounting(100000)

        # Having this limit to avoid storing the complete anchor data on
        # memory and instead performing bulk updates in batches of 10k
        self.MAX_ANCHOR_COUNT_PER_BULK_UPDATE = 10000
        self.anchor_matches = list()

        ELASTICSEARCH_HOSTS = self.config['ELASTICSEARCH']['hosts']
        ELASTICSEARCH_TIMEOUT = self.config['ELASTICSEARCH']['timeout']
        ELASTICSEARCH_MAX_RETRIES = self.config['ELASTICSEARCH']['max_retries']
        self.es = Elasticsearch(ELASTICSEARCH_HOSTS,
                                timeout=ELASTICSEARCH_TIMEOUT,
                                max_retries=ELASTICSEARCH_MAX_RETRIES,
                                retry_on_timeout=True)

    def set_config(self, cfg):
        self.cfg = cfg
        build_id = cfg['env'].get('build_id')
        self.log_id = f'log_{build_id}'.lower()

        self.log_view_base_url = self.config['LOG_VIEW_BASE_URL'].replace('LOG_ID', self.log_id)

        # Check for anchors in log lines with timestamps
        timestamped_only = True

        anchor_files = cfg.get('anchor_files', [])
        anchor_keys = cfg.get('anchor_keys', None)
        self.anchor_matcher = AnchorMatcher(anchor_files, anchor_keys, timestamped_only)

    def process(self, iters):
        """ Performs analysis on all iterables """
        timeline.track_start('analytics')
        for it in iters:
            for tuple in it:
                msg_dict = self.tuple_to_dict(tuple)

                self.check_for_duplicate_entry(msg_dict)
                self.check_and_store_anchor_match(msg_dict)

        # Anchor matches
        self.store_anchor_matches()

        # Most duplicated logs
        self.generate_most_duplicates_entries()
        timeline.track_end('analytics')

    def check_for_duplicate_entry(self, msg_dict):
        """ Hashing the current log message to check if exists already """
        msg = msg_dict['line']

        # Creates a hash from the log line to compare with
        # other log lines
        hashval = hashlib.md5(msg.encode('utf-8')).digest()
        self.duplicate_counter.count(hashval, msg_dict)

    def get_most_duplicated_entries(self, entries=10):
        # Sorting by count and picking up the top entries
        return heapq.nlargest(entries, self.duplicate_counter.get_iter(2),
                                key=lambda entry: entry['count'])

    def generate_most_duplicates_entries(self):
        """
        Get the top 50 most duplicated log entries.
        Generate HTML page with analyzed data for the build_id.
        """
        most_duplicated_entries = self.get_most_duplicated_entries(entries=50)
        most_duplicated_entries_list = []

        for entry in most_duplicated_entries:
            msg = entry['entry']
            # Kibana query should be enclosed within quotations for exact match
            # Removing special characters
            # TODO(Sourabh): Better approach for handling special characters
            query = '"{}"'.format(msg['line'].replace('\\','').replace('"',' ').replace('\'', '!\'')).replace('!', '!!').replace('%', ' ').replace('/', ' ').replace('(', ' ').replace(')', ' ').replace("'", ' ')
            search_query = { 'query': query.strip() }
            log_view_url = f'{self.log_view_base_url}?search={quote(json.dumps(search_query))}'

            most_duplicated_entries_list.append({
                'count': entry['count'],
                'system_id': msg.get('system_id', 'N/A'),
                'link': log_view_url,
                'datetime': str(msg['datetime']),
                'source': msg.get('uid', 'N/A'),
                'level': msg.get('level'),
                'msg': msg.get('line')
            })

        if (len(most_duplicated_entries_list) > 0):
            self._save_json('duplicates.json', most_duplicated_entries_list)

    def check_and_store_anchor_match(self, msg_dict):
        match = self.anchor_matcher.generate_match(msg_dict)
        if match:
            self.anchor_matches.append(match)
            # Storing anchors in batches
            if len(self.anchor_matches) >= self.MAX_ANCHOR_COUNT_PER_BULK_UPDATE:
                self.store_anchor_matches()

    def store_anchor_matches(self):
        """ Updating the ES documents with anchor details """
        actions = list()
        for match in self.anchor_matches:
            es_doc_id = match.msg_dict['doc_id']
            is_failure = match.anchor.get('is_failure', False)
            anchor_text = match.short_desc if match.short_desc else match.msg_dict['line']

            # ES format for bulk operations where _op_type defines
            # the type of operation
            actions.append({
                '_op_type': 'update',
                '_index': self.log_id,
                '_id': es_doc_id,
                'doc': {
                    'is_anchor': True,
                    'is_failure': is_failure,
                    'anchor_text': anchor_text
                }
            })

        # Resetting the anchor matches
        self.anchor_matches = list()
        # Performing parallel bulk updates to save time on updating
        for success, info in parallel_bulk(self.es, actions):
            if not success:
                logging.error(f'Failed to add anchor to the log document: {info}')

    def _save_json(self, filename, data):
        """ Sends the file to the file server """
        try:
            FILE_SERVER_URL = self.config['FILE_SERVER_URL']
            url = f'{FILE_SERVER_URL}/{self.log_id}/file'

            files = [
                ('file', (filename, json.dumps(data), 'application/json'))
            ]

            response = requests.post(url, files=files)
            response.raise_for_status()
            logging.info(f'File {filename} uploaded!')
        except Exception as e:
            logging.exception(f'Uploading file {filename} failed.')