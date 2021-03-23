#!/usr/bin/env python3

#
# Flask app for log viewing.
#
# Performs elasticsearch queries to obtain logs and to allow back and forth
# navigation. Still a work in progress.
#

import json
import os
import requests
import sys
import time

import jinja2

from elasticsearch7 import Elasticsearch
from flask import Flask
from flask import request
from pathlib import Path
from requests.exceptions import HTTPError
from urllib.parse import quote_plus

from ingester import ingester_page
from web_usage import web_usage

sys.path.append('..')

import config_loader


app = Flask(__name__)
app.register_blueprint(ingester_page)
app.register_blueprint(web_usage, url_prefix='/events')


@app.errorhandler(Exception)
def handle_exception(error):
    """
    Handling exceptions by sending only the error message.
    This function is called whenever an unhandled Exception
    is raised.
    """
    # TODO(Sourabh): Maybe redirect to a template with an error message instead
    # of just displaying a message. Also print error stacktrace.
    print('ERROR:', str(error))
    return str(error), 500


def main():
    config = config_loader.get_config()

    # Updating Flask's config with the configs from file
    app.config.update(config)
    app.run(host='0.0.0.0')


@app.route('/')
def root():
    """ Serves the root page, which shows a list of logs """
    ELASTICSEARCH_HOSTS = app.config['ELASTICSEARCH']['hosts']
    es = Elasticsearch(ELASTICSEARCH_HOSTS)

    # Using the ES CAT API to get indices
    # CAT API supports sorting and returns more data
    indices = es.cat.indices(
        index='log_*',
        h='health,index,id,docs.count,store.size,creation.date',
        format='json',
        s='creation.date:desc'
    )

    # Assume our template is right next door to us.
    dir = os.path.join(_get_script_dir(), 'templates')

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
    template_dict['logs'] = list()

    for log in log_ids:
        id = log['index']
        log_view_base_url = _get_log_view_base_url(id)
        creation_date_epoch = int(log['creation.date'])
        # Separting out seconds and milliseconds from epoch
        creation_date_s, creation_date_ms = divmod(creation_date_epoch, 1000)
        creation_date = '{}'.format(
                            time.strftime('%B %d, %Y %H:%M:%S', time.gmtime(creation_date_s)),
                            )

        template_dict['logs'].append({
            'name': id,
            'link': log_view_base_url,
            'creation_date': creation_date,
            'health': log['health'],
            'doc_count': log['docs.count'],
            'es_size': log['store.size']
        })

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
        ELASTICSEARCH_HOSTS = app.config['ELASTICSEARCH']['hosts']
        self.es = Elasticsearch(ELASTICSEARCH_HOSTS)
        self.index = index

        # Check if index does not exist
        if not self.es.indices.exists(index):
            raise Exception(f'Logs not found for {index}')

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
            "state" { opaque state object holding search state },
            "total_search_hits" { "value": 10000, "relation": "gte" }
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
        # A dict with value (upto 10k) and relation if
        # the actual hits is exact or greater than
        total_search_hits = result['hits']['total']
        result = result['hits']['hits']

        new_state = ElasticLogState.clone(state)
        new_state.before_sort_val, new_state.after_sort_val = self._get_delimiting_sort_values(result)

        return {'hits': result, 'state': new_state, 'total_search_hits': total_search_hits}

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
        if state.before_sort_val != -1:
            body['search_after'] = [state.before_sort_val]

        # The recipe for search_before is to do a search_after in descending
        # sort order, and then reverse the list of results. Quirky.
        result = self.es.search(body=body,
                                index=self.index,
                                size=query_size,
                                sort='@timestamp:desc')
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
                                size=0)  # we're not really searching

        buckets = result['aggregations']['unique_vals']['buckets']
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
                                size=0)  # we're not really searching

        buckets = result['aggregations'][parent_fields[0]]['buckets']
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
        result = self.es.count(index=self.index, body=body)
        count = result['count']
        return count

@app.route('/log/<log_id>', methods=['GET'])
def get_log_page(log_id):
    """
    Displays a log page for a particular log_id.

    Subsequent updates to the page are handled via POST requests.
    """
    state, total_search_hits, table_body = _get_requested_log_lines(log_id)

    # Assume our template is right next door to us.
    dir = os.path.join(_get_script_dir(), 'templates')

    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(dir),
                             trim_blocks=True,
                             lstrip_blocks=True)
    template = jinja_env.get_template('log_template.html')

    return _render_log_page(table_body, total_search_hits, state,
                            log_id, jinja_env, template)


