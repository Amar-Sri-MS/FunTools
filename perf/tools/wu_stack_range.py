import collections


class WuStackRange(collections.namedtuple("Range", ["start", "end"])):
    def __str__(self):
        return "(0x%016x, 0x%016x)" % self

    def xkphys_to_xkseg(self):
        return WuStackRange(xkphys_to_xkseg(self.start), xkphys_to_xkseg(self.end))


def xkphys_to_xkseg(va):
    assert va >> 48 == 0xA800
    assert (va & 4095) == 0
    va &= (1 << 48) - 1
    va *= 2
    va |= 0xC000 << 48
    return va
