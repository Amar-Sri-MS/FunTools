#
# Analytics Output Block
# Creates HTML files for each analysis
#
import datetime
import hashlib
import jinja2
import json
import os
import re
import sys

from pathlib import Path
from urllib.parse import quote_plus

from blocks.block import Block


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
        short_desc = anchor['short']
        if 'rematch' in anchor:
            for key, value in match.groupdict().items():
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
            print('INFO: Reading Anchor file from:', anchor_file)

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
    """ Creates HTML pages after analysing the logs """

    def __init__(self):
        self.cfg = None
        self.dir = None
        # Maintains hash of unique log entry for detecting duplicates.
        # This might take up memory as the log entries increase.
        self.duplicate_entries = {}
        self.anchor_matches = list()
        self.config = {}
        # Reading config file if available.
        try:
            with open('./config.json', 'r') as f:
                self.config = json.load(f)
        except IOError:
            print('Config file not found! Checking for default config file..')

        # Reading default config file if available.
        try:
            with open('./default_config.json', 'r') as f:
                default_config = json.load(f)
            # Overriding default config with custom config
            self.config = { **default_config, **self.config }
        except IOError:
            sys.exit('Default config file not found! Exiting..')

    def set_config(self, cfg):
        self.cfg = cfg
        build_id = cfg['env'].get('build_id')
        self.dir = cfg['dir'].replace('${build_id}', build_id)

        KIBANA_HOST = self.config['KIBANA']['host']
        KIBANA_PORT = self.config['KIBANA']['port']
        # KIBANA defaults.
        # TODO(Sourabh): Would be better to have this in config files
        kibana_time_filter = "from:'1970-01-01T00:00:00.000Z',to:now"
        kibana_selected_columns = 'src,level,msg'
        self.kibana_base_url = ("http://{}:{}/app/kibana#/discover/?_g=(time:({}))&_a=(columns:!({}),index:log_{},"
                                "query:(language:kuery,query:'KIBANA_QUERY'))").format(KIBANA_HOST,
                                                                                        KIBANA_PORT,
                                                                                        kibana_time_filter,
                                                                                        kibana_selected_columns,
                                                                                        build_id)

        # Check for anchors in log lines with timestamps
        timestamped_only = True

        anchor_files = cfg.get('anchor_files', [])
        anchor_keys = cfg.get('anchor_keys', None)
        self.anchor_matcher = AnchorMatcher(anchor_files, anchor_keys, timestamped_only)

    def process(self, iters):
        """ Performs analysis on all iterables """

        for it in iters:
            for tuple in it:
                msg_dict = self.tuple_to_dict(tuple)

                self.check_for_duplicate_entry(msg_dict)
                self.check_for_anchor_match(msg_dict)

        # Most duplicated logs
        self.generate_most_duplicates_entries()
        # Anchors
        self.store_anchor_matches()

    def check_for_duplicate_entry(self, msg_dict):
        """ Hashing the current log message to check if exists already """
        msg = msg_dict['line']

        # Creates a hash from the log line to compare with
        # other log lines
        hashval = hashlib.md5(msg.encode('utf-8')).digest()

        # If the hashval is new, then create a new key
        # in the duplicate_entries, which will be assigned
        # a value of a dict with msg and count set to 0.
        # If hashval already exists, then just
        # increment the count
        if hashval not in self.duplicate_entries:
            self.duplicate_entries[hashval] = {
                'msg': msg_dict,
                'count': 0
            }
        self.duplicate_entries[hashval]['count'] += 1

    def get_most_duplicated_entries(self, entries=10):
        # Sorting by count and picking up the top entries
        most_duplicated_entries = sorted(self.duplicate_entries.values(),
                                key=lambda entry: entry['count'],
                                reverse=True)[:entries]
        return most_duplicated_entries

    def generate_most_duplicates_entries(self):
        """
        Get the top 10 most duplicated log entries.
        Generate HTML page with analyzed data for the build_id.
        """
        most_duplicated_entries = self.get_most_duplicated_entries()

        table_head = ['Duplicates', 'Source', 'Timestamp', 'Log Message']
        table_body = []
        for entry in most_duplicated_entries:
            msg = entry['msg']
            # Kibana query should be enclosed within quotations for exact match
            # Removing special characters
            # TODO(Sourabh): Better approach for handling special characters
            query = '"{}"'.format(msg['line'].replace('\\','').replace('"',' ').replace('\'', '!\'')).replace('!', '!!')
            kibana_url = self.kibana_base_url.replace('KIBANA_QUERY', quote_plus(query))

            table_body.append(
                '<tr><td>{}</td><td>{}</td><td>{}</td><td><a href="{}" target="_blank">{}</a></td></tr>'.format(entry['count'],
                                                                                                                msg['uid'],
                                                                                                                msg['datetime'],
                                                                                                                kibana_url,
                                                                                                                msg['line'])
            )

        template_dict = {}
        template_dict['head'] = table_head
        template_dict['body'] = '\n'.join(table_body)

        path = os.path.join(self.dir, 'duplicates.html')
        self._create_template(path, template_dict)


    def check_for_anchor_match(self, msg_dict):
        match = self.anchor_matcher.generate_match(msg_dict)
        if match:
            self.anchor_matches.append(match)

    def store_anchor_matches(self):
        anchors_list = []
        # Sort the anchor matches by timestamp
        matches = sorted(self.anchor_matches)

        for match in matches:
            is_failure = match.anchor.get('is_failure', False)
            source = match.msg_dict.get('uid', 'N/A')
            system_id = match.msg_dict.get('system_id', 'N/A')
            msg = match.msg_dict['line']
            datetime = match.msg_dict['datetime']
            # Kibana query should be enclosed within quotations for exact match
            # Removing special characters
            # TODO(Sourabh): Better approach for handling special characters
            query = '"{}"'.format(msg.replace('\\','').replace('"',' ').replace('\'', '!\'')).replace('!', '!!')
            kibana_url = self.kibana_base_url.replace('KIBANA_QUERY', quote_plus(query))

            anchors_list.append({
                'source': source,
                'system_id': system_id,
                'is_failure': is_failure,
                'link': kibana_url,
                'datetime': str(datetime),
                'level': match.msg_dict['level'],
                'msg': match.msg_dict['line'],
                'description': match.short_desc
            })

        path = os.path.join(self.dir, 'anchors.json')
        try:
            # Creating the directory if it does not exist
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w+') as f:
                json.dump(anchors_list, f)
        except IOError as e:
            print("I/O error", e)

    def _create_template(self, path, template_dict):
        """ Creates a template in the specified path using the template_dict """
        MODULE_PATH = Path(__file__)
        # This is equivalent to path.parent.parent
        MODULE_DIR = MODULE_PATH.resolve().parents[1] / 'view' / 'templates'

        jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(MODULE_DIR),
                                 trim_blocks=True,
                                 lstrip_blocks=True)
        template = jinja_env.get_template('log_entries.html')

        result = template.render(template_dict, env=jinja_env)
        try:
            # Creating the directory if it does not exist
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w+') as f:
                f.write(result)
        except IOError as e:
            print('I/O error', e)
