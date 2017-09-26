//
//  DKBitAddress.swift
//  DataKit
//
//  Created by Bertrand Serlet on 8/11/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// Given a stream, a bit offset

struct DKBitAddress {
	let data: DKBitStream
	var bitOffset: UInt64
	var isByteAligned: Bool {
		return bitOffset & 7 == 0
	}
	mutating func fetchUpTo64Bits(_ numBitsWanted: UInt8) -> UInt64? {
		return data.fetchUpTo64Bits(numBitsWanted: numBitsWanted, bitOffset: &bitOffset)
	}
	mutating func fetchByte() -> UInt8? {
		return data.fetchByte(bitOffset: &bitOffset)
	}
	mutating func fetchZeroTerminatedString(okToEndWithoutZero: Bool = false) -> String? {
		assert(isByteAligned)
		return data.fetchZeroTerminatedString(bitOffset: &bitOffset, okToEndWithoutZero: okToEndWithoutZero)
	}
	mutating func forceByteAlignment() {
		if bitOffset & 7 != 0 {
			bitOffset += 8 - (bitOffset & 7)
		}
	}
	func addBitOffset(_ bo: UInt64) -> DKBitAddress {
		return DKBitAddress(data: data, bitOffset: bitOffset + bo)
	}
	func compare(numberOfBits: UInt64, other: DKBitAddress) -> Bool {
		var bo2 = other.bitOffset
		var same = true
		_ = data.fetchBits(numBitsWanted: numberOfBits, bitOffset: bitOffset) { word1, nb in
			_ = other.data.fetchBits(numBitsWanted: UInt64(nb), bitOffset: bo2) { word2, nb2 in
				if word1 != word2 || nb != nb2 {
					same = false
				}
				bo2 += UInt64(nb2)
				return false
			}
			return !same
		}
		return same
	}
}
