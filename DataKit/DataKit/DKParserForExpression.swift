//
//  DKParserForExpression.swift
//  DataKit
//
//  Created by Bertrand Serlet on 10/5/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// Parse an expression.  If type is given it is assumed or checked.  Else it can be specified by the syntax: <type>: <expr>
// Expressions can be:
// - a variable starting with $ like $0
// - a N-ary function applied to several sub-expressions like +(1, 2) or .first_name($0)
// - a unary function prefixed like - $0
// - a projection postfixed like $0.first_name
// - a bunch of sub-expressions separated by an operator and following the usual priority rules, like 1 + 2 + 3 * 4
// - a constant like 42
// - a parenthesized expression like (42)

extension DKParser {
	func parseExpression(_ type: DKType!, _ variables: [DKType], _ allowRecursive: Bool = true) throws -> DKExpression {
		let saved = (token, lexerState)
		// We have a priority list of things to try
		// First, we try parsing with operators as that will "absorb" more than 1 expression
		// We try paren before constant so that "(42)" is a parentethical expression rather than a struct
		var trials = [parseExpressionWithType, parseExpressionParen, parseExpressionConstant, parseExpressionVariable, parseExpressionUnary, parseExpressionApplication]
		if allowRecursive {
			trials = [parseExpressionWithOperators] + trials
		}
		for p in trials {
			do {
				return try p(type, variables)
			} catch _ {
			}
			(currentToken, lexerState) = saved
		}
		throw DKParsingError("No match for expression", self)
	}
	func parseExpressionWithType(_ type: DKType!, _ variables: [DKType]) throws -> DKExpression {
		let t = try parseType()
		try expectReservedWord(":")
		if type != nil && type! != t {
			throw DKParsingError("Type mismatch \(type!) vs. \(t) for expression", self)
		}
		return try parseExpression(t, variables)
	}
	func parseExpressionParen(_ type: DKType!, _ variables: [DKType]) throws -> DKExpression {
		try expectReservedWord("(")
		let e = try parseExpression(type, variables)
		try expectReservedWord(")")
		return e
	}
	func parseExpressionConstant(_ type: DKType!, _ variables: [DKType]) throws -> DKExpression {
		let v = try parseValue(type)
		return DKExpressionConstant(v)
	}
	func parseExpressionVariable(_ type: DKType!, _ variables: [DKType]) throws -> DKExpression {
		let s = maybeIdent()
		if s == nil || s!.unichar0() != "$" {
			throw DKParsingError("No match for expression variable", self)
		}
		let n = Int(s!.substringAfter(1))
		if n == nil {
			throw DKParsingError("No match for expression variable", self)
		}
		if n! >= variables.count {
			throw DKParsingError("No match for variable $\(n!)", self)
		}
		accept()
		var t = variables[n!]
		var expr: DKExpression = DKExpressionVariable(index: n!, type: t)
		while (t is DKTypeStruct) && peekReservedWord(".") {
			let f = try parseFunctionProjection(t as! DKTypeStruct)
			if f.signature.numberOfArguments != 1 || f.signature.input[0] != t {
				throw DKParsingError("Mismatch for projection \(f) - t=\(t)", self)
			}
			expr = DKExpressionFuncCall(fun: f, arguments: [expr])
			t = f.signature.output
		}
		if type != nil && type! != t {
			throw DKParsingError("Mismatch for variable $\(n!)", self)
		}
		return expr
	}
	func parseExpressionWithOperators(_ type: DKType!, _ variables: [DKType]) throws -> DKExpression {
		var exprs: [DKExpression] = []
		var operators: [String] = []
		exprs |= try parseExpression(nil, variables, false)
		let op = peekAnyPunctuationOrReservedWord()
		if op == nil || !DKOperator.allNonUnaryOperatorStrings.contains(op!) {
			throw DKParsingError("Single sub-expression, not a suitable term", self)
		}
		accept()
		operators |= op!
		exprs |= try parseExpression(nil, variables, false)
		while true {
			let op = peekAnyPunctuationOrReservedWord()
			if op == nil || !DKOperator.allNonUnaryOperatorStrings.contains(op!) {
				break
			}
			accept()
			operators |= op!
			exprs |= try parseExpression(nil, variables, false)
		}
//		print("Got \(operators.count) operators")
		// Now we make an expression tree from all that
		return try makeExpression(type, exprs: exprs, operators: operators)
	}
	func parseExpressionUnary(_ type: DKType!, _ variables: [DKType]) throws -> DKExpression {
		let op = peekAnyPunctuationOrReservedWord()
		if op == nil || !DKAlgebraicOperator.unaryOperatorStrings.contains(op!) {
			throw DKParsingError("Not a suitable unary operator", self)
		}
		accept()
		let expr = try parseExpression(type, variables)
		let oper = DKAlgebraicOperator(domain: type ?? expr.type, op: op!, arity: 1)
		if oper == nil {
			throw DKParsingError("Can't create unary expression for \(op!) \(expr)", self)
		}
		let f = DKFunctionOperator(oper: oper!, uniquingTable)
		return DKExpressionFuncCall(fun: f, arguments: [expr])
	}
	func parseExpressionApplication(_ type: DKType!, _ variables: [DKType]) throws -> DKExpression {
		let f = try parseFunctionReturning(type)
		if type != nil && f.signature.output != type! {
			throw DKParsingError("Type mismatch for application of function", self)
		}
		let n = f.signature.numberOfArguments
		try expectReservedWord("(")
		var exprs: [DKExpression] = []
		for i in 0 ..< n {
			exprs |= try parseExpression(f.signature[i], variables)
			if i == n - 1 {
				if peekReservedWord(",") { accept() }
			} else {
				try expectReservedWord(",")
			}
		}
		try expectReservedWord(")")
		return DKExpressionFuncCall(fun: f, arguments: exprs)
	}
}

