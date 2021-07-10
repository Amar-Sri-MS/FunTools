#!/usr/bin/env python3

#
# Timeline module for tracking the time each pipeline
# block takes during an ingestion.
#
# This also generates a timeline graph in png based on
# the collected data.
#
# Usage:
# track_start(MODULE_NAME) to start tracking the module
# track_end(MODULE_NAME) to end tracking the module
# Where, MODULE_NAME is the name to identify the block
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

import json
import logging
import logger
import matplotlib.pyplot as plt
import os
import requests
import time

from matplotlib.collections import PolyCollection

import config_loader

# Log ID to track the timeline for a particular ingestion
log_id = None
start_time = None
timeline = {}

# Decorator to track the start and end of a function
def timeline_logger(module):
    def timeline_decorator(func):
        def logger(*args, **kwargs):
            track_start(module)

            result = func(*args, **kwargs)

            track_end(module)
            return result

        return logger
    return timeline_decorator


def init(logid):
    """ Timeline tracker initialization """
    global log_id
    global start_time
    global timeline

    if log_id:
        if log_id != logid:
            logging.error(f'Timeline logger log_id mismatch. {logid} != {log_id}')
        logging.info('Timeline logger already initialized')
        return

    log_id = logid
    start_time = time.time()
    timeline = {}


def track_start(module):
    _track('START', module)


def track_end(module):
    _track('END', module)


def _track(status, module):
    """ Tracking module """
    if not log_id:
        logging.error('Timeline logger not initialized')
    current_time = time.time()
    time_diff = current_time - start_time

    if module not in timeline:
        timeline[module] = dict()
    if status not in timeline[module]:
        timeline[module][status] = list()

    timeline[module][status].append(time_diff)


def generate_timeline():
    """ Generating timeline based on the collected data """
    global log_id
    global timeline

    if not timeline:
        return

    data = list()
    blocks = dict()

    # Storing the timeline tracking history in a json
    timeline_file = os.path.join(logger.LOGS_DIRECTORY, f'{log_id}_timeline.json')
    with open(timeline_file, 'w') as f:
        json.dump(timeline, f)

    block_id = 1
    for block, status in timeline.items():
        total_time = 0
        blocks[block] = {
            'id': block_id
        }
        block_id += 1

        for times in zip(status['START'], status['END']):
            total_time += (times[1] - times[0])
            data.append((times[0], times[1], block))

        blocks[block]['total_time'] = total_time

    verts = []
    for d in data:
        v = [(d[0], blocks[d[2]]['id']-.4),
            (d[0], blocks[d[2]]['id']+.4),
            (d[1], blocks[d[2]]['id']+.4),
            (d[1], blocks[d[2]]['id']-.4),
            (d[0], blocks[d[2]]['id']-.4)]
        verts.append(v)

    bars = PolyCollection(verts)

    fig, ax = plt.subplots()
    ax.add_collection(bars)
    ax.autoscale()

    textstr = 'Total Time:\n'
    textstr += '\n'.join([f'{name}: {round(block["total_time"], 2)} seconds' for name, block in blocks.items()])

    # these are matplotlib.patch.Patch properties
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

    # place a text box below the x axis
    ax.text(0.5, -0.5, textstr, transform=ax.transAxes, fontsize=14,
            horizontalalignment='center', verticalalignment='center',
            bbox=props)

    plt.xticks(rotation=70)
    plt.xlabel('Seconds since the start of ingestion')

    ax.set_yticks(range(1, len(blocks)+1))
    ax.set_yticklabels(blocks.keys())
    file_path = os.path.join(logger.LOGS_DIRECTORY, f'{log_id}_timeline.png')
    fig.savefig(file_path, bbox_inches='tight')


def backup_timeline_files():
    """
    Backing up the timeline logs collected during ingestion
    of the given "log_id".

    Sending the json and png to FILE_SERVER at the end of ingestion.
    """
    try:
        global log_id
        config = config_loader.get_config()
        FILE_SERVER_URL = config['FILE_SERVER_URL']
        url = f'{FILE_SERVER_URL}/{log_id}/file'

        timeline_files = [
            os.path.join(logger.LOGS_DIRECTORY, f'{log_id}_timeline.json'),
            os.path.join(logger.LOGS_DIRECTORY, f'{log_id}_timeline.png')
        ]
        files = list()

        for file in timeline_files:
            filename = os.path.basename(file)
            files.append(
                (filename, (filename, open(file, 'rb')))
            )

        if len(files) > 0:
            response = requests.post(url, files=files)
            response.raise_for_status()
            logging.info(f'Timeline files for {log_id} uploaded!')

            # Removing the collected log files
            for file in timeline_files:
                os.remove(file)

    except Exception as e:
        logging.exception(f'Uploading timeline files for {log_id} failed.')
