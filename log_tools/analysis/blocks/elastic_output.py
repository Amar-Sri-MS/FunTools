#
# Elasticsearch output.
#
import datetime
import logging

from elasticsearch7 import Elasticsearch
from elasticsearch7.helpers import parallel_bulk
from itertools import tee

from blocks.block import Block
import config_loader


class ElasticsearchOutput(Block):
    """ Adds all messages as documents in an elasticsearch index. """

    def __init__(self):
        self.config = config_loader.get_config()

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
        # Limitation with ES that it only supports lowercase
        # index names.
        build_id = self.env['build_id'].lower()
        self.index = cfg['index'].replace('${build_id}', build_id)

    def process(self, iters):
        """ Writes contents from all iterables to elasticsearch """
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
            for success, info in parallel_bulk(
                                        self.es,
                                        self.generate_es_doc(it),
                                        raise_on_error=True,
                                        raise_on_exception=True,
                                        chunk_size=10000):
                if not success:
                    logging.error(f'Failed to index a document: {info}')
                else:
                    yield from self._add_doc_id_in_iters(next(it_copy), info)

    def _add_doc_id_in_iters(self, tuple, info):
        """ Adding ES doc id to the message tuple """
        yield (*tuple, info['index']['_id'])

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
                'system_type': tuple[2],
                'system_id': tuple[3],
                'src': tuple[4],
                'level': tuple[6],
                'msg': tuple[7]
            }

            yield doc
