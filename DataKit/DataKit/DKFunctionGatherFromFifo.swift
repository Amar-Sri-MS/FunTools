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
	let itemType: DKType
	let itemTypeShortcut: DKType.Shortcut // derived from signature
	let sugaredDesc: String	// derived
	private init(_ uniquingTable: DKTypeTable, _ fifoIndex: Int, _ itemType: DKType) {
		itemTypeShortcut = itemType.toTypeShortcut(uniquingTable)
		self.fifoIndex = fifoIndex
		self.itemType = itemType
		sugaredDesc = "gatherFromFifo(\(fifoIndex), \(itemType.sugaredDescription(uniquingTable)))"
	}
	init(_ uniquingTable: DKTypeTable, _ node: DKNode) {
		// TODO -----------------
		// REMOVE item type and instead have a signature in the node
		let it = node.signature.output is DKTypeSequence ? (node.signature.output as! DKTypeSequence).sub : node.signature.output
		itemTypeShortcut = it.toTypeShortcut(uniquingTable)
		self.fifoIndex = node.graphIndex
		self.itemType = it
		sugaredDesc = "gatherFromFifo(\(node.graphIndex), \(it.sugaredDescription(uniquingTable)))"
	}
	var sequenceType: DKType { return itemType.makeSequence }
	override var signature: DKTypeSignature {
		return DKTypeSignature(input: DKTypeStruct.void, output: sequenceType)
	}
	override var functionToJSONDict: [String: JSON] {
		return [
			"gather": .integer(fifoIndex),
			"item": itemTypeShortcut.toJSON
		]
	}
	override class func functionFromJSON(_ uniquingTable: DKTypeTable, _ dict: [String: JSON]) -> DKFunctionGatherFromFifo! {
		let g = dict["gather"]
		if g == nil || !g!.isInteger { return nil }
		let fifoIndex = g!.integerValue
		let itemType = dict["item"]?.toDKType(uniquingTable)
		if itemType == nil { return nil }
		return DKFunctionGatherFromFifo(uniquingTable, fifoIndex, itemType!)
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

