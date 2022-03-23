#!/usr/bin/env python3

#
# Flask app for serving files.
#
# APIs to store files generated during log ingestion and fetch them
# to show it in the dashboard
#
# Run with
# server.py [--port 11000] [--dir]
#
# Get or save files using GET/POST to
# http://SERVER:11000/LOG_ID/file
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

import argparse
import logging
import os
import shutil

from flask import Flask
from flask import request, jsonify, send_file
from werkzeug.utils import secure_filename

import logger


ALLOWED_EXTENSIONS = {'json'}
FILE_PATH = os.path.abspath(os.path.dirname(__file__))
DEFAULT_UPLOAD_DIRECTORY = f'{FILE_PATH}/files/analytics'

app = Flask(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=11000,
                        help='port for HTTP file server')

    parser.add_argument('--dir', type=str, default=DEFAULT_UPLOAD_DIRECTORY,
                        help='path to upload directory')

    args = parser.parse_args()
    port = args.port

    app.config.update({
        'UPLOAD_DIRECTORY': args.dir
    })
    app.run(host='0.0.0.0', port=port)


def _allowed_file(filename):
    """ Check if the file extension is allowed """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/<log_id>/file/<file_name>', methods=['GET'])
def get_file(log_id, file_name):
    """ Fetches file with 'file_name' within the 'log_id' directory """
    try:
        path = os.path.join(app.config['UPLOAD_DIRECTORY'], log_id, file_name)

        return send_file(path, as_attachment=False)
    except Exception as e:
        app.logger.exception('Could not find file')
        return jsonify({
            'success': False,
            'error': 'Could not find file'
        }), 404


@app.route('/<log_id>/file', methods=['POST'])
def save_file(log_id):
    """ Saves within the 'log_id' directory """
    if len(request.files) == 0:
        return jsonify({
            'success': False,
            'error': 'No files uploaded'
        }), 404

    BASE_PATH = os.path.join(app.config['UPLOAD_DIRECTORY'], log_id)
    errors = list()

    for file in list(request.files.values()):
        try:
            # if filename not present
            if file.filename == '':
                errors.append('File name not set')
                continue

            if not file:
                errors.append(f'Unsupported file format: {file.filename}')
                continue

            filename = secure_filename(file.filename)
            # Creating the directory if it does not exist
            os.makedirs(BASE_PATH, exist_ok=True)
            path = os.path.join(BASE_PATH, filename)

            file.save(path)
            app.logger.info(f'File saved at {path}')
        except Exception as e:
            app.logger.exception(f'Error while saving file: {file.filename}')
            errors.append(f'error while saving file: {file.filename} - {str(e)}')

    if len(errors) != 0:
        logging.error(errors)
        return jsonify({
            'success': False,
            'errors': errors
        }), 500

    return jsonify({'success': True})

#
# @app.route('/<log_id>/file/<file_name>', methods=['DELETE'])
# def delete_file(log_id, file_name):
#     """ Delete file with 'file_name' within the 'log_id' directory """
#     file_type = request.args.get('type', 'json')
#     file_name = f'{file_name}.{file_type}'
#     path = os.path.join(app.config['UPLOAD_DIRECTORY'], log_id, file_name)

#     try:
#         os.remove(path)
#         app.logger.info(f'File deleted at {path}')
#     except Exception as e:
#         app.logger.exception(f'Error while deleting file: {file_name}')
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

#     return jsonify({'success': True})


@app.route('/<log_id>', methods=['DELETE'])
def delete_dir(log_id):
    """ Delete all the files within the 'log_id' directory """
    path = os.path.join(app.config['UPLOAD_DIRECTORY'], log_id)

    try:
        shutil.rmtree(path)
        app.logger.info(f'All files deleted under directory: {path}')
    except FileNotFoundError as e:
        app.logger.info(f'Files not found under directory: {path}')
        return jsonify({
            'success': False,
            'error': f'Files not found under directory: {path}'
        }), 404
    except Exception as e:
        app.logger.exception(f'Error while deleting directory: {path}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

    return jsonify({'success': True})


if __name__ == '__main__':
    log_handler = logger.get_logger(filename='file_server.log')

    # Get the flask logger and add our custom handler
    flask_logger = logging.getLogger('werkzeug')
    flask_logger.setLevel(logging.INFO)
    flask_logger.addHandler(log_handler)
    flask_logger.propagate = False
    main()
else:
    log_handler = logger.get_logger(filename='file_server.log')

    # Get the gunicorn logger and add our custom handler
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    app.logger.addHandler(log_handler)
    app.logger.propagate = False

    app.config.update({
        'UPLOAD_DIRECTORY': DEFAULT_UPLOAD_DIRECTORY
    })