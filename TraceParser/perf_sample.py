#
# Common code describing a perf sample.
#

class PerfSample(object):
    """
    Represents a perf sample.
    """
    # Slots are part of python's data model, and allow us to explicitly
    # declare data members. We do this to avoid the implicit __dict__
    # which is expensive (I was measuring 1kB per object, which is
    # unbelievable).
    __slots__ = ['wuid', 'arg0', 'timestamp', 'cp0_count', 'perf_counts',
                 'vp', 'is_custom_data', 'custom_data']
    def __init__(self):
        self.wuid = None
        self.arg0 = None
        self.timestamp = None
        self.cp0_count = None
        self.perf_counts = [None, None, None, None]
        self.vp = None

        # True if this is a custom data sample, else False
        self.is_custom_data = False
        self.custom_data = None

    def __str__(self):
        return ('%s = wu: %s  '
                'time: %s  '
                'cycle: %s  '
                'perf0: %s  '
                'perf1: %s  '
                'perf2: %s  '
                'perf3: %s' % (self.vp,
                               format(self.wuid, '>4d'),
                               self.timestamp,
                               format(self.cp0_count, '>7d'),
                               format(self.perf_counts[0], '>6d'),
                               format(self.perf_counts[1], '>6d'),
                               format(self.perf_counts[2], '>6d'),
                               format(self.perf_counts[3], '>10d')))

    def to_perfmon_data(self):
        """
        Returns a representation of the data in this perf sample that
        is close to the perfmon format for perf visualization tools.

        The only difference is that instead of a global VP number, we only
        provide a local VP number in the lowest 8 bits. Callers must
        read and modify the lower 8 bits to set the global VP.

        C code from FunOS describing the format for perf samples:
        vpnum_t vp = vplocal_vpnum();
        cp0_kscratch6_write((timestamp) << 8 | vp);
        cp0_kscratch6_write((cp0_count) << 8 | vp);
        cp0_kscratch6_write((perf_cnt0) << 8 | vp);
        cp0_kscratch6_write((perf_cnt1) << 8 | vp);
        cp0_kscratch6_write((perf_cnt2) << 8 | vp);
        cp0_kscratch6_write((perf_cnt3) << 8 | vp);
        cp0_kscratch6_write(((arg0) >> 56) << 24 | ((wuid) << 8) | vp);
        cp0_kscratch6_write((arg0) << 8 | vp);
        """

        if self.is_custom_data:
            return self.to_custom_perfmon_data()

        # Note: in some cases we can avoid masking because the values are
        # 32-bits or less.
        vals = list()
        vals.append((self.timestamp << 8) & 0xffffffffffffffff | self.vp)
        vals.append(self.cp0_count << 8 | self.vp)
        vals.append(self.perf_counts[0] << 8 | self.vp)
        vals.append(self.perf_counts[1] << 8 | self.vp)
        vals.append(self.perf_counts[2] << 8 | self.vp)
        vals.append(self.perf_counts[3] << 8 | self.vp)
        vals.append((self.arg0 >> 56 << 24) | (self.wuid << 8) | self.vp)
        vals.append((self.arg0 << 8) & 0xffffffffffffffff | self.vp)
        return vals

    def to_custom_perfmon_data(self):
        """
        C code describing the format for custom data samples
        vpnum_t vp = vplocal_vpnum();
        cp0_kscratch6_write((timestamp) << 8 | vp);
        cp0_kscratch6_write((0xaccell << 32) << 8 | vp);
        cp0_kscratch6_write(((user_data) >> 56) << 8 | vp);
        cp0_kscratch6_write((user_data) << 8 | vp);
        cp0_kscratch6_write((0) << 8 | vp);
        cp0_kscratch6_write((0) << 8 | vp);
        cp0_kscratch6_write(((arg0) >> 56) << 24 | ((0) << 8) | vp);
        cp0_kscratch6_write((arg0) << 8 | vp);
        """
        vals = list()
        vals.append((self.timestamp << 8) & 0xffffffffffffffff | self.vp)
        vals.append((0xacce << 32) << 8 | self.vp)
        vals.append((self.custom_data >> 56) << 8 | self.vp)
        vals.append((self.custom_data << 8) & 0xffffffffffffffff | self.vp)
        vals.append(0 << 8 | self.vp)
        vals.append(0 << 8 | self.vp)
        vals.append((self.arg0 >> 56 << 24) | (0 << 8) | self.vp)
        vals.append((self.arg0 << 8) & 0xffffffffffffffff | self.vp)
        return vals
