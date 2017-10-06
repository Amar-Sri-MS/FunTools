//
//  DKExpressionVariable.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/23/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

class DKExpressionVariable: DKExpression {
	let index: Int
	let actualType: DKType
	init(index: Int, type: DKType) {
		self.index = index
		self.actualType = type
	}
	override var type: DKType { return actualType }
	override func evaluate(context: DKEvaluationContext) -> DKValue {
		let value = context[index]
		// TODO: Check here the variable is of the right type - or cast to it
		let vt = value.type
		assert(vt == type)
		return value
	}
	override func expressionToJSON(_ uniquingTable: DKTypeTable) -> JSON {
		let dict: [String: JSON] = [
			"var": .integer(index),
			"type": actualType.toTypeShortcut(uniquingTable).toJSON
		]
		return .dictionary(dict)
	}
	override class func expressionFromJSON(_ uniquingTable: DKTypeTable, _ j: JSON) -> DKExpression! {
		let dict = j.dictionaryValue
		let vj = dict["var"]
		if vj == nil { return nil }
		let index = vj!.integerValue
		let tj = dict["type"]?.toDKType(uniquingTable)
		if tj == nil { return nil }
		return DKExpressionVariable(index: index, type: tj!)
	}
	override func sugaredDescription(_ uniquingTable: DKTypeTable) -> (desc: String, needsParen: Bool) {
		return ("$\(index)", false)
	}
}
