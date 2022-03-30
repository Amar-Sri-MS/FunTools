#!/usr/bin/env python3

#
# View for log searcher across multiple ingested log
# archives.
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2022 Fungible Inc.  All rights reserved.

from flask import Blueprint, jsonify, request
from flask import current_app
from flask import render_template

from common import login_required

import elastic_log_searcher

searcher_page = Blueprint('searcher_page', __name__)


@searcher_page.route('/logs', methods=['GET'])
def get_logs():
    """
    Returns the Elasticsearch indexes for the given
    "prefix", "limit_by" [count, days] and "limit_value".
    """
    try:
        prefix = request.args.get('prefix', 'log_*')
        limit_by = request.args.get('limit_by', None)
        limit_value = request.args.get('limit_value', None)

        if limit_value:
            limit_value = int(limit_value)

        indices = elastic_log_searcher.get_logs(prefix, limit_by, limit_value)
        return jsonify(indices), 200
    except Exception as e:
        current_app.logger.exception('Exception while fetching indices')
        return jsonify({
            'error': str(e)
        }), 500


@searcher_page.route('/', methods=['GET'])
def get_searcher_page():
    return render_template('searcher_template.html')