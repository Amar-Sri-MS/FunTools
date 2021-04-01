#!/usr/bin/env python3

#
# Wrapper class for storing & fetching the metadata
# stored on Elasticsearch
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

import config_loader

from elasticsearch7 import Elasticsearch
from elasticsearch7.exceptions import NotFoundError


class ElasticsearchMetadata(object):
    """
    Hides some elasticsearch specific queries for storing
    and fetching metadata of ingested log.
    """

    def __init__(self):
        self.index = 'metadata'
        self.config = config_loader.get_config()

        ELASTICSEARCH_HOSTS = self.config['ELASTICSEARCH']['hosts']
        self.es = Elasticsearch(ELASTICSEARCH_HOSTS)

    def get(self, log_id):
        """ Fetches metadata for a given "log_id" """
        try:
            result = self.es.get(self.index, log_id)
        except NotFoundError as e:
            return {}

        return self._format_doc(result)

    def get_all(self):
        """
        Fetches all the stored metadata in the index.
        """
        results = self._search()

        return self._format_results(results)

    def get_by_log_ids(self, log_ids):
        """ Fetches all the metadata for the given log_ids """
        body = {
            'ids': log_ids
        }
        results = self.es.mget(body=body, index=self.index)

        return self._format_results(results['docs'])

    def get_by_tags(self, tags):
        """
        Fetches all the metadata if the given tags exist in it
        """
        body = {
            'query': {
                'constant_score': {
                    'filter': {
                        'terms': {
                            'tags': tags
                        }
                    }
                }
            }
        }
        result = self._search(body)

        return self._format_results(result)

    def _search(self, body={}, size=-1):
        """
        Performs the Elasticsearch query to fetch the metadata.
        """
        result = self.es.search(body=body,
                                index=self.index,
                                size=size)

        return result['hits']['hits']

    def _format_results(self, results):
        """
        Formatting the list of ES documents.

        Returns an object with the document id as key
        Example:
        {
            'log_qa-1234': {
                'tags': []
            },
            'log_qa-4321': {
                'tags': []
            }
        }
        """
        formatted_results = {}
        for result in results:
            formatted_results[result['_id']] = self._format_doc(result)

        return formatted_results

    def _format_doc(self, doc):
        """
        Formatting the ES document.

        Returns:
        {} if not document is not found

        {
            'notes': [],
            'tags': [],
            'metadata': {}
        }
        """
        if not doc.get('found', True):
            return {}

        tags = doc['_source'].get('tags', '')
        return {
            **doc['_source'],
            'tags': [tags] if type(tags) == str else tags
        }

    def store(self, log_id, metadata):
        """
        Stores the given "metadata" (object) in the
        index.
        """
        data = {
            **metadata,
            'logID': log_id
        }
        result = self.es.index(self.index,
                               data,
                               id=log_id)

        return result

    def update(self, log_id, metadata):
        """ Updating the metadata document of "log_id" """
        result = self.es.update(self.index,
                                id=log_id,
                                body=metadata)
        return result