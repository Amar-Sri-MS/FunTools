#!/usr/bin/env python2.7
import struct

def packing_query(size, big_endian):
  endianness = '>' if big_endian else '<'
  if size == 8:
    int_kind = 'Q'
  elif size == 4:
    int_kind = 'I'
  elif size == 2:
    int_kind = 'H'
  elif size == 1:
    int_kind = 'B'
  else:
    raise Exception('Unknown int kind')
  return endianness + int_kind


def unpack_uint(data, size, big_endian):
  return struct.unpack(packing_query(size, big_endian), data)[0]


def unpack_uint_array(bytelist, size, big_endian):
  result = []
  for i in range(0, len(bytelist), size):
    s = ''.join(map(chr, bytelist[i:i + size]))
    result.append(struct.unpack(packing_query(size, big_endian), s)[0])
  return result


def unpack_u32(data, big_endian):
  return unpack_uint(data, 4, big_endian)


def pack_uint(data, size, big_endian):
  return map(ord, struct.pack(packing_query(size, big_endian), data))