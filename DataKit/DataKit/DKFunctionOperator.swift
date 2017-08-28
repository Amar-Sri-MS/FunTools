//
//  DKFunctionOperator.swift
//  DataKit
//
//  Created by Bertrand Serlet on 8/22/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

class DKFunctionOperator: DKFunction {
	let oper: DKOperator
	let domainShortcut: DKType.Shortcut // derived from signature
	init(oper: DKOperator, _ uniquingTable: DKTypeTable) {
		// We make sure we have all the proper types
		domainShortcut = oper.baseType.toTypeShortcut(uniquingTable)
		self.oper = oper
	}
	override var signature: DKTypeSignature { return oper.signature }
	override func isEqualTo(_ rhs: DKFunction) -> Bool {
		if let r = rhs as? DKFunctionOperator {
			return oper == r.oper
		}
		return false
	}
	override var functionToJSON: [String: JSON] {
		var dict: [String: JSON] = [
			"op": .string(oper.op),
			"domain": domainShortcut.toJSON
		]
		if let a = oper as? DKAlgebraicOperator {
			dict["genre"] = .string("algebraic")
			dict["arity"] = .integer(a.arity)
		} else if let _ = oper as? DKComparisonOperator {
			dict["genre"] = .string("comparison")
		}
		return dict
	}
	override class func functionFromJSON(_ uniquingTable: DKTypeTable, _ dict: [String: JSON]) -> DKFunctionOperator! {
		let o = dict["op"]
		if o == nil || !o!.isString { return nil }
		let op = o!.stringValue
		let domain = dict["domain"]?.toDKType(uniquingTable)
		if domain == nil { return nil }
		if dict["genre"] == "algebraic" {
			let arity = dict["arity"]!.integerValue
			let oper = DKAlgebraicOperator(domain: domain!, op: op, arity: arity)
			return DKFunctionOperator(oper: oper!, uniquingTable)
		} else if dict["genre"] == "comparison" {
			let oper = DKComparisonOperator(domain: domain!, op: op)
			return DKFunctionOperator(oper: oper!, uniquingTable)
		} else {
			return nil
		}
	}
	override func evaluate(context: DKEvaluationContext, _ exprs: [DKExpression]) -> DKValue {
		return oper.evaluator(context, exprs)
	}
	override var description: String {
		return oper.op
	}
	override func sugaredDescription(_ knowns: [DKType: String]) -> String {
		return oper.op
	}
}
