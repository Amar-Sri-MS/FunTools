//
//  DKTypeInt.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/23/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

private var all: [DKTypeInt] = []

class DKTypeInt: DKType {
	let signed: Bool
	let algebraic: Bool	// usual integer arithmetic applies
	let numBits: UInt8
	let usualAlign: Bool	// true means power of two, false means no alignment

	// ===============  CREATION ===============

	private init(signed: Bool, algebraic: Bool, numBits: UInt8, usualAlign: Bool) {
		self.signed = signed
		self.algebraic = algebraic
		self.numBits = numBits
		self.usualAlign = usualAlign
	}
	class var uint8: DKTypeInt {
		return .shared(signed: false, numBits: 8)
	}
	class var uint32: DKTypeInt {
		return .shared(signed: false, numBits: 32)
	}
	class var uint64: DKTypeInt {
		return .shared(signed: false, numBits: 64)
	}
	class var int64: DKTypeInt {
		return .shared(signed: true, numBits: 64)
	}
	class func shared(signed: Bool, numBits: UInt8, usualAlign: Bool = true, algebraic: Bool = true) -> DKTypeInt {
		// Do a linear search, simple
		var this = all.first {
			$0.signed == signed && $0.algebraic == algebraic && $0.numBits == numBits && $0.usualAlign == usualAlign}
		if this == nil {
			this = DKTypeInt(signed: signed, algebraic: algebraic, numBits: numBits, usualAlign: usualAlign)
			all |= this!
		}
		return this!
	}
	class var bool: DKTypeInt {
		return DKTypeInt.shared(signed: false, numBits: 1, usualAlign: true, algebraic: false)
	}
	class var byte: DKTypeInt {
		return DKTypeInt.shared(signed: false, numBits: 8, usualAlign: true, algebraic: false)
	}

	// ===============  LAYOUT ===============

	override func widthInBits() -> UInt64! {
		return UInt64(numBits)
	}
	override func requiredAlignmentInBits() -> UInt64! {
		if usualAlign {
			switch numBits {
			case 0: return nil
			case 1: return 1
			case 2...8: return 8
			case 9...16: return 16
			case 17...32: return 32
			default: return 64
			}
		} else {
			return nil
		}
	}

	// ===============  TO JSON ===============

	override func typeToRawJSON(_ uniquingTable: DKTypeTable) -> JSON {
		if numBits == 1 && !algebraic && !signed && usualAlign { return "Bool" }
		if usualAlign && algebraic {
			return .string((signed ? "Int" : "UInt") + numBits.description)
		} else {
			let dict: [String: JSON] = [
				"genre": "int",
				"signed": .bool(signed),
				"algebraic": .bool(algebraic),
				"usual_align": .bool(usualAlign),
				"num_bits": .integer(Int(numBits))
			]
			return .dictionary(dict)
		}
	}
	override class func typeFromJSON(_ uniquingTable: DKTypeTable, _ j: JSON) -> DKType? {
		if j.isDictionary {
			let dict = j.dictionaryValue
			if dict["genre"] != "int" { return nil }
			let signed = dict["signed"]?.boolValue
			if signed == nil { return nil }
			let algebraic = dict["algebraic"]?.boolValue
			if algebraic == nil { return nil }
			let usualAlign = dict["usual_align"]?.boolValue
			if usualAlign == nil { return nil }
			let numBits = dict["num_bits"]?.integerValue
			if numBits == nil { return nil }
			return shared(signed: signed!, numBits: UInt8(numBits!), usualAlign: usualAlign!, algebraic: algebraic!)
		}
		let s = j.stringValue
		if s == "Bool" {
			return DKTypeInt.bool
		}
		if s.hasPrefix("Int") {
			let n = UInt8(s.substringAfter(3))
			if n != nil { return DKTypeInt.shared(signed: true, numBits: n!) }
		} else if s.hasPrefix("UInt") {
			let n = UInt8(s.substringAfter(4))
			if n != nil { return DKTypeInt.shared(signed: false, numBits: n!) }
		}
		return nil
	}

	// ===============  VALUE HANDLING ===============

	override func valueFromRawJSON(_ uniquingTable: DKTypeTable, _ j: JSON) -> DKValue? {
		return DKValueSimple(type: self, json: j)
	}
	override func canAcceptIntValue(_ value: Int) -> Bool {
		if numBits == 0 { return false }
		if value == 0 { return true }
		if numBits >= 64 { return true }
		let value64 = value > 0 ? UInt64(value) : UInt64(-value - 1)
		if numBits == 64 { return !signed || (value64 < (UInt64(1) << 63)) }
		let nb = signed ? numBits - 1 : numBits
		return value64 < (UInt64(1) << nb)
	}
	override func fromAddressAndAdvance(_ addr: inout DKBitAddress) -> DKValue? {
		let word = addr.fetchUpTo64Bits(numBits)
		return word != nil ? DKValueSimple(type: self, value: word!) : nil
	}
}
