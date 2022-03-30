#!/usr/bin/env python3

#
# Flask app for log viewing.
#
# Performs elasticsearch queries to obtain logs and to allow back and forth
# navigation. Still a work in progress.
#

import argparse
import datetime
import jinja2
import json
import logging
import os
import requests
import sys
import time


from flask import Flask
from flask import jsonify
from flask import request
from flask import g, redirect, session
from flask_session import Session

from pathlib import Path
from requests.exceptions import HTTPError
from urllib.parse import quote, quote_plus
from urllib.parse import unquote, unquote_plus

from common import login_required
from elastic_log_searcher import ElasticLogSearcher
from elastic_log_searcher import ElasticLogState
from elastic_metadata import ElasticsearchMetadata
from ingester import ingester_page
from web_usage import web_usage
from tools_view import tools_page

sys.path.append('..')

import elastic_log_searcher
import config_loader
import logger


app = Flask(__name__)
app.register_blueprint(ingester_page)
app.register_blueprint(web_usage, url_prefix='/events')
app.register_blueprint(tools_page, url_prefix='/tools')


config = config_loader.get_config()

# Updating Flask's config with the configs from file
app.config.update(config)

Session(app)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000,
                        help='port for HTTP file server')

    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)


# Checking for user session before processing
# the request.
@app.before_request
def load_user():
    g.user = None

    if 'user_email' in session:
        g.user = session['user_email']

    # Allowing users to ingest using API without maintaining session
    # provided users sends email in 'submitted_by' field.
    elif (
            request.endpoint in
            ('ingester_page.ingest',
             'ingester_page.upload',
             'ingester_page.upload_file'
            )
        ) and request.method == 'POST':
        g.user = request.form.get('submitted_by', None)


@app.route('/')
@login_required
def root():
    """ Serves the root page, which shows a list of logs """
    es_metadata = ElasticsearchMetadata()

    tags = request.args.get('tags', '')

    # Using the ES CAT API to get indices
    # CAT API supports sorting and returns more data
    indices = elastic_log_searcher._get_indices('log_*')

    if len(tags) > 0:
        tags_list = [tag.strip() for tag in tags.split(',')]
        metadata = es_metadata.get_by_tags(
                        tags_list,
                        size=len(indices))

        # Sadly indicies API does not let us select the indicies to filter
        # Filtering out the indices
        indices = [index for index in indices if index['index'] in metadata]
    else:
        log_ids = [index['index'] for index in indices]
        metadata = es_metadata.get_by_log_ids(log_ids)

    # Assume our template is right next door to us.
    dir = os.path.join(_get_script_dir(), 'templates')

    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(dir),
                             trim_blocks=True,
                             lstrip_blocks=True)
    template = jinja_env.get_template('root_template.html')

    return _render_root_page(indices, metadata, jinja_env, template)


def _get_script_dir():
    """ Obtains the directory where this script resides """
    module_path = os.path.realpath(__file__)
    return os.path.dirname(module_path)


def _render_root_page(log_ids, metadata, jinja_env, template):
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

        tags = metadata.get(id, {}).get('tags', [])

        template_dict['logs'].append({
            'name': id,
            'link': log_view_base_url,
            'creation_date': creation_date,
            'health': log['health'],
            'doc_count': log['docs.count'],
            'es_size': log['store.size'],
            'tags': tags,
            'metadata': metadata.get(id, {})
        })

    result = template.render(template_dict, env=jinja_env)
    return result


@app.route('/login', methods=['POST', 'GET'])
def login():
    # if login form is submitted
    if request.method == 'POST':
        # record the user email
        session['user_email'] = request.form.get('user_email')
        # redirect to the root page
        return redirect('/')

    if g.user:
        return redirect('/')

    # Assume our template is right next door to us.
    dir = os.path.join(_get_script_dir(), 'templates')

    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(dir),
                             trim_blocks=True,
                             lstrip_blocks=True)
    template = jinja_env.get_template('login.html')

    return template.render(env=jinja_env)


