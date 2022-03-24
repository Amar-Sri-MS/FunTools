#!/usr/bin/env python3

#
# Wrapper class for storing & fetching the metadata
# stored on Elasticsearch
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

import datetime

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
        # Setting a high size to fetch all metadata
        results = self._search(size=10000)

        return self._format_results(results)

    def get_by_log_ids(self, log_ids):
        """ Fetches all the metadata for the given log_ids """
        if not log_ids or len(log_ids) == 0:
            return {}

        body = {
            'ids': log_ids
        }
        results = self.es.mget(body=body, index=self.index)

        return self._format_results(results['docs'])

    def get_by_tags(self, tags, size=-1):
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
        result = self._search(body, size)

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

        tags = doc['_source'].get('tags', None)
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
            'logID': log_id,
            '@timestamp': datetime.datetime.utcnow()
        }
        result = self.es.index(self.index,
                               data,
                               id=log_id)

        return result

    def update(self, log_id, metadata):
        """
        Updates the existing metadata with the given
        "metadata" (object).
        """
        body = {
            'doc': {
                **metadata,
                'logID': log_id,
                '@timestamp': datetime.datetime.utcnow()
            },
            'doc_as_upsert': True
        }
        result = self.es.update(self.index,
                                log_id,
                                body)

        return result

    def update_notes(self, log_id, note):
        """ Updating the notes in metadata document of "log_id" """
        body = self._build_query_to_append_to_array(log_id, 'notes', note)

        result = self.es.update(self.index,
                                id=log_id,
                                body=body)
        return result

    def update_tags(self, log_id, tags):
        """ Updating the tags in metadata document of "log_id" """
        body = self._build_query_to_append_to_array(log_id, 'tags', tags)

        result = self.es.update(self.index,
                                id=log_id,
                                body=body)
        return result

    def _build_query_to_append_to_array(self, log_id, field, value):
        # Sadly no easier way to append to arrays.
        # ES uses painless script.
        body = {
            'script': {
                'source': f"""
                            if (ctx._source.containsKey(\"{field}\"))
                                {{ ctx._source.{field}.add(params.value); }}
                            else
                                {{ ctx._source.{field} = [params.value]; }}

                            ctx._source['@timestamp'] = params['@timestamp'];
                            """,
                'lang': 'painless',
                'params': {
                    'value': value,
                    '@timestamp': datetime.datetime.utcnow()
                }
            },
            'upsert': {
                'logID': log_id,
                field: [value],
                '@timestamp': datetime.datetime.utcnow()
            }
        }
        return body

    def remove(self, log_id):
        """ Deleting the metadata for the given log_id """
        result = self.es.delete(self.index, log_id)

        return result
