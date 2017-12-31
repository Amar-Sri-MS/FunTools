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
	func evaluate(context: DKEvaluationContext, _ exprs: [DKExpression]) -> DKValue {
		fatalErrorMustBeImplementedBySubclass()
	}
	static func ==(lhs: DKFunction, rhs: DKFunction) -> Bool {
		return lhs.isEqualTo(rhs)
	}
	var functionToJSONDict: [String: JSON] {
		fatalErrorMustBeImplementedBySubclass()
	}
	var functionToJSON: JSON { return .dictionary(functionToJSONDict) }
	class func functionFromJSON(_ uniquingTable: DKTypeTable, _ j: [String: JSON]) -> DKFunction! {
		for f in [DKFunctionOperator.functionFromJSON, DKFunctionProjection.functionFromJSON, DKFunctionFilter.functionFromJSON, DKFunctionComposition.functionFromJSON, DKFunctionClosure.functionFromJSON, DKFunctionGenerator.functionFromJSON, DKFunctionGatherFromFifo.functionFromJSON, DKFunctionMap.functionFromJSON, DKFunctionReduce.functionFromJSON, DKFunctionMaker.functionFromJSON, DKFunctionCompress.functionFromJSON] {
			let fun = f(uniquingTable, j)
			if fun != nil { return fun }
		}
		return nil
	}
	var description: String {
		fatalErrorMustBeImplementedBySubclass()
	}
	// If function takes a [T] and returns () or [U], is it OK to send smaller batches of its input and combine the output
	var isInputGroupable: Bool {
		return false
	}
}




