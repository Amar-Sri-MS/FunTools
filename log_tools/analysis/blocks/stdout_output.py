#
# stdout output block.
#

from blocks.block import Block

class StdOutput(Block):

    def process(self, iters):
        iter = iters[0]

        for tuple in iter:
            print(self.tuple2line(tuple))

    @staticmethod
    def tuple2line(tuple):
        return '{} {} {}'.format(tuple[2], tuple[3], tuple[4])