//
//  DKFifo.swift
//  DataKit
//
//  Created by Bertrand Serlet on 9/13/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

class DKFifo: CustomStringConvertible {
	let label: Int
	var itemType: DKType
	private var asDest: DKValueStreamDest!
	private var asSource: DKValueStreamSource!
	var predicateOnInput: DKFunction!	// predicate on input, nil => always
	enum AppendStyle {
		case none
		case all
		case gatherByBatch	// gathers values to produce, consumed by batches
	}
	var toAppend: AppendStyle = .all
	init(label: Int, itemType: DKType) {
		self.label = label
		self.itemType = itemType
	}
	var sequenceType: DKTypeSequence { return DKTypeSequence(subType: itemType) }
	var streamForProducer: DKValueStreamDest {
		if asDest == nil { asDest = DKValueStreamDest(itemType: itemType) }
		return asDest!
	}
	var streamForConsumer: DKValueStreamSource {
		if asSource == nil { asSource = DKValueStreamSource(itemType: itemType) }
		return asSource!
	}
	func sugaredDescription(_ knowns: [DKType: String]) -> String {
		return "FIFO#\(label)(t=\(itemType.sugaredDescription(knowns)); pred=\(predicateOnInput == nil ? "nil" : predicateOnInput.sugaredDescription(knowns)); append=\(toAppend))"
	}
	var description: String {
		return sugaredDescription([:])
	}
	func fifoToJSON(_ uniquingTable: DKTypeTable) -> JSON {
		var dict: [String: JSON] = [
			"label": .integer(label),
			"item_type": .string(itemType.toTypeShortcut(uniquingTable)),
			]
		if predicateOnInput != nil {
			dict["predicate"] = predicateOnInput!.functionToJSON
		}
		if toAppend != .all {
			dict["append"] = toAppend == .none ? "none" : "gather"
		}
		return .dictionary(dict)
	}
}
