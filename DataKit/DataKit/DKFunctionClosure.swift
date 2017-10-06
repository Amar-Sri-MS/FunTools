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
	let sugaredDesc: String	// derived
	let bodyJSON: JSON	// we compute the expression serialization at creation type to avoid needing to create types later
	init(structParams: DKTypeStruct, body: DKExpression, _ uniquingTable: DKTypeTable) {
		self.structParams = structParams
		self.body = body
		paramsShortcut = structParams.toTypeShortcut(uniquingTable)
		let paramsSugaredDesc = structParams.subs.joinDescriptions(", ") {
			$0.sugaredDescription(uniquingTable)
		}
		let bodyTypeSugaredDesc = body.type.sugaredDescription(uniquingTable)
		sugaredDesc = "{ (\(paramsSugaredDesc)) -> \(bodyTypeSugaredDesc) in \(body.sugaredDescription(uniquingTable).desc) }"
		bodyJSON = body.expressionToJSON(uniquingTable)
	}
	convenience init(params: [DKType], body: DKExpression, _ uniquingTable: DKTypeTable) {
		self.init(structParams: DKTypeStruct(funcParams: params), body: body, uniquingTable)
	}
	override var signature: DKTypeSignature {
		return DKTypeSignature(input: structParams, output: body.type)
	}
	override var functionToJSONDict: [String: JSON] {
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
	override func evaluate(context: DKEvaluationContext, _ subs: [DKExpression]) -> DKValue {
		assert(subs.count == self.structParams.subs.count)
		let evaluated = subs.map { $0.evaluate(context: context) }
		let newContext = context.newContextWith(values: evaluated)
		return self.body.evaluate(context: newContext)
	}
	override var description: String {
		return sugaredDesc
	}
	class func identity(_ uniquingTable: DKTypeTable, _ t: DKType) -> DKFunctionClosure {
		let expr = DKExpressionVariable(index: 0, type: t)
		return DKFunctionClosure(params: [t], body: expr, uniquingTable)
	}

	// Function returning always the same constant
	class func constant(_ uniquingTable: DKTypeTable, _ value: DKValue) -> DKFunctionClosure {
		let t = value.type
		let expr = DKExpressionConstant(value)
		return DKFunctionClosure(params: [t], body: expr, uniquingTable)
	}
}


