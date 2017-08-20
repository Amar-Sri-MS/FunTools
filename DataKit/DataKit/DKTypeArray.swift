//
//  DKTypeArray.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/22/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

class DKTypeArray: DKTypeSequence {
	let numItems: UInt64!	// nil if array has variable size
	let packed: Bool
	let alignment: UInt64!
	// If alignmentInBits==nil the only alignment constraint is derived from the sub
	init(subType: DKType, numItems: UInt64! = nil, packed: Bool = true, alignmentInBits: UInt64! = nil) {
		self.numItems = numItems
		self.packed = packed
		if alignmentInBits != nil {
			assert(alignmentInBits! != 0)
		}
		self.alignment = alignmentInBits
		let w = subType.widthInBits()
		assert(w != nil)	// or else we dont know how to layout this type
		super.init(subType: subType)
	}
	var actualNumberOfBitsOfEach: UInt64 {
		var w = sub.widthInBits()!
		let a = sub.requiredAlignmentInBits()
		if a != nil && ((w % a!) != 0) {
			// for example w=48b and a=32b
			w = ((w / a!) + 1) * a!
		}
		// If we dont pack, we go to the next byte
		if !packed { w = ((w + 7) / 8) * 8 }
		return w
	}
	func startOffsetForElement(index: Int) -> UInt64! {
		return UInt64(index) * UInt64(actualNumberOfBitsOfEach)
	}
	override func widthInBits() -> UInt64! {
		if numItems == nil { return nil }
		let ww = numItems * actualNumberOfBitsOfEach
		if alignment == nil { return ww }
		return ((ww + alignment! - 1) / alignment!) * alignment!
	}
	override func requiredAlignmentInBits() -> UInt64! {
		return alignment
	}
	func isEqualToArray(_ r: DKTypeArray) -> Bool {
		if sub != r.sub { return false }
		if numItems == nil && r.numItems != nil { return false }
		if numItems != nil && r.numItems == nil { return false }
		if numItems != nil && r.numItems != nil && numItems! != r.numItems! { return false }
		if packed != r.packed { return false }
		if alignment == nil && r.alignment != nil { return false }
		if alignment != nil && r.alignment == nil { return false }
		if alignment != nil && r.alignment != nil && alignment! != r.alignment! { return false }
		return true
	}
	override func typeToRawJSON(_ uniquingTable: DKTypeTable) -> JSON {
		var dict: [String: JSON] = [
			"genre": "array",
			"sub": sub.toTypeShortcut(uniquingTable).toJSON
		]
		if numItems != nil { dict["numItems"] = .integer(Int(numItems)) }
		if packed { dict["packed"] = true }
		if alignment != nil { dict["alignment"] = .integer(Int(alignment!)) }
		return .dictionary(dict)
	}
	class func fromJSONInternal(_ uniquingTable: DKTypeTable, _ j: JSON) -> DKType? {
		let dict = j.dictionaryValue
		if dict["genre"] != "array" { return nil }
		let nn = dict["numItems"]?.integerValue
		let n = nn == nil || nn! < 0 ? nil : UInt64(nn!)
		let p = dict["packed"]?.boolValue ?? false
		let a = dict["alignment"]?.integerValue
		let align = a == nil || a! < 0 ? nil : UInt64(a!)
		let st = dict["sub"]?.toDKType(uniquingTable)
		if st == nil { return nil }
		return DKTypeArray(subType: st!, numItems: n, packed: p, alignmentInBits: align)
	}
	override class func typeFromJSON(_ uniquingTable: DKTypeTable, _ j: JSON) -> DKType? {
		let t = fromJSONInternal(uniquingTable, j)
		return t == nil ? super.typeFromJSON(uniquingTable, j) : t
	}
}
