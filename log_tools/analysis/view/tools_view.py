#!/usr/bin/env python3

#
# View for handling tools built on top of Log Analyzer.
# Storage Tools:
#   - Lifecycle of a volume
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

import sys

sys.path.insert(0, '.')

from flask import Blueprint, jsonify, request
from flask import render_template

from tools.volume_lifecycle import Volume

tools_page = Blueprint('tools_page', __name__)

@tools_page.route('/<log_id>/volume', methods=['GET'])
def render_volume_lifecycle_tool(log_id):
    """ UI for Volume lifecycle tool """
    return render_template('volume_lifecycle_tool.html', log_id=log_id)


@tools_page.route('/<log_id>/volume', methods=['POST'])
def get_volume_lifecycle(log_id):
    """ Returns the lifecycle of the given volume """
    request_data = request.get_json(force=True)
    vol_id = request_data.get('volume_id')

    if not vol_id:
        return jsonify('Volume ID missing'), 400

    try:
        volume = Volume(log_id, vol_id)
        lifecycle = volume.get_lifecycle()
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500
    return jsonify(lifecycle)