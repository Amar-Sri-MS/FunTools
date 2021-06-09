#!/usr/bin/env python3
#
# Filters the log lines based on given filters.
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

from datetime import datetime, timezone
from dateutil import tz

from blocks.block import Block


class LogFilter(Block):
    """ Filters the logs based on the given filters """

    def set_config(self, config):
        self.filters = config['filters']
        time_filter = self.filters.get('include', {}).get('time')
        self.start_time, self.end_time = self._convert_time_filter(time_filter)

    def _convert_time_filter(self, time_filter):
        """
        Convert the given time filter into datetime objects.
        Args:
            time_filter: (tuple) containing epoch start and end time.
        Returns:
            tuple of datetime objects for start and end time. None if not
            found.
        """
        if not time_filter:
            return (None, None)

        start_time = time_filter[0]
        end_time = time_filter[1]

        if start_time:
            start_time = datetime.fromtimestamp(start_time, tz=timezone.utc)
        if end_time:
            end_time = datetime.fromtimestamp(end_time, tz=timezone.utc)

        return (start_time, end_time)

    def process(self, iters):
        for iter in iters:
            for tuple in iter:
                filtered = False
                # Making the datetime object timezone aware
                date_time = tuple[0].astimezone(tz.UTC)
                if self.start_time and date_time < self.start_time:
                    filtered = True

                if self.end_time and date_time > self.end_time:
                    filtered = True

                if not filtered:
                    yield tuple

