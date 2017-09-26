//
//  DKDataStream.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/25/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

import Foundation

protocol DKBitStream {
	// Given the number of bits wanted, and where to start, fetches words of data
	// eachWord is called (numBitsWanted + 63)/64 times, with each word and the number of bits, and in order
	// If the stream is lazily fed, fetches more bits as needed
	// If the stream cannot provide all the bits wanted, false is returned
	// Callback can return true to mean stop, in which case fetchBits() will always return true
	func fetchBits(numBitsWanted: UInt64, bitOffset: UInt64, eachWord: (UInt64, UInt8) -> Bool) -> Bool
}

extension DKBitStream {
	// Advances bitOffset
	// Always starts by doing a byte-alignemnt
	// Return whether all the bytes requested have been provided
	fileprivate func fetchBytes(numBytesWanted: UInt64, bitOffset: inout UInt64, eachByte: (UInt8) -> Void) -> Bool {
		var bo = bitOffset
		// byte-align
		if bo & 7 != 0 { bo += 8 - (bo & 7) }
		let ok = fetchBits(numBitsWanted: numBytesWanted * 8, bitOffset: bo) {
			var w = $0
			for _ in 0 ..< (($1 + 7)/8) {
				eachByte(UInt8(w & 0xff))
				w >>= 8
			}
			return false
		}
		if ok {
			bitOffset = bo + numBytesWanted * 8
		}
		return ok
	}
	func fetchUpTo64Bits(numBitsWanted: UInt8, bitOffset: inout UInt64) -> UInt64? {
		assert(numBitsWanted <= 64)
		var word: UInt64 = 0
		let ok = fetchBits(numBitsWanted: UInt64(numBitsWanted), bitOffset: bitOffset) { w, b in
			word = w
			return false
		}
		if ok {
			bitOffset += UInt64(numBitsWanted)
			return word
		} else {
			return nil
		}
	}
	func fetchByte(bitOffset: inout UInt64) -> UInt8? {
		let word = fetchUpTo64Bits(numBitsWanted: 8, bitOffset: &bitOffset)
		return word == nil ? nil : UInt8(word!)
	}
	fileprivate func fetchData(numBytesWanted: UInt64, bitOffset: inout UInt64) -> Data? {
		var data = Data()
		let ok = fetchBytes(numBytesWanted: numBytesWanted, bitOffset: &bitOffset) {
			data.append($0)
		}
		return ok ? data : nil
	}
	func fetchZeroTerminatedString(bitOffset: inout UInt64, okToEndWithoutZero: Bool = false) -> String? {
		var str = ""
		while true {
			let byte = fetchByte(bitOffset: &bitOffset)
			if byte == nil && !okToEndWithoutZero { return nil }
			if byte == nil || byte! == 0 { break }
			str += String(byte!)
		}
		return str
	}
}

extension Data: DKBitStream {
	func fetchBits(numBitsWanted: UInt64, bitOffset: UInt64, eachWord: (UInt64, UInt8) -> Bool) -> Bool {
		var bitsStillWanted = numBitsWanted
		var word: UInt64 = 0 // the word we are gathering
		var wordBitOffset: UInt64 = 0 // offset in the word we are gathering
		var bo = bitOffset // the input bit offset as it evolves
		var byteOffset: Int { return Int(bo >> 3) }
		while byteOffset < count {
			let maxBits: UInt64 = Swift.min(8 - UInt64(bo & 7), bitsStillWanted, 64 - wordBitOffset)
			let byte = self[byteOffset]
			word |= ((UInt64(byte) >> (bo & 7)) & ((1 << maxBits) - 1)) << wordBitOffset
			bo += UInt64(maxBits)
			wordBitOffset += maxBits
			assert(wordBitOffset <= 64)
			if wordBitOffset == 64 {
				wordBitOffset = 0
				let stop = eachWord(word, 64)
				if stop { return true }
				word = 0
			}
			bitsStillWanted -= UInt64(maxBits)
			if bitsStillWanted == 0 {
				_ = eachWord(word, UInt8(wordBitOffset))
				return true
			}
		}
		if wordBitOffset != 0 {
			let stop = eachWord(word, UInt8(wordBitOffset))
			if stop { return true }
		}
		return bitsStillWanted == 0
	}
}

