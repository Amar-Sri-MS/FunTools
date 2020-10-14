#!/usr/bin/env python3

#
# Flask app for log viewing.
#
# Performs elasticsearch queries to obtain logs and to allow back and forth
# navigation. Still a work in progress.
#

import json
import os

import jinja2

from elasticsearch7 import Elasticsearch
from flask import Flask
from flask import request


app = Flask(__name__)


def main():
    app.run(host='0.0.0.0')


@app.route('/')
def root():
    """ Serves the root page, which shows a list of logs """
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

    indices = es.indices.get('log_*')

    # Assume our template is right next door to us.
    dir = _get_script_dir()

    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(dir),
                             trim_blocks=True,
                             lstrip_blocks=True)
    template = jinja_env.get_template('root_template.html')

    return _render_root_page(indices, jinja_env, template)


def _get_script_dir():
    """ Obtains the directory where this script resides """
    module_path = os.path.realpath(__file__)
    return os.path.dirname(module_path)


def _render_root_page(log_ids, jinja_env, template):
    """ Renders the root page from a template """
    template_dict = {}
    template_dict['logs'] = log_ids

    result = template.render(template_dict, env=jinja_env)
    return result


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
        self.es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
        self.index = index

    def search(self, state,
               query_term=None, source_filters=None, time_filters=None,
               query_size=1000):
        """
        Returns up to query_size logs that match the query_term and the
        filters.

        The starting point of the search is dictated by the "after_sort_val" in
        the state argument (see ElasticLogState). The search only considers
        entries with timestamp sort values that are greater than the state's
        "after_sort_val".

        If the query_term is unspecified (None), this will match against any
        log entry.

        The source_filters parameter is a list of sources to filter on. If a
        message source does not match any of the values in the list then
        the message will be omitted.

        The time_filters parameter is a two-element list containing a lower and
        upper bound (both inclusive). Time is specified in ISO8601 format
        e.g. 2015-01-01T12:10:30.123456Z.
        If the timestamp of a message does not lie within the range then it
        will be omitted.

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
            "state" { opaque state object holding search state }
        }

        All results are returned in ascending timestamp order.

        TODO (jimmy): hide elastic specific stuff in return value?
        """
        body = self._build_query_body(query_term, source_filters, time_filters)
        if state.after_sort_val is not None:
            body['search_after'] = [state.after_sort_val]

        result = self.es.search(body=body,
                                index=self.index,
                                size=query_size,
                                sort='@timestamp:asc')
        result = result['hits']['hits']

        new_state = ElasticLogState.clone(state)
        _, new_state.after_sort_val = self._get_delimiting_sort_values(result)

        return {'hits': result, 'state': new_state}

    def _build_query_body(self, query_term,
                          source_filters, time_filters):
        """
        Constructs a query body from the specified query term
        (which is treated as an elasticsearch query string) and
        the filters.
        """

        # We treat the text filter as a query string, which is Lucerne
        # query DSL. The text filter is capable of complex filtering and
        # search (this will double up as our "advanced" search function)
        must_queries = []
        if query_term is not None:
            must_queries.append({'query_string': {
                'query': query_term
            }})

        # Source filters are treated as "terms" queries, which try to
        # match exactly against all provided values.
        filter_queries = []
        if source_filters:
            term = {'terms': {
                'src': source_filters
            }}
            filter_queries.append(term)

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
                         query_size=1000):
        """
        The same as search, but only considers entries with timestamps that
        have lower values than the "before_sort_val" in the state argument.
        """
        body = self._build_query_body(query_term, source_filters, time_filters)
        body['search_after'] = [state.before_sort_val]

        # The recipe for search_before is to do a search_after in descending
        # sort order, and then reverse the list of results. Quirky.
        result = self.es.search(body=body,
                                index=self.index,
                                size=query_size,
                                sort='@timestamp:desc')
        result = result['hits']['hits']
        result.reverse()

        new_state = ElasticLogState.clone(state)
        new_state.before_sort_val, _ = self._get_delimiting_sort_values(result)

        return {'hits': result, 'state': new_state}

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
        Obtains a list of unique values for the given field.

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
                                size=1)  # we're not really searching
        buckets = result['aggregations']['unique_vals']['buckets']
        return [bucket['key'] for bucket in buckets]

    def get_document_by_id(self, doc_id):
        """
        Look up a specific log line by document id.

        The doc_id is specified by elasticsearch, and is unique per index.
        TODO (jimmy): spoils our agnostic API
        """
        return self.es.get(index=self.index, id=doc_id)


