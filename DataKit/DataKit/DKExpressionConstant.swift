//
//  DKExpressionConstant.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/22/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

class DKExpressionConstant: DKExpression, Equatable, ExpressibleByBooleanLiteral, ExpressibleByIntegerLiteral, ExpressibleByStringLiteral {
	let value: DKValue
	init(_ value: DKValue) {
		self.value = value
	}
	override var type: DKType {
		return value.type;
	}
	override func evaluate(context: DKEvaluationContext) -> DKValue {
		return value
	}
	static func ==(lhs: DKExpressionConstant, rhs: DKExpressionConstant) -> Bool {
		return lhs.value == rhs.value
	}
	convenience required init(booleanLiteral value: BooleanLiteralType) {
		self.init(DKValueSimple(value))
	}
	convenience required init(integerLiteral value: IntegerLiteralType) {
		self.init(DKValueSimple(type: DKTypeInt.int64, value: value))
	}
	convenience required init(stringLiteral s: StringLiteralType) {
		self.init(DKValueSimple(s))
	}
	convenience required init(extendedGraphemeClusterLiteral s: String) {
		self.init(DKValueSimple(s))
	}
	convenience required init(unicodeScalarLiteral s: String) {
		self.init(DKValueSimple(s))
	}
	override func expressionToJSON(_ uniquingTable: DKTypeTable) -> JSON {
		let dict: [String: JSON] = [
			"constant": value.valueToJSON(uniquingTable)
		]
		return .dictionary(dict)
	}
	override class func expressionFromJSON(_ uniquingTable: DKTypeTable, _ j: JSON) -> DKExpression! {
		let dict = j.dictionaryValue
		let ej = dict["constant"]?.toDKValue(uniquingTable)
		if ej == nil { return nil }
		return DKExpressionConstant(ej!)
	}
	override func sugaredDescription(_ uniquingTable: DKTypeTable) -> (desc: String, needsParen: Bool) {
		return (value.description, false)
	}

}
