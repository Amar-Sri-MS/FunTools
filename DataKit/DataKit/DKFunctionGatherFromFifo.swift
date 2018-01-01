//
//  DKFunctionGatherFromFifo.swift
//  DataKit
//
//  Created by Bertrand Serlet on 9/17/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// Conceptually gathers all the items from a Fifo and produces a (lazy) sequence
class DKFunctionGatherFromFifo: DKFunction {
	let fifoIndex: Int
	let valueType: DKType
	let valueTypeShortcut: DKType.Shortcut // derived from signature

	let sugaredDesc: String	// derived
	private init(_ uniquingTable: DKTypeTable, _ fifoIndex: Int, _ valueType: DKType) {
		self.fifoIndex = fifoIndex
		self.valueType = valueType
		valueTypeShortcut = valueType.toTypeShortcut(uniquingTable)
		sugaredDesc = "gatherFromFifo(\(fifoIndex), \(valueType.sugaredDescription(uniquingTable)))"
	}
	init(_ uniquingTable: DKTypeTable, _ node: DKNode) {
		self.fifoIndex = node.graphIndex
		valueType = node.signature.output
		valueTypeShortcut = valueType.toTypeShortcut(uniquingTable)
		sugaredDesc = "gatherFromFifo(\(node.graphIndex), \(valueType.sugaredDescription(uniquingTable)))"
	}
	var sequenceType: DKType {
		assert(valueType is DKTypeSequence)
		return valueType
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
	override class func functionFromJSON(_ uniquingTable: DKTypeTable, _ dict: [String: JSON]) -> DKFunctionGatherFromFifo! {
		let g = dict["gather"]
		if g == nil || !g!.isInteger { return nil }
		let fifoIndex = g!.integerValue
		let valueType = dict["value_type"]?.toDKType(uniquingTable)
		if valueType == nil { return nil }
		return DKFunctionGatherFromFifo(uniquingTable, fifoIndex, valueType!)
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

