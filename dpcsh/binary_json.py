##
##  binary_json.py
##
##  Created by Renat Idrisov on 2022-06-25
##  Copyright (C) 2022 Fungible. All rights reserved.
##
##  Implementation of binary json encoding which is defined in FunOS,
##  the only two functions to use are encode(Any) -> bytes and decode(bytes) -> Any
##  please refer to binary_json_test and dpc_binary for example integrations

import struct
from typing import Any, Tuple, Union

class EncodeError(Exception):
    pass

class DecodeError(Exception):
    pass

# Constants below are defined in FunOS, do not change separately
bjsonNull = struct.pack('B', 0)
bjsonTrue = struct.pack('B', 1)
bjsonFalse = struct.pack('B', 2)
bjsonZeroD = struct.pack('B', 3)
bjsonArray = struct.pack('B', 4)
bjsonDict = struct.pack('B', 5)
bjsonByteArray = struct.pack('B', 6)
bjsonDouble = struct.pack('B', 7)
bjsonSmallString = struct.pack('B', 9)
bjsonSmallStringMaxLen = 0xffff
bjsonString = struct.pack('B', 0xA)
bjsonError = struct.pack('B', 0xB)
bjsonInt16 = struct.pack('B', 0xC)
bjsonInt32 = struct.pack('B', 0xD)
bjsonInt64 = struct.pack('B', 0xE)

maxByte    = 255
maxInt16   = 32767
minInt16   = -32768
maxUInt16  = 0xFFFF
maxInt32   = 2147483647
minInt32   = -2147483648
maxInt64   = 9223372036854775807
minInt64   = -9223372036854775808

bjsonTinyString = 0x40
bjsonTinyStringMaxLen = 0x3f

bjsonUint7 = 0x80
maxUint7   = 0x7f


class BinaryJsonArray:
    def __init__(self, raw_data=None):
        self.data = []
        self.raw_data = raw_data
        self.decoded = False
        self.size = decodeUint32LittleEndian(raw_data[5:])

    def __getitem__(self, key):
        if not self.decoded:
            self._decode()
        return self.data[key]

    def __setitem__(self, key, value):
        if not self.decoded:
            self._decode()
        self.data[key] = value

    def __len__(self):
        if not self.decoded:
            return self.size
        return len(self.data)
    
    def _decode(self):
        offset = 1 + 8
        self.data = []
        for _ in range(0, self.size):
          self.data.append(decode(self.raw_data[offset:]))
          offset += serialization_size(self.raw_data[offset:])
        self.decoded = True

    def encode(self):
        if not self.decoded:
            return self.raw_data
        return encodeList(self.data)


class BinaryJsonDict:
    def __init__(self, raw_data=None):
        self.data = {}
        self.raw_data = raw_data
        self.decoded = False
        self.size = decodeUint32LittleEndian(raw_data[5:])

    def __getitem__(self, key):
        if not self.decoded:
            self._decode()
        return self.data[key]

    def __setitem__(self, key, value):
        if not self.decoded:
            self._decode()
        self.data[key] = value

    def __len__(self):
        if not self.decoded:
            return self.size
        return len(self.data)
    
    def _decode(self):
        offset = 1 + 8
        self.data = {}
        for _ in range(0, self.size):
          key = decode(b[offset:])
          offset += serialization_size(self.raw_data[offset:])
          value = decode(b[offset:])
          offset += serialization_size(self.raw_data[offset:])
          self.data[key] = value

        self.decoded = True

    def encode(self):
        if not self.decoded:
            return self.raw_data
        return encodeDict(self.data)


def uInt64LittleEndian(u: int) -> bytes:
  return struct.pack('<Q', u)


def uInt32LittleEndian(u: int) -> bytes:
  return struct.pack('<I', u)


def uInt16LittleEndian(u: int) -> bytes:
  return struct.pack('<H', u)


def int64LittleEndian(u: int) -> bytes:
  return struct.pack('<q', u)


def int32LittleEndian(u: int) -> bytes:
  return struct.pack('<i', u)


def int16LittleEndian(u: int) -> bytes:
  return struct.pack('<h', u)


def float64BigEndian(f: float) -> bytes:
  return struct.pack('>d', f)


def decodeUint32LittleEndian(b: bytes) -> int:
  return struct.unpack('<I', b[:4])[0]


def decodeUint16LittleEndian(b: bytes) -> int:
  return struct.unpack('<H', b[:2])[0]


def decodeUint64LittleEndian(b: bytes) -> int:
  return struct.unpack('<Q', b[:8])[0]

def decodeInt32LittleEndian(b: bytes) -> int:
  return struct.unpack('<i', b[:4])[0]


def decodeInt16LittleEndian(b: bytes) -> int:
  return struct.unpack('<h', b[:2])[0]


def decodeInt64LittleEndian(b: bytes) -> int:
  return struct.unpack('<q', b[:8])[0]


def decodeFloat64BigEndian(b: bytes) -> float:
  return struct.unpack('>d', b[:8])[0]

def isByte(n: Any) -> bool:
  if isinstance(n, int) or (isinstance(n, float) and n.is_integer()):
    return n >= 0 and n <= maxByte
  return False


def isByteArray(a: list) -> bool:
  if len(a) > maxUInt16:
    return False

  for n in a:
    if not isByte(n):
      return False

  return True


def encodeNone() -> bytes:
  return bjsonNull


def encodeBool(b: bool) -> bytes:
  return bjsonTrue if b else bjsonFalse


