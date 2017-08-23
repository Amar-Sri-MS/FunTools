//
//  DKFunctionClosure.swift
//  DataKit
//
//  Created by Bertrand Serlet on 8/22/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// Create a closure that requires parameters of type params
// When evaluating, binds each argument to $0, $1, ...
class DKFunctionClosure: DKFunction {
	let structParams: DKTypeStruct
	let body: DKExpression
	let paramsShortcut: DKType.Shortcut	// derived
	let bodyJSON: JSON	// we compute the expression serialization at creation type to avoid needing to create types later
	init(structParams: DKTypeStruct, body: DKExpression, _ uniquingTable: DKTypeTable) {
		self.structParams = structParams
		self.body = body
		paramsShortcut = structParams.toTypeShortcut(uniquingTable)
		bodyJSON = body.expressionToJSON(uniquingTable)
	}
	convenience init(params: [DKType], body: DKExpression, _ uniquingTable: DKTypeTable) {
		self.init(structParams: DKTypeStruct(funcParams: params), body: body, uniquingTable)
	}
	override var signature: DKTypeSignature {
		return DKTypeSignature(input: structParams, output: body.type)
	}
	override var functionToJSON: [String: JSON] {
		return [
			"closure": .string(paramsShortcut),
			"body": bodyJSON
		]
	}
	override class func functionFromJSON(_ uniquingTable: DKTypeTable, _ dict: [String: JSON]) -> DKFunction! {
		let structParams = dict["closure"]?.toDKType(uniquingTable) as? DKTypeStruct
		if structParams == nil { return nil }
		let body = dict["body"]?.toDKExpression(uniquingTable)
		if body == nil { return nil }
		return DKFunctionClosure(structParams: structParams!, body: body!, uniquingTable)
	}
	override var evaluator: DKNAryEvaluator {
		return {  context, subs in
			assert(subs.count == self.structParams.subs.count)
			let evaluated = subs.map { $0.evaluate(context: context) }
			let newContext = context.newContextWith(values: evaluated)
			return self.body.evaluate(context: newContext)
		}
	}
	override func sugaredDescription(_ knowns: [DKType: String]) -> String {
		let p = structParams.subs.joinDescriptions(", ") {
			$0.sugaredDescription(knowns)
		}
		return "{ (\(p)) -> \(body.type.sugaredDescription(knowns)) in \(body.sugaredDescription(knowns).desc) }"
	}
}


