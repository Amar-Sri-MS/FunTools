import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *

def dumphexsane(x):
    r = ""
    for i in x:
        j = ord(i)
        if (j < 32) or (j >= 127):
            r = r + "."
        else:
            r = r + i
    return r

def dumppayload(x):
    x = str(x)
    l = len(x)
    i = 0
    R = ""
    while i < l:
        R += "\n "
        for j in range(16):
            if i + j < l:
                R += "%02X " % ord(x[i + j])
            else:
                R += "   "
            if j % 16 == 7:
                R += " "
        R += "    "
        i += 16

    return R

def dumphex(x):
    x = str(x)
    l = len(x)
    i = 0
    R = ""
    while i < l:
        R += "\n%04x:  " % i
        for j in range(16):
            if i + j < l:
                R += "%02X " % ord(x[i + j])
            else:
                R += "   "
            if j % 16 == 7:
                R += " "
        R += "    "
        R += dumphexsane(x[i:i + 16])
        i += 16

    return R

def arraypack(H):
    BLOB = struct.pack('%sB'%len(H), *H)
    return BLOB

def bytepack(BYTES):
    H = [int(i, 16) for i in ['0x'+x for x in BYTES.split()]]
    BLOB = struct.pack('%sB'%len(H), *H)
    return BLOB

def wordpack(WORD):
    H = [int(i, 16) for i in ['0x'+x for x in WORD.split()]]
    BLOB = struct.pack('%sI'%len(H), *H)
    return BLOB

def LEwordpack(LEWORD):
    H = [int(i, 16) for i in ['0x'+x for x in LEWORD.split()]]
    BLOB = struct.pack('<%sI'%len(H), *H)
    return BLOB


class VPacket(Packet):

    def verify_field(self, field, value, msg=""):
        m = field if not msg else msg + '.' + field
        (f, v) = self.getfield_and_val(field)
        comparev = value if type(value) is str else hex(value)
        actualv = f.i2repr(self, v).replace( '\'', '') if type(value) is str else hex(v)
        print("    compare ... %s (observed=%s, expected=%s) ..." % (m, actualv, comparev))
        status = True if actualv == comparev else False
        print("ok" if status else "fail")
        return status

    def find_field(self, field, value, msg=""):
        import re
        m = field if not msg else msg + '.' + field
        (f, v) = self.getfield_and_val(field)
        comparev = value
        actualv = str(f.i2repr(self, v).replace( '\'', '') if type(value) is str else hex(v))
        print("    find ... %s (observed=%s, comparedto=%s) ..." % (m, actualv, comparev))
        status = True if re.search(comparev, actualv) else False
        print("ok" if status else "fail")
        return status

    def compare_value(self, field):
        (f, v) = self.getfield_and_val(field)
        return f.i2repr(self, v)

    def verify(self, *args, **kwargs):
        print("packet (%s) verification ... skipped" % self.__class__.__name__)
        return True

class XStrLenField(StrFixedLenField):
    def i2repr(self, pkt, x):
        import string
        return dumphex(x) #repr(x) #"%s" % x if all(c in string.printable for c in x) else ' '.join(b.encode('hex') for b in x)
        return "%s" % x if all(c in string.printable for c in x) else ' '.join(b.encode('hex') for b in x)

class XStrField(StrField):
    def i2repr(self, pkt, x):
        return ' '.join(b.encode('hex') for b in x)

class RFlagsField(FlagsField, object):
    def i2repr(self, pkt, v):
        return "[%s] %s" % (lhex(v), super(CFlagsField, self).i2repr(pkt, v))

class CFlagsField(FlagsField):
    def i2repr(self, pkt, x):
        flgs = []
        d = dict(enumerate(self.names)) if type(self.names) is list else self.names
        for (k, v) in d.items():
            v = v if type(v) is not list else v[0]
            tf = '' if (x & (1<<k)) == 0 else 'on'
            #flgs.append('%s=%s' % (v, tf))
            flgs.append('{0:20} = {1:7}'.format(v, tf))
        return "[%s]\n" % lhex(x) + "\n".join(flgs)

class CLEFlagsField(FlagsField):
    def i2repr(self, pkt, x):
        flgs = []
        x = struct.unpack('H', struct.pack('>H', x))[0]
        d = dict(enumerate(self.names)) if type(self.names) is list else self.names
        for (k, v) in d.items():
            v = v if type(v) is not list else v[0]
            tf = '' if (x & (1<<k)) == 0 else 'on'
            flgs.append('{0:20} = {1:7}'.format(v, tf))
        return "[%s]\n" % lhex(x) + "\n".join(flgs)

class CByteEnumField(ByteEnumField, object):
    def i2repr(self, pkt, v):
        return "[%s] %s" % (lhex(v), super(CByteEnumField, self).i2repr(pkt, v))

