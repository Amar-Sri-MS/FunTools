#!/usr/bin/env python3

#
# Tracking web usage events by ingesting them
# to Elasticsearch.
#
# An event payload should contain the following:
# - event name
# - timestamp
# - user_email
# - event data (Optional)
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

import datetime

from elasticsearch7 import Elasticsearch
from flask import Blueprint
from flask import jsonify
from flask import g, request
from flask import current_app as app

from common import login_required


web_usage = Blueprint('web_usage', __name__)
INDEX_NAME_PREFIX = 'web_stats'


@web_usage.route('/track', methods=['POST'])
@login_required
def track_event():
    """
    Storing the web events sent by the View.
    The payload must contain the following:
    'event' which is the name of the event.
    'timestamp' time at which the event was created.
    """
    data = request.json
    event_name = data['event']

    # Setting the user email from session.
    data['user_email'] = g.user

    if not event_name or 'timestamp' not in data:
        return jsonify({
            'status': 'failed',
            'error': 'Could not find event name or timestamp'
        }), 400

    result = index(data)

    return jsonify({'status': 'success'})

def index(data):
    ELASTICSEARCH_HOSTS = app.config['ELASTICSEARCH']['hosts']
    ELASTICSEARCH_TIMEOUT = app.config['ELASTICSEARCH']['timeout']
    ELASTICSEARCH_MAX_RETRIES = app.config['ELASTICSEARCH']['max_retries']
    es = Elasticsearch(ELASTICSEARCH_HOSTS,
                        timeout=ELASTICSEARCH_TIMEOUT,
                        max_retries=ELASTICSEARCH_MAX_RETRIES,
                        retry_on_timeout=True)

    # index name based on time
    index = _get_index_name(INDEX_NAME_PREFIX)
    result = es.index(index, data)

    return result

def _get_index_name(prefix):
    """
    Creating index name based on time
    Format: PREFIX_YYYY_MM
    """
    now = datetime.datetime.utcnow()
    return f'{prefix}_{now.year}_{now.month}'