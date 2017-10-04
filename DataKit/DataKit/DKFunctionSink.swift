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
		return DKTypeSignature(input: DKTypeStruct(funcParamType: itemType.makeSequence), output: .void)
	}
	class func canBeSinkAndItemType(_ type: DKType) -> DKType! {
		if let signature = type as? DKTypeSignature {
			if signature.numberOfArguments != 1 { return nil }
			if signature.output != DKType.void { return nil }
			let seqType = signature.input[0] as? DKTypeSequence
			return seqType?.sub
		}
		return nil
	}
	override var functionToJSONDict: [String: JSON] {
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
		let x = subs[0].evaluate(context: context)
		assert(x.type == itemType.makeSequence)
		if name == "logger" {
			x.dumpDescription()
		} else {
			let sink = DKFunctionSink.registry[name]!
			sink(x)
		}
		return .null
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
