//
//  DKDataLayout.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/25/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// A layout provides an abstract way to get to bits and bytes
// In its simplest form it encapsulates a pointer to bytes and length, and it can answer the questions are there N bytes for me, or it can give the pointer to use for these bytes
// But it can also provide bytes dynamically using a stream formalism
// And it can function at the bit-level.

///////UNUSED

protocol DataLayout {
	func numberOfBytesImmediatelyAvailable() -> UInt64

	// Whether it is possible to ask for more bytes with provideAdditionalBytes
	// You may or may not get them though...
	func canProvideAdditionalBytes() -> Bool

	// Get additional bytes.  Returns true if was able to do so
	func provideAdditionalBytes() -> Bool

	// Fetch aka load
	// TODO: Avoid copying...
	func fetchBytes(_ numBytes: UInt64) -> [UInt8]
}

protocol DataLayoutBit {
	func numberOfBitsImmediatelyAvailable() -> UInt64
	func canProvideAdditionalBits() -> Bool
	func provideAdditionalBits() -> Bool
	func fetchBits(_ numBits: UInt64) -> (words: [UInt64], residue: UInt64, numBitsInResidue: UInt8)
}

extension DataLayoutBit {
	func numberOfBytesImmediatelyAvailable() -> UInt64 {
		let nbits = numberOfBitsImmediatelyAvailable()
		return nbits >> 3
	}
	func canProvideAdditionalBytes() -> Bool {
		return canProvideAdditionalBits()
	}
	func provideAdditionalBytes() -> Bool {
		return provideAdditionalBits()
	}
	func fetchBytes(_ numBytes: UInt64) -> [UInt8] {
		// TODO: For now we copy - need to do better...
		let bitsWanted = numBytes << 3
		var (words, residue, numBitsInResidue) = fetchBits(bitsWanted)
		var bytes: [UInt8] = []
		for var word in words {
			if UInt64(bytes.count) >= numBytes { break }
			for _ in 0 ..< min(UInt64(8), numBytes - UInt64(bytes.count)) {
				bytes |= UInt8(word & 0xff)
				word >>= 8
			}
		}
		while numBitsInResidue >= 8 && UInt64(bytes.count) < numBytes {
			bytes |= UInt8(residue & 0xff)
			residue >>= 9
			numBitsInResidue -= 8
		}
		return bytes
	}
}


