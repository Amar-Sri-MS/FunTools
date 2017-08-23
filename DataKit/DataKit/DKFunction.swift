//
//  DKFunction.swift
//  DataKit
//
//  Created by Bertrand Serlet on 8/22/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// A function has a signature

class DKFunction: Equatable, CustomStringConvertible {
	var signature: DKTypeSignature {
		fatalErrorMustBeImplementedBySubclass()
	}
	func isEqualTo(_ rhs: DKFunction) -> Bool {
		fatalErrorMustBeImplementedBySubclass()
	}
	func prepareToEvaluate(context: DKEvaluationContext) {
		// nothing by default
	}
	var evaluator: DKNAryEvaluator {
		fatalErrorMustBeImplementedBySubclass()
	}
	static func ==(lhs: DKFunction, rhs: DKFunction) -> Bool {
		return lhs.isEqualTo(rhs)
	}
	var functionToJSON: [String: JSON] {
		fatalErrorMustBeImplementedBySubclass()
	}
	class func functionFromJSON(_ uniquingTable: DKTypeTable, _ j: [String: JSON]) -> DKFunction! {
		for f in [DKFunctionOperator.functionFromJSON, DKFunctionProjection.functionFromJSON, DKFunctionFilter.functionFromJSON, DKFunctionClosure.functionFromJSON] {
			let fun = f(uniquingTable, j)
			if fun != nil { return fun }
		}
		return nil
	}
	var description: String {
		return sugaredDescription([:])
	}
	func sugaredDescription(_ knowns: [DKType: String]) -> String {
		fatalErrorMustBeImplementedBySubclass()
	}
}




