//
//  DKType_Test.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/23/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

extension DKType {

	class func selfTest() {
		// struct { bool, bool, byte }
		let t1 = DKType.bool
		let t2 = DKTypeInt.byte
		let s1 = DKTypeStruct(subTypes: [t1, t1, t2], subNames: nil, packed: true, alignmentInBits: nil)
		print("s1=\(s1)")
		assert(s1.count == 3)
		assert(s1[2] == t2)
		let index: Int! = s1["foo"]
		assert(index == nil)
		let subt: DKType! = s1["foo"]
		assert(subt == nil)
		assert(s1.startOffsetFor(index: 0) == 0)
		assert(s1.startOffsetFor(index: 1) == 1)
		assert(s1.startOffsetFor(index: 2) == 8)
		assert(s1.widthInBits() == 16)
		assert(s1.requiredAlignmentInBits() == nil)

		let s2 = DKTypeStruct(subTypes: [t1, t1, t2], subNames: nil, packed: true, alignmentInBits: 32)
		assert(s2.startOffsetFor(index: 0) == 0)
		assert(s2.startOffsetFor(index: 1) == 1)
		assert(s2.startOffsetFor(index: 2) == 8)
		assert(s2.widthInBits() == 32)
		assert(s2.requiredAlignmentInBits() == 32)

		let s3 = DKTypeStruct(subTypes: [t1, t1, t2], subNames: nil, packed: false, alignmentInBits: nil)
		assert(s3.startOffsetFor(index: 0) == 0)
		assert(s3.startOffsetFor(index: 1) == 8)
		assert(s3.startOffsetFor(index: 2) == 16)
		assert(s3.widthInBits() == 24)
		assert(s3.requiredAlignmentInBits() == nil)

		let s4 = DKTypeStruct(subTypes: [t1, t1, t2], subNames: ["bool1", "bool2", "byte"], packed: false, alignmentInBits: nil)
		assert(s4["bool2"] === t1)
		let index4: Int! = s4["bool2"]
		assert(index4 == 1)
		let subt4: DKType! = s4["bool2"]
		assert(subt4 === t1)

		let genc = DKGenC()
		print("To C:\n\(genc.toC(s4))")
		print("To C:\n    \(genc.toC(s4, level: 1))")
		let uniquingTable = DKTypeTable()
		let json = s4.typeToRawJSON(uniquingTable)
		let shortcut = s4.toTypeShortcut(uniquingTable)
		print("As RAW JSON: \(json) and shortcut=\(shortcut)")
		let json2 = shortcut.toJSON
		let s5 = json2.toDKType(uniquingTable)
		assert(s4 == s5!)

		let arr = DKTypeArray(subType: s4, numItems: 42, packed: true, alignmentInBits: 32)
		print("To C:\n\(genc.toC(arr))")
		print("To C:\n    \(genc.toC(arr, level: 1))")
		let jsonArr = arr.typeToRawJSON(uniquingTable)
		print("As RAW JSON: \(jsonArr)")
		let json3 = arr.toTypeShortcut(uniquingTable).toJSON
		let arr2 = json3.toDKType(uniquingTable)
		assert(arr == arr2)

		let int32 = DKTypeInt.shared(signed: true, numBits: 32)
		assert(DKTypeInt.shared(signed: true, numBits: 32) == int32)
		assert(int32.widthInBits() == 32)
		assert(int32.toTypeShortcut(uniquingTable).toJSON.toDKType(uniquingTable)! == int32)
		assert(int32.canAcceptIntValue(0))
		assert(int32.canAcceptIntValue(1 << 30))
		assert(int32.canAcceptIntValue((1 << 31) - 1))
		assert(!int32.canAcceptIntValue(1 << 31))
		
		print("== Types self-test complete!")
	}

}
