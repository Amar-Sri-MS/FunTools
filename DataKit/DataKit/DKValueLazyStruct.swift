//
//  DKValueLazyStruct.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/27/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// A lazy struct value that fetches from a stream
class DKValueLazyStruct: DKValue, DKValueIsEqualToOther {
	let structType: DKTypeStruct
	let data: DKBitStream
	init(type: DKTypeStruct, data: DKBitStream) {
		assert(type.widthInBytes() != nil)
		self.data = data
		structType = type
	}
	override var type: DKType { return structType }
	func isEqualTo(_ rhs: DKValue) -> Bool {
		if let r = rhs as? DKValueLazyStruct {
			if r.type != type { return false }
			let nbits = structType.widthInBits()!
			let addr1 = DKBitAddress(data: data, bitOffset: 0)
			let addr2 = DKBitAddress(data: r.data, bitOffset: 0)
			return addr1.compare(numberOfBits: nbits, other: addr2)
		}
		return false
	}
	func subValueAt(_ i: Int) -> DKValue {
		let subt = structType[i]
		var addr = DKBitAddress(data: data, bitOffset: structType.startOffsetFor(index: i)!)
		return subt.fromAddressAndAdvance(&addr)!
	}
	override var rawValueToJSON: JSON {
		var a = [JSON]()
		forEach { a |= $0.rawValueToJSON }
		return .array(a)
	}
	override func append(to: inout DKMutableBitStream) {
		to.pad(toAlignmentInBits: structType.requiredAlignmentInBits())
		forEach { $0.append(to: &to) }
	}
	func forEach(_ f: (DKValue) -> Void) {
		for i in 0 ..< structType.count {
			f(subValueAt(i))
		}
	}
}
