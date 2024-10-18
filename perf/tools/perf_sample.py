class PerfSample(object):
    """
    Contains a perf sample.

    For standard perf samples, the custom_data variable will be None. For
    custom data samples, the variable will hold the custom data value.
    """

    LINES_PER_SAMPLE = 8
    PERF_SAMPLE_FMT = "%s  %16x  %8x  %8x  %8x  %8x  %8x %16x %s"
    PERF_HEADER_FMT = "%s  %16s  %8s  %8s  %8s  %8s  %8s %16s %s"

    # The magic value of CP0 when the data in the sample represents
    # custom data. This value will never be seen in regular samples
    # because the CP0 register is only 32 bits.
    CUSTOM_DATA_VALUE_CP0 = 0xACCE00000000

    def __init__(self, vp, wu_list, *args):
        assert PerfSample.LINES_PER_SAMPLE == 8
        assert len(args) == PerfSample.LINES_PER_SAMPLE
        self.vp = vp2ccv(vp)
        self.timestamp = args[0] >> 8
        self.cp0_count = args[1] >> 8
        if self.cp0_count == self.CUSTOM_DATA_VALUE_CP0:
            #
            # The upper 8 bits of custom data come from arg2[15:8], and
            # the rest come from arg3[63:8]. Recall that the lowest 8 bits
            # of every sample represent a global VPID.
            #
            self.custom_data = (args[2] >> 8 << 56) & 0xFF00000000000000
            self.custom_data = self.custom_data | (args[3] >> 8)
        else:
            self.custom_data = None
            self.perf_cnt0 = args[2] >> 8
            self.perf_cnt1 = args[3] >> 8
        self.perf_cnt2 = args[4] >> 8
        self.perf_cnt3 = args[5] >> 8
        wu_id = (args[6] >> 8) & 0xFFFF
        assert wu_id < len(wu_list), (wu_id, len(wu_list), [hex(a) for a in args])
        self.wu = wu_list[wu_id]
        self.arg0 = ((args[6] >> 24) & 0xFF) << 56
        self.arg0 |= args[7] >> 8

    @staticmethod
    def header_str():
        return PerfSample.PERF_HEADER_FMT % (
            "vp",
            "timestamp",
            "cp0_count",
            "perf0",
            "perf1",
            "perf2",
            "perf3",
            "arg0",
            "wu",
        )

    def __str__(self):
        return PerfSample.PERF_SAMPLE_FMT % (
            self.vp,
            self.timestamp,
            self.cp0_count,
            self.perf_cnt0,
            self.perf_cnt1,
            self.perf_cnt2,
            self.perf_cnt3,
            self.arg0,
            self.wu,
        )


def perf_table_from_perf_samples(perf_samples, event_types):
    rows = [
        (
            "timestamp",
            "vp",
            "wu",
            "cycles",
            event_types[0],
            event_types[1],
            event_types[2],
            event_types[3],
            "arg0",
        )
    ]
    for sample in perf_samples:
        rows.append(
            (
                sample.timestamp,
                sample.vp,
                sample.wu,
                sample.cp0_count * 2,
                sample.perf_cnt0,
                sample.perf_cnt1,
                sample.perf_cnt2,
                sample.perf_cnt3,
                sample.arg0,
            )
        )
    return rows


def table_from_custom_samples(custom_samples):
    """
    Constructs a list of custom samples (where samples are represented as
    tuples).

    The first tuple in the list contains strings that are effectively
    column titles.
    """
    rows = [
        (
            "timestamp",
            "vp",
            "data",
            "arg0",
        )
    ]
    for sample in custom_samples:
        rows.append(
            (
                sample.timestamp,
                sample.vp,
                sample.custom_data,
                sample.arg0,
            )
        )
    return rows


def vp2ccv(vp):
    return "%s.%s.%s" % (vp // 24, (vp % 24) // 4, (vp % 24) % 4)
