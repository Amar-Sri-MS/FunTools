#
# Filters to convert epoch-based timestamps to display dates and times.
#

import datetime as d
import re

from blocks.block import Block

class HumanDateTime(Block):

    def process(self, iters):
        iter = iters[0]

        for secs, usecs, uid, _, line in iter:
            display = self.human_timestamp(secs, usecs)
            yield (secs, usecs, uid, display, line)

    @staticmethod
    def human_timestamp(secs, usecs):
        return d.datetime.fromtimestamp(secs + float(usecs) * 1e-6).strftime("%b %d %H:%M:%S.%f")

