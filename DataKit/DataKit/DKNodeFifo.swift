//
//  DKNodeFifo.swift
//  DataKit
//
//  Created by Bertrand Serlet on 9/13/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

class DKNodeFifo: DKNode {
	private var asDest: DKValueStreamDest!
	private var asSource: DKValueStreamSource!
	var predicateOnInput: DKFunction!	// predicate on input, nil => always
	enum AppendStyle {
		case none
		case all
		case gatherByBatch(DKFunction)	// gathers values to produce, consumed by batches
		// if function is non-nil, it is applied
	}
	var toAppend: AppendStyle = .all
	init(label: Int, itemType: DKType) {
		super.init(label, itemType: itemType)
	}
	var sequenceType: DKTypeSequence { return DKTypeSequence(itemType) }
	var streamForProducer: DKValueStreamDest {
		if asDest == nil { asDest = DKValueStreamDest(itemType: itemType) }
		return asDest!
	}
	var streamForConsumer: DKValueStreamSource {
		if asSource == nil { asSource = DKValueStreamSource(itemType: itemType) }
		return asSource!
	}
	override func sugaredDescription(_ uniquingTable: DKTypeTable) -> String {
		var app = ""
		switch toAppend {
			case .all: app = "all"
			case .none: app = "none"
			case let .gatherByBatch(fun):
				app = "gather(\(fun))"
		}
		return "FIFO#\(graphIndex)(t=\(itemType.sugaredDescription(uniquingTable)); pred=\(predicateOnInput == nil ? "nil" : predicateOnInput.description); append=\(app))"
	}
	override func nodeToJSONDict(_ uniquingTable: DKTypeTable) -> [String: JSON] {
		var dict: [String: JSON] = [
			"item_type": .string(itemType.toTypeShortcut(uniquingTable)),
			]
		if predicateOnInput != nil {
			dict["predicate"] = predicateOnInput!.functionToJSON
		}
		switch toAppend {
			case .all: break // nothing
			case .none:
				dict["append"] = "none"
			case let .gatherByBatch(fun):
				dict["append"] = "gather"
				dict["gather_fun"] = fun.functionToJSON
		}
		return dict
	}
	var hasDefaultBehavior: Bool {
		switch toAppend {
			case .all: return predicateOnInput == nil
			default: return false
		}
	}
	func compose(outer: DKFunction) {
		switch toAppend {
			case .none: return
			case .all: toAppend = .gatherByBatch(outer)
			case let .gatherByBatch(inner):
				let comp = DKFunctionComposition(outer: outer, inner: inner)
				toAppend = .gatherByBatch(comp)
		}
	}
}