@app.route('/search', methods=['POST'])
def perform_search():
    """
    Performs search across different indices.
    """
    try:
        search_payload = request.get_json(force=True).get('search', None)
        log_ids = request.get_json(force=True).get('log_ids', None)
        if not search_payload:
                return jsonify({
                    'error': 'Could not find the search payload'
                }), 400
        if not log_ids:
                return jsonify({
                    'error': 'Could not find the log_ids'
                }), 400

        search_results = get_search_results(log_ids)
        return jsonify(search_results)
    except Exception as e:
        app.logger.exception('Error while performing search across indices.')
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/log/<log_id>', methods=['GET'])
@login_required
def get_log_page(log_id):
    """
    Displays a log page for a particular log_id.

    Subsequent updates to the page are handled via POST requests.
    """
    # Assume our template is right next door to us.
    dir = os.path.join(_get_script_dir(), 'templates')

    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(dir),
                             trim_blocks=True,
                             lstrip_blocks=True)
    template = jinja_env.get_template('log_template.html')
    jinja_env.filters['formatdatetime'] = _format_datetime

    return _render_log_page(log_id, jinja_env, template)


@app.route('/log/<log_id>/content', methods=['POST'])
def get_log_contents(log_id):
    """
    Obtains log contents which can be used to update a page.
    """
    try:
        state, total_search_hits, page_body = _get_requested_log_lines(log_id,
                                                                    include_hyperlinks=False)
    except Exception as e:
        app.logger.exception('Could not get log contents')
        return jsonify({
            'error': str(e)
        }), 500

    return {'content': ''.join(page_body),
            'total_search_hits': total_search_hits,
            'state': state.to_dict()}


def _get_requested_log_lines(log_id, include_hyperlinks=True):
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
        line = _convert_to_table_row(hit, include_hyperlinks)
        page_body.append(line)

    return state, total_search_hits, page_body


def _convert_to_table_row(hit, include_hyperlinks=True):
    """ Converts a search hit into an HTML table row """
    s = hit['_source']
    log_id = hit['_index']
    log_view_base_url = _get_log_view_base_url(log_id)

    msg = s['msg']
    timestamp = s['@timestamp']

    # The log lines are organized as table rows in the template
    line = '<tr style="vertical-align: baseline">'
    if hit.get('anchor_link'):
        line = '<tr class={} id={}>'.format('search_highlight',
                                            hit.get('anchor_link'))

    line += """
            <td class="table-source">{}</td>
            <td class="table-system_id">{}</td>
            <td class="table-timestamp">{}</td>
            <td class="table-level">{}</td>""".format(s['src'],
                                                      s.get('system_id'),
                                                      timestamp,
                                                      s.get('level'))
    if include_hyperlinks:
        state = f'"before":"{timestamp}","after":"{timestamp}"'
        log_view_url = ('{}?state={{{}}}&next=true&prev=true&include={}#0').format(
                            log_view_base_url,
                            quote_plus(state),
                            hit['_id'])
        line += '<td class="table-msg"><a href="{}" target="_blank">{}</a></td>'.format(log_view_url,
                                                                    msg)
    else:
        line += '<td class="table-msg">{}</td>'.format(msg)
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
    source_filters = filters.get('sources', {})
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


def _render_log_page(log_id, jinja_env, template):
    """ Renders the log page """
    try:
        es = ElasticLogSearcher(log_id)
        es_metadata = ElasticsearchMetadata()

        metadata = es_metadata.get(log_id)

        sources = es.get_unique_entries('src')
        unique_entries = es.get_aggregated_unique_entries(['system_type', 'system_id'], ['src'])

        template_dict = {}
        template_dict['log_id'] = log_id
        template_dict['sources'] = sources
        template_dict['unique_entries'] = unique_entries
        template_dict['log_view_base_url'] = _get_log_view_base_url(log_id)
        template_dict['metadata'] = metadata
        template_dict['job_link'] = _get_actual_job_link(log_id)

        state, total_search_hits, table_body = _get_requested_log_lines(
                                                    log_id,
                                                    include_hyperlinks=False
                                                )
        search_results = get_search_results(log_id)

        template_dict['body'] = ''.join(table_body)
        template_dict['total_search_hits'] = total_search_hits
        template_dict['state'] = state.to_json_str()
        template_dict['search_results'] = json.dumps(search_results)
    except Exception as e:
        app.logger.exception('Error while rendering log page')
        template_dict['error'] = str(e)
        template_dict['state'] = {}
        template_dict['search_results'] = {}

    result = template.render(template_dict, env=jinja_env)
    return result


