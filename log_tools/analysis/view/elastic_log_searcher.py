#!/usr/bin/env python3

import datetime
import json
import time

from elasticsearch7 import Elasticsearch

import config_loader

from elastic_metadata import ElasticsearchMetadata

config = config_loader.get_config()


def get_logs(prefix, limit_by=None, limit_value=None):
    """ Returns all the ingested logs """
    es_metadata = ElasticsearchMetadata()

    limit = {}
    if limit_by and limit_by != "tags" and limit_value:
        limit = {
            'by': limit_by,
            'value': limit_value
        }

    indices = _get_indices(prefix, limit)
    if limit_by == 'tags':
        tags = limit_value
        tags_list = [tag.strip() for tag in tags.split(',')]
        metadata = es_metadata.get_by_tags(
                        tags_list,
                        size=len(indices))
        indices = [index for index in indices if index['index'] in metadata]
    else:
        log_ids = [index['index'] for index in indices]
        metadata = es_metadata.get_by_log_ids(log_ids)

    logs = list()
    for index in indices:
        id = index['index']
        creation_date_epoch = int(index['creation.date'])
        # Separting out seconds and milliseconds from epoch
        creation_date_s, creation_date_ms = divmod(creation_date_epoch, 1000)
        creation_date = '{}'.format(
                            time.strftime('%B %d, %Y %H:%M:%S', time.gmtime(creation_date_s)),
                            )

        tags = metadata.get(id, {}).get('tags', [])
        logs.append({
            'name': id,
            'creation_date': creation_date,
            'health': index['health'],
            'doc_count': index['docs.count'],
            'es_size': index['store.size'],
            'tags': tags,
            'metadata': metadata.get(id, {})
        })

    return logs


def _get_indices(prefix, limit=None):
    """
    Returns list of dicts containing data about an index.

    Args:
    prefix (str) - prefix for index name
    limit (dict) - controlling how to limit the indices
                   by count or days. Ex: last 7 days.
    """
    ELASTICSEARCH_HOSTS = config['ELASTICSEARCH']['hosts']
    ELASTICSEARCH_TIMEOUT = config['ELASTICSEARCH']['timeout']
    ELASTICSEARCH_MAX_RETRIES = config['ELASTICSEARCH']['max_retries']
    es = Elasticsearch(ELASTICSEARCH_HOSTS,
                       timeout=ELASTICSEARCH_TIMEOUT,
                       max_retries=ELASTICSEARCH_MAX_RETRIES,
                       retry_on_timeout=True)

    # Using the ES CAT API to get indices.
    # CAT API supports sorting and returns more data.
    # Args: h is for limiting the data needed.
    # Args: s is for sorting based on the data.
    indices = es.cat.indices(
        index=prefix,
        h='health,index,id,docs.count,store.size,creation.date',
        format='json',
        # Sorting the indices based on creation date.
        s='creation.date:desc'
    )

    if limit:
        limit_by = limit.get('by')
        limit_value = limit.get('value')
        if limit_by == 'count':
            indices = indices[:int(limit_value)]
        elif limit_by == 'days':
            limited_indices = list()
            limit_day = datetime.datetime.combine(
                            datetime.datetime.today(),
                            datetime.time.min
                        ) - datetime.timedelta(days=limit_value)
            # ES CAT API sends timestamp in nanoseconds.
            limit_epoch = limit_day.timestamp() * 1000
            for index in indices:
                if float(index['creation.date']) < limit_epoch:
                    break
                limited_indices.append(index)
            indices = limited_indices

    return indices


class ElasticLogState(object):
    """
    Holds state for an elastic log search query so we can resume searching
    from earlier results.

    The intention is that this is an opaque object that is held by the client.
    Only the ElasticLogSearcher looks at its innards.
    """
    def __init__(self):
        # Holds the sort value (an integer) of the first result in the current
        # search.
        #
        # The sort value is an elasticsearch-computed value for each document
        # for a particular search ordering. In our case, it is based on the
        # timestamp.
        self.before_sort_val = -1

        # Holds the sort value of the last result in the current search.
        self.after_sort_val = -1

    @classmethod
    def clone(cls, state):
        """ Clone from an existing state """
        s = ElasticLogState()
        s.before_sort_val = state.before_sort_val
        s.after_sort_val = state.after_sort_val
        return s

    def to_dict(self):
        """ Returns the state as a dict """
        return {
            'before': self.before_sort_val,
            'after': self.after_sort_val
        }

    def to_json_str(self):
        """ Serializes state as json """
        return json.dumps(self.to_dict(), separators=(',', ':'))

    def from_json_str(self, js_str):
        """ Deserializes the state from json """
        if js_str:
            js = json.loads(js_str)
            self.before_sort_val = js['before']
            self.after_sort_val = js['after']


