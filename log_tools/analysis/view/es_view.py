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
    """ Serves the root page """
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

    indices = es.indices.get('bug_*')
    indices = [s.replace('bug_', '', 1) for s in indices]

    # Assume our template is right next door to us.
    MODULE_PATH = os.path.realpath(__file__)
    MODULE_DIR = os.path.dirname(MODULE_PATH)

    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(MODULE_DIR),
                             trim_blocks=True,
                             lstrip_blocks=True)
    template = jinja_env.get_template('root_template.html')

    return render_root(indices, jinja_env, template)


def render_root(indices, jinja_env, template):
    template_dict = {}
    template_dict['bugs'] = indices

    result = template.render(template_dict, env=jinja_env)
    return result


@app.route('/bug/<bug>', methods=['GET'])
def get_log_root(bug):
    """
    Serves a page of log messages.
    """
    first_sort_val, last_sort_val, page_body = get_page_body(bug)
    filter_term = request.args.get('filter', '')

    # Assume our template is right next door to us.
    MODULE_PATH = os.path.realpath(__file__)
    MODULE_DIR = os.path.dirname(MODULE_PATH)

    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(MODULE_DIR),
                             trim_blocks=True,
                             lstrip_blocks=True)
    template = jinja_env.get_template('log_template.html')

    return render_page(page_body, first_sort_val, last_sort_val, filter_term,
                       bug, jinja_env, template)


@app.route('/bug/<bug>/logs', methods=['POST'])
def get_log_contents(bug):
    first_sort_val, last_sort_val, page_body = get_page_body(bug)

    return {'logs': ''.join(page_body),
            'before': first_sort_val, 
            'after': last_sort_val}


def get_page_body(bug):
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

    search_before = request.args.get('before', None)
    search_after = request.args.get('after', None)
    include = request.args.get('include', None)
    search_term = request.args.get('filter', None)

    before, after = get_temporally_close_hits(es, bug, 1000,
                                              search_term,
                                              search_before,
                                              search_after)

    centre = []
    if include is not None:
        doc = get_document(es, bug, include)
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


def get_temporally_close_hits(es, bug_id, size,
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
    index='bug_{}'.format(bug_id)

    before = []
    after = []

    if search_after_val is not None:
        after = search_after(es, index, size, search_term, search_after_val)
    if search_before_val is not None:
        before = search_before(es, index, size, search_term, search_before_val)

    if search_after_val is None and search_before_val is None:
        after = search_after(es, index, size, search_term, None)

    return before, after


def search_after(es, index, size, term, sort_val):
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


def get_document(es, bug, doc_id):
    index = 'bug_{}'.format(bug)
    result = es.get(index=index, id=doc_id)
    return result


def render_page(page_body, first, last, text_filter, bug, jinja_env, template):
    template_dict = {}
    template_dict['body'] = ''.join(page_body)
    template_dict['bug'] = bug
    template_dict['first'] = first
    template_dict['last'] = last
    template_dict['filter'] = text_filter

    result = template.render(template_dict, env=jinja_env)
    return result


@app.route('/bug/<bug>/search', methods=['POST'])
def search(bug):
    """
    Returns an HTML snippet containing links to log entries matching
    the search term.
    """
    search_term = request.args.get('query')
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

    body = {}
    body['query'] = {'query_string': {'query': search_term}}
    result = es.search(body=body,
                       index='bug_{}'.format(bug),
                       size=25,
                       sort='@timestamp:asc')

    links = []
    hits = result['hits']['hits']
    for hit in hits:
        s = hit['_source']
        links.append(('<a href="/bug/{}?'
                      'before={}&'
                      'after={}&'
                      'include={}#0">{} {}</a>').format(bug,
                                                        hit['sort'][0],
                                                        hit['sort'][0],
                                                        hit['_id'],
                                                        s['@timestamp'],
                                                        s['msg']))
    return {'html': '<br>'.join(links)}


if __name__ == '__main__':
    main()