@app.route('/log/<log_id>/search', methods=['GET', 'POST'])
def search(log_id):
    """
    Returns a JSON payload containing search results and search state.
    """
    try:
        if request.method == 'GET':
            search_str = request.args.get('search', None)
            if not search_str:
                return jsonify({
                    'error': 'Could not find the search query parameter'
                }), 400
        else:
            search_payload = request.get_json(force=True).get('search', None)
            if not search_payload:
                return jsonify({
                    'error': 'Could not find the search payload'
                }), 400

        search_results = get_search_results(log_id)
        return jsonify(search_results)
    except Exception as e:
        app.logger.exception('Error while searching for logs')
        return jsonify({
            'error': str(e)
        }), 500


def get_search_results(log_id):
    """
    Returns a dict payload containing search results and search state.

    Parameters on the flask request object control which lines are returned.
    Request parameters includes "search" which contains:

        query=str: Search string
        page=int : Page number of search results
        size=int : Number of results per page
        next=true: Get up to 1000 log lines with timestamps greater than the
                   current state.
        prev=true: Get up to 1000 log lines with timestamps smaller than the
                   current state.
        state=dict: state object for searching

    Request parameters also includes "filters" which contains:

        text=str : Query to filter search results
        sources=dict: hierarchical data of system_type, system_id
                      and sources to filter on
        time=list: 2 elements list containing start and end timestamp

    Returns a dict containing:
        query: searched query
        state: next state object for future searches
        total_search_hits: object containing total hits value
        results: list of log lines returned by ES
        page: page number
        size: count of results per page
    """
    es = ElasticLogSearcher(log_id)

    if request.method == 'GET':
        search_str = request.args.get('search', None)
        if not search_str:
            return None
        search_payload = json.loads(search_str)
    else:
        search_payload = request.get_json(force=True).get('search')
        if not search_payload:
            return None

    filters = {}
    if request.method == 'GET':
        filter_str = request.args.get('filter', None)
        if filter_str:
            filters = json.loads(filter_str)
    else:
        filters = request.get_json(force=True).get('filters', {})

    query = unquote_plus(search_payload.get('query'))
    page = int(search_payload.get('page', 1))
    size = int(search_payload.get('size', 20))
    next = search_payload.get('next', True)
    match_all = search_payload.get('match_all', False)

    if filters.get('text'):
        if query:
            query = f'{filters.get("text")} AND (msg:"{query}")'
        else:
            query = f'{filters.get("text")}'

    source_filters = filters.get('sources', None)
    time_filters = filters.get('time')

    state_str = search_payload.get('state', None)
    state = ElasticLogState()
    state.from_json_str(state_str)

    if next:
        results = es.search(state, query,
                        source_filters, time_filters,
                        query_size=size,
                        match_all=match_all)
    else:
        results = es.search_backwards(state, query,
                        source_filters, time_filters,
                        query_size=size,
                        match_all=match_all)

    search_results = results['hits']
    state.before_sort_val, state.after_sort_val = es._get_delimiting_sort_values(search_results)
    total_search_hits = results['total_search_hits']

    return {
        **search_payload,
        'results': search_results,
        'total_search_hits': total_search_hits,
        'state': state.to_dict(),
        'page': page,
        'size': size,
        'next': next
    }


