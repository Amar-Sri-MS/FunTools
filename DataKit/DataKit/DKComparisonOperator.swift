//
//  DKComparisonOperator.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/29/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

class DKComparisonOperator: DKOperator {
	init?(domain t: DKType, op: String) {
		let ev = DKComparisonOperator.evaluationForComparator(domain: t, op: op)
		if ev == nil { return nil }
		super.init(op: op, baseType: t, evaluator: ev!)
	}
	override var signature: DKTypeSignature {
		let input = DKTypeStruct(funcParamType: baseType, repeated: 2)
		return DKTypeSignature(input: input, output: DKTypeInt.bool)
	}
	fileprivate class func evaluationForComparator(domain: DKType, op: String) -> DKNAryEvaluator? {
		if (op == "==") || (op == "!=") || (op == "<") || (op == "<=") || (op == ">") || (op == ">=") {
			if domain == DKTypeInt.bool {
				if (op != "==") && (op != "!=") { return nil }
				return {  context, subs in
					assert(subs.count == 2)
					let x = subs[0].evaluate(context: context).boolValue
					let y = subs[1].evaluate(context: context).boolValue
					return .bool(op == "==" ? x == y : x != y)
				}
			} else if domain is DKTypeInt {
				return {  context, subs in
					assert(subs.count == 2)
					let x = subs[0].evaluate(context: context).intValue
					let y = subs[1].evaluate(context: context).intValue
					let b: Bool = op == "==" ? x == y : op == "!=" ? x != y : op == "<" ? x < y : op == "<=" ? x <= y : op == ">" ? x > y : x >= y
					return .bool(b)
				}
			} else if domain is DKTypeString {
				return {  context, subs in
					assert(subs.count == 2)
					let x = subs[0].evaluate(context: context).stringValue
					let y = subs[1].evaluate(context: context).stringValue
					let b: Bool = op == "==" ? x == y : op == "!=" ? x != y : op == "<" ? x < y : op == "<=" ? x <= y : op == ">" ? x > y : x >= y
					return .bool(b)
				}
			}
		}
		return nil
	}
	override func isEqualTo(_ rhs: DKOperator) -> Bool {
		if let r = rhs as? DKComparisonOperator {
			return op == r.op && baseType == r.baseType
		}
		return false
	}
}


