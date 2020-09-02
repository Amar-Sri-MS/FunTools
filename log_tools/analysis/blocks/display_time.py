#
# Filters to convert epoch-based timestamps to display dates and times.
#

import re

from blocks.block import Block

class HumanDateTime(Block):

    def process(self, iters):
        iter = iters[0]

        for date_time, usecs, uid, _, line in iter:
            display = self.human_timestamp(date_time)
            yield (date_time, usecs, uid, display, line)

    @staticmethod
    def human_timestamp(date_time):
        return date_time.strftime("%b %d %H:%M:%S.%f")

