//
//  DKFunctionProjection.swift
//  DataKit
//
//  Created by Bertrand Serlet on 8/22/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

class DKFunctionProjection: DKFunction {
	let structType: DKTypeStruct
	let fieldIndex: Int
	let domainShortcut: DKType.Shortcut
	init(structType: DKTypeStruct, fieldIndex: Int, _ uniquingTable: DKTypeTable) {
		assert(fieldIndex < structType.count)
		self.structType = structType
		self.fieldIndex = fieldIndex
		domainShortcut = structType.toTypeShortcut(uniquingTable)
	}
	convenience init(structType: DKTypeStruct, fieldName: String, _ uniquingTable: DKTypeTable) {
		let i: Int? = structType[fieldName]
		assert(i != nil)
		self.init(structType: structType, fieldIndex: i!, uniquingTable)
	}
	override func isEqualTo(_ rhs: DKFunction) -> Bool {
		if let r = rhs as? DKFunctionProjection {
			return structType == r.structType && fieldIndex == r.fieldIndex
		}
		return false
	}
	override var signature: DKTypeSignature {
		let input = DKTypeStruct(funcParamType: structType, repeated: 1)
		return DKTypeSignature(input: input, output: structType[fieldIndex])
	}
	override var evaluator: DKNAryEvaluator {
		return {  context, subs in
			assert(subs.count == 1)
			let x = subs[0].evaluate(context: context)
			if let s = x as? DKValueLazyStruct {
				return s.subValueAt(self.fieldIndex)
			}
			if let structType = x.type as? DKTypeStruct {
				let j = x.rawValueToJSON.arrayValue
				return DKValueSimple(type: structType[self.fieldIndex], json: j[self.fieldIndex])
			}
			fatalError("*** Expecting a struct \(self.structType) instead got value \(x)")
		}
	}
	override var functionToJSON: [String: JSON] {
		return [
			"projection": .integer(fieldIndex),
			"domain": domainShortcut.toJSON
		]
	}
	override class func functionFromJSON(_ uniquingTable: DKTypeTable, _ dict: [String: JSON]) -> DKFunction! {
		let p = dict["projection"]
		if p == nil || !p!.isInteger { return nil }
		let t = dict["domain"]?.toDKType(uniquingTable) as? DKTypeStruct
		if t == nil { return nil }
		return DKFunctionProjection(structType: t!, fieldIndex: p!.integerValue, uniquingTable)
	}
	var projectedFieldName: String {
		return structType.names == nil ? fieldIndex.description : structType.names![fieldIndex]
	}
	override func sugaredDescription(_ knowns: [DKType: String]) -> String {
		return "{ $0.\(projectedFieldName) }"
	}
}
