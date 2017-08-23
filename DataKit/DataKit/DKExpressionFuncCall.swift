//
//  DKExpressionFuncCall.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/23/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

class DKExpressionFuncCall: DKExpression {
	let fun: DKFunction
	let arguments: [DKExpression]
	init(fun: DKFunction, arguments: [DKExpression]) {
		assert(arguments.count == fun.signature.numberOfArguments)
		self.fun = fun
		self.arguments = arguments
	}
	convenience init(oper: DKOperator, arguments: [DKExpression], _ uniquingTable: DKTypeTable) {
		let fun = DKFunctionOperator(oper: oper, uniquingTable)
		self.init(fun: fun, arguments: arguments)
	}
	var signature: DKTypeSignature { return fun.signature }
	var evaluator: DKNAryEvaluator { return fun.evaluator }
	override var type: DKType { return signature.output }
	override func prepareToEvaluate(context: DKEvaluationContext) {
		fun.prepareToEvaluate(context: context)
	}
	override func evaluate(context: DKEvaluationContext) -> DKValue {
		assert(arguments.count == signature.numberOfArguments)
		return evaluator(context, arguments)
	}
	override func expressionToJSON(_ uniquingTable: DKTypeTable) -> JSON {
		let dict: [String: JSON] = [
			"func": .dictionary(fun.functionToJSON),
			"args": .array(arguments.map { $0.expressionToJSON(uniquingTable) })
		]
		return .dictionary(dict)
	}
	override class func expressionFromJSON(_ uniquingTable: DKTypeTable, _ j: JSON) -> DKExpression! {
		let dict = j.dictionaryValue
		let fd = dict["func"]
		if fd == nil || !fd!.isDictionary { return nil }
		let f = DKFunction.functionFromJSON(uniquingTable, fd!.dictionaryValue)
		if f == nil { return nil }
		let aj = dict["args"]
		if aj == nil { return nil }
		let args = aj!.arrayValue.flatMap { $0.toDKExpression(uniquingTable) }
		return DKExpressionFuncCall(fun: f!, arguments: args)
	}
	override func sugaredDescription(_ knowns: [DKType: String]) -> (desc: String, needsParen: Bool) {
		func parenthesized(_ arg: DKExpression) -> String {
			let d = arg.sugaredDescription(knowns)
			return d.needsParen ? "(\(d.desc))" : d.desc
		}
		if arguments.count == 1 {
			let a0 = parenthesized(arguments[0])
			if let oper = fun as? DKFunctionOperator {
				return (oper.oper.op + a0, true)
			} else if let proj = fun as? DKFunctionProjection {
				return ("\(a0).\(proj.projectedFieldName)", false)
			}
		} else {
			if let oper = fun as? DKFunctionOperator {
				return (arguments.joinDescriptions(" " + oper.oper.op + " ", parenthesized), true)
			}
		}
		let a = arguments.joinDescriptions(", ", parenthesized)
		return (fun.description + "(" + a + ")", false)
	}
}
