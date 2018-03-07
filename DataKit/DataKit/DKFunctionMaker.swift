//
//  DKFunctionMaker.swift
//  DataKit
//
//  Created by Bertrand Serlet on 11/12/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// Built-in function that makes values, like "studentMaker" or "randomInt" or "sequentialInt"

class DKFunctionMaker: DKFunction {
	let name: String
	let params: JSON
	let itemType: DKType
	let itemShortcut: DKType.Shortcut
	init(_ uniquingTable: DKTypeTable, name: String, itemType: DKType, params: JSON = .null) {
		self.name = name
		self.params = params
		self.itemType = itemType
		itemShortcut = itemType.toTypeShortcut(uniquingTable)
	}
	override var signature: DKTypeSignature {
		return DKTypeSignature(input: .void, output: itemType)
	}
	override var functionToJSONDict: [String: JSON] {
		return [
			"maker": .string(name),
			"item_type": itemShortcut.toJSON,
			"params": params
		]
	}
	override class func functionFromJSON(_ uniquingTable: DKTypeTable, _ dict: [String: JSON]) -> DKFunction! {
		let g = dict["maker"]
		if g == nil || !g!.isString { return nil }
		let i = dict["item_type"]?.toDKType(uniquingTable)
		if i == nil { return nil }
		let params: JSON = dict["params"] ?? JSON.null
		return DKFunctionMaker(uniquingTable, name: g!.stringValue, itemType: i!, params: params)
	}
	override func evaluate(context: DKEvaluationContext, _ subs: [DKExpression]) -> DKValue {
		assert(subs.count == 0)
		let itemGen = DKFunctionMaker.registry[name]!
		return itemGen(params)
	}
	override var description: String {
		return "\(name)(\(params))"
	}
	static var registry: [String: (JSON) -> DKValue] = [:]
	class func registerMaker(name: String, _ maker: @escaping (JSON) -> DKValue) {
		registry[name] = maker
	}
}

