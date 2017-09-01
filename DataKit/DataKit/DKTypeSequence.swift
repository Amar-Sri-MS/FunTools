//
//  DKTypeSequence.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/25/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

class DKTypeSequence: DKType {
	let sub: DKType
	init(subType: DKType) {
		self.sub = subType
	}
	override func typeToRawJSON(_ uniquingTable: DKTypeTable) -> JSON {
		let dict: [String: JSON] = [
			"genre": "sequence",
			"sub": sub.toTypeShortcut(uniquingTable).toJSON
		]
		return .dictionary(dict)
	}
	override class func typeFromJSON(_ uniquingTable: DKTypeTable, _ j: JSON) -> DKType? {
		let dict = j.dictionaryValue
		if dict["genre"] != "sequence" { return nil }
		let st = dict["sub"]?.toDKType(uniquingTable)
		if st == nil { return nil }
		return DKTypeSequence(subType: st!)
	}
	override func valueFromRawJSON(_ uniquingTable: DKTypeTable, _ j: JSON) -> DKValue? {
		return DKValueSimple(type: self, json: j)
	}
	override func fromAddressAndAdvance(_ addr: inout DKBitAddress) -> DKValue? {
		var subj: [JSON] = []
		while true {
			let subv = sub.fromAddressAndAdvance(&addr)
			if subv == nil { break }
			// TODO: it seems the alignment should be done at the start of the inner loop, not at the end
			addr.bitOffset = sub.forceAlignBitOffset(addr.bitOffset)
			subj |= subv!.rawValueToJSON
		}
		return DKValueSimple(type: self, json: .array(subj))
	}
	override func fromDataLazy(_ data: DKBitStream) -> DKValue? {
		return DKValueLazySequence(itemType: sub, data: data)
	}
}
