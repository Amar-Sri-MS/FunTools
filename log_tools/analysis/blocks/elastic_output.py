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

