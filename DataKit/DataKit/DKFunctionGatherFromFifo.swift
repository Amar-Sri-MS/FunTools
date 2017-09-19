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
	let typeShortcut: DKType.Shortcut // derived from signature
	init(_ uniquingTable: DKTypeTable, _ fifoIndex: Int, _ itemType: DKType) {
		typeShortcut = itemType.toTypeShortcut(uniquingTable)
		self.fifoIndex = fifoIndex
		self.itemType = itemType
	}
	var sequenceType: DKType { return itemType.makeSequence }
	override var signature: DKTypeSignature {
		return DKTypeSignature(input: DKTypeStruct.void, output: sequenceType)
	}
	override var functionToJSONDict: [String: JSON] {
		return [
			"gather": .integer(fifoIndex),
			"item": typeShortcut.toJSON
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
	override func sugaredDescription(_ knowns: [DKType: String]) -> String {
		return "gatherFromFifo(\(fifoIndex), \(itemType.sugaredDescription(knowns)))"
	}
}

