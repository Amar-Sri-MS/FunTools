#!/usr/bin/env python3

#
# Network Tool for finding the information related to network service.
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2022 Fungible Inc.  All rights reserved.

import datetime
import json
import logging
import re


import config_loader

from elastic_log_searcher import build_query_body

from elasticsearch7 import Elasticsearch
from pprint import pprint

SEARCH_QUERIES = {
    # ztp log
    'DPU_REGISTER_WITH_SNS': {
        'query': '"etcdctl" AND "status" AND "up"',
        'description': 'DPU connects with SNS',
    },
    'DPU_SNS_DISCONNECT': {
        'query': '"etcdctl" AND "lease" AND "keep-alive"',
        'description': 'DPU lost connection with SNS',
    },

    # health check
    'FIRST_TIME_HEALTHCHECK': {
        'query': '"FV cons: First time to report health check true"',
        'description': 'DPU could reach to TOR',
    },
    'DPU_HEALTHCHECK_FAIL': {
        'query': '"system_healthy: False" AND "cpu_usage"',
        'description': 'DPU lost connection with TOR',
    },

    # funos checks
    'CC_INIT_DONE': {
        'query': '"FV cons: End of CC startup"',
        'description': 'CC init is done',
    },
    'DPU_PINGABLE_STATUS': {
        'query': '"FV cons: First time to report health check true"',
        'description': 'DPU is pingable with TOR',
    },
    'NETWORK_ROUTE_ADDED': {
        'query': '"NOTICE network_unit Forwarding: Route Add:"'
    },

    # ipmonitor events
    'NETLINK_STATUS': {
        'query': '"state" AND ("UP" OR "DORMANT" OR "DOWN") AND "group default link"'
    }
}

class Network(object):
    """ """

    def __init__(self, log_id):
        self.index = log_id
        self.config = config_loader.get_config()

        ELASTICSEARCH_HOSTS = self.config['ELASTICSEARCH']['hosts']
        ELASTICSEARCH_TIMEOUT = self.config['ELASTICSEARCH']['timeout']
        ELASTICSEARCH_MAX_RETRIES = self.config['ELASTICSEARCH']['max_retries']
        self.es = Elasticsearch(ELASTICSEARCH_HOSTS,
                                timeout=ELASTICSEARCH_TIMEOUT,
                                max_retries=ELASTICSEARCH_MAX_RETRIES,
                                retry_on_timeout=True)

    def _perform_es_search(self, queries, group_by_field=None, time_filters=None):
        """
        Returns ES results based on the given queries and performs
        group by the given group_by_field.
        """
        query_term = f' '.join([f'{query}' for query in queries])
        body = build_query_body(query_term, None, time_filters, match_all=True)
        result = self.es.search(body=body,
                                index=self.index,
                                size=1000,
                                sort='@timestamp:asc',
                                ignore_throttled=False)

        results = list()
        for hit in result['hits']['hits']:
            document = {
                '_id': hit['_id'],
                **hit['_source']
            }
            results.append(document)

        if group_by_field:
            return self._group_by(results, group_by_field)

        return results

    def _check_dpu_boot_info(self):
        """
        Searches in CC_startup.log
        """
        pass

    def _check_dpu_registration_info(self):
        """
        Searches in CC_ztp.log
        """
        # DPU registers with SNS
        search_query = SEARCH_QUERIES['DPU_REGISTER_WITH_SNS']['query']
        dpu_register_sns_info = self._perform_es_search([search_query])

        # DPU disconnect with SNS
        search_query = SEARCH_QUERIES['DPU_SNS_DISCONNECT']['query']
        dpu_disconnect_sns_info = self._perform_es_search([search_query])

        return {
            'register': dpu_register_sns_info,
            'disconnect': dpu_disconnect_sns_info
        }

    def _check_health(self):
        """
        Searches in CC_health.log
        """
        # DPU could reach to TOR
        search_query = SEARCH_QUERIES['FIRST_TIME_HEALTHCHECK']['query']
        first_healthcheck = self._perform_es_search([search_query])

        # DPU healthcheck fail
        search_query = SEARCH_QUERIES['DPU_HEALTHCHECK_FAIL']['query']
        healthcheck_fail = self._perform_es_search([search_query])

        return {
            'first_success': first_healthcheck,
            'fail': healthcheck_fail
        }

    def _check_cc_netlink_events(self):
        """
        Searches in ipmonitor logs for netlink statuses.
        """
        search_query = SEARCH_QUERIES['NETLINK_STATUS']['query']
        return self._perform_es_search([search_query])

    def _check_funos_events(self):
        """
        Searches in funos logs
        """
        # DPU could reach to TOR
        search_query = SEARCH_QUERIES['CC_INIT_DONE']['query']
        cc_init_info = self._perform_es_search([search_query])

        # DPU could reach to TOR
        search_query = SEARCH_QUERIES['DPU_PINGABLE_STATUS']['query']
        dpu_pingable_status = self._perform_es_search([search_query])

        # DPU could reach to TOR
        search_query = SEARCH_QUERIES['NETWORK_ROUTE_ADDED']['query']
        routes_added = self._perform_es_search([search_query])

        return {
            'cc_init': cc_init_info,
            'dpu_pingable_status': dpu_pingable_status,
            'network_routes_added': routes_added
        }

    def _group_by(self, results, field):
        """
        Performs a group by operations on the results list and
        returns a dict with keys as the values of the given field name.
        """
        grouped_results = dict()
        for result in results:
            field_value = result[field] if field in result else None
            if not field_value:
                continue
            if field_value not in grouped_results:
                grouped_results[field_value] = list()
            grouped_results[field_value].append(result)

        return grouped_results

    def get_info(self):
        """
        """
        registration_info = self._check_dpu_registration_info()
        health_info = self._check_health()
        funos_events = self._check_funos_events()
        netlink_events = self._check_cc_netlink_events()

        return {
            'registration_info': registration_info,
            'health_info': health_info,
            'funos_events': funos_events,
            'netlink_events': netlink_events
        }


if __name__ == '__main__':
    log_id = 'log_fod_network-tool'
    network = Network(log_id)
    pprint(network._check_funos_events())