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
    term = request.args.get('query')
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

    body = {}
    body['query'] = {'query_string': {'query': term}}
    result = es.search(body=body,
                       index='bug_{}'.format(bug),
                       size=10,
                       sort='@timestamp:asc')

    links = []
    hits = result['hits']['hits']
    for hit in hits:
        s = hit['_source']
        links.append('<a href="/bug/{}?after={}">{}</a>'.format(bug,
                                                                hit['sort'][0],
                                                                s['msg']))

    return {'html': '<br>'.join(links)}


@app.route('/bug/<bug>', methods=['GET'])
def show_logs(bug):
    """ Serves a page full of log messages """
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

    search_before = request.args.get('before', None)
    search_after = request.args.get('after', None)

    body = {}

    # This quirky magic is how we get paging in search queries. We determine
    # the sort tag for the first and last entry in this query.
    #
    # It gets even quirkier for previous pages: first we ask for searches
    # after a tag in descending order, then reverse the list.
    sort_direction = 'asc'
    if search_after:
        body['search_after'] = [search_after]
    elif search_before:
        body['search_after'] = [search_before]
        sort_direction = 'desc'

    result = es.search(body=body,
                       index='bug_{}'.format(bug),
                       size=1000,
                       sort='@timestamp:{}'.format(sort_direction))

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
    # The log lines are organized as table rows in the template
    hits = result['hits']['hits']
    if sort_direction == 'desc':
        hits = hits.reverse()

    for hit in result['hits']['hits']:
        s = hit['_source']

        if first_sort_val is None:
            first_sort_val = hit['sort'][0]
        last_sort_val = hit['sort'][0]

        page_body.append('<tr><td>{}</td> <td>{}</td> <td>{}</td></tr>'.format(s['src'], s['@timestamp'], s['msg']))

    return render_page(page_body, first_sort_val, last_sort_val, bug,
                       jinja_env, template)


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
