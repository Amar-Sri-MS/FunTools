#
# Elasticsearch output.
#
import datetime

from elasticsearch7 import Elasticsearch

from blocks.block import Block


class ElasticsearchOutput(Block):
    """ Adds all messages as documents in an elasticsearch index. """

    def __init__(self):
        self.es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

    def set_config(self, cfg):
        self.index = cfg['index']

    def process(self, iters):
        iter = iters[0]

        for tuple in iter:
            self.index_in_es(tuple)

    def index_in_es(self, tuple):
        """ Indexes the tuple in elasticsearch """

        # Elasticsearch with date_nanos as a timestamp type requires
        # ISO timestamps.
        dt = datetime.datetime.fromtimestamp(tuple[0] + tuple[1] * 1e-6)
        iso_ts = datetime.datetime.isoformat(dt)

        doc = {
            '@timestamp': iso_ts,
            'src': tuple[2],
            'msg': tuple[4]
        }

        res = self.es.index(index=self.index, body=doc)
