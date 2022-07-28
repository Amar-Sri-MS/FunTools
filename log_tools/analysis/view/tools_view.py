#!/usr/bin/env python3

#
# View for handling tools built on top of Log Analyzer.
# Storage Tools:
#   - Lifecycle of a volume
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

import logging
import sys

sys.path.insert(0, '.')

from flask import Blueprint, jsonify, request
from flask import render_template

from common import login_required
from tools.network import Network
from tools.volume_lifecycle import Volume

tools_page = Blueprint('tools_page', __name__)

@tools_page.route('/<log_id>/volume', methods=['GET'])
@login_required
def render_volume_lifecycle_tool(log_id):
    """ UI for Volume lifecycle tool """
    return render_template('volume_lifecycle_tool.html', log_id=log_id)


@tools_page.route('/<log_id>/volume', methods=['POST'])
@login_required
def get_volume_lifecycle(log_id):
    """ Returns the lifecycle of the given volume """
    request_data = request.get_json(force=True)
    vol_id = request_data.get('volume_id')

    if not vol_id:
        logging.error('Volume ID missing')
        return jsonify({'error': 'Volume ID missing'}), 400

    try:
        volume = Volume(log_id, vol_id)
        lifecycle = volume.get_lifecycle()
    except Exception as e:
        logging.exception('Error in storage tool')
        return jsonify({
            'error': str(e)
        }), 500
    return jsonify(lifecycle)


@tools_page.route('/<log_id>/vswitch', methods=['GET'])
@login_required
def render_vswitch_tool(log_id):
    """ UI for Virtual Switch Tool """
    return render_template('vswitch_tool.html', log_id=log_id)


@tools_page.route('/<log_id>/network', methods=['GET'])
@login_required
def render_network_tool(log_id):
    """ UI for Network Tool """
    return render_template('network_tool.html', log_id=log_id)

@tools_page.route('/<log_id>/network/info', methods=['GET'])
@login_required
def get_network_tool_info(log_id):
    """ Info for Network Tool """
    try:
        network = Network(log_id)
        network_info = network.get_info()
    except Exception as e:
        logging.exception(f'Error while fetching info for Network Tool. log_id: {log_id}')
        return jsonify({
            'error': str(e)
        }), 500

    return jsonify(network_info)
