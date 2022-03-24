#!/usr/bin/env python3

#
# Implementation of Lossy Counting Algorithm for approximately
# counting frequent elements in a stream.
#
# The algorithm divides the stream into windows and counts
# each element in the window. Removes elements at the end of
# the window which are not frequent.
#
# Higher the window size better the accuracy and higher the memory
# usage.
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.


class EntryItem(object):
    """ Entry item for storing the duplicate entry """
    __slots__ = ['bucket_id', 'count', 'entry']

    def __init__(self, bucket_id, count, entry):
        self.bucket_id = bucket_id
        self.count = count
        self.entry = entry

class LossyCounting(object):
    """
    Implementation of Lossy Counting Algorithm for approximately
    counting frequent elements in a stream.

    The algorithm divides the stream into windows and counts
    each element in the window. Removes elements at the end of
    the window which were not frequent.

    Higher the window size better the accuracy and higher the memory
    usage.
    """

    def __init__(self, window_size):
        self._n = 0
        # Hashmap for item as key and EntryItem as value
        self._entries = dict()
        self._window_size = window_size
        # Current window id
        self._current_bucket_id = 1

    def count(self, item, entry=None):
        """
        Add item and the entry associated to the item for counting.
        """
        self._n += 1
        if item not in self._entries:
            self._entries[item] = EntryItem(bucket_id=self._current_bucket_id - 1,
                                            count=0,
                                            entry=entry)

        self._entries[item].count = self._entries[item].count + 1

        # Remove less frequent elements at the end of window.
        if self._n % self._window_size == 0:
            self._trim()
            self._current_bucket_id += 1

    def _trim(self):
        """ Trim data which does not fit the criteria """
        for item, entry in list(self._entries.items()):
            count = entry.count
            bucket_id = entry.bucket_id
            if count <= self._current_bucket_id - bucket_id:
                del self._entries[item]

    def get_iter(self, threshold_count):
        """
        Returns an iterator with entry dict whose duplicate count
        is greater than the threshold.
        """
        self._trim()
        # This could be the max error in the count.
        error_count = self._n/self._window_size
        for item, entry in self._entries.items():
            count = entry.count
            if count >= threshold_count - error_count:
                yield {
                    'item': item,
                    'entry': entry.entry,
                    'count': count
                }
