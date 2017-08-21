//
//  DKExpression.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/22/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

class DKExpression {
	var type: DKType {
		fatalErrorMustBeImplementedBySubclass()
	}
	func prepareToEvaluate(context: DKEvaluationContext) {
		// Subclass should redefine
	}
	func evaluate(context: DKEvaluationContext) -> DKValue {
		fatalErrorMustBeImplementedBySubclass()
	}
	func expressionToJSON(_ uniquingTable: DKTypeTable) -> JSON {
		fatalErrorMustBeImplementedBySubclass()
	}
	class func expressionFromJSON(_ uniquingTable: DKTypeTable, _ j: JSON) -> DKExpression! {
		fatalErrorMustBeImplementedBySubclass()
	}
	func sugaredDescription(_ knowns: [DKType: String]) -> (desc: String, needsParen: Bool) {
		fatalErrorMustBeImplementedBySubclass()
	}
}

extension JSON {
	func toDKExpression(_ uniquingTable: DKTypeTable) -> DKExpression? {
		for f in [DKExpressionConstant.expressionFromJSON, DKExpressionFuncCall.expressionFromJSON, DKExpressionVariable.expressionFromJSON] {
			let e = f(uniquingTable, self)
			if e != nil { return e }
		}
		return nil
	}
}
