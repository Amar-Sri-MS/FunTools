//
//  DKEvaluationContext.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/29/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// Evaluation contexts resemble frames in an ABI
// The variables are called $0, $1, ...
// There is a parent context

class DKEvaluationContext: Cardinality {
	let parent: DKEvaluationContext!
	var variables: [DKValue]
	init() {
		parent = nil
		variables = []
	}
	private init(parent: DKEvaluationContext, values: [DKValue]) {
		self.parent = parent
		variables = values
	}
	func newContextWith(values: [DKValue]) -> DKEvaluationContext {
		return DKEvaluationContext(parent: self, values: values)
	}
	var count: Int { return variables.count }
	subscript(index: Int) -> DKValue { return variables[index] }
}
