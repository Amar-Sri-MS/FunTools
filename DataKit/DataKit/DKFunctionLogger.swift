//
//  DKFunctionLogger.swift
//  DataKit
//
//  Created by Bertrand Serlet on 9/17/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// Logs anything
class DKFunctionLogger: DKFunction {
	let type: DKType
	let shortcut: DKType.Shortcut
	init(_ uniquingTable: DKTypeTable, _ type: DKType) {
		self.type = type
		shortcut = type.toTypeShortcut(uniquingTable)
	}
	override var signature: DKTypeSignature {
		return DKTypeSignature(unaryArg: type, output: .void)
	}
	override var functionToJSONDict: [String: JSON] {
		return ["logger": shortcut.toJSON]
	}
	override class func functionFromJSON(_ uniquingTable: DKTypeTable, _ dict: [String: JSON]) -> DKFunction! {
		let g = dict["logger"]
		if g == nil || !g!.isString { return nil }
		let t = g?.toDKType(uniquingTable)
		if t == nil { return nil }
		return DKFunctionLogger(uniquingTable, t!)
	}
	override func evaluate(context: DKEvaluationContext, _ subs: [DKExpression]) -> DKValue {
		assert(subs.count == 1)
		let x = subs[0].evaluate(context: context)
		x.dumpDescription()
		return .null
	}
	override var description: String {
		return "logger(\(shortcut))"
	}
	override var isInputGroupable: Bool {
		return true
	}
}
