//
//  DKFunctionGenerator.swift
//  DataKit
//
//  Created by Bertrand Serlet on 8/27/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// Generates a sequence of <T>, i.e. the signature is () -> [T]
// For now, we have a name identifying the generator

class DKFunctionGenerator: DKFunction {
	let name: String
	let params: JSON
	let itemType: DKType
	let itemShortcut: DKType.Shortcut
	init(_ uniquingTable: DKTypeTable, name: String, params: JSON, itemType: DKType) {
		self.name = name
		self.params = params
		self.itemType = itemType
		itemShortcut = itemType.toTypeShortcut(uniquingTable)
	}
	override var signature: DKTypeSignature {
		return DKTypeSignature(input: .void, output: itemType.makeSequence)
	}
	override var functionToJSONDict: [String: JSON] {
		return [
			"generator": .string(name),
			"item_type": itemShortcut.toJSON,
			"params": params
		]
	}
	override class func functionFromJSON(_ uniquingTable: DKTypeTable, _ dict: [String: JSON]) -> DKFunction! {
		let g = dict["generator"]
		if g == nil || !g!.isString { return nil }
		let i = dict["item_type"]?.toDKType(uniquingTable)
		if i == nil { return nil }
		let params: JSON = dict["params"] ?? JSON.null
		return DKFunctionGenerator(uniquingTable, name: g!.stringValue, params: params, itemType: i!)
	}
	override func evaluate(context: DKEvaluationContext, _ subs: [DKExpression]) -> DKValue {
		assert(subs.count == 0)
		let itemGen = DKFunctionGenerator.registry[name]!
		var stream: DKMutableBitStream = DataAsMutableBitStream()
		// For now we generate the whole stream
		while true {
			let next = itemGen(params)
			if next == nil { break }
			assert(next!.type == itemType)
			stream.pad(toByteAlign: 4)
			next!.append(to: &stream)
		}
		let data = stream.finishAndData()
		return DKValueLazySequence(itemType: itemType, data: data)
	}
	override func sugaredDescription(_ knowns: [DKType: String]) -> String {
		return "generator(\(name), \(itemType.sugaredDescription(knowns)), \(params))"
	}
	static var registry: [String: (JSON) -> DKValue?] = [:]
	class func registerItemGenerator(name: String, _ itemGen: @escaping (JSON) -> DKValue?) {
		registry[name] = itemGen
	}
}
