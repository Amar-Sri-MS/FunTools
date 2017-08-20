//
//  DKValueLazySequence.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/28/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

class DKValueLazySequence: DKValue, DKValueIsEqualToOther, Sequence {
	let itemType: DKType
	let data: DKBitStream
	init(itemType: DKType, data: DKBitStream) {
		self.data = data
		self.itemType = itemType
	}
	func makeIterator() -> Iterator {
		return LazyIterator(self)
	}
	override var type: DKType { return DKTypeSequence(subType: itemType) }
	class LazyIterator: Iterator {
		let seq: DKValueLazySequence
		var addr: DKBitAddress
		init(_ seq: DKValueLazySequence) {
			self.seq = seq
			addr = DKBitAddress(data: seq.data, bitOffset: 0)
		}
		override func next() -> DKValue? {
			let v = seq.itemType.fromAddressAndAdvance(&addr)
			addr.bitOffset = seq.itemType.forceAlignBitOffset(addr.bitOffset)
			return v
		}
	}
	func isEqualTo(_ rhs: DKValue) -> Bool {
		if let r = rhs as? DKValueLazySequence {
			if itemType == r.itemType { return true }
			// We do a deep comparison
			if totalCount != r.totalCount { return false }
			return zip(self, r).every { $0.0 == $0.1 }
		}
		return false
	}
	override var rawValueToJSON: JSON {
		let jsubs: [JSON] = map { $0.rawValueToJSON }
		return .array(jsubs)
	}
	var totalCount: Int {
		var c = 0
		for _ in self { c += 1 }
		return c
	}
	class Iterator: IteratorProtocol {
		func next() -> DKValue? {
			fatalErrorMustBeImplementedBySubclass()
		}
	}
	override func append(to: inout DKMutableBitStream) {
		to.pad(toAlignmentInBits: type.requiredAlignmentInBits())
		forEach { $0.append(to: &to) }
	}
}

