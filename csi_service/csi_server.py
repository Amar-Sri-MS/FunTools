#!/usr/bin/env python3

#
# CSI service
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


WORK_DIR_CFG = 'WORK_DIR'
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


def main():
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
    """ Creates a resource for the trace and returns its id """
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
    result = {'ret': True}
    file = flask.request.files['file']

    filename = file.filename
    if not filename.startswith('trace_cluster_'):
        result['ret'] = False
    else:
        filename = secure_filename(filename)
        cm_dir = os.path.join(app.config[WORK_DIR_CFG], uuid, 'odp', 'cache_miss_dumps')
        file.save(os.path.join(cm_dir, filename))

    return flask.jsonify(result)


@app.route('/traces/<uuid>/process', methods=['POST'])
def process_trace(uuid):
    result = {'ret': True}
    trace_dir = os.path.join(SCRIPT_DIR, app.config[WORK_DIR_CFG], uuid)

    try:
        os.system('cp funos-s1 %s' % trace_dir)

        t = threading.Thread(target=process_trace_async, args=[trace_dir])
        t.start()
    except subprocess.CalledProcessError as e:
        result['ret'] = False

    return flask.jsonify(result)


def process_trace_async(path):
    out = subprocess.check_output([os.path.join(SCRIPT_DIR, 'process.py'), path])
    print(out)


@app.route('/traces/<uuid>/process', methods=['GET'])
def get_process_results(uuid):
    result = {'ret': True}

    result_summary = os.path.join(app.config[WORK_DIR_CFG], uuid, 'odp', 'process.json')
    if os.path.exists(result_summary):
        with open(result_summary, 'r') as f:
            r = json.load(f)
            result['summary'] = r
    else:
        result['ret'] = False

    return flask.jsonify(result)


@app.route('/traces/<uuid>/results/<file>', methods=['GET'])
def get_process_result(uuid, file):

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
