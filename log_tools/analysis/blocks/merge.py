#
# Merge block: merge streams by timestamp.
#

import heapq

from blocks.block import Block


class Merge(Block):
    """
    Merge the inputs.

    Depends on the tuple's first two elements being comparable timestamp
    parts.
    """
    def process(self, iters):
        return heapq.merge(*iters)
