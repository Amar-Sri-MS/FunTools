#!/usr/bin/env python3

#
# Script to send email alerts based on the alerts
# stored on the Elasticsearch index "alerts*".
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2022 Fungible Inc.  All rights reserved.

import json
import time

import config_loader
import logger

from elasticsearch7 import Elasticsearch

from alerts.email_alert import EmailAlert


config = config_loader.get_config()

log_handler = logger.get_logger(filename='alerter.log')


class Alerter(object):
    """ """
    def __init__(self, index='alerts*', sync_freq=30, last_sync_time=0):
        ELASTICSEARCH_HOSTS = config['ELASTICSEARCH']['hosts']
        ELASTICSEARCH_TIMEOUT = config['ELASTICSEARCH']['timeout']
        ELASTICSEARCH_MAX_RETRIES = config['ELASTICSEARCH']['max_retries']
        self.es = Elasticsearch(ELASTICSEARCH_HOSTS,
                                timeout=ELASTICSEARCH_TIMEOUT,
                                max_retries=ELASTICSEARCH_MAX_RETRIES,
                                retry_on_timeout=True)

        # Elasticsearch index where the alerts are stored.
        self.index = index

        # Time (in seconds) to check for new documents in the index.
        self.sync_freq = sync_freq
        # Epoch time (in milliseconds)
        self.last_sync_time = last_sync_time

        # List of alert types (eg. email, stdout, etc)
        self.alert_types = list()

    def add_alert_type(self, alert_type):
        """ """
        self.alert_types.append(alert_type)

    def _search(self, since_time):
        log_handler.info(f'Searching for alerts in {self.index} since {since_time}')
        # Query to fetch documents from the last sync time.
        query_body = {
            "query": {
                "range": {
                    "@timestamp": {
                        "gte": str(since_time),
                    }
                }
            }
        }

        result = self.es.search(query_body,
                                self.index,
                                size=10000,
                                sort='@timestamp:asc',
                                ignore_throttled=False)
        return result['hits']

    def start(self):
        """ """
        while True:
            try:
                result = self._search(self.last_sync_time)
                result_count = result['total']
                if result_count['relation'] != 'eq':
                    #TODO(Sourabh): Fetch the next set of results
                    pass
                results = result['hits']
                for document in results:
                    log_handler.info(f'Document: {document}')
                    self.handle_alert(document)

                # Storing time in milliseconds.
                self.last_sync_time = time.time() * 1000
            except:
                log_handler.exception(f'Error while searching for alerts in {self.index}')
            finally:
                time.sleep(self.sync_freq)

    def _form_alert_dict(self, document):
        alert = document['_source']

        # Convert comma separated tags into list
        tags_str = alert.get('tags')
        alert['tags'] = tags_str.split(',') if tags_str else []

        # hits are comma separated dicts stored as string.
        # Converting them into list of dicts.
        formatted_hits = []
        if alert['hits'] != '':
            formatted_hits = json.loads(f"""[{alert['hits']}]""")
        alert['hits'] = formatted_hits
        alert['hits'] = [
            {
                'index': hit['_index'],
                **hit['_source']
            } for hit in alert['hits']
        ]

        return alert

    def handle_alert(self, document):
        if len(self.alert_types) == 0:
            raise Exception('No alert types defined')

        for alert_type in self.alert_types:
            alert = self._form_alert_dict(document)
            status = alert_type.process(alert)
            log_handler.info(f'Alert status: {status}')


def main():
    alerter = Alerter()

    email_alerter = EmailAlert()
    alerter.add_alert_type(email_alerter)

    alerter.start()


if __name__ == '__main__':
    main()