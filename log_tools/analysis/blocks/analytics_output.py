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


class AnalyticsOutput(Block):
    """ Creates HTML pages after analysing the logs """

    def __init__(self):
        self.cfg = None
        self.dir = None
        # Maintains hash of unique log entry for detecting duplicates.
        # This might take up memory as the log entries increase.
        self.duplicate_entries = {}
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

    def process(self, iters):
        """ Performs analysis on all iterables """

        for it in iters:
            for tuple in it:
                msg_block = self.tuple_to_dict(tuple)

                self.check_for_duplicate_entry(msg_block)

        # Most duplicated logs
        self.generate_most_duplicates_entries()

    def check_for_duplicate_entry(self, msg_block):
        """ Hashing the current log message to check if exists already """
        msg = msg_block['line']

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
                'msg': msg_block,
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
            print("I/O error", e)