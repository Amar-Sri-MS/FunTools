#!/usr/bin/env python3

#
# Post processing service for CSI traces.
#
# Currently only handles cache miss traces. The expected REST API usage
# is documented in code, see cm_pipeline.py. Individual REST calls are
# documented here in each implementing function.
#
# TODO: should use HTTP response codes where possible.
# TODO: logging
#
# Copyright (c) 2022 Fungible Inc. All rights reserved.
#

import argparse
import json
import os
import subprocess
import threading
import uuid

import flask
from werkzeug.utils import secure_filename


app = flask.Flask(__name__)
app.config.from_file("config.json", load=json.load)


WORK_DIR_CFG = 'WORK_DIR'
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


def main():
    """
    Development server entry point.

    Production wsgi servers will use the global app object and its file-based
    configuration instead.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8008,
                        help='port for CSI server')
    parser.add_argument('--dir', type=str, default='work',
                        help='working directory')

    args = parser.parse_args()
    port = args.port

    app.config.update({
        WORK_DIR_CFG: args.dir
    })

    app.run(host='0.0.0.0', port=port)


@app.route('/traces', methods=['POST'])
def create_trace():
    """
    Creates a resource for the trace and returns its id.

    The id can be thought of as a session id and is used for all future
    calls for this particular trace.

    request: curl -X POST server:port/traces
    response: {"ret": bool, "msg": string, "id": string}. id is only valid
    if ret is True.
    """
    id = str(uuid.uuid4())
    path = os.path.join(app.config[WORK_DIR_CFG], id)
    cm_path = os.path.join(path, 'odp', 'cache_miss_dumps')

    result = {'ret': True, 'msg': None, 'id': id}
    try:
        os.makedirs(path)
        os.makedirs(cm_path)
    except OSError as e:
        result['ret'] = False

    return flask.jsonify(result)


@app.route('/traces/<uuid>', methods=['POST'])
def add_trace_file(uuid):
    """
    Uploads a trace file for the trace with the specified id.

    The request uses multipart-form data to send a file. Not the most elegant,
    but hopefully the files are small enough to avoid having to deal with
    chunking or resuming.

    request: curl -X POST -F file=@trace_cluster_00 server:port/traces/<id>
    response: {"ret": bool, "msg" string}.
    """
    result = {'ret': True, 'msg': 'OK'}
    file = flask.request.files['file']

    filename = file.filename
    expected_prefix = 'trace_cluster_'
    if not filename.startswith(expected_prefix):
        result['ret'] = False
        result['msg'] = 'File should start with %s' % expected_prefix
    else:
        filename = secure_filename(filename)
        cm_dir = os.path.join(app.config[WORK_DIR_CFG], uuid, 'odp', 'cache_miss_dumps')
        file.save(os.path.join(cm_dir, filename))

    return flask.jsonify(result)


@app.route('/traces/<uuid>/process', methods=['POST'])
def process_trace(uuid):
    """
    Starts processing the trace.

    request: curl -X POST server:port/traces/<id>/process
    response: {"ret": bool, "msg" string}.
    """
    result = {'ret': True, 'msg': 'OK'}
    trace_dir = os.path.join(SCRIPT_DIR, app.config[WORK_DIR_CFG], uuid)

    rc = os.system('cp funos-s1 %s' % trace_dir)
    if rc != 0:
        flask.abort(500, description='Server failed to copy binary')

    t = threading.Thread(target=process_trace_async, args=[trace_dir])
    t.start()

    return flask.jsonify(result)


def process_trace_async(path):
    try:
        # TODO: what happens if something goes wrong before process.py runs?
        out = subprocess.check_output([os.path.join(SCRIPT_DIR, 'process.py'), path])
        print(out)
    except subprocess.CalledProcessError as e:
        print(e.output)


@app.route('/traces/<uuid>/process', methods=['GET'])
def get_process_results(uuid):
    """
    Poll this to find out when results are available from processing.

    request: curl -X GET server:port/traces/<id>/process
    response: {"complete": bool, "ret": bool, "msg": string, "files": [string]}
    """
    result = {'complete': False}

    result_summary = os.path.join(app.config[WORK_DIR_CFG], uuid, 'odp', 'process.json')
    if os.path.exists(result_summary):
        with open(result_summary, 'r') as f:
            js = json.load(f)
            result['complete'] = True
            result['ret'] = js['ret']
            result['msg'] = js['msg']
            result['files'] = js['files']

    return flask.jsonify(result)


@app.route('/traces/<uuid>/results/<file>', methods=['GET'])
def get_process_result(uuid, file):
    """
    Downloads the result files.
    """
    if not file.startswith('cache_miss_'):
        flask.abort(404, description='Results should start with cache_miss_*')
    else:
        filename = secure_filename(file)
        filename = os.path.join(os.path.join(app.config[WORK_DIR_CFG], uuid, 'odp', filename))
        if not os.path.exists(filename):
            flask.abort(404, description='No such file %s' % file)

        return flask.send_file(filename)


if __name__ == '__main__':
    main()
