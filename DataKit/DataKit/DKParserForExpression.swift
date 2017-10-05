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
// - a unary function postfixed like $0.first_name
// - a bunch of sub-expressions separated by an operator and following the usual priority rules, like 1 + 2 + 3 * 4
// - a constant like 42
// - a parenthesized expression like (42)

// Example: $0.first_name == "Joe"

extension DKParser {
	func parseExpression(_ type: DKType!, _ variables: [DKType]) throws -> DKExpression {
		let saved = (token, lexerState)
		// We have a priority list of things to try
		// We try paren before constant so that "(42)" is a parentethical expression rather than a struct
		for p in [parseExpressionWithType, parseExpressionParen, parseExpressionConstant, parseExpressionVariable, parseExpressionApplication, parseExpressionUnary] {
			do {
				return try p(type, variables)
			} catch _ {
			}
			(currentToken, lexerState) = saved
		}
		throw DKParsingError("No match for expression", token)
	}
	func parseExpressionWithType(_ type: DKType!, _ variables: [DKType]) throws -> DKExpression {
		let t = try parseType()
		try expectReservedWord(":")
		if type != nil && type! != t {
			throw DKParsingError("Type mismatch \(type!) vs. \(t) for expression", token)
		}
		return try parseExpression(t, variables)
	}
	func parseExpressionConstant(_ type: DKType!, _ variables: [DKType]) throws -> DKExpression {
		let v = try parseValue(type)
		return DKExpressionConstant(v)
	}
	func parseExpressionVariable(_ type: DKType!, _ variables: [DKType]) throws -> DKExpression {
		let s = maybeIdent()
		if s == nil || s!.unichar0() != "$" {
			throw DKParsingError("No match for expression variable", token)
		}
		let n = Int(s!.substringAfter(1))
		if n == nil {
			throw DKParsingError("No match for expression variable", token)
		}
		if n! >= variables.count {
			throw DKParsingError("No match for variable \(n!)", token)
		}
		let t = variables[n!]
		if type != nil && type! != t {
			throw DKParsingError("Mismatch for variable \(n!)", token)
		}
		return DKExpressionVariable(index: n!, type: t)
	}
	func parseExpressionApplication(_ type: DKType!, _ variables: [DKType]) throws -> DKExpression {
		throw DKParsingError("NYI", token)
	}
	func parseExpressionUnary(_ type: DKType!, _ variables: [DKType]) throws -> DKExpression {
		throw DKParsingError("NYI", token)
	}
	func parseExpressionParen(_ type: DKType!, _ variables: [DKType]) throws -> DKExpression {
		try expectReservedWord("(")
		let e = try parseExpression(type, variables)
		try expectReservedWord(")")
		return e
	}
}
