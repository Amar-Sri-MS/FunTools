//
//  DKExpression_Test.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/23/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

extension DKExpression {
	class func selfTest() {
		let uniquingTable = DKTypeTable()
		let con = DKEvaluationContext()
		let btrue = DKValue.bool(true)
		let bfalse = DKValue.bool(false)
		let ktrue = DKExpressionConstant(btrue)
		let kfalse = DKExpressionConstant(bfalse)
		let and0 = DKAlgebraicOperator(domain: DKTypeInt.bool, op: "&&", arity: 0)!
		let boolExpr0 = DKExpressionFuncCall(oper: and0, arguments: [], uniquingTable)
		let r0 = boolExpr0.evaluate(context: con)
		assert(r0 == btrue)
		let not = DKAlgebraicOperator(domain: DKTypeInt.bool, op: "!", arity: 1)!
		let boolExpr1 = DKExpressionFuncCall(oper: not, arguments: [kfalse], uniquingTable)
		let r1 = boolExpr1.evaluate(context: con)
		assert(r1 == btrue)
		let and2 = DKAlgebraicOperator(domain: DKTypeInt.bool, op: "&&", arity: 2)!
		let boolExpr2 = DKExpressionFuncCall(oper: and2, arguments: [ktrue, kfalse], uniquingTable)
		let r2 = boolExpr2.evaluate(context: con)
		assert(r2 == bfalse)
		let or3 = DKAlgebraicOperator(domain: DKTypeInt.bool, op: "||", arity: 3)!
		let boolExpr3 = DKExpressionFuncCall(oper: or3, arguments: [kfalse, kfalse, kfalse], uniquingTable)
		let r3 = boolExpr3.evaluate(context: con)
		assert(r3 == bfalse)

		let uint16 = DKTypeInt.shared(signed: false, numBits: 16)
		let k1 = DKExpressionConstant(DKValueSimple(type: uint16, value: 1))
		let k13 = DKExpressionConstant(DKValueSimple(type: uint16, value: 13))
		let k14 = DKExpressionConstant(DKValueSimple(type: uint16, value: 14))
		let plus2 = DKAlgebraicOperator(domain: uint16, op: "+", arity: 2)!
		let intExpr2 = DKExpressionFuncCall(oper: plus2, arguments: [k13, k1], uniquingTable)
		let rr2 = intExpr2.evaluate(context: con)
		assert(rr2 == k14.value)

		let s1: DKExpressionConstant = "foo"
		let s2: DKExpressionConstant = "bar"
		let concat2 = DKAlgebraicOperator(domain: DKTypeString.string, op: "|", arity: 2)!
		let sExpr = DKExpressionFuncCall(oper: concat2, arguments: [s1, s2], uniquingTable)
		let ss = sExpr.evaluate(context: con)
		assert(ss.stringValue == "foobar")

		let le2 = DKComparisonOperator(domain: uint16, op: "<=")!
		let comp1 = DKExpressionFuncCall(oper: le2, arguments: [k1, k13], uniquingTable)
		assert(comp1.evaluate(context: con).boolValue == true)
		let comp2 = DKExpressionFuncCall(oper: le2, arguments: [k13, k1], uniquingTable)
		assert(comp2.evaluate(context: con).boolValue == false)

		print("== Expressions self-test complete!")

	}
}
