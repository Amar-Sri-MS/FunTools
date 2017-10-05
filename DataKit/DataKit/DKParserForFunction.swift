//
//  DKParserForFunction.swift
//  DataKit
//
//  Created by Bertrand Serlet on 10/5/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// A function may be given a signature, or have an explicit type: <signature> : <function>
// The body can be:
// - an operator like + - * / && || ^ ! | < > == != <= >=
// - a projection like .first_name
// - a functional constructor like filter(<predicate>) or map(.first_name) or compose(<f1>, <f2>)
// - a closure like { $0.first == "Joe" }

extension DKParser {
	func parseFunction(_ signature: DKTypeSignature!) throws -> DKFunction {
		var sig = signature
		let saved = (token, lexerState)
		do {
			let t = try parseType()
			if !(t is DKTypeSignature) {
				throw DKParsingError("Function type is not a signature \(t)", token)
			}
			try expectReservedWord(":")
			sig = t as? DKTypeSignature
		} catch _ {
			(currentToken, lexerState) = saved
		}
		return try parseFunctionBody(sig!)
	}
	func parseFunctionBody(_ signature: DKTypeSignature!) throws -> DKFunction {
		if token == nil {
			throw DKParsingError("Parsing function: premature end", token)
		}
		switch token!.type {
		case let .identifier(s):
			if signature == nil {
				throw DKParsingError("Function constructor needs a signature", token)
			}
			return try parseFunctionConstructor(s, signature!)
		case let .punctuation(ch):
			if ch == "." {
				if signature == nil {
					throw DKParsingError("Function projection needs a signature", token)
				}
				return try parseProjection(signature!)
			}
			let s = String(ch)
			if DKOperator.allOperatorStrings.contains(s) {
				if signature == nil {
					throw DKParsingError("Function operator needs a signature", token)
				}
				accept()
				return try! parseOperatorFunction(s, signature!)
			}
			throw DKParsingError("Function can't start with punctuation \(s) - signature \(signature)", token)
		case let .reservedWord(s):
			if s == "{" {
				if signature == nil {
					throw DKParsingError("Function closure needs a signature", token)
				}
				print("Going to parse closure with type \(signature)")
				return try! parseClosure(signature!)
			}
			if DKOperator.allOperatorStrings.contains(s) {
				if signature == nil {
					throw DKParsingError("Function operator needs a signature", token)
				}
				accept()
				return try! parseOperatorFunction(s, signature!)
			}
			throw DKParsingError("Function can't start with word \(s) - signature \(signature)", token)
		default: throw DKParsingError("Unknown function", token)
		}
	}
	func parseClosure(_ signature: DKTypeSignature) throws -> DKFunctionClosure {
		try expectReservedWord("{")
		let variables = signature.input.subs
		let e = try parseExpression(signature.output, variables)
		try expectReservedWord("}")
		return DKFunctionClosure(params: variables, body: e, uniquingTable)
	}
	func parseOperatorFunction(_ op: String, _ signature: DKTypeSignature) throws -> DKFunction {
		if signature.output == DKTypeInt.bool && signature.numberOfArguments == 2 && signature.input[0] == signature.input[1] {
			let f = DKComparisonOperator(domain: signature.input[0], op: op)
			if f != nil { return DKFunctionOperator(oper: f!, uniquingTable) }
		}
		let f = DKAlgebraicOperator(domain: signature.output, op: op, arity: signature.numberOfArguments)
		if f != nil { return DKFunctionOperator(oper: f!, uniquingTable) }
		throw DKParsingError("Can't find operator '\(op)' with signature \(signature)", token)
	}
	func parseFunctionConstructor(_ s: String, _ signature: DKTypeSignature) throws -> DKFunction {
		enum Genre { case unary; case bookend }
		let constructors: [String: Genre] = [
			"filter": .unary,
			"map": .unary,
			"generator": .bookend,
			"sink": .bookend
		]
		let genre = constructors[s]
		if genre != nil {
			accept()
			try expectReservedWord("(")
			var f: DKFunction
			switch genre! {
			case .unary: f = try parseUnaryFunctionConstructor(s, signature)
			case .bookend: f = try parseSinkOrGen(s == "sink", signature)
			}
			try expectReservedWord(")")
			return f
		}
		throw DKParsingError("Unknown function constructor '\(s)' with signature \(signature)", token)
	}
	func parseUnaryFunctionConstructor(_ s: String, _ signature: DKTypeSignature) throws -> DKFunction {
		if s == "filter" {
			let predSig = DKFunctionFilter.canBeFilterAndPredicateSignature(signature)
			if predSig == nil {
				throw DKParsingError("Filter has wrong signature \(signature)", token)
			}
			let pred = try parseFunction(predSig)
			return DKFunctionFilter(predicate: pred)
		}
		if s == "map" {
			let eachSig = DKFunctionMap.canBeMapAndPredicateSignature(signature)
			if eachSig == nil {
				throw DKParsingError("Map has wrong signature \(signature)", token)
			}
			let each = try parseFunction(eachSig)
			return DKFunctionMap(each: each)
		}
		fatalError()
	}
	func parseSinkOrGen(_ sink: Bool, _ signature: DKTypeSignature) throws -> DKFunction {
		let itemType = sink ? DKFunctionSink.canBeSinkAndItemType(signature) : DKFunctionGenerator.canBeGeneratorAndItemType(signature)
		if itemType == nil {
			throw DKParsingError("Generator has wrong signature \(signature)", token)
		}
		let name = try parseIdent()
		// This is totally hackish
		var params: JSON = JSON.null
		if peekReservedWord(",") {
			accept()
			let num = try parseNumber()
			params = .integer(Int(num))
		}
		if sink {
			return DKFunctionSink(uniquingTable, name: name, itemType: itemType!)
		} else {
			return DKFunctionGenerator(uniquingTable, name: name, params: params, itemType: itemType!)
		}
	}
	func parseProjection(_ signature: DKTypeSignature) throws -> DKFunction {
		try expectReservedWord(".")
		if signature.numberOfArguments != 1 {
			throw DKParsingError("Projection has wrong signature \(signature)", token)
		}
		if let structType = signature.input[0] as? DKTypeStruct {
			if token == nil {
				throw DKParsingError("Premature end for projection", token)
			}
			var fieldIndex: Int! = nil
			switch token!.type {
			case let .natural(n):
				if n <= UInt64(structType.count) {
					fieldIndex = Int(n)
				}
			case let .identifier(s):
				fieldIndex = structType[s]
			default: break
			}
			if fieldIndex == nil {
				throw DKParsingError("Field improper for \(structType)", token)
			}
			accept()
			return DKFunctionProjection(structType: structType, fieldIndex: fieldIndex!, uniquingTable)
		} else {
			throw DKParsingError("Projection has wrong signature \(signature)", token)
		}
	}
}
