//
//  DKType.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/21/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// Denotes a type for arbitrary data
// Immutable

class DKType: Equatable, Hashable, CustomStringConvertible {
	typealias Shortcut = String

	static func ==(lhs: DKType, rhs: DKType) -> Bool {
		// Default: pointer equality
		// We do a sub-type method call 
		if lhs === rhs { return true }
		return lhs.description == rhs.description
	}

	var hashValue: Int {
		return description.hashValue
	}
	
	var description: String {
		let uniquingTable = DKTypeTable()
		return typeToRawJSON(uniquingTable).description
	}
	func sugaredDescription(_ knowns: [DKType: String]) -> String {
		let k = knowns[self]
		if k != nil { return k! }
		let uniquingTable = DKTypeTable()
		let j = typeToRawJSON(uniquingTable)
		if j.isString { return j.stringValue }
		return j.description
	}

	// ===============  SERIALIZATION ===============

	// Adds type to uniquing context, returns shortcut string
	final func toTypeShortcut(_ uniquingTable: DKTypeTable) -> Shortcut {
		let rawJSON = typeToRawJSON(uniquingTable)
		if rawJSON.isString {
			return rawJSON.stringValue
		}
		let typeCode = "T_" + rawJSON.description.toSHA256().word2.toHexString(true) // word 2 is as good as any; we only use 64b of a SHA2 as risk of colliding is low
		uniquingTable[typeCode] = rawJSON
		return typeCode
	}
	// Converts the type to JSON
	func typeToRawJSON(_ uniquingTable: DKTypeTable) -> JSON {
		fatalErrorMustBeImplementedBySubclass()
	}
	class func typeFromJSON(_ uniquingTable: DKTypeTable, _ j: JSON) -> DKType? {
		fatalErrorMustBeImplementedBySubclass()
	}

	// ===============  LAYOUT ===============

	// width in number of bits
	// a nil return means undefined, or variable sized
	func widthInBits() -> UInt64! {
		return nil
	}
	// alignment, in bits
	// a nil return means no requirement, or N/A
	func requiredAlignmentInBits() -> UInt64! {
		return nil
	}

	// ===============  VALUE HANDLING ===============

	// Whether an int is acceptable for a value of this type
	func canAcceptIntValue(_ value: Int) -> Bool {
		return false
	}

	// Creates the value
	func valueFromRawJSON(_ uniquingTable: DKTypeTable, _ j: JSON) -> DKValue? {
		fatalErrorMustBeImplementedBySubclass()
	}
	// Fetch a value from a bit address
	// Explicit retrieval; the bitOffset is advanced by callee
	func fromAddressAndAdvance(_: inout DKBitAddress) -> DKValue? {
		return nil
	}
	// Lazy retrieval - by default do the non-lazy retrieval
	func fromDataLazy(_ data: DKBitStream) -> DKValue? {
		var addr = DKBitAddress(data: data, bitOffset: 0)
		return fromAddressAndAdvance(&addr)
	}
}

// ===============  LAYOUT EXTRAS ===============

extension DKType {
	func widthInBytes() -> UInt64! {
		let b = widthInBits()
		return b == nil ? b : (b! + 7) / 8
	}
	func forceAlignBitOffset(_ bitOffset: UInt64) -> UInt64 {
		let align = requiredAlignmentInBits()
		if align == nil { return bitOffset }
		assert(align! != 0)
		return ((bitOffset + align! - 1) / align!) * align!
	}
}

// ===============  JSON EXTRAS ===============

extension DKType.Shortcut {
	var toJSON: JSON {
		return .string(self)
	}
}

extension JSON {
	// A JSON string to a type
	func toDKType(_ uniquingTable: DKTypeTable) -> DKType? {
		assert(isString)
		let code: DKType.Shortcut = stringValue
		var raw = uniquingTable[code]
		if raw == nil && code.hasPrefix("T_") { return nil }
		if raw == nil { raw = self }
		// TODO: Need to avoid this...
		for f in [DKTypeInt.typeFromJSON, DKTypeStruct.typeFromJSON, DKTypeArray.typeFromJSON, DKTypeSignature.typeFromJSON] {
			let t = f(uniquingTable, raw!)
			if t != nil { return t }
		}
		return nil
	}
}

extension Sequence where Self.Iterator.Element: DKType {
	func typesToShortcuts(_ uniquingTable: DKTypeTable) -> [DKType.Shortcut] {
		return map { $0.toTypeShortcut(uniquingTable) }
	}
	func typesToShortcutsInJSON(_ uniquingTable: DKTypeTable) -> JSON {
		return .array(typesToShortcuts(uniquingTable).map { $0.toJSON })
	}
}

extension JSON {
	func shortcutsToDKTypes(_ uniquingTable: DKTypeTable) -> [DKType]? {
		if !isArray { return nil }
		var types: [DKType] = []
		for x in arrayValue {
			let t = x.toDKType(uniquingTable)
			if t == nil { return nil }
			types |= t!
		}
		return types
	}
}

