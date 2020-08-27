#
# Elasticsearch output.
#
import datetime

from elasticsearch7 import Elasticsearch
from elasticsearch7.helpers import bulk

from blocks.block import Block


class ElasticsearchOutput(Block):
    """ Adds all messages as documents in an elasticsearch index. """

    def __init__(self):
        self.es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

    def set_config(self, cfg):
        self.index = cfg['index']

    def process(self, iters):
        """ Writes contents from all iterables to elasticsearch """
        for it in iters:
            bulk(self.es, self.generate_es_doc(it))

    def generate_es_doc(self, it):
        """ Maps iterable contents to elasticsearch document """
        for tuple in it:
            # Elasticsearch with date_nanos as a timestamp type requires
            # ISO timestamps.
            #
            # We use date_nanos instead of the standard date because the latter
            # is limited to millisecond granularity, and a lot of our timestamps
            # are at the microsecond granularity.
            #
            # TODO (jimmy): use datetime as the object in the tuple to avoid all
            # these repeated conversions.
            dt = datetime.datetime.fromtimestamp(tuple[0] + tuple[1] * 1e-6)
            iso_ts = datetime.datetime.isoformat(dt)

            doc = {
                '_index': self.index,
                '@timestamp': iso_ts,
                'src': tuple[2],
                'msg': tuple[4]
            }

            yield doc

