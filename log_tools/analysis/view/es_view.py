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
                      'before={}&after={}">{}</a>').format(bug,
                                                           hit['sort'][0],
                                                           hit['sort'][0],
                                                           s['msg']))
    return {'html': '<br>'.join(links)}


@app.route('/bug/<bug>', methods=['GET'])
def show_logs(bug):
    """
    Serves a page of log messages.
    """
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

    search_before = request.args.get('before', None)
    search_after = request.args.get('after', None)

    result = get_temporally_close_hits(es, bug, search_before, search_after)

    # Assume our template is right next door to us.
    MODULE_PATH = os.path.realpath(__file__)
    MODULE_DIR = os.path.dirname(MODULE_PATH)

    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(MODULE_DIR),
                             trim_blocks=True,
                             lstrip_blocks=True)
    template = jinja_env.get_template('log_template.html')

    page_body = []
    first_sort_val = None
    last_sort_val = None

    # This quirky magic is how we get paging in search queries. We determine
    # the sort value for the first and last entry in this query.
    for hit in result:
        s = hit['_source']

        if first_sort_val is None:
            first_sort_val = hit['sort'][0]
        last_sort_val = hit['sort'][0]

        # The log lines are organized as table rows in the template
        page_body.append('<tr><td>{}</td> <td>{}</td> <td>{}</td></tr>'.format(s['src'], s['@timestamp'], s['msg']))

    return render_page(page_body, first_sort_val, last_sort_val, bug,
                       jinja_env, template)


def get_temporally_close_hits(es, bug_id,
                              search_before=None,
                              search_after=None):
    """
    Obtains a list of search hits that have timestamp sort values before
    search_before and after search_after.

    If both search_before and search_after are None (the default) we return
    hits from the beginning of the index.

    Note that the timestamp sort value used as arguments to search_before and
    search_after is returned by elasticsearch, and does not correspond to the
    actual timestamp value. It can be obtained by looking up the 'sort' key
    in the returned list elements.

    The returned list of hits is ordered by timestamp.
    """
    size = 1000
    if search_before is not None and search_after is not None:
        size = size // 2
    index='bug_{}'.format(bug_id)

    body = {}
    result = []

    if search_after is not None or search_before is None:
        if search_after is not None:
            body['search_after'] = [search_after]
        sort_direction = 'asc'
        result.extend(es.search(body=body,
                                index=index
                                size=size,
                                sort='@timestamp:{}'.format(sort_direction)))

    if search_before is not None:
        body['search_after'] = [search_before]
        sort_direction = 'desc'

        # The recipe for search_before is to do a search_after in descending
        # sort order, and then reverse the list of results. Quirky.
        reversed = es.search(body=body,
                             index=index
                             size=size,
                             sort='@timestamp:{}'.format(sort_direction))
        result.extend(reversed.reverse())

    hits = result['hits']['hits']
    return hits


def render_page(page_body, first, last, bug, jinja_env, template):
    template_dict = {}
    template_dict['body'] = ''.join(page_body)
    template_dict['bug'] = bug
    template_dict['first'] = first
    template_dict['last'] = last

    result = template.render(template_dict, env=jinja_env)
    return result


if __name__ == '__main__':
    main()