@app.route('/log/<log_id>/content', methods=['POST'])
def get_log_contents(log_id):
    """
    Obtains log contents which can be used to update a page.
    """
    state, total_search_hits, page_body = _get_requested_log_lines(log_id)

    return {'content': ''.join(page_body),
            'total_search_hits': total_search_hits,
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
        total_search_hits: object containing total hits value
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
    before, after, state, total_search_hits = get_temporally_close_hits(es, state, size,
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

    return state, total_search_hits, page_body


def _convert_to_table_row(hit):
    """ Converts a search hit into an HTML table row """
    s = hit['_source']
    log_id = hit['_index']
    log_view_base_url = _get_log_view_base_url(log_id)

    msg = s['msg']
    timestamp = s['@timestamp']
    query = '"{}"'.format(msg.replace('\\','').replace('"',' ').replace('\'', '!\'')).replace('!', '!!')
    state = f'"before":"{timestamp}","after":"{timestamp}"'
    log_view_url = ('{}?state={{{}}}&next=true&prev=true&include={}#0').format(log_view_base_url, quote_plus(state), hit['_id'])

    # The log lines are organized as table rows in the template
    line = '<tr style="vertical-align: baseline">'
    if hit.get('anchor_link'):
        line = '<tr class={} id={}>'.format('search_highlight',
                                            hit.get('anchor_link'))

    line += '<td>{}</td> <td>{}</td> <td>{}</td>'.format(s['src'],
                                                         timestamp,
                                                         s.get('level'))
    line += '<td><a href="{}" target="_blank">{}</a></td>'.format(log_view_url,
                                                                  s['msg'])
    line += '</tr>'
    return line


def get_temporally_close_hits(es, state, size, filters, next, prev):
    """
    Obtains a list of search hits that have timestamps before
    and/or after the current state.

    The prev and next booleans control whether to return before, after or both.

    The returned tuple is (before_list, after_list, next_state, total_search_hits).
    Both lists are ordered by timestamp. We only return empty lists, never None.
    """
    before = []
    after = []
    total_search_hits = 0

    query_string = filters.get('text')
    source_filters = filters.get('sources', [])
    time_filters = filters.get('time')

    # The default is to return "next" results if both are unspecified
    if next or (not next and not prev):
        results = es.search(state, query_string,
                            source_filters, time_filters, query_size=size)
        after = results['hits']
        state = results['state']
        total_search_hits = results['total_search_hits']
    if prev:
        results = es.search_backwards(state, query_string,
                                      source_filters, time_filters,
                                      query_size=size)
        before = results['hits']
        state = results['state']
        total_search_hits = results['total_search_hits']

    return before, after, state, total_search_hits


def _render_log_page(table_body, total_search_hits, state,
                     log_id, jinja_env, template):
    """ Renders the log page """
    es = ElasticLogSearcher(log_id)
    sources = es.get_unique_entries('src')
    unique_entries = es.get_aggregated_unique_entries(['system_type', 'system_id'], ['src'])

    template_dict = {}
    template_dict['body'] = ''.join(table_body)
    template_dict['log_id'] = log_id
    template_dict['total_search_hits'] = total_search_hits
    template_dict['sources'] = sources
    template_dict['unique_entries'] = unique_entries
    template_dict['log_view_base_url'] = _get_log_view_base_url(log_id)
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
    time_start = request.args.get('time_start', '')
    time_end = request.args.get('time_end', '')
    time_filters = [time_start, time_end]

    # TODO (jimmy): we ought to do this only once
    total_search_hits = _get_total_hit_count(log_id, search_term, time_filters)

    state_str = request.args.get('state', None)
    state = ElasticLogState()
    state.from_json_str(state_str)

    es = ElasticLogSearcher(log_id)
    size = 20

    results = es.search(state, search_term, time_filters=time_filters, query_size=size)
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


def _get_total_hit_count(log_id, search_term, time_filters):
    """ Obtains the search hit count, up to a maximum of 1000 """
    es = ElasticLogSearcher(log_id)
    state = ElasticLogState()
    size = 1000

    results = es.search(state, search_term, time_filters=time_filters, query_size=size)
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

    dir = os.path.join(_get_script_dir(), 'templates')
    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(dir),
                             trim_blocks=True,
                             lstrip_blocks=True)
    template = jinja_env.get_template('search_template.html')

    result = template.render(template_dict, env=jinja_env)
    return result


@app.route('/log/<log_id>/dashboard', methods=['GET'])
def dashboard(log_id):
    """ Renders the dashboard page for a particular log_id """
    # Assume our template is right next door to us.
    dir = os.path.join(_get_script_dir(), 'templates')

    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(dir),
                             trim_blocks=True,
                             lstrip_blocks=True)
    template = jinja_env.get_template('dashboard_template.html')

    return _render_dashboard_page(log_id, jinja_env, template)