def encodeInt(n: int) -> bytes:
  if n >= 0 and n <= maxUint7:
    result = bytes([bjsonUint7 + n])
    return result

  if n >= minInt16 and n <= maxInt16:
    return bjsonInt16 + int16LittleEndian(n)

  if n >= minInt32 and n <= maxInt32:
    return bjsonInt32 + int32LittleEndian(n)

  if n >= minInt64 and n <= maxInt64:
    return bjsonInt64 + int64LittleEndian(n)

  raise EncodeError("Too large integer to encode {0}".format(n))


def encodeFloat(f: float) -> bytes:
  if f == 0.0:
    return bjsonZeroD
  return bjsonDouble + float64BigEndian(f)


def encodeStr(s: str) -> bytes:
  count = len(s)
  if count <= bjsonTinyStringMaxLen:
    prefix = bytes([bjsonTinyString + count])
  elif count <= bjsonSmallStringMaxLen:
    prefix = bjsonSmallString + uInt16LittleEndian(count)
  else:
    prefix = bjsonString + uInt32LittleEndian(count)

  return prefix + s.encode('utf8') + b'\0'


def encodeByteArray(l: list) -> bytes:
  return bjsonByteArray + uInt16LittleEndian(len(l)) + bytes(bytearray(l))


def encodeByteArrayFromBytes(b: bytes) -> bytes:
  return bjsonByteArray + uInt16LittleEndian(len(b)) + b


def encodeList(l: list) -> bytes:
  if isByteArray(l):
    return encodeByteArray(l)

  data = b''
  for el in l:
    data += encode(el)

  return bjsonArray + uInt32LittleEndian(len(data)) + uInt32LittleEndian(len(l)) + data


def encodeDict(d: dict) -> bytes:
  data = b''
  for k in sorted(d.keys()):
    data += encode(k) + encode(d[k])

  return bjsonDict + uInt32LittleEndian(len(data)) + uInt32LittleEndian(len(d)) + data


def encode(d: Any) -> bytes:
  if d is None:
    return encodeNone()
  
  if isinstance(d, BinaryJsonArray):
    return d.encode()

  if isinstance(d, BinaryJsonDict):
    return d.encode()

  if isinstance(d, bool):
    return encodeBool(d)

  if isinstance(d, int):
    return encodeInt(d)

  if isinstance(d, float):
    return encodeFloat(d)

  if isinstance(d, str):
    return encodeStr(d)

  if isinstance(d, list):
    return encodeList(d)

  if isinstance(d, bytes):
    return encodeByteArrayFromBytes(d)

  if isinstance(d, dict):
    return encodeDict(d)

  raise EncodeError("Unsupported datatype {0}".format(type(d)))


def serialization_size(b: bytes) -> int:
  size = len(b)
  if size == 0:
    return -1

  if b.startswith(bjsonNull) or b.startswith(bjsonTrue) or \
     b.startswith(bjsonFalse) or b.startswith(bjsonZeroD):
    return 1

  if b.startswith(bjsonArray) or b.startswith(bjsonDict):
    if size < 5:
      return -1
    return 9 + decodeUint32LittleEndian(b[1:])

  if b.startswith(bjsonByteArray):
    if size < 3:
      return -1
    return 3 + decodeUint16LittleEndian(b[1:])

  if b.startswith(bjsonSmallString):
    if size < 3:
      return -1
    return 3 + decodeUint16LittleEndian(b[1:]) + 1

  if b.startswith(bjsonString) or b.startswith(bjsonError):
    return 5 + decodeUint32LittleEndian(b[1:]) + 1

  if b[0] >= bjsonTinyString and b[0] < bjsonUint7:
    return 1 + (b[0] - bjsonTinyString) + 1

  if b[0] >= bjsonUint7:
    return 1

  if b.startswith(bjsonDouble):
    return 9

  if b.startswith(bjsonInt16):
    return 3

  if b.startswith(bjsonInt32):
    return 5

  if b.startswith(bjsonInt64):
    return 9

  return -1


def decode(b: bytes) -> Any:
  if b.startswith(bjsonNull):
    return None

  if b.startswith(bjsonTrue):
    return True

  if b.startswith(bjsonFalse):
    return False

  if b.startswith(bjsonZeroD):
    return 0.0

  if b.startswith(bjsonDouble):
    return decodeFloat64BigEndian(b[1:])

  if b.startswith(bjsonInt16):
    return decodeInt16LittleEndian(b[1:])

  if b.startswith(bjsonInt32):
    return decodeInt32LittleEndian(b[1:])

  if b.startswith(bjsonInt64):
    return decodeInt64LittleEndian(b[1:])

  if b[0] >= bjsonTinyString and b[0] < bjsonUint7:
    size = b[0] - bjsonTinyString
    return b[1:size+1].decode("utf-8")

  if b[0] >= bjsonUint7:
    return int(b[0] - bjsonUint7)

  if b.startswith(bjsonSmallString):
    size = decodeUint16LittleEndian(b[1:])
    return b[3:size+3].decode("utf-8")

  if b.startswith(bjsonString) or b.startswith(bjsonError):
    size = decodeUint32LittleEndian(b[1:])
    return b[5:size+5].decode("utf-8")

  if b.startswith(bjsonArray):
    return BinaryJsonArray(b[:serialization_size(b)])

  if b.startswith(bjsonDict):
    return BinaryJsonDict(b[:serialization_size(b)])

  if b.startswith(bjsonByteArray):
    size = decodeUint16LittleEndian(b[1:])
    return list(b[3:size+3])
