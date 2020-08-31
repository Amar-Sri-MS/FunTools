#!/usr/bin/env python3

#
# Flask app for log viewing.
#
# Performs elasticsearch queries to obtain logs and to allow back and forth
# navigation. Still a work in progress.
#
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


@app.route('/log/<log_id>', methods=['GET'])
def get_log_page(log_id):
    """
    Displays a log page for a particular log_id.

    Subsequent updates to the page are handled via POST requests.
    """
    first_sort_val, last_sort_val, table_body = _get_requested_log_lines(log_id)
    filter_term = request.args.get('filter', '')

    # Assume our template is right next door to us.
    dir = _get_script_dir()

    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(dir),
                             trim_blocks=True,
                             lstrip_blocks=True)
    template = jinja_env.get_template('log_template.html')

    return _render_log_page(table_body, first_sort_val, last_sort_val, filter_term,
                            log_id, jinja_env, template)


@app.route('/log/<log_id>/content', methods=['POST'])
def get_log_contents(log_id):
    """
    Obtains log contents which can be used to update a page.
    """
    first_sort_val, last_sort_val, page_body = _get_requested_log_lines(log_id)

    return {'content': ''.join(page_body),
            'before': first_sort_val, 
            'after': last_sort_val}


def _get_requested_log_lines(log_id):
    """
    Obtains the requested log lines.

    The request can include before and after sort values to show logs before
    and/or after a particular sort value. Filter terms are also accepted.

    Returns a tuple containing:
    (sort_value of first item,
     sort value of last item,
     log lines as HTML table body)
    """
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

    search_before = request.args.get('before', None)
    search_after = request.args.get('after', None)
    include = request.args.get('include', None)
    search_term = request.args.get('filter', None)

    # Elasticsearch has a limit of 10K results, so pagination is required
    size = 1000
    before, after = get_temporally_close_hits(es, log_id, size,
                                              search_term,
                                              search_before,
                                              search_after)

    # Before and after are not inclusive searches, so we have to include
    # the actual search result here via a direct document lookup. Very sad.
    #
    # TODO (jimmy): find another way around this kludge.
    centre = []
    if include is not None:
        doc = _get_document_by_id(es, log_id, include)

        # Stash an anchor id in here so we can jump straight to the line
        # that we searched for.
        doc['anchor_link'] = '0'
        centre = [doc]

    result = before + centre + after

    page_body = []
    first_sort_val = -1
    last_sort_val = -1

    # This quirky magic is how we get paging in search queries. We determine
    # the sort value for the first and last entry in this query.
    for hit in result:
        sort_vals = hit.get('sort')

        if first_sort_val == -1 and sort_vals is not None:
            first_sort_val = sort_vals[0]
        if sort_vals is not None:
            last_sort_val = sort_vals[0]

        s = hit['_source']
        # The log lines are organized as table rows in the template
        line = '<tr>'
        if hit.get('anchor_link'):
            line = '<tr id={}>'.format(hit.get('anchor_link'))

        line += '<td>{}</td> <td>{}</td> <td>{}</td>'.format(s['src'],
                                                             s['@timestamp'],
                                                             s['msg'])
        line += '</tr>'
        page_body.append(line)

    return first_sort_val, last_sort_val, page_body


def get_temporally_close_hits(es, log_id, size,
                              search_term,
                              search_before_val=None,
                              search_after_val=None):
    """
    Obtains a list of search hits that have timestamp sort values before
    and/or after the sort value.

    If all search_* arguments are None we return hits from the beginning of 
    the index.

    Note that the timestamp sort value used as argument to search_* 
    parameters is returned by elasticsearch, and does not correspond to the
    actual timestamp value. It can be obtained by looking up the 'sort' key
    in the returned list elements.

    The returned tuple is (before_list, after_list). Both lists are ordered
    by timestamp. We only return empty lists, never None.
    """
    index = log_id

    before = []
    after = []

    if search_after_val is not None:
        after = search_after(es, index, size, search_term, search_after_val)
    if search_before_val is not None:
        before = search_before(es, index, size, search_term, search_before_val)

    # Default condition: do a search after
    if search_after_val is None and search_before_val is None:
        after = search_after(es, index, size, search_term, None)

    return before, after


def search_after(es, index, size, term, sort_val):
    """ Issues a search after query """
    body = {}
    if term is not None:
        body['query'] = {'query_string': {'query': term}}
    if sort_val is not None:
        body['search_after'] = [sort_val]
    sort_direction = 'asc'
    result = es.search(body=body,
                       index=index,
                       size=size,
                       sort='@timestamp:{}'.format(sort_direction))
    return result['hits']['hits']


def search_before(es, index, size, term, sort_val):
    """ Issues a search before query """
    body = {}
    if term is not None:
        body['query'] = {'query_string': {'query': term}}
    body['search_after'] = [sort_val]
    sort_direction = 'desc'

    # The recipe for search_before is to do a search_after in descending
    # sort order, and then reverse the list of results. Quirky.
    result = es.search(body=body,
                       index=index,
                       size=size,
                       sort='@timestamp:{}'.format(sort_direction))
    result = result['hits']['hits']
    result.reverse()
    return result


def _get_document_by_id(es, log_id, doc_id):
    """ 
    Look up a specific log line by document id.

    The doc_id is specified by elasticsearch, and is unique per index.
    """
    index = log_id
    result = es.get(index=index, id=doc_id)
    return result


def _render_log_page(table_body, first, last, text_filter, log_id, jinja_env, template):
    """ Renders the log page """
    template_dict = {}
    template_dict['body'] = ''.join(table_body)
    template_dict['log_id'] = log_id
    template_dict['first'] = first
    template_dict['last'] = last
    template_dict['filter'] = text_filter

    result = template.render(template_dict, env=jinja_env)
    return result


@app.route('/log/<log_id>/search', methods=['POST'])
def search(log_id):
    """
    Returns an HTML snippet containing links to log entries matching
    the search term.
    """
    search_term = request.args.get('query')
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

    body = {}
    body['query'] = {'query_string': {'query': search_term}}
    result = es.search(body=body,
                       index=log_id,
                       size=25,
                       sort='@timestamp:asc')

    links = []
    hits = result['hits']['hits']
    for hit in hits:
        s = hit['_source']

        # The #0 anchor is how we jump to the searched-for line when the link
        # is selected.
        links.append(('<a href="/log/{}?'
                      'before={}&'
                      'after={}&'
                      'include={}#0">{} {}</a>').format(log_id,
                                                        hit['sort'][0],
                                                        hit['sort'][0],
                                                        hit['_id'],
                                                        s['@timestamp'],
                                                        s['msg']))
    return {'html': '<br>'.join(links)}


if __name__ == '__main__':
    main()