class CMultiEnumField(MultiEnumField, object):
    def i2repr(self, pkt, v):
        return "[%s] %s" % (lhex(v), super(CMultiEnumField, self).i2repr(pkt, v))

class CBitEnumField(BitEnumField, object):
    def i2repr(self, pkt, v):
        return "[%s] %s" % (lhex(v), super(CBitEnumField, self).i2repr(pkt, v))

class UBitEnumField(BitEnumField, object):
    def i2repr(self, pkt, x):
        d = dict(enumerate(self.names)) if type(self.names) is list else self.names
        for (k, v) in d.items():
            v = v if type(v) is not list else v[0]
            tf = '' if (x & (1<<k)) == 0 else 'on'
            #flgs.append('%s=%s' % (v, tf))
            flgs.append('{0:20} = {1:7}'.format(v, tf))
        return "[%s]\n" % lhex(x) + "\n".join(flgs)

class RsvBitField(BitField):
    def i2repr(self, pkt, v):
        return "%s" % ("reserved" if v == 0 else "[%s] bad-reserved" % (lhex(v)))

class CBitField(BitField):
    def i2repr(self, pkt, v):
        return "[%s] %s" % (lhex(v), v)

class CByteField(ByteField):
    def i2repr(self, pkt, v):
        return "%s" % ("unsupported" if v == 0xff else "[%s] %s" % (lhex(v), v))


class CLongField(LongField):
    def i2repr(self, pkt, v):
        return "%s" % ("unsupported" if v == 0xffffffffffffffff else "[%s] %s" % (lhex(v), v))
class CLELongField(LELongField):
    def i2repr(self, pkt, v):
        return "%s" % ("unsupported" if v == 0xffffffffffffffff else "[%s] %s" % (lhex(v), v))

class CIntEnumField(IntEnumField, object):
    def i2repr(self, pkt, v):
        return "[%s] %s" % (lhex(v), super(CIntEnumField, self).i2repr(pkt, v))

class CLEIntEnumField(LEIntEnumField, object):
    def i2repr(self, pkt, v):
        return "[%s] %s" % (lhex(v), super(CLEIntEnumField, self).i2repr(pkt, v))


class CIntField(IntField):
    def i2repr(self, pkt, v):
        return "%s" % ("unsupported" if v == 0xffffffff else "[%s] %s" % (lhex(v), v))
class CLEIntField(LEIntField):
    def i2repr(self, pkt, v):
        return "%s" % ("unsupported" if v == 0xffffffff else "[%s] %s" % (lhex(v), v))

class CShortEnumField(ShortEnumField, object):
    def i2repr(self, pkt, v):
        return "[%s] %s" % (lhex(v), super(CShortEnumField, self).i2repr(pkt, v))
class CLEShortEnumField(LEShortEnumField, object):
    def i2repr(self, pkt, v):
        return "[%s] %s" % (lhex(v), super(CLEShortEnumField, self).i2repr(pkt, v))

class CShortField(ShortField):
    def i2repr(self, pkt, v):
        return "%s" % ("unsupported" if v == 0xffffffff else "[%s] %s" % (lhex(v), v))
class CLEShortField(LEShortField):
    def i2repr(self, pkt, v):
        return "%s" % ("unsupported" if v == 0xffffffff else "[%s] %s" % (lhex(v), v))

class ByteLenField(StrFixedLenField):
    def i2repr(self, pkt, v):
        l = self.length_from(pkt)
        if l == len(v):
            return dumphex(v)
        else:
            return "[Bad Data of %d bytes, Expecting %d bytes ]%s" % (len(v), l, dumphex(v))

class HexDumpStrField(StrField):
    def i2repr(self, pkt, x):
        return dumphex(x)

class BCDVersionField(ByteLenField):
    def i2repr(self, pkt, x):
        s = ""
        for b in x:
            if b > 99 and b < 243 : s = "[bad-format]"
            return '.'.join(b.encode('hex') for b in x) + s

class VersionField(ByteLenField):
    def i2repr(self, pkt, x):
        return '.'.join(b.encode('hex') for b in x)

class XLEIntField(LEIntField):
    def i2repr(self, pkt, x):
        return lhex(self.i2h(pkt, x))


class XLEShortField(LEShortField):
    def i2repr(self, pkt, x):
        return lhex(self.i2h(pkt, x))

class XAddressField(StrLenField):
    def i2repr(self, pkt, x):
        return ':'.join(b.encode('hex') for b in x)

class XFieldLenField(FieldLenField):
    def i2repr(self, pkt, x):
        return lhex(x)

def field2str(pkt, pktf):
    (f, v) = pkt.getfield_and_val(pktf)
    return f.i2repr(pkt, v)

def hexdumpdata2str(p):
    return ' '.join(hex(ord(b)) for b in str(p))

class BYTEORDER:
    BE = 0x01020304
    LE = 0x04030201
