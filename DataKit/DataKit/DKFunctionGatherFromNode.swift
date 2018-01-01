//
//  DKFunctionGatherFromNode.swift
//  DataKit
//
//  Created by Bertrand Serlet on 9/17/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// Conceptually gathers all the items from a Fifo and produces a (lazy) sequence
class DKFunctionGatherFromNode: DKFunction {
	let fifoIndex: Int
	let valueType: DKType
	let valueTypeShortcut: DKType.Shortcut // derived from signature
	let sugaredDesc: String	// derived
	private init(_ uniquingTable: DKTypeTable, _ fifoIndex: Int, _ valueType: DKType) {
		self.fifoIndex = fifoIndex
		self.valueType = valueType
		valueTypeShortcut = valueType.toTypeShortcut(uniquingTable)
		sugaredDesc = "gatherFromNode(\(fifoIndex), valueType=\(valueType.sugaredDescription(uniquingTable)))"
	}
	convenience init(_ uniquingTable: DKTypeTable, _ node: DKNode) {
		self.init(uniquingTable, node.graphIndex, node.signature.output)
	}
	override var signature: DKTypeSignature {
		return DKTypeSignature(input: DKTypeStruct.void, output: valueType)
	}
	override var functionToJSONDict: [String: JSON] {
		return [
			"gather": .integer(fifoIndex),
			"value_type": valueTypeShortcut.toJSON
		]
	}
	override class func functionFromJSON(_ uniquingTable: DKTypeTable, _ dict: [String: JSON]) -> DKFunctionGatherFromNode! {
		let g = dict["gather"]
		if g == nil || !g!.isInteger { return nil }
		let fifoIndex = g!.integerValue
		let valueType = dict["value_type"]?.toDKType(uniquingTable)
		if valueType == nil { return nil }
		return DKFunctionGatherFromNode(uniquingTable, fifoIndex, valueType!)
	}
	override func evaluate(context: DKEvaluationContext, _ subs: [DKExpression]) -> DKValue {
		assert(subs.count == 0)
		// Needs the FIFO in the evaluation context
		fatalErrorNYI()
	}
	override var isInputGroupable: Bool {
		return true
	}
	override var description: String {
		return sugaredDesc
	}
}

