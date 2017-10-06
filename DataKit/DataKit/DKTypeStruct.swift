//
//  DKTypeStruct.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/22/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

private var theVoid: DKTypeStruct!

class DKTypeStruct: DKType, Cardinality {
	let subs: [DKType]
	let names: [String]!
	let bitOffsets: [UInt64]! // nil => struct has no fixed width
	let packed: Bool
	let alignment: UInt64!
	// If alignmentInBits==nil the only alignment constraints are derived from the subs
	override class var void: DKTypeStruct {
		if theVoid == nil { theVoid = DKTypeStruct() }
		return theVoid
	}
	override convenience init() {
		self.init(subTypes: [], subNames: [])
	}
	init(subTypes: [DKType], subNames: [String]!, packed: Bool = true, alignmentInBits: UInt64! = nil) {
		if subTypes == [] {
			self.subs = []
			self.names = []
			bitOffsets = []
			self.packed = true
			alignment = nil
			return /* void */
		}
		if subNames != nil {
			assert(subTypes.count == subNames.count)
		}
		self.subs = subTypes
		self.names = subNames
		self.packed = packed
		if alignmentInBits != nil {
			assert(alignmentInBits! != 0)
		}
		self.alignment = alignmentInBits
		var bo: [UInt64] = []
		var offset: UInt64 = 0
		for (i, sub) in subTypes.enumerated() {
			// We require a width for the sub types - except the last
			let w = sub.widthInBits()
			if i != subTypes.count-1 {
				if w == nil {
					// bit offsets don't apply
					offset = .max
					break
				}
			}
			// We align the beginning
			offset = sub.forceAlignBitOffset(offset)
			bo |= offset
			if i != subTypes.count-1 {
				offset += w!
			}
			// If we are not packing, start at the next byte
			if !packed {
				offset = ((offset + 7) / 8) * 8
			}

		}
		if offset != .max {
			bitOffsets = bo
		} else {
			bitOffsets = nil
		}
	}
	convenience init(funcParams types: [DKType]) {
		self.init(subTypes: types, subNames: nil, packed: false, alignmentInBits: 32)
	}
	convenience init(funcParamType type: DKType, repeated: Int = 1) {
		let types = [DKType](repeating: type, count: repeated)
		self.init(subTypes: types, subNames: nil, packed: false, alignmentInBits: 32)
	}
	func realignForFuncParams() -> DKTypeStruct {
		if alignment != nil { return self }
		return DKTypeStruct(subTypes: subs, subNames: names, packed: false, alignmentInBits: 32)
	}
	var count: Int { return subs.count }
	subscript(i: Int) -> DKType {
		assert(i < count);
		return subs[i];
	}
	subscript(n: String) -> Int! {
		if names == nil { return nil }
		return names.index(of: n)
	}
	subscript(n: String) -> DKType! {
		let i: Int! = self[n]
		return i == nil ? nil : subs[i!]
	}
	func startOffsetFor(index: Int) -> UInt64! {
		return bitOffsets?[index]
	}
	override func widthInBits() -> UInt64! {
		if bitOffsets == nil { return nil }
		if subs.isEmpty { return 0 }
		let lastWidth = subs.last!.widthInBits()
		if lastWidth == nil { return nil }
		let w = bitOffsets[subs.count-1] + lastWidth!
		if alignment == nil { return w }
		return ((w + alignment! - 1) / alignment!) * alignment!
	}
	override func requiredAlignmentInBits() -> UInt64! {
		return alignment
	}
	override func typeToRawJSON(_ uniquingTable: DKTypeTable) -> JSON {
		if subs.isEmpty {
			return "Void"
		}
		var dict: [String: JSON] = [
			"genre": "struct",
			"subs": subs.typesToShortcutsInJSON(uniquingTable)
		]
		if packed { dict["packed"] = true }
		if alignment != nil { dict["alignment"] = .integer(Int(alignment!)) }
		if names != nil { dict["names"] = .array(names.map { JSON.string($0) }) }
		return .dictionary(dict)
	}
	override class func typeFromJSON(_ uniquingTable: DKTypeTable, _ j: JSON) -> DKType? {
		if j.stringValue == "Void" {
			return .void
		}
		let dict = j.dictionaryValue
		if dict["genre"] != "struct" { return nil }
		let p = dict["packed"]?.boolValue ?? false
		let a = dict["alignment"]?.integerValue
		let align = a == nil || a! < 0 ? nil : UInt64(a!)
		let subs = dict["subs"]?.shortcutsToDKTypes(uniquingTable)
		if subs == nil { return nil }
		let names = dict["names"]?.arrayValue.flatMap { $0.stringValue }
		return DKTypeStruct(subTypes: subs!, subNames: names, packed: p, alignmentInBits: align)
	}
	override func valueFromRawJSON(_ uniquingTable: DKTypeTable, _ j: JSON) -> DKValue? {
		if j.arrayValue.count != subs.count { return nil }
		return DKValueSimple(type: self, json: j)
	}
	override func fromAddressAndAdvance(_ addr: inout DKBitAddress) -> DKValue? {
		addr.forceByteAlignment() // structs are byte-aligned
		var subv = [JSON]()
		for i in 0 ..< count {
			let subt = self[i]
			var v: DKValue! = nil
			if bitOffsets != nil {
				var thisField = addr.addBitOffset(startOffsetFor(index: i)!)
				v = subt.fromAddressAndAdvance(&thisField)!
			} else {
				addr.bitOffset = subt.forceAlignBitOffset(addr.bitOffset)
				v = subt.fromAddressAndAdvance(&addr)
			}
			if v == nil {
				return nil
			}
			subv |= v.rawValueToJSON
		}
		return DKValueSimple(type: self, json: .array(subv))
	}
	override func fromDataLazy(_ data: DKBitStream) -> DKValue? {
		if widthInBytes() == nil {
			// We can't lazily retrieve a struct, since we dont know its size
			return super.fromDataLazy(data)
		}
		return DKValueLazyStruct(type: self, data: data)
	}
	override func sugaredDescription(_ uniquingTable: DKTypeTable) -> String {
		if names != nil {
			return "(" + zip(names!, subs).joinDescriptions(", ") {
				$0.0 + ": " + $0.1.sugaredDescription(uniquingTable)
				} + ")"
		}
		return "(" + subs.joinDescriptions(", ") { $0.sugaredDescription(uniquingTable) } + ")"
	}
}
