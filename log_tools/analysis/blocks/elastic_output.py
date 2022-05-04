#
# Elasticsearch output.
#
import datetime
import logging

from elasticsearch7 import Elasticsearch
from elasticsearch7.helpers import parallel_bulk

from blocks.block import Block
import config_loader
from utils import timeline


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
        timeline.track_start('indexing')
        DOCUMENT_COUNT_PER_BULK_INGEST = 100000
        documents = list()
        for it in iters:
            for tuple in it:
                # Converting the iterator into list to send them to the
                # next output block.
                documents.append(tuple)

                if len(documents) >= DOCUMENT_COUNT_PER_BULK_INGEST:
                    yield from self._ingest_documents(documents)
                    documents = list()

            # If any documents are left to ingest
            if len(documents) > 0:
                yield from self._ingest_documents(documents)

        timeline.track_end('indexing')

    def _ingest_documents(self, documents):
        """
        Ingest the documents and yields them for the next output block.
        Args:
            documents: list of tuple containing log information
        Yields:
            tuple with log information and Elasticsearch document id
        """
        try:
            # parallel_bulk is a wrapper around bulk to provide threading.
            # default thread_count is 4 and it returns a generator with indexing result.
            # chunk_size of 10k works best based on tests on existing logs on single ES node
            # running with 4GB heap.
            # TODO(Sourabh): Need to test again if there's any change in resources of the ES node
            statuses = parallel_bulk(self.es,
                                    self.generate_es_doc(documents),
                                    raise_on_error=True,
                                    raise_on_exception=True,
                                    chunk_size=10000)
            # parallel_bulk returns a generator of tuples containing two elements: status flag (bool)
            # and result of document creation (object).
            for idx, status in enumerate(statuses):
                if status[0] == False:
                    logging.error(f'Failed to index a document: {status}')
                else:
                    yield from self._add_doc_id_in_iters(documents[idx], status[1]['index']['_id'])
        except:
            logging.exception('Something went wrong while indexing.')

    def _add_doc_id_in_iters(self, tuple, doc_id):
        """ Adding ES doc id to the message tuple """
        yield (*tuple, doc_id)

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
