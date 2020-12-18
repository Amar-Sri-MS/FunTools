#!/usr/bin/env python3

#
# Flask app for log viewing.
#
# Performs elasticsearch queries to obtain logs and to allow back and forth
# navigation. Still a work in progress.
#

import json
import os
import sys
import time

import jinja2

from elasticsearch7 import Elasticsearch
from flask import Flask
from flask import request
from pathlib import Path
from urllib.parse import quote_plus


app = Flask(__name__)


def main():
    config = {}
    try:
        with open('../config.json', 'r') as f:
            config = json.load(f)
    except IOError:
        print('Config file not found! Checking for default config file..')

    try:
        with open('../default_config.json', 'r') as f:
            default_config = json.load(f)
        # Overriding default config with custom config
        config = { **default_config, **config }
    except IOError:
        sys.exit('Default config file not found! Exiting..')

    # Updating Flask's config with the configs from file
    app.config.update(config)
    app.run(host='0.0.0.0')


@app.route('/')
def root():
    """ Serves the root page, which shows a list of logs """
    ELASTICSEARCH_HOSTS = app.config['ELASTICSEARCH']['hosts']
    es = Elasticsearch(ELASTICSEARCH_HOSTS)

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
    template_dict['logs'] = list()

    for id, log in log_ids.items():
        kibana_base_url = _get_kibana_base_url(id)
        # Replacing KIBANA_QUERY with empty string since we do not
        # want to query and want only the URL to the Kibana Dashboard
        kibana_url = kibana_base_url.replace('KIBANA_QUERY', '')
        creation_date_epoch = int(log.get('settings').get('index').get('creation_date'))
        # Separting out seconds and milliseconds from epoch
        creation_date_s, creation_date_ms = divmod(creation_date_epoch, 1000)
        creation_date = '{}.{:03d}'.format(
                                    time.strftime('%B %d, %Y %H:%M:%S', time.gmtime(creation_date_s)),
                                    creation_date_ms)

        template_dict['logs'].append({
            'name': id,
            'link': kibana_url,
            'creation_date': creation_date
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
        if state.before_sort_val != -1:
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
    log_id = hit['_index']
    kibana_base_url = _get_kibana_base_url(log_id)

    msg = s['msg']
    query = '"{}"'.format(msg.replace('\\','').replace('"',' ').replace('\'', '!\'')).replace('!', '!!')
    # This will be used to link Kibana dashboard from the log message
    kibana_url = kibana_base_url.replace('KIBANA_QUERY', quote_plus(query))

    # The log lines are organized as table rows in the template
    line = '<tr style="vertical-align: baseline">'
    if hit.get('anchor_link'):
        line = '<tr class={} id={}>'.format('search_highlight',
                                            hit.get('anchor_link'))

    line += '<td>{}</td> <td>{}</td> <td>{}</td>'.format(s['src'],
                                                         s['@timestamp'],
                                                         s.get('level'))
    line += '<td><a href="{}" target="_blank">{}</a></td>'.format(kibana_url,
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

    dir = _get_script_dir()
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
    dir = _get_script_dir()

    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(dir),
                             trim_blocks=True,
                             lstrip_blocks=True)
    template = jinja_env.get_template('dashboard_template.html')

    return _render_dashboard_page(log_id, jinja_env, template)


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
    kibana_time_filter = 'from:now-90d,to:now'
    kibana_selected_columns = 'src,level,msg'
    kibana_base_url = ("http://{}:{}/app/kibana#/discover/?_g=(time:({}))&_a=(columns:!({}),index:{},"
                  "query:(language:kuery,query:'KIBANA_QUERY'))").format(KIBANA_HOST,
                                                                         KIBANA_PORT,
                                                                         kibana_time_filter,
                                                                         kibana_selected_columns,
                                                                         log_id)
    return kibana_base_url


def _render_dashboard_page(log_id, jinja_env, template):

    es = ElasticLogSearcher(log_id)
    kibana_base_url = _get_kibana_base_url(log_id)

    sources = es.get_unique_entries('src')
    system_types = es.get_unique_entries('system_type')
    system_ids = es.get_unique_entries('system_id')
    unique_entries = es.get_aggregated_unique_entries(['system_type', 'system_id'], ['src'])
    recent_logs = _get_recent_logs(log_id, 50, log_levels=['error'])

    template_dict = {}
    template_dict['log_id'] = log_id
    template_dict['sources'] = sources
    template_dict['system_types'] = system_types
    template_dict['system_ids'] = system_ids
    template_dict['unique_entries'] = unique_entries
    template_dict['kibana_base_url'] = kibana_base_url
    template_dict['log_level_stats'] = _get_log_level_stats(log_id)
    template_dict['recent_logs'] = _render_log_entries(recent_logs)

    result = template.render(template_dict, env=jinja_env)
    return result


@app.route('/log/<log_id>/dashboard/level-stats', methods=['GET'])
def log_level_stats(log_id):
    sources = request.args.getlist('source')
    result = _get_log_level_stats(log_id, sources)
    return result


def _get_log_level_stats(log_id, sources=[], log_levels=None, time_filters=None):
    es = ElasticLogSearcher(log_id)
    kibana_base_url = _get_kibana_base_url(log_id)
    query = ''
    if len(sources) > 0:
        query = f'src:({" OR ".join(sources)}) AND'

    keyword_for_level = app.config.get('LEVEL_KEYWORDS')

    default_log_levels = keyword_for_level.keys()
    if log_levels is None:
        log_levels = default_log_levels

    document_counts = {}
    for idx, level in enumerate(log_levels):
        kibana_query = f'{query} msg:({keyword_for_level[level]})'
        document_counts[level] = {
            'order': idx,
            'count': es.get_document_count(keyword_for_level[level], sources, time_filters),
            'kibana_url': kibana_base_url.replace('KIBANA_QUERY', kibana_query),
            'keywords': keyword_for_level[level]
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
            level_keywords.append(keyword_for_level[level])

        # Check for the log level in either the level field or the msg field
        query_string = f'level:({" OR ".join(level_keywords)}) OR msg:({" OR ".join(level_keywords)})'

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
