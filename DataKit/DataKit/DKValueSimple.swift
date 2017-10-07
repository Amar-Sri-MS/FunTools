//
//  DKValueSimple.swift
//  DataKit
//
//  Created by Bertrand Serlet on 8/11/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// A simple value that uses JSON for storage

class DKValueSimple: DKValue, DKValueIsEqualToOther {
	// Simple atomic values are representated by their natural json
	// Explicit Structs are represented as an array of values
	// Explicit Sequences are also represented as an array of values
	let json: JSON
	let actualType: DKType

	// ===============  CREATION ===============

	init(type: DKType, json: JSON) {
		self.json = json
		self.actualType = type
	}
	convenience init(type: DKType, value: UInt64) {
		let i: Int = Int(Int64(bitPattern:value))
		assert(type.canAcceptIntValue(i))
		self.init(type: type, json: .integer(i))
	}
	convenience init(type: DKType, value: Int64) {
		let i: Int = Int(value)
		assert(type.canAcceptIntValue(i))
		self.init(type: type, json: .integer(i))
	}
	convenience init(type: DKType, value: Int) {
		assert(type.canAcceptIntValue(value))
		self.init(type: type, json: .integer(value))
	}
	convenience init(_ b: Bool) {
		self.init(type: .bool, value: b ? 1 : 0)
	}
	convenience init(_ b: UInt8) {
		self.init(type: DKTypeInt.uint8, value: UInt64(b))
	}
	convenience init(_ w: UInt64) {
		self.init(type: DKTypeInt.uint64, value: w)
	}
	convenience init(_ s: String) {
		self.init(type: .string, json: .string(s))
	}

	// ===============  BASIC PROTOCOLS ===============

	override var type: DKType { return actualType }

	func isEqualTo(_ rhs: DKValue) -> Bool {
		if let r = rhs as? DKValueSimple {
			if actualType != r.actualType { return false }
			return r.json == json
		}
		return false
	}

	override var description: String {
		if type is DKTypeStruct {
			return "(" + json.arrayValue.joinDescriptions(", ") + ")"
		}
		if  type is DKTypeSequence {
			return "[" + json.arrayValue.joinDescriptions(", ") + "]"
		}
		if json.isArray || json.isDictionary {
			return super.description
		}
		// Go with the typeless, simple form
		return json.description
	}

	// ===============  SERIALIZATION ===============

	override var rawValueToJSON: JSON {
		return json
	}
	override func append(to: inout DKMutableBitStream) {
		to.pad(toAlignmentInBits: type.requiredAlignmentInBits())
		if actualType is DKTypeInt {
			let numBits = type.widthInBits()!
			to.appendBits(numBits: UInt64(numBits)) { self.uint64Value }
		} else if actualType is DKTypeString {
			to.appendString(stringValue)
		} else if actualType is DKTypeStruct {
			forEach {
				$0.append(to: &to)
			}
		} else if actualType is DKTypeSequence {
			forEach {
				$0.append(to: &to)
			}
		} else {
			abort()
		}
	}

	// ===============  LAZY ENUMERATION ===============

	// Only applies to structs and sequences
	func forEach(_ f: (DKValue) -> Void) {
		if let structType = actualType as? DKTypeStruct {
			let c = structType.count
			assert(json.arrayValue.count == c)
			for i in 0 ..< c {
				let v = json.arrayValue[i]
				f(DKValueSimple(type: structType[i], json: v))
			}
		} else if let sequenceType = actualType as? DKTypeSequence {
			let itemType = sequenceType.sub
			for subj in json.arrayValue {
				f(DKValueSimple(type: itemType, json: subj))
			}
		} else {
			abort()
		}
	}
}
