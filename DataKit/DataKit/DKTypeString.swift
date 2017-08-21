//
//  DKTypeString.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/23/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

private var theString: DKTypeString!

class DKTypeString: DKType {
	class var string: DKTypeString {
		if theString == nil { theString = DKTypeString() }
		return theString
	}
	override func typeToRawJSON(_ uniquingTable: DKTypeTable) -> JSON {
		return "String"
	}
	override class func typeFromJSON(_ uniquingTable: DKTypeTable, _ j: JSON) -> DKType? {
		if j.stringValue == "String" {
			return DKTypeString.string
		}
		return nil
	}
	override func valueFromRawJSON(_ uniquingTable: DKTypeTable, _ j: JSON) -> DKValue? {
		return DKValueSimple(j.stringValue)
	}
	override func fromAddressAndAdvance(_ addr: inout DKBitAddress) -> DKValue? {
		let str = addr.fetchZeroTerminatedString()
		if str == nil { return nil }
		return DKValueSimple(str!)
	}
	// We define a lazy way to fetch a string
	override func fromDataLazy(_ data: DKBitStream) -> DKValue? {
		return DKValueLazy(type: self, data: data) {
			return self.fromAddressAndAdvance(&$1)!
		}
	}
}
