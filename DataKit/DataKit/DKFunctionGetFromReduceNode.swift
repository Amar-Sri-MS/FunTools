//
//  DKFunctionGetFromReduceNode.swift
//  DataKit
//
//  Created by Bertrand Serlet on 9/17/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// Conceptually gathers all the items from a Fifo and produces a (lazy) sequence
class DKFunctionGetFromReduceNode: DKFunction {
	let fifoIndex: Int
	let valueType: DKType
	let typeShortcut: DKType.Shortcut // derived from signature
	let sugaredDesc: String	// derived
	init(_ uniquingTable: DKTypeTable, _ fifoIndex: Int, _ valueType: DKType) {
		typeShortcut = valueType.toTypeShortcut(uniquingTable)
		self.fifoIndex = fifoIndex
		self.valueType = valueType
		sugaredDesc = "getFromReduceNode(\(fifoIndex), \(valueType.sugaredDescription(uniquingTable)))"
	}
	override var signature: DKTypeSignature {
		return DKTypeSignature(input: DKTypeStruct.void, output: valueType)
	}
	override var functionToJSONDict: [String: JSON] {
		return [
			"get_from_reduce_node": .integer(fifoIndex),
			"value_type": typeShortcut.toJSON
		]
	}
	override class func functionFromJSON(_ uniquingTable: DKTypeTable, _ dict: [String: JSON]) -> DKFunctionGetFromReduceNode! {
		let g = dict["get_from_reduce_node"]
		if g == nil || !g!.isInteger { return nil }
		let fifoIndex = g!.integerValue
		let valueType = dict["value_type"]?.toDKType(uniquingTable)
		if valueType == nil { return nil }
		return DKFunctionGetFromReduceNode(uniquingTable, fifoIndex, valueType!)
	}
	override func evaluate(context: DKEvaluationContext, _ subs: [DKExpression]) -> DKValue {
		assert(subs.count == 0)
		// Needs the FIFO in the evaluation context
		fatalErrorNYI()
	}
	override var description: String {
		return sugaredDesc
	}
}

