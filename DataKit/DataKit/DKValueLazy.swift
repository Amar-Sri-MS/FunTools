//
//  DKValueLazy.swift
//  DataKit
//
//  Created by Bertrand Serlet on 8/11/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

class DKValueLazy: DKValue, DKValueIsEqualToOther {
	let data: DKBitStream
	let actualType: DKType
	let fetcher: (DKType, inout DKBitAddress) -> DKValue
	var actualEvaluated: DKValue!	// lazily evaluated
	init(type: DKType, data: DKBitStream, fetcher: @escaping (DKType, inout DKBitAddress) -> DKValue) {
		self.data = data
		self.actualType = type
		self.fetcher = fetcher
	}

	var evaluated: DKValue {
		if actualEvaluated != nil { return actualEvaluated! }
		var addr = DKBitAddress(data: data, bitOffset: 0)
		actualEvaluated = fetcher(actualType, &addr)
		assert(actualEvaluated!.type == type)
		return actualEvaluated!
	}

	// ===============  BASIC PROTOCOLS ===============

	override var type: DKType { return actualType }
	func isEqualTo(_ rhs: DKValue) -> Bool {
		return rhs == evaluated
	}

	// ===============  SERIALIZATION ===============

	override func append(to: inout DKMutableBitStream) {
		evaluated.append(to: &to)
	}
	override var rawValueToJSON: JSON {
		return evaluated.rawValueToJSON
	}
}