def _get_log_view_base_url(log_id):
    """
    Base URL of home grown log viewer
    """
    log_view_base_url = ("/log/{}").format(log_id)
    return log_view_base_url


@app.route('/log/<log_id>/dashboard/anchors', methods=['GET'])
def get_anchors(log_id):
    """
    Returns current, previous and next anchor files
    for the given page number.
    page number is zero indexed.
    """
    page_num = int(request.args.get('page', 0))
    anchors = _read_paginated_anchor_file(log_id, page_num)
    return anchors


def _get_kibana_base_url(log_id):
    """
    Creates a Kibana Base URL which could be used to create kibana urls
    with any given query.
    URL contains a term 'KIBANA_QUERY' which should be replaced with
    the given search query.
    URL contains defaults for selected columns to show in Kibana dashboard
    and time filter to be within last 90 days.
    """

    KIBANA_HOST = app.config['KIBANA']['host']
    KIBANA_PORT = app.config['KIBANA']['port']
    # KIBANA defaults.
    # TODO(Sourabh): Would be better to have this in config files
    kibana_time_filter = "from:'1970-01-01T00:00:00.000Z',to:now"
    kibana_selected_columns = 'src,level,msg'
    kibana_base_url = ("http://{}:{}/app/kibana#/discover/?_g=(time:({}))&_a=(columns:!({}),index:{},"
                  "query:(language:kuery,query:'KIBANA_QUERY'))").format(KIBANA_HOST,
                                                                         KIBANA_PORT,
                                                                         kibana_time_filter,
                                                                         kibana_selected_columns,
                                                                         log_id)
    return kibana_base_url

def _read_file(log_id, file_name, default={}):
    """
    Gets file from file server
    Returns 'default' if no file found or errored out
    """
    FILE_SERVER_URL = app.config['FILE_SERVER_URL']
    url = f'{FILE_SERVER_URL}/{log_id}/file/{file_name}'
    data = default
    try:
        response = requests.get(url)
         # If the response was successful, no Exception will be raised
        response.raise_for_status()
        data = response.json()

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6
    except Exception as e:
        print('Could not find file', e)

    return data

def _read_paginated_anchor_file(log_id, page_num=0):
    """
    Returns current, previous and next anchor files
    for the given page number
    """
    previous_anchors = _read_file(log_id, f'anchors_{page_num-1}.json', default=None)
    anchors = _read_file(log_id, f'anchors_{page_num}.json', default=[])
    next_anchors = _read_file(log_id, f'anchors_{page_num+1}.json', default=None)

    return {
        'previous_anchors': previous_anchors,
        'anchors': anchors,
        'next_anchors': next_anchors
    }

def _get_analytics_data(log_id):
    """
    Get all the analytics data
    Returns a dict containing duplicates and anchors
    """
    # Reading metadata of detected anchors file
    anchors_meta = _read_file(log_id, 'anchors_meta.json', default={})
    # Reading detected anchors from the JSON file
    anchors = _read_paginated_anchor_file(log_id)

    # Reading detected duplicates from the JSON file
    duplicates = _read_file(log_id, 'duplicates.json', default=[])

    return {
        **anchors,
        'anchors_meta': anchors_meta,
        'duplicates': duplicates
    }