class ElasticLogSearcher(object):
    """
    Hides some elasticsearch specific queries behind a (hopefully) generic
    log search interface.

    This object must remain stateless. It will be reconstructed on every
    client request. Any state must be provided as arguments to its public
    methods.
    """

    def __init__(self, index):
        """ New searcher, looking at a specific index """
        ELASTICSEARCH_HOSTS = config['ELASTICSEARCH']['hosts']
        ELASTICSEARCH_TIMEOUT = config['ELASTICSEARCH']['timeout']
        ELASTICSEARCH_MAX_RETRIES = config['ELASTICSEARCH']['max_retries']
        self.es = Elasticsearch(ELASTICSEARCH_HOSTS,
                                timeout=ELASTICSEARCH_TIMEOUT,
                                max_retries=ELASTICSEARCH_MAX_RETRIES,
                                retry_on_timeout=True)
        self.index = index

        # Check if index does not exist
        if not self.es.indices.exists(index):
            raise Exception(f'Logs not found for {index}')

    def search(self, state,
               query_term=None, source_filters=None, time_filters=None,
               query_size=1000, match_all=False):
        """
        Returns up to query_size logs that match the query_term and the
        filters.

        The starting point of the search is dictated by the "after_sort_val" in
        the state argument (see ElasticLogState). The search only considers
        entries with timestamp sort values that are greater than the state's
        "after_sort_val".

        If the query_term is unspecified (None), this will match against any
        log entry.

        The source_filters parameter is an object containing hierarchical data of
        system_type, system_id and sources to filter on. If system_type, system_id
        and source of the message does not match any of the values in the object
        then the message will be omitted from the result.

        The time_filters parameter is a two-element list containing a lower and
        upper bound (both inclusive). Time is specified in ISO8601 format
        e.g. 2015-01-01T12:10:30.123456Z.
        If the timestamp of a message does not lie within the range then it
        will be omitted.

        The match_all parameter is a boolean (False) which controls if the
        query_term should be matched exactly or just partial matches are
        acceptable.

        Returns a list with the following entry dicts:
        {
            "hits": [
                "sort": [sort values from search engine],
                "_source": {
                    "@timestamp": value,
                    "src": log source,
                    "msg": log content
                }, ...
            ],
            "state" { opaque state object holding search state },
            "total_search_hits" { "value": 10000, "relation": "gte" }
        }

        All results are returned in ascending timestamp order.

        TODO (jimmy): hide elastic specific stuff in return value?
        """
        body = self._build_query_body(query_term, source_filters, time_filters, match_all)
        if state.after_sort_val is not None:
            body['search_after'] = [state.after_sort_val]

        result = self.es.search(body=body,
                                index=self.index,
                                size=query_size,
                                sort='@timestamp:asc',
                                ignore_throttled=False)
        # A dict with value (upto 10k) and relation if
        # the actual hits is exact or greater than
        total_search_hits = result['hits']['total']
        result = result['hits']['hits']

        new_state = ElasticLogState.clone(state)
        _, new_state.after_sort_val = self._get_delimiting_sort_values(result)

        return {'hits': result, 'state': new_state, 'total_search_hits': total_search_hits}

    def _build_query_body(self, query_term,
                          source_filters, time_filters, match_all=False):
        """
        Constructs a query body from the specified query term
        (which is treated as an elasticsearch query string) and
        the filters.
        """

        def _generate_match_query(field, value):
            return {
                'match': {
                    field: value
                }
            }

        def _generate_must_query(must_list):
            if not must_list:
                return {}
            return {
                'bool': {
                    'must': must_list
                }
            }

        def _generate_should_query(should_list):
            if not should_list:
                return {}
            return {
                'bool': {
                    'should': should_list,
                    'minimum_should_match': 1
                }
            }

        # We treat the text filter as a query string, which is Lucerne
        # query DSL. The text filter is capable of complex filtering and
        # search (this will double up as our "advanced" search function)
        must_queries = []
        if query_term is not None:
            must_queries.append({'query_string': {
                'query': query_term,
                'default_operator': 'AND' if match_all else 'OR'
            }})

        # Source filters are either simple (list of src) or
        # hierarchical (system_type -> system_id -> src).
        # In ES, should queries are equivalent to performing OR query and
        # must queries are for performing AND queries.
        #
        # The hierarchical source filters is a dict which looks liks this:
        # {
        #   system_type: {
        #       system_id: {
        #           [src]
        #       }
        #   }
        # }
        #
        # The query is: [(system_type) AND [(sytem_id) AND ([src])]]
        # which gets converted into the following filter query:
        # {
        # 'bool': {
        #   'should': [{
        #       'bool': {
        #           'must': [{
        #               'match': {'system_type': 'cluster'}
        #           },{
        #               'bool': {
        #                   'should': [{
        #                       'bool': {
        #                           'must': [{
        #                               'match': {'system_id': 'node-1-cab18-fc-04'}
        #                           },{
        #                           'bool': {
        #                               'should': [
        #                                   {'match': {'src': 'apigateway'}},
        #                                   {'match': {'src': 'dataplacement'}},
        #                                   {'match': {'src': 'discovery'}}
        #                               ]
        #                           }
        #                       }
        #                   ]}
        #               },{
        #                   'bool': {
        #                       'must': [{
        #                           'match': {'system_id': 'node-3-cab18-fc-06'}
        #                       },{
        #                       'bool': {
        #                           'should': [{'match': {'src': 'apigateway'}}]
        #                       }
        #                   }]}
        # }]}}]}}]}}
        #
        # A simple source filter is a list of src which looks liks this:
        # ['funos']
        #
        # The query is: src:('funos' OR 'storage_agent')
        # which gets converted into the following filter query:
        # {
        #  'bool': {
        #       'should': [
        #           {'match': {'src': 'funos'}},
        #           {'match': {'src': 'apigateway'}}
        #       ]
        #   }
        # }

        filter_queries = []
        if source_filters and len(source_filters) > 0:
            if type(source_filters) == dict:
                system_type_list = []
                for system_type, system_ids in source_filters.items():
                    system_id_list = []
                    for system_id, sources in system_ids.items():
                        source_list = [_generate_match_query('src', source)
                                    for source in sources]
                        source_query = _generate_should_query(source_list)

                        system_id_query = _generate_must_query([
                            _generate_match_query('system_id', system_id),
                            source_query
                        ])
                        system_id_list.append(system_id_query)

                    system_type_query = _generate_must_query([
                        _generate_match_query('system_type', system_type),
                        _generate_should_query(system_id_list)
                    ])
                    system_type_list.append(system_type_query)

                compound_source_queries = _generate_should_query(system_type_list)
                filter_queries.append(compound_source_queries)

            elif type(source_filters) == list:
                source_query_list = [_generate_match_query('src', source)
                                     for source in source_filters]
                source_query = _generate_should_query(source_query_list)
                print(source_query)
                filter_queries.append(source_query)

        # Time filters are range filters
        if time_filters:
            start = time_filters[0]
            end = time_filters[1]
            time_range = {}
            if start:
                time_range['gte'] = start
            if end:
                time_range['lte'] = end
            range = {'range': {
                '@timestamp': time_range
            }}
            filter_queries.append(range)

        compound_query = {}
        compound_query['must'] = must_queries
        compound_query['filter'] = filter_queries

        body = {}
        body['query'] = {}
        # The "bool" key is essentially an "AND" of all the search and filter
        # terms. Elasticsearch DSL is weird in that way.
        body['query']['bool'] = compound_query
        return body

    def search_backwards(self, state,
                         query_term=None,
                         source_filters=None, time_filters=None,
                         query_size=1000,
                         match_all=False):
        """
        The same as search, but only considers entries with timestamps that
        have lower values than the "before_sort_val" in the state argument.
        """
        body = self._build_query_body(query_term, source_filters, time_filters, match_all)
        if state.before_sort_val != -1:
            body['search_after'] = [state.before_sort_val]

        # The recipe for search_before is to do a search_after in descending
        # sort order, and then reverse the list of results. Quirky.
        result = self.es.search(body=body,
                                index=self.index,
                                size=query_size,
                                sort='@timestamp:desc',
                                ignore_throttled=False)
        # A dict with value (upto 10k) and relation if
        # the actual hits is exact or greater than
        total_search_hits = result['hits']['total']
        result = result['hits']['hits']
        result.reverse()

        new_state = ElasticLogState.clone(state)
        new_state.before_sort_val, _ = self._get_delimiting_sort_values(result)

        return {'hits': result, 'state': new_state, 'total_search_hits': total_search_hits}

    @staticmethod
    def _get_delimiting_sort_values(result):
        """
        Obtains the sort values for the first and last entries in the
        result list, returning a tuple of (first_val, last_val).
        """
        first = -1
        last = -1

        if result:
            vals = result[0].get('sort')
            if vals:
                first = vals[0]
            vals = result[-1].get('sort')
            if vals:
                last = vals[0]

        return (first, last)

    def get_unique_entries(self, field):
        """
        Obtains a dict of unique values along with the count of documents for the given field.

        The field can be thought of as a column in a table, or a key in a
        structured log.
        """
        max_unique_entries = 100

        # Construct a search query that does a term-aggregation to determine
        # unique values. Anything prefixed with dontcare is really just a
        # user-determined identifier.
        body = {}
        body['aggs'] = {
            'unique_vals': {
                'terms': {
                    'field': field,
                    'size': max_unique_entries
                }
            }
        }

        result = self.es.search(body=body,
                                index=self.index,
                                ignore_throttled=False,
                                size=0)  # we're not really searching

        buckets = result.get('aggregations', {}).get('unique_vals',{}).get('buckets', [])
        return {bucket['key']: bucket['doc_count'] for bucket in buckets}

    def get_aggregated_unique_entries(self, parent_fields, child_fields=[]):
        """
        Obtains aggregated unique entries based on the a list of parent & child fields.

        Parent fields define multi level aggregations. For ex: ['system_type', 'system_id']
        will have unique entries of field 'system_id' for each unique entry of field 'system_type'

        Child fields define single level aggregations.
        """
        max_unique_entries = 100
        def generate_aggs_body(parent_fields, child_fields=[]):
            body = dict()
            if len(parent_fields) == 0:
                return body

            field = parent_fields.pop()
            has_more_fields = len(parent_fields) > 0
            body['aggs'] = {
                field: {
                    'terms': { 'field': field, 'size': max_unique_entries },
                }
            }

            if has_more_fields:
                body['aggs'][field] = {
                    **body['aggs'][field],
                    **generate_aggs_body(parent_fields, child_fields)
                }
            elif len(child_fields) > 0:
                aggs = dict()
                for child_field in child_fields:
                    aggs[child_field] = {
                        'terms': {'field': child_field, 'size': max_unique_entries}
                    }

                body['aggs'][field] = {
                    **body['aggs'][field],
                    'aggs': aggs
                }

            return body

        body = generate_aggs_body(list(parent_fields[::-1]), child_fields)

        result = self.es.search(body=body,
                                index=self.index,
                                ignore_throttled=False,
                                size=0)  # we're not really searching

        buckets = result.get('aggregations', {}).get(parent_fields[0], {}).get('buckets', [])
        return buckets

    def get_document_by_id(self, doc_id):
        """
        Look up a specific log line by document id.

        The doc_id is specified by elasticsearch, and is unique per index.
        TODO (jimmy): spoils our agnostic API
        """
        return self.es.get(index=self.index, id=doc_id)

    def get_document_count(self, query_terms=None, source_filters=None, time_filters=None):
        """ Returns count of documents for the given search query and filters """
        body = self._build_query_body(query_terms, source_filters, time_filters)
        result = self.es.count(index=self.index, body=body, ignore_throttled=False)
        count = result['count']
        return count

