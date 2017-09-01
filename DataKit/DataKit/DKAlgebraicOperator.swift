//
//  DKAlgebraicOperator.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/29/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

class DKAlgebraicOperator: DKOperator {
	let arity: Int
	init?(domain t: DKType, op: String, arity: Int) {
		let ev = DKAlgebraicOperator.evaluationForNaryOperator(domain: t, op: op, arity: arity)
		if ev == nil { return nil }
		self.arity = arity
		super.init(op: op, baseType: t, evaluator: ev!)
	}
	override var signature: DKTypeSignature {
		let input = DKTypeStruct(funcParamType: baseType, repeated: arity)
		return DKTypeSignature(input: input, output: baseType)
	}
	fileprivate class func evaluationForNaryBoolOperator(op: String) -> DKNAryEvaluator? {
		switch op {
		case "&&": return { context, subs in
			for sub in subs {
				let esub = sub.evaluate(context: context)
				let x = esub.boolValue
				// only evaluate rest if necessary
				if !x { return esub }
			}
			return .bool(true)
			}
		case "||": return { context, subs in
			for sub in subs {
				let esub = sub.evaluate(context: context)
				let x = esub.boolValue
				// only evaluate rest if necessary
				if x { return esub }
			}
			return .bool(false)
			}
		case "^": return { context, subs in
			var x = false
			for sub in subs {
				let esub = sub.evaluate(context: context)
				if esub.boolValue { x = !x }
			}
			return .bool(x)
			}
		default: return nil
		}
	}

	fileprivate class func evaluationForNaryIntOperator(domain: DKTypeInt, op: String) -> DKNAryEvaluator? {
		switch op {
		case "+": return { context, subs in
			let r = subs.reduce(0) { $0 + $1.evaluate(context: context).intValue }
			return .int(type: domain, intValue: r)
			}
		case "*": return { context, subs in
			let r = subs.reduce(1) { $0 * $1.evaluate(context: context).intValue }
			return .int(type: domain, intValue: r)
			}
		default: return nil
		}
	}

	fileprivate class func evaluationForNaryOperator(domain: DKType, op: String, arity: Int) -> DKNAryEvaluator? {
		// First unary operators
		if (arity == 1) && (op == "!") && (domain == DKTypeInt.bool) {
			return {  context, subs in
				assert(subs.count == 1)
				let esub = subs[0].evaluate(context: context)
				let x = esub.boolValue
				return .bool(!x)
			}
		}
		if (arity == 1) && (op == "-") && (domain is DKTypeInt) {
			return { context, subs in
				assert(subs.count == 1)
				let esub = subs[0].evaluate(context: context)
				let x = -esub.intValue
				return .int(type: domain as! DKTypeInt, intValue: x)
			}
		}
		// Then binary operators
		if (arity == 2) && (op == "-") && (domain is DKTypeInt) {
			return { context, subs in
				assert(subs.count == 2)
				let esub1 = subs[0].evaluate(context: context)
				let esub2 = subs[1].evaluate(context: context)
				let x1 = esub1.intValue
				let x2 = esub2.intValue
				let x = x1 - x2
				return .int(type: domain as! DKTypeInt, intValue: x)
			}
		}
		// First N-ary operators
		if domain == DKTypeInt.bool {
			return evaluationForNaryBoolOperator(op: op)
		}
		if domain is DKTypeInt {
			return evaluationForNaryIntOperator(domain: domain as! DKTypeInt, op: op)
		}
		if (op == "|") && domain is DKTypeString {
			return { context, subs in
				let r = subs.reduce("") { $0 + $1.evaluate(context: context).stringValue }
				return .string(r)
			}
		}
		return nil
	}
	override func isEqualTo(_ rhs: DKOperator) -> Bool {
		if let r = rhs as? DKAlgebraicOperator {
			return op == r.op && baseType == r.baseType && arity == r.arity
		}
		return false
	}
}