@app.route('/log/<log_id>', methods=['GET'])
def get_log_page(log_id):
    """
    Displays a log page for a particular log_id.

    Subsequent updates to the page are handled via POST requests.
    """
    state, table_body = _get_requested_log_lines(log_id)

    es = ElasticLogSearcher(log_id)
    sources = es.get_unique_entries('src')

    # Assume our template is right next door to us.
    dir = _get_script_dir()

    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(dir),
                             trim_blocks=True,
                             lstrip_blocks=True)
    template = jinja_env.get_template('log_template.html')

    return _render_log_page(table_body, sources, state,
                            log_id, jinja_env, template)


@app.route('/log/<log_id>/content', methods=['POST'])
def get_log_contents(log_id):
    """
    Obtains log contents which can be used to update a page.
    """
    state, page_body = _get_requested_log_lines(log_id)

    return {'content': ''.join(page_body),
            'state': state.to_dict()}


def _get_requested_log_lines(log_id):
    """
    Obtains the requested log lines.

    Parameters on the flask request object control which lines are returned.
    Request parameters include:

        next=true: Get up to 1000 log lines with timestamps greater than the
                   current state.
        prev=true: Get up to 1000 log lines with timestamps smaller than the
                   current state.
        include=id: Include a specific log line with the given id
        filter=term: Only include log lines that match the filter.

    Returns a tuple containing: (
        state: next state object for future searches
        body: log lines formatted as HTML table body
    )
    """
    next = request.args.get('next', False) == 'true'
    prev = request.args.get('prev', False) == 'true'
    include = request.args.get('include', None)

    filters = {}
    filter_str = request.args.get('filter', None)
    if filter_str:
        filters = json.loads(filter_str)

    state_str = request.args.get('state', None)
    state = ElasticLogState()
    state.from_json_str(state_str)

    # Elasticsearch has a limit of 10K results, so pagination is required
    size = 1000
    es = ElasticLogSearcher(log_id)
    before, after, state = get_temporally_close_hits(es, state, size,
                                                     filters, next, prev)

    # Before and after are not inclusive searches, so we have to include
    # the actual search result here via a direct document lookup. Very sad.
    #
    # TODO (jimmy): find another way around this kludge.
    centre = []
    if include is not None:
        doc = es.get_document_by_id(include)

        # Stash an anchor id in here so we can jump straight to the line
        # that we searched for.
        doc['anchor_link'] = '0'
        centre = [doc]

    result = before + centre + after

    page_body = []

    # This quirky magic is how we get paging in search queries. We determine
    # the sort value for the first and last entry in this query.
    for hit in result:
        line = _convert_to_table_row(hit)
        page_body.append(line)

    return state, page_body


def _convert_to_table_row(hit):
    """ Converts a search hit into an HTML table row """
    s = hit['_source']

    # The log lines are organized as table rows in the template
    line = '<tr style="vertical-align: baseline">'
    if hit.get('anchor_link'):
        line = '<tr class={} id={}>'.format('search_highlight',
                                            hit.get('anchor_link'))

    line += '<td>{}</td> <td>{}</td> <td style="white-space: pre">{}</td>'.format(s['src'],
                                                         s['@timestamp'],
                                                         s['msg'])
    line += '</tr>'
    return line


