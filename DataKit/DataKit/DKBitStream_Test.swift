//
//  DKBitStream_Test.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/29/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

import Foundation

extension DKBitAddress {

	static func selfTest() {
		var data = Data()
		for i in 0 ..< 255 {
			data.append(UInt8(i))
		}
		var addr = DKBitAddress(data: data, bitOffset: 0)
		assert(addr.fetchByte() == 0)
		assert(addr.fetchByte() == 1)
		assert(addr.fetchUpTo64Bits(8) == 2)
		assert(addr.fetchUpTo64Bits(4) == 3)
		assert(addr.fetchUpTo64Bits(4) == 0)
		assert(addr.fetchByte() == 4)
		assert(addr.fetchUpTo64Bits(8) == 5)
		assert(addr.bitOffset == 6 * 8)
	}

}
