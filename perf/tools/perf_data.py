import collections


class PerfData(object):
    """The object representing all perf data"""

    EVENT_COUNT = 4

    def __init__(
        self, event_types, wu_stack_range, debug_build, perf_table, overflow_stats=None
    ):
        """
        Creates a new instance of the perf data object.

        :param event_types:
        :param wu_stack_range:
        :param debug_build:
        :param perf_table:
        :param overflow_stats: dict of cluster.core to overflow stats, or None
                               if there was no overflow
        """
        self.event_types = event_types
        self.wustack_start = wu_stack_range.start
        self.wustack_end = wu_stack_range.end
        self.debug_build = debug_build
        self.rows = perf_table
        if overflow_stats is None:
            self.overflow_stats = {}
        else:
            self.overflow_stats = overflow_stats

    def calculate_dispatch_cycles(self):
        assert self.rows[0][0] == "timestamp"
        assert self.rows[0][1] == "vp"
        assert self.rows[0][3] == "cycles"

        vp_to_rows = collections.defaultdict(list)
        for r in self.rows[1:]:
            vp = r[1]
            vp_to_rows[vp].append(r)

        new_rows = []
        for vp, rows in vp_to_rows.iteritems():
            new_rows.append(rows[0] + ("unknown",))
            for i in xrange(1, len(rows)):
                dispatch_time = rows[i][0] - rows[i - 1][0]
                dispatch_cycles = dispatch_time * 16 / 10
                dispatch_cycles -= rows[i - 1][3]
                new_rows.append(rows[i] + (dispatch_cycles,))

        new_rows.sort(cmp=lambda x, y: cmp(x[0], y[0]))
        new_rows.insert(0, self.rows[0] + ("dispatch_cycles",))
        self.rows = new_rows
