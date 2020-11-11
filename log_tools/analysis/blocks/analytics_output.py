#
# Analytics Ouput Block
# Creates HTML files for each analysis
#
import datetime
import hashlib
import heapq
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

    def process(self, iters):
        """ Performs analysis on all iterables """

        for it in iters:
            self.check_for_duplicate_entry(it)

        # Most duplicated logs
        self.generate_most_duplicates_entries()

    def check_for_duplicate_entry(self, it):
        """ Hashing the current log message to check if exists already """
        for tuple in it:
            msg_dict = self.tuple_to_dict(tuple)
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

    def generate_most_duplicates_entries(self):
        """
        Get the top 10 most duplicated log entries.
        Generate HTML page with analyzed data for the build_id.
        """
        # Sorting by count and picking up the top 10 entries
        most_duplicated_entries = sorted(self.duplicate_entries.items(),
                                key=lambda entry: entry[1]['count'],
                                reverse=True)[:10]

        MODULE_PATH = Path(__file__)
        # This is equivalent to path.parent.parent
        MODULE_DIR = MODULE_PATH.resolve().parents[1] / 'view' / 'templates'

        jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(MODULE_DIR),
                                 trim_blocks=True,
                                 lstrip_blocks=True)
        template = jinja_env.get_template('log_entries.html')

        KIBANA_HOST = self.config['KIBANA']['host']
        KIBANA_PORT = self.config['KIBANA']['port']

        table_head = ['Duplicates', 'Source', 'Timestamp', 'Log Message']
        table_body = []
        for entry in most_duplicated_entries:
            msg = entry[1]['msg']
            # Kibana query should be enclosed within quotations for exact match
            # Removing special characters
            # TODO(Sourabh): Better approach for handling special characters
            query = '"{}"'.format(msg['line'].replace('\\','').replace('"',' ').replace('\'', '!\''))

            kibana_url = ("http://{}:{}/app/kibana#/discover/?_g=(time:(from:now-90d,to:now))"
                          "&_a=(columns:!(src,msg),filters:!(),index:log_{},interval:auto,"
                          "query:(language:kuery,query:'{}'),sort:!())").format(KIBANA_HOST,
                                                                                KIBANA_PORT,
                                                                                self.cfg['env'].get('build_id'),
                                                                                quote_plus(query))

            table_body.append(
                '<tr><td>{}</td><td>{}</td><td>{}</td><td><a href="{}">{}</a></td></tr>'.format(entry[1]['count'],
                                                                                              msg['uid'],
                                                                                              msg['datetime'],
                                                                                              kibana_url,
                                                                                              msg['line'])
            )

        template_dict = {}
        template_dict['head'] = table_head
        template_dict['body'] = '\n'.join(table_body)

        result = template.render(template_dict, env=jinja_env)
        try:
            # Creating the directory if it does not exist
            os.makedirs(os.path.dirname(self.dir), exist_ok=True)
            with open(self.dir, 'w+') as f:
                f.write(result)
        except IOError as e:
            print("I/O error", e)