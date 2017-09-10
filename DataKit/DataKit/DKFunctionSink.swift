//
//  DKFunctionSink.swift
//  DataKit
//
//  Created by Bertrand Serlet on 8/27/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// Absorbs a sequence of <T>, i.e. the signature is [T] -> ()
// For now, we have a name identifying the sink
// and "logger" is defined by default

class DKFunctionSink: DKFunction {
	let name: String
	let itemType: DKType
	let itemShortcut: DKType.Shortcut
	init(_ uniquingTable: DKTypeTable, name: String, itemType: DKType) {
		self.name = name
		self.itemType = itemType
		itemShortcut = itemType.toTypeShortcut(uniquingTable)
	}
	override var signature: DKTypeSignature {
		let seqType = DKTypeSequence(subType: itemType)
		return DKTypeSignature(input: DKTypeStruct(funcParamType: seqType), output: .void)
	}
	override var functionToJSON: [String: JSON] {
		return [
			"sink": .string(name),
			"item_type": itemShortcut.toJSON
		]
	}
	override class func functionFromJSON(_ uniquingTable: DKTypeTable, _ dict: [String: JSON]) -> DKFunction! {
		let g = dict["sink"]
		if g == nil || !g!.isString { return nil }
		let i = dict["item_type"]?.toDKType(uniquingTable)
		if i == nil { return nil }
		return DKFunctionSink(uniquingTable, name: g!.stringValue, itemType: i!)
	}
	override func evaluate(context: DKEvaluationContext, _ subs: [DKExpression]) -> DKValue {
		assert(subs.count == 1)
		let seqType = DKTypeSequence(subType: itemType)
		let x = subs[0].evaluate(context: context)
		assert(x.type == seqType)
		if name == "logger" {
			x.dumpDescription()
		} else {
			let sink = DKFunctionSink.registry[name]!
			sink(x)
		}
		return DKValueSimple(type: .void, json: .null)
	}
	override func sugaredDescription(_ knowns: [DKType: String]) -> String {
		return "sink(\(name), \(itemType.sugaredDescription(knowns)))"
	}
	static var registry: [String: (DKValue) -> Void] = [:]
	class func registerItemGenerator(name: String, _ sink: @escaping (DKValue) -> Void) {
		registry[name] = sink
	}
	override var isInputGroupable: Bool {
		return true
	}
}
