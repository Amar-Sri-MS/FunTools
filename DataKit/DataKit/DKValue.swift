//
//  DKValue.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/27/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

protocol DKValueIsEqualToOther {
	func isEqualTo(_ rhs: DKValue) -> Bool
}

class DKValue: Equatable, CustomStringConvertible {
	var type: DKType {
		fatalErrorMustBeImplementedBySubclass()
	}
	// Encodes the value stripped of its type
	// This does not take a uniquing type table - and should not
	var rawValueToJSON: JSON {
		fatalErrorMustBeImplementedBySubclass()
	}
	func append(to: inout DKMutableBitStream) {
		fatalErrorMustBeImplementedBySubclass()
	}

	// ===============  CREATION ===============

	class func bool(_ b: Bool) -> DKValue {
		return DKValueSimple(b)
	}
	class func int(type: DKTypeInt, intValue v: Int) -> DKValue {
		return DKValueSimple(type: type, value: v)
	}
	class func string(_ s: String) -> DKValue {
		return DKValueSimple(s)
	}
	class var null: DKValue {
		return DKValueSimple(type: .void, json: .null)
	}

	// ===============  ACCESS CONVENIENCES ===============

	// These should be in an extension, but extensions can't be overridden yet
	var boolValue: Bool {
		return rawValueToJSON.boolValue
	}
	var intValue: Int {
		return rawValueToJSON.integerValue
	}
	var uint64Value: UInt64 {
		let i = rawValueToJSON.integerValue
		return UInt64(bitPattern: Int64(i))
	}
	var stringValue: String {
		return rawValueToJSON.stringValue
	}

	// ===============  BASIC PROTOCOLS ===============

	static func ==(lhs: DKValue, rhs: DKValue) -> Bool {
		if let l = lhs as? DKValueIsEqualToOther {
			return l.isEqualTo(rhs)
		}
		return lhs === rhs
	}

	var description: String {
		let uniquingTable = DKTypeTable()
		return valueToJSON(uniquingTable).description
	}
	func sugaredDescription(_ knowns: [DKType: String]) -> String {
		return description
	}
	func dumpDescription(indent: Int = 0) {
		let spaces = String(repeating: "    ", count: indent);
		print(spaces + description)
	}

	// ===============  SERIALIZATION ===============

	// Encode value (including type) as JSON
	final func valueToJSON(_ uniquingTable: DKTypeTable) -> JSON {
		let dict: [String: JSON] = [
			"type": type.toTypeShortcut(uniquingTable).toJSON,
			"value": rawValueToJSON
		]
		return .dictionary(dict)
	}

}

// ===============  MISC ===============

extension JSON {
	func toDKValue(_ uniquingTable: DKTypeTable) -> DKValue? {
		if !isDictionary { return nil }
		let tj = dictionaryValue["type"]?.toDKType(uniquingTable)
		let vj = dictionaryValue["value"]
		if vj == nil { return nil }
		return tj?.valueFromRawJSON(uniquingTable, vj!)
	}
}
