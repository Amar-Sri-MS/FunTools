//
//  DKNodeFifo.swift
//  DataKit
//
//  Created by Bertrand Serlet on 9/13/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

class DKNodeFifo: DKNode {
	var itemType: DKType // type of items for the input
	var predicateOnInput: DKFunction!	// predicate on input, nil => always
	enum AppendStyle {
		case none
		case all
		case gatherByBatch(DKFunction)	// gathers values to produce, consumed by batches
		// if function is non-nil, it is applied
	}
	var toAppend: AppendStyle = .all
	init(label: Int, itemType: DKType) {
		self.itemType = itemType
		super.init(label)
	}
	var outputType: DKType {
		switch toAppend {
		case .all: return DKTypeSequence(itemType)
		case .none: return DKType.void
		case let .gatherByBatch(fun):
			assert(fun.signature.numberOfArguments == 1)
			assert(fun.signature.input[0] == itemType)
			return DKTypeSequence(fun.signature.output)
		}
	}
	override var signature: DKTypeSignature {
		return DKTypeSignature(unaryArg: sequenceType, output: outputType)
	}
	var sequenceType: DKTypeSequence { return DKTypeSequence(itemType) }
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
		var dict: [String: JSON] = [:]
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
