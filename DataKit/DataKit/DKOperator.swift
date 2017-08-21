//
//  DKOperator.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/23/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

typealias DKNAryEvaluator = (DKEvaluationContext, [DKExpression]) -> DKValue

protocol DKOperatorIsEqualToOtherOperator {
	func isEqualTo(_ rhs: DKOperator) -> Bool
}

class DKOperator: Equatable, DKOperatorIsEqualToOtherOperator {
	let op: String
	let baseType: DKType
	let evaluator: DKNAryEvaluator
	var signature: DKTypeSignature {
		fatalErrorMustBeImplementedBySubclass()
	}
	init(op: String, baseType: DKType, evaluator: @escaping DKNAryEvaluator) {
		self.op = op
		self.baseType = baseType
		self.evaluator = evaluator
	}
	static func ==(lhs: DKOperator, rhs: DKOperator) -> Bool {
		return lhs.isEqualTo(rhs)
	}
	func isEqualTo(_ rhs: DKOperator) -> Bool {
		fatalErrorMustBeImplementedBySubclass()
	}

}