@app.route('/log/<log_id>/dashboard', methods=['GET'])
@login_required
def dashboard(log_id):
    """ Renders the dashboard page for a particular log_id """
    # Assume our template is right next door to us.
    dir = os.path.join(_get_script_dir(), 'templates')

    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(dir),
                             trim_blocks=True,
                             lstrip_blocks=True)
    template = jinja_env.get_template('dashboard_template.html')
    jinja_env.filters['formatdatetime'] = _format_datetime

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

    # Reading metadata of detected anchors file
    anchors_meta = _read_file(log_id, 'anchors_meta.json', default={})

    # If the metadata is found then anchors are stored as files
    if anchors_meta:
        anchors = _read_paginated_anchor_file(log_id, page_num)
    else:
        anchors = _search_anchors(log_id, size=50)

    return anchors


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
        app.logger.error(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        app.logger.error(f'Other error occurred: {err}')  # Python 3.6
    except Exception as e:
        app.logger.exception('Could not find file')

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

def _search_anchors(log_id, size=50):
    """
    Returns a dict payload containing search results and state for anchors.

    Parameters on the flask request object control which lines are returned.
    Request parameters includes:

        next=true: Get up to 50 log lines with timestamps greater than the
                   current state.
        state=dict: state object for searching
        query=str: search string to search
        sources=list: List of sources to filter the searched results
        only_failed=bool: Toggle to display only failed anchors

    Returns a dict containing:
        query: searched query
        state: next state object for future searches
        total_anchors: object containing total hits value
        anchors: list of anchors returned by ES
        page: page number
        size: count of results per page
    """
    es = ElasticLogSearcher(log_id)
    log_view_base_url = _get_log_view_base_url(log_id)

    query = request.args.get('query')
    sources = request.args.getlist('source')
    page = int(request.args.get('page', 0))
    next = json.loads(request.args.get('next', 'true'))
    only_failed = json.loads(request.args.get('failed', 'false'))
    match_all = json.loads(request.args.get('match_all', 'false'))

    state_str = request.args.get('state', None)
    state = ElasticLogState()
    state.from_json_str(state_str)

    if "all" in sources:
        sources = []

    if next:
        page += 1
    else:
        page -= 1

    text_filter = 'is_anchor:true'
    if only_failed:
        text_filter += ' AND is_failure:true'
    if query:
        text_filter += f' AND {query}'

    if next:
        results = es.search(state, text_filter,
                        sources,
                        query_size=size,
                        match_all=match_all)
    else:
        results = es.search_backwards(state, text_filter,
                        sources,
                        query_size=size,
                        match_all=match_all)

    search_results = results['hits']
    state.before_sort_val, state.after_sort_val = es._get_delimiting_sort_values(search_results)
    total_anchors = results['total_search_hits']

    anchors = []
    for hit in search_results:
        source = hit['_source']
        timestamp = source['@timestamp']
        search_state = f'"before":"{timestamp}","after":"{timestamp}"'
        log_view_url = ('{}?state={{{}}}&next=true&prev=true&include={}#0').format(
                            log_view_base_url,
                            quote_plus(search_state),
                            hit['_id'])
        source['link'] = log_view_url

        anchors.append(source)

    return {
        'state': state.to_dict(),
        'total_anchors': total_anchors,
        'anchors': anchors,
        'page': page,
        'query': query,
        'next': next,
        'size': size
    }

def _get_analytics_data(log_id):
    """
    Get all the analytics data
    Returns a dict containing duplicates and anchors
    """
    # Reading metadata of detected anchors file
    anchors_meta = _read_file(log_id, 'anchors_meta.json', default={})

    # If the metadata is found then anchors are stored as files
    if anchors_meta:
        # Reading detected anchors from the JSON file
        anchors = _read_paginated_anchor_file(log_id)
    else:
        # Searching for anchors in ES
        anchors = _search_anchors(log_id)

    # Reading detected duplicates from the JSON file
    duplicates = _read_file(log_id, 'duplicates.json', default=[])

    return {
        **anchors,
        'anchors_meta': anchors_meta,
        'duplicates': duplicates
    }

def _get_actual_job_link(log_id):
    """ Returns the link to the job which generated the logs """
    ids = log_id.split('-')
    # QA jobs: log_qa-JOBID
    if log_id.startswith('log_qa-'):
        job_id = ids[1]
        return f'http://integration.fungible.local/regression/suite_detail/{job_id}'

    # Fun-on-demand jobs: log_fod-JOBID_JOBDIR
    if log_id.startswith('log_fod-'):
        job_id = ids[1]
        return f'http://palladium-jobs.fungible.local:8080/job/{job_id}'

def _render_dashboard_page(log_id, jinja_env, template):

    es = ElasticLogSearcher(log_id)
    es_metadata = ElasticsearchMetadata()

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
    log_event_stats = _get_log_event_stats(log_id)

    # Fetch the first non zero log level
    nonzero_log_levels = [level for level in default_log_levels if log_level_stats[level]['count'] > 0]

    recent_logs = _get_recent_logs(log_id, RECENT_LOGS_SIZE, log_levels=nonzero_log_levels[0:1])

    analytics_data = _get_analytics_data(log_id)

    metadata = es_metadata.get(log_id)

    template_dict = {}
    template_dict['log_id'] = log_id
    template_dict['sources'] = sources
    template_dict['system_types'] = system_types
    template_dict['system_ids'] = system_ids
    template_dict['unique_entries'] = unique_entries
    template_dict['log_view_base_url'] = log_view_base_url
    template_dict['log_level_stats'] = log_level_stats
    template_dict['log_event_stats'] = log_event_stats
    template_dict['log_level_for_recent_logs'] = nonzero_log_levels[0] if len(nonzero_log_levels) > 0 else None
    template_dict['recent_logs'] = _render_log_entries(recent_logs)
    template_dict['analytics_data'] = json.dumps(analytics_data)
    template_dict['metadata'] = metadata
    template_dict['job_link'] = _get_actual_job_link(log_id)

    result = template.render(template_dict, env=jinja_env)
    return result


@app.route('/log/<log_id>/dashboard/level-stats', methods=['GET'])
def log_level_stats(log_id):
    sources = request.args.getlist('source')
    return {
        'levels': _get_log_level_stats(log_id, sources),
        'events': _get_log_event_stats(log_id, sources)
    }

def _get_log_level_stats(log_id, sources=[], time_filters=None):
    level_keywords = app.config.get('LEVEL_KEYWORDS')
    return _get_log_count_for_keywords(log_id, level_keywords, sources, time_filters)

def _get_log_event_stats(log_id, sources=[], time_filters=None):
    event_keywords = app.config.get('EVENTS_BY_SOURCE')
    source_keywords = dict()
    for source, keywords in event_keywords.items():
        # Filter the events for only the sources we want or select all
        # events if no source is provided.
        if len(sources) == 0 or source in sources:
            source_keywords.update(keywords)

    return _get_log_count_for_keywords(log_id, source_keywords, sources, time_filters)

def _get_log_count_for_keywords(log_id, keywords, sources=[], time_filters=None):
    """
    Args:
    log_id (str)
    keywords (dict): keywords as keys with a list of search mappings as values.
    sources (list): sources to filter
    time_filter (tuple): time filter

    Returns a dict with keywords as keys and document count and log_view_url as values.
    Example:
    {
        'error': {
            'order': 1,
            'count': 10,
            'log_view_url': SEARCH URL,
            'keywords': 'error, err'
        }
    }
    """
    try:
        es = ElasticLogSearcher(log_id)
        log_view_base_url = _get_log_view_base_url(log_id)
        query = ''
        if len(sources) > 0:
            query = f'src:({" OR ".join(sources)}) AND'

        document_counts = {}
        for idx, keyword in enumerate(keywords.keys()):
            search_keywords = [f'"{keyword}"' for keyword in keywords[keyword]]
            keyword_query_terms = ' OR '.join(search_keywords)
            log_level_query = f'{query} (level:({keyword_query_terms}) OR msg:({keyword_query_terms}))'
            search_query = { 'query': log_level_query.strip() }
            log_view_url = f'{log_view_base_url}?search={quote(json.dumps(search_query))}'
            document_counts[keyword] = {
                'order': idx,
                'count': es.get_document_count(keyword_query_terms, sources, time_filters),
                'log_view_url': log_view_url,
                'keywords': ', '.join(keywords[keyword])
            }
    except Exception as e:
        app.logger.exception('Could not get log count for keywords')

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


def _get_recent_logs(log_id, size, sources={}, log_levels=None, time_filters=None):
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

    header = ['Source', 'System ID', 'Timestamp', 'Level', 'Log Message']
    template_dict = {}
    template_dict['head'] = header
    template_dict['body'] = '\n'.join(entries)

    result = template.render(template_dict, env=jinja_env)
    return result


def _format_datetime(timestamp, format="%a, %d %b %Y %I:%M:%S %Z"):
    """Format a date time to (Default): Weekday, Day Mon YYYY HH:MM:SS TZ"""
    if timestamp is None:
        return ''

    return datetime.datetime.fromtimestamp(timestamp/1000).strftime(format)


@app.route('/log/<log_id>/dashboard/notes', methods=['POST'])
@login_required
def save_notes(log_id):
    try:
        note = request.get_json()

        es_metadata = ElasticsearchMetadata()
        result = es_metadata.update_notes(log_id, note)

        return result
    except Exception as e:
        app.logger.exception('Error when creating a note')
        return jsonify({
            'error': str(e)
        }), 500


if __name__ == '__main__':
    log_handler = logger.get_logger(filename='es_view.log')

    # Get the flask logger and add our custom handler
    flask_logger = logging.getLogger('werkzeug')
    flask_logger.setLevel(logging.INFO)
    flask_logger.addHandler(log_handler)
    flask_logger.propagate = False
    main()
else:
    log_handler = logger.get_logger(filename='es_view.log')

    # Get the gunicorn logger and add our custom handler
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    app.logger.addHandler(log_handler)
    app.logger.propagate = False