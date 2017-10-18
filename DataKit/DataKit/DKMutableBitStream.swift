//
//  DKMutableBitStream.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/29/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

import Foundation

protocol DKMutableBitStream {
	mutating func appendBits(numBits: UInt64, produceWord: () -> UInt64)
	var bitCount: UInt64 { get }
	mutating func finishAndData() -> Data
}

extension DKMutableBitStream {
	mutating func append(_ b: UInt8) {
		let word = UInt64(b)
		appendBits(numBits: 8) { word }
	}
	mutating func append(_ u: UInt32) {
		let word = UInt64(u)
		appendBits(numBits: 32) { word }
	}
	mutating func append(_ u: UInt64) {
		appendBits(numBits: 64) { u }
	}
	mutating func appendString(_ s: String) {
		s.withCString {
			let len = Int(strlen($0))
			for i in 0 ..< len + 1 {
				let b: UInt8 = UInt8($0[i])
				append(b)
			}
		}
	}
	mutating func pad(toByteAlign m: Int) {
		pad(toAlignmentInBits: UInt64(m * 8))
	}
	mutating func pad(toAlignmentInBits a: UInt64!) {
		if a != nil {
			assert(a! != 0)
			let r = bitCount % a!
			if r != 0 {
				appendBits(numBits: a! - r) { 0 }
			}
		}
	}
}

extension Data {
	mutating func appendString(_ string: String) {
		string.withCString {
			let len = Int(strlen($0))
			for i in 0 ..< len + 1 {
				let b: UInt8 = UInt8($0[i])
				append(b)
			}
		}
	}
	// Pad to a multiple of m (e.g. m==4 for 32-bit alignment)
	mutating func pad(toByteAlign m: Int) {
		assert(m > 0)
		let r = count % m
		if r != 0 {
			for _ in 0 ..< (m - r) { append(UInt8(0)) }
		}
	}
}

struct DataAsMutableBitStream: DKMutableBitStream {
	var isClosed = false
	var pendedWord: UInt64 = 0
	var numPendedBits: UInt64 = 0
	var data: Data = Data()
	var bitCount: UInt64 {
		return UInt64(data.count * 8) + numPendedBits
	}
	mutating func appendBits(numBits: UInt64, produceWord: () -> UInt64) {
		assert(!isClosed)
		var nb = numBits // numbits left
		while nb != 0 {
			let word = produceWord()
			var nbAvail = min(nb, 64)
			nb -= nbAvail
			if nbAvail + numPendedBits > 64 {
				pendedWord |= word << numPendedBits
				data.append(pendedWord)
				pendedWord = 0
				nbAvail -= 64 - numPendedBits
				numPendedBits = 0
			}
			if nbAvail != 0 {
				pendedWord |= word << numPendedBits
				numPendedBits += nbAvail
				if numPendedBits == 64 {
					data.append(pendedWord)
					pendedWord = 0
					numPendedBits = 0
				}
			}
			assert(numPendedBits < 64)
		}
	}
	mutating func pushPending() {
		assert(!isClosed)
		while numPendedBits != 0 {
			let byte = UInt8(pendedWord & 0xff)
			data.append(byte)
			numPendedBits -= numPendedBits >= 8 ? 8 : numPendedBits
			pendedWord >>= 8
		}
	}
	mutating func finishAndData() -> Data {
		pushPending()
		isClosed = true
		return Data(data)
	}
}