/*=============== MAKING AN EXPRESSION TREE ===============*/

extension DKParser {
	func makeExpression(_ type: DKType!, exprs: [DKExpression], operators: [String]) throws -> DKExpression {
		assert(exprs.count == operators.count + 1)
		// First, if we have 1 exprs only, that's it!
		if operators.isEmpty { return exprs[0] }
//		print("In makeExpression with exprs=\(exprs) ops=\(operators)")
		let priorities: [String: Int] = [
			"==": 0, "!=": 0, "<": 0, ">": 0, "<=": 0, ">=": 0,
			"+": 1, "-": 1, "|": 1,
			"*": 2, "/": 2, "%": 2, "^": 2,
			"||": 3,
			"&&": 4,
		]
		// We pick the lowest priority and right-most op
		var i = operators.count - 1
		var j = i - 1
		while j >= 0 {
			let pi = priorities[operators[i]]!
			let pj = priorities[operators[j]]!
			if pj < pi { i = j }
			j -= 1
		}
		let op = operators[i]
		let isComparison = DKComparisonOperator.operatorStrings.contains(op)
		let lexprs: [DKExpression] = exprs[0 ... i].map { $0 }
		let lops: [String] = operators[0 ..< i].map { $0 }
		let left = try makeExpression(nil, exprs: lexprs, operators: lops)
		let rexprs: [DKExpression] = exprs[(i+1) ..< exprs.count].map { $0 }
		let rops: [String] = operators[(i+1) ..< operators.count].map { $0 }
		let right = try makeExpression(nil, exprs: rexprs, operators: rops)
		if left.type != right.type {
			throw DKParsingError("Type mismatch for comparison", self)
		}
		var oper: DKOperator! = nil
		if isComparison {
			oper = DKComparisonOperator(domain: left.type, op: op)
			if oper == nil {
				print("*** Couldn't create expression for \(exprs) and \(operators) - type=\(left.type)")
			}
		} else {
			oper = DKAlgebraicOperator(domain: type ?? left.type, op: op, arity: 2)
		}
		if oper == nil {
			throw DKParsingError("Can't create expression for \(exprs) and \(operators)", self)
		}
		let f = DKFunctionOperator(oper: oper!, uniquingTable)
//		print("In makeExpression with exprs=\(exprs) ops=\(operators) - f=\(f)")
		return DKExpressionFuncCall(fun: f, arguments: [left, right])
	}
}