def get_temporally_close_hits(es, state, size, filters, next, prev):
    """
    Obtains a list of search hits that have timestamps before
    and/or after the current state.

    The prev and next booleans control whether to return before, after or both.

    The returned tuple is (before_list, after_list, next_state).
    Both lists are ordered by timestamp. We only return empty lists, never None.
    """
    before = []
    after = []

    query_string = filters.get('text')
    source_filters = filters.get('sources', [])
    time_filters = filters.get('time')

    # The default is to return "next" results if both are unspecified
    if next or (not next and not prev):
        results = es.search(state, query_string,
                            source_filters, time_filters, query_size=size)
        after = results['hits']
        state = results['state']
    if prev:
        results = es.search_backwards(state, query_string,
                                      source_filters, time_filters,
                                      query_size=size)
        before = results['hits']
        state = results['state']

    return before, after, state


def _render_log_page(table_body, sources, state,
                     log_id, jinja_env, template):
    """ Renders the log page """
    template_dict = {}
    template_dict['body'] = ''.join(table_body)
    template_dict['log_id'] = log_id
    template_dict['sources'] = sources
    template_dict['state'] = state.to_json_str()

    result = template.render(template_dict, env=jinja_env)
    return result


@app.route('/log/<log_id>/search', methods=['GET'])
def search(log_id):
    """
    Returns an HTML snippet containing links to log entries matching
    the search term.
    """
    search_term = request.args.get('query')
    page = request.args.get('page', 1)
    page = int(page)

    # TODO (jimmy): we ought to do this only once
    total_search_hits = _get_total_hit_count(log_id, search_term)

    state_str = request.args.get('state', None)
    state = ElasticLogState()
    state.from_json_str(state_str)

    es = ElasticLogSearcher(log_id)
    size = 20

    results = es.search(state, search_term, query_size=size)
    hits = results['hits']
    state = results['state']

    links = []
    for hit in hits:
        s = hit['_source']

        # TODO (jimmy): urgh, we exposed the elastic state here.
        hit_state = ElasticLogState()
        hit_state.before_sort_val = hit['sort'][0]
        hit_state.after_sort_val = hit['sort'][0]

        # The #0 anchor is how we jump to the searched-for line when the link
        # is selected.
        #
        # Also note that we use double quotes here in python and single quotes
        # in the link HTML to avoid escape magic because of the state JSON
        # string.
        hit_state_str = hit_state.to_json_str()
        link = ("<a href='/log/{}?"
                "state={}&"
                "next=true&"
                "prev=true&"
                "include={}#0'>{} {}</a>".format(log_id,
                                                 hit_state_str,
                                                 hit['_id'],
                                                 s['@timestamp'],
                                                 s['msg']))
        links.append(link)

    return _render_search_page(links, log_id, search_term, state, page,
                               total_search_hits)


def _get_total_hit_count(log_id, search_term):
    """ Obtains the search hit count, up to a maximum of 1000 """
    es = ElasticLogSearcher(log_id)
    state = ElasticLogState()
    size = 1000

    results = es.search(state, search_term, query_size=size)
    return len(results['hits'])


def _render_search_page(search_results, log_id, search_term, state, page,
                        total_search_hits):
    """ Renders the search results page """
    template_dict = {}
    template_dict['body'] = '<br><br>'.join(search_results)
    template_dict['log_id'] = log_id
    template_dict['query'] = search_term
    template_dict['state'] = state.to_json_str()
    template_dict['page'] = page
    template_dict['page_entry_count'] = len(search_results)
    template_dict['search_hits'] = total_search_hits

    dir = _get_script_dir()
    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(dir),
                             trim_blocks=True,
                             lstrip_blocks=True)
    template = jinja_env.get_template('search_template.html')

    result = template.render(template_dict, env=jinja_env)
    return result


if __name__ == '__main__':
    main()
