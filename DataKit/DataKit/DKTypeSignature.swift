//
//  DKTypeSignature.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/23/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

class DKTypeSignature: DKType {
	let input: DKTypeStruct
	let output: DKType
	init(input: DKTypeStruct, output: DKType) {
		self.input = input
		self.output = output
	}
	var numberOfArguments: Int {
		return input.count
	}
	subscript(argument: Int) -> DKType {
		return input[argument]
	}
	override func typeToRawJSON(_ uniquingTable: DKTypeTable) -> JSON {
		let dict: [String: JSON] = [
			"genre": "signature",
			"input": input.toTypeShortcut(uniquingTable).toJSON,
			"output": output.toTypeShortcut(uniquingTable).toJSON
		]
		return .dictionary(dict)
	}
	override class func typeFromJSON(_ uniquingTable: DKTypeTable, _ j: JSON) -> DKType? {
		let dict = j.dictionaryValue
		if dict["genre"] != "signature" { return nil }
		let i = dict["input"]?.toDKType(uniquingTable) as? DKTypeStruct
		if i == nil { return nil }
		let oj = dict["output"]?.toDKType(uniquingTable)
		if oj == nil { return nil }
		return DKTypeSignature(input: i!, output: oj!)
	}
	override func valueFromRawJSON(_ uniquingTable: DKTypeTable, _ j: JSON) -> DKValue? {
		return DKValueFunc.fromRawJSON(uniquingTable, j)
	}
	var isPredicate: Bool {
		return numberOfArguments == 1 && output == DKTypeInt.bool
	}
	var predicateOf: DKType? {
		if !isPredicate { return nil }
		return self[0]
	}
	override func subclassableSugaryDescription(_ uniquingTable: DKTypeTable) -> String {
		return input.subclassableSugaryDescription(uniquingTable) + " -> " + output.sugaredDescription(uniquingTable)
	}

}