def _render_dashboard_page(log_id, jinja_env, template):

    es = ElasticLogSearcher(log_id)
    log_view_base_url = _get_log_view_base_url(log_id)
    keyword_for_level = app.config.get('LEVEL_KEYWORDS')

    default_log_levels = list(keyword_for_level.keys())
    # Number of documents to fetch for most recent logs
    RECENT_LOGS_SIZE = 50

    sources = es.get_unique_entries('src')
    system_types = es.get_unique_entries('system_type')
    system_ids = es.get_unique_entries('system_id')
    unique_entries = es.get_aggregated_unique_entries(['system_type', 'system_id'], ['src'])
    log_level_stats = _get_log_level_stats(log_id)

    # Fetch the first non zero log level
    nonzero_log_levels = [level for level in default_log_levels if log_level_stats[level]['count'] > 0]

    recent_logs = _get_recent_logs(log_id, RECENT_LOGS_SIZE, log_levels=nonzero_log_levels[0:1])

    analytics_data = _get_analytics_data(log_id)

    template_dict = {}
    template_dict['log_id'] = log_id
    template_dict['sources'] = sources
    template_dict['system_types'] = system_types
    template_dict['system_ids'] = system_ids
    template_dict['unique_entries'] = unique_entries
    template_dict['log_view_base_url'] = log_view_base_url
    template_dict['log_level_stats'] = log_level_stats
    template_dict['log_level_for_recent_logs'] = nonzero_log_levels[0]
    template_dict['recent_logs'] = _render_log_entries(recent_logs)
    template_dict['analytics_data'] = json.dumps(analytics_data)

    result = template.render(template_dict, env=jinja_env)
    return result


@app.route('/log/<log_id>/dashboard/level-stats', methods=['GET'])
def log_level_stats(log_id):
    sources = request.args.getlist('source')
    result = _get_log_level_stats(log_id, sources)
    return result


def _get_log_level_stats(log_id, sources=[], log_levels=None, time_filters=None):
    es = ElasticLogSearcher(log_id)
    log_view_base_url = _get_log_view_base_url(log_id)
    query = ''
    if len(sources) > 0:
        query = f'src:({" OR ".join(sources)}) AND'

    keyword_for_level = app.config.get('LEVEL_KEYWORDS')

    default_log_levels = keyword_for_level.keys()
    if log_levels is None:
        log_levels = default_log_levels

    document_counts = {}
    for idx, level in enumerate(log_levels):
        keywords = [f'"{keyword}"' for keyword in keyword_for_level[level]]
        keyword_query_terms = ' OR '.join(keywords)
        log_level_query = f'{query} (level:({keyword_query_terms}) OR msg:({keyword_query_terms}))'
        log_view_url = f'{log_view_base_url}/search?query={quote_plus(log_level_query)}'
        document_counts[level] = {
            'order': idx,
            'count': es.get_document_count(keyword_query_terms, sources, time_filters),
            'log_view_url': log_view_url,
            'keywords': ', '.join(keyword_for_level[level])
        }

    return document_counts


@app.route('/log/<log_id>/dashboard/recent', methods=['GET'])
def recent_logs(log_id):
    sources = request.args.getlist('source')
    levels = request.args.getlist('level')
    # Number of log entries. Defaults to 50
    size = request.args.get('size', 50)

    recent_logs = _get_recent_logs(log_id, size, sources, levels)
    result = _render_log_entries(recent_logs)
    return result


def _get_recent_logs(log_id, size, sources=[], log_levels=None, time_filters=None):
    """
    Returns table body of recent log entries.

    size parameter determines the number of log entries.
    log_levels parameter is of list type which contains log level
    """
    es = ElasticLogSearcher(log_id)
    state = ElasticLogState()

    keyword_for_level = app.config.get('LEVEL_KEYWORDS')

    level_keywords = []
    query_string = ''
    if log_levels:
        for level in log_levels:
            level_keywords.extend([f'"{keyword}"' for keyword in keyword_for_level[level]])

        keyword_query_terms = ' OR '.join(level_keywords)
        # Check for the log level in either the level field or the msg field
        query_string = f'level:({keyword_query_terms}) OR msg:({keyword_query_terms})'

    results = es.search_backwards(state, query_string,
                                      sources, time_filters,
                                      query_size=size)
    hits = results['hits']
    # search_backwards returns the result in reverse order
    hits.reverse()

    page_body = []
    for hit in hits:
        line = _convert_to_table_row(hit)
        page_body.append(line)

    return page_body


def _render_log_entries(entries):
    """
    Returns an html table generated using the list of log entries
    """

    MODULE_PATH = Path(__file__)
    # This is equivalent to path.parent.parent
    MODULE_DIR = MODULE_PATH.resolve().parents[1] / 'view' / 'templates'

    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(MODULE_DIR),
                                trim_blocks=True,
                                lstrip_blocks=True)
    template = jinja_env.get_template('log_entries.html')

    header = ['Source', 'Timestamp', 'Level', 'Log Message']
    template_dict = {}
    template_dict['head'] = header
    template_dict['body'] = '\n'.join(entries)

    result = template.render(template_dict, env=jinja_env)
    return result


if __name__ == '__main__':
    main()
