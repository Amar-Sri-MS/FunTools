#
# Elasticsearch output.
#
import datetime
import json
import requests
import sys

from elasticsearch7 import Elasticsearch
from elasticsearch7.helpers import parallel_bulk
from itertools import tee

from blocks.block import Block

class ElasticsearchOutput(Block):
    """ Adds all messages as documents in an elasticsearch index. """

    def __init__(self):
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

        ELASTICSEARCH_HOSTS = self.config['ELASTICSEARCH']['hosts']
        ELASTICSEARCH_TIMEOUT = self.config['ELASTICSEARCH']['timeout']
        ELASTICSEARCH_MAX_RETRIES = self.config['ELASTICSEARCH']['max_retries']
        self.es = Elasticsearch(ELASTICSEARCH_HOSTS,
                                timeout=ELASTICSEARCH_TIMEOUT,
                                max_retries=ELASTICSEARCH_MAX_RETRIES,
                                retry_on_timeout=True)
        self.env = {}
        self.index = None

        # We use the date_nanos type in elasticsearch, which limits us to
        # the epoch in UTC as a lower limit.
        #
        # If we find entries before this time we'll clamp to the limit by
        # adding an offset. This is primarily for FunOS timestamps which
        # aren't correct until the time jump is applied by control plane.
        #
        # TODO(jimmy): is there a pleasant solution? changing data upsets me.
        # an alternative would be to provide estimates for
        # the early FunOS timestamps, perhaps via extrapolation.
        self.min_datetime = datetime.datetime.utcfromtimestamp(0)
        self.datetime_boost = datetime.timedelta(days=1)

    def set_config(self, cfg):
        self.env = cfg['env']
        build_id = self.env['build_id']
        self.index = cfg['index'].replace('${build_id}', build_id)

    def process(self, iters):
        """ Writes contents from all iterables to elasticsearch """
        # Creating an index pattern for Kibana
        self.create_kibana_index_pattern()

        for it in iters:
            # Copying the iterator to send to the next output block.
            # Might have performance implications because of copying.
            # TODO(Sourabh): Need to check alternative solutions
            # to share data between the output blocks.
            it, it_copy = tee(it)
            # parallel_bulk is a wrapper around bulk to provide threading.
            # default thread_count is 4 and it returns a generator with indexing result.
            # chunk_size of 10k works best based on tests on existing logs on single ES node
            # running with 4GB heap.
            # TODO(Sourabh): Need to test again if there's any change in resources of the ES node
            for success, info in parallel_bulk(self.es, self.generate_es_doc(it), chunk_size=10000):
                if not success:
                    print('Failed to index a document', info)
            yield from it_copy

    def generate_es_doc(self, it):
        """ Maps iterable contents to elasticsearch document """
        for tuple in it:
            # Elasticsearch with date_nanos as a timestamp type requires
            # ISO timestamps.
            #
            # We use date_nanos instead of the standard date because the latter
            # is limited to millisecond granularity, and a lot of our timestamps
            # are at the microsecond granularity.
            date_time = tuple[0]

            # Hack: change incompatible dates
            if date_time < self.min_datetime:
                date_time += self.datetime_boost

            iso_ts = datetime.datetime.isoformat(date_time)

            doc = {
                '_index': self.index,
                '@timestamp': iso_ts,
                'src': tuple[2],
                'msg': tuple[4]
            }

            yield doc

    def create_kibana_index_pattern(self):
        """ Creates an index pattern based on Elasticsearch index for Kibana """
        KIBANA_HOST = self.config['KIBANA']['host']
        KIBANA_PORT = self.config['KIBANA']['port']
        kibana_url = f'http://{KIBANA_HOST}:{KIBANA_PORT}/api/saved_objects/index-pattern/{self.index}'
        headers = {
            'kbn-xsrf': 'true'
        }

        data = {
            "attributes": {
                "title": self.index,
                "timeFieldName": "@timestamp"
            }
        }
        response = requests.post(kibana_url, headers=headers, json=data)
        # TODO(Sourabh): Error handling if index pattern creation fails
        if response.status_code != 200:
            print(response.json())
