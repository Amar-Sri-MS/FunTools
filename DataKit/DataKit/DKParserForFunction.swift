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
// - a functional constructor like filter(<predicate>) or map(.first_name) or reduce(0, +) or compose(<f1>, <f2>) or logger() or compress("deflate") or decompress("deflate")
// - a closure like { $0.first == "Joe" }
// - or a parenthesized function, e.g. ((Int8) -> Int8: -)

extension DKParser {
	enum ConstructorGenre { case noarg; case unary; case binary; case generator }
	func parseFunction(_ signature: DKTypeSignature!) throws -> DKFunction {
		var sig = signature
		let saved = (token, lexerState)
		do {
			let t = try parseType()
			if !(t is DKTypeSignature) {
				throw DKParsingError("Function type is not a signature \(t)", self)
			}
			try expectReservedWord("|")
			if sig != nil && signature != nil && sig! != signature! {
				throw DKParsingError("Function type mismatch \(sig!) vs. \(signature!)", self)
			}
			sig = t as? DKTypeSignature
		} catch _ {
			(currentToken, lexerState) = saved
		}
//		print("In parseFunction(\(signature) got sig now=\(sig)")
		return try parseFunctionBody(sig)
	}
	func parseFunctionReturning(_ retType: DKType!) throws -> DKFunction {
		// TODO: Implement this!
		return try parseFunction(nil)
	}
	func parseFunctionBody(_ signature: DKTypeSignature!) throws -> DKFunction {
		if token == nil {
			throw DKParsingError("Parsing function: premature end", self)
		}
		switch token!.type {
		case let .identifier(s):
			return try parseFunctionConstructor(s, signature)
		case let .punctuation(ch):
			if ch == "." {
				if signature == nil {
					throw DKParsingError("Function projection needs a signature", self)
				}
				if signature.numberOfArguments != 1 {
					throw DKParsingError("Projection has wrong signature \(signature)", self)
				}
				if let structType = signature.input[0] as? DKTypeStruct {
					let f = try parseFunctionProjection(structType)
					if f.signature.output != signature.output {
						throw DKParsingError("Projection has type mismatch \(f.signature.output) vs. \(signature.output)", self)
					}
					return f
				} else {
					throw DKParsingError("Projection has non-struct argument \(signature)", self)
				}
			}
			let s = String(ch)
			if DKOperator.allOperatorStrings.contains(s) {
				if signature == nil {
					throw DKParsingError("Function operator needs a signature", self)
				}
				accept()
				return try parseOperatorFunction(s, signature!)
			}
			throw DKParsingError("Function can't start with punctuation \(s) - signature \(signature)", self)
		case let .reservedWord(s):
			if s == "(" {
				accept()
				let f = try parseFunction(signature)
				try expectReservedWord(")")
				return f
			}
			if s == "{" {
				return try parseClosure(signature)
			}
			if DKOperator.allOperatorStrings.contains(s) {
				if signature == nil {
					throw DKParsingError("Function operator needs a signature", self)
				}
				accept()
				return try parseOperatorFunction(s, signature!)
			}
			throw DKParsingError("Function can't start with word '\(s)' - signature \(signature)", self)
		default: throw DKParsingError("Unknown function", self)
		}
	}
	func parseClosure(_ signature: DKTypeSignature!) throws -> DKFunctionClosure {
		try expectReservedWord("{")
		let variables = signature?.input.subs ?? [DKType]()
		let e = try parseExpression(signature?.output, variables)
		try expectReservedWord("}")
		return DKFunctionClosure(params: variables, body: e, uniquingTable)
	}
	func parseOperatorFunction(_ op: String, _ signature: DKTypeSignature) throws -> DKFunction {
		if signature.output == .bool && signature.numberOfArguments == 2 && signature.input[0] == signature.input[1] {
			let f = DKComparisonOperator(domain: signature.input[0], op: op)
			if f != nil { return DKFunctionOperator(oper: f!, uniquingTable) }
		}
		let f = DKAlgebraicOperator(domain: signature.output, op: op, arity: signature.numberOfArguments)
		if f != nil { return DKFunctionOperator(oper: f!, uniquingTable) }
		throw DKParsingError("Can't find operator '\(op)' with signature \(signature)", self)
	}
	func parseFunctionConstructor(_ s: String, _ signature: DKTypeSignature!) throws -> DKFunction {
		let constructors: [String: ConstructorGenre] = [
			"logger": .noarg,
			"filter": .unary,
			"map": .unary,
			"compress": .unary,
			"decompress": .unary,
			"reduce": .binary,
			"compose": .binary,
			"generator": .generator,
		]
		let parserFunc: [ConstructorGenre: (String, DKTypeSignature?) throws -> DKFunction] = [
			.noarg: parseNoargFunctionConstructor,
			.unary: parseUnaryFunctionConstructor,
			.binary: parseBinaryFunctionConstructor,
			.generator: parseGen
		]
		let genre = constructors[s]
		if genre != nil {
			accept()
			try expectReservedWord("(")
			let f: DKFunction = try parserFunc[genre!]!(s, signature)
			try expectReservedWord(")")
			return f
		}
		throw DKParsingError("Unknown function constructor '\(s)' with signature \(signature)", self)
	}
	func parseNoargFunctionConstructor(_ s: String, _ signature: DKTypeSignature!) throws -> DKFunction {
		if signature == nil || signature!.numberOfArguments != 1 {
			throw DKParsingError("Function constructor '\(s)' needs a signature", self)
		}
		if s == "logger" {
			return DKFunctionLogger(uniquingTable, signature.input[0])
		}
		fatalError()
	}
	// Does not parse the "(" nor ")"
	func parseUnaryFunctionConstructor(_ s: String, _ signature: DKTypeSignature!) throws -> DKFunction {
		if s == "filter" {
			var predSig: DKTypeSignature! = nil
			if signature != nil {
				predSig = DKFunctionFilter.canBeFilterAndPredicateSignature(signature)
				if predSig == nil {
					throw DKParsingError("Filter has wrong signature \(signature!)", self)
				}
			}
			let pred = try parseFunction(predSig)
			return DKFunctionFilter(predicate: pred)
		}
		if s == "map" {
			var eachSig: DKTypeSignature! = nil
			if signature != nil {
				eachSig = DKFunctionMap.canBeMapAndPredicateSignature(signature)
				if eachSig == nil {
					throw DKParsingError("Map has wrong signature \(signature)", self)
				}
			}
			let each = try parseFunction(eachSig)
			return DKFunctionMap(each: each)
		}
		if s == "compress" || s == "decompress" {
			let c = s == "compress"
			if signature == nil {
				throw DKParsingError("Signature must be provided for \(s)", self)
			}
			if !DKFunctionCompress.canBeSignature(signature: signature!, compress: c) {
				throw DKParsingError("Signature \(signature!) improper for \(s)", self)
			}
			let arg = try parseJSON()
			if !arg.isString {
				throw DKParsingError("Expecting compress method for \(s) instead of \(arg)", self)
			}
			let base = c ? signature!.input[0] : signature.output
			return DKFunctionCompress(uniquingTable, base: base, compress: c, method: arg.stringValue)
		}
		fatalError()
	}
	// Does not parse the "(" nor ")"
	func parseBinaryFunctionConstructor(_ s: String, _ signature: DKTypeSignature!) throws -> DKFunction {
		if s == "reduce" {
			var eachSig: DKTypeSignature! = nil
			var initialValueType: DKTypeInt! = nil
			if signature != nil {
				eachSig = DKFunctionReduce.canBeReduceSignature(signature)
				if eachSig == nil {
					throw DKParsingError("Reduce has wrong signature \(signature)", self)
				}
				if signature.output is DKTypeInt {
					initialValueType = signature.output as! DKTypeInt
				} else {
					throw DKParsingError("Reduce has wrong signature \(signature) - output limited to number", self)
				}
			}
			let initJSON = try parseJSON()
			try expectReservedWord(",")
			let each = try parseFunction(eachSig)
			let initialValue = DKValueSimple(potentialType: initialValueType, json: initJSON)
			if initialValue == nil {
				throw DKParsingError("Reduce has wrong initial value", self)
			}
			let fun = DKFunctionReduce(initialValue: initialValue!, each: each)
			return fun
		}
		if s == "compose" {
			var intermediateType: DKType! = nil
			var outer: DKFunction! = nil
			var inner: DKFunction! = nil
			func outerSig() -> DKTypeSignature! {
				if signature == nil || intermediateType == nil {
					return nil
				}
				return DKTypeSignature(unaryArg: intermediateType!, output: signature!.output)
			}
			func innerSig() -> DKTypeSignature! {
				if signature == nil || intermediateType == nil {
					return nil
				}
				return DKTypeSignature(input: signature!.input, output: intermediateType!)
			}
			func setOuter(_ f: DKFunction) throws {
				if f.signature.numberOfArguments != 1 {
					throw DKParsingError("Compose: uncomposable signatures", self)
				}
				if intermediateType != nil && f.signature.input[0] != intermediateType! {
					throw DKParsingError("Compose: outer has unexpected signature", self)
				}
				if outer != nil {
					throw DKParsingError("Compose: outer set twice", self)
				}
				outer = f
				intermediateType = f.signature.input[0]
			}
			func setInner(_ f: DKFunction) throws {
				if signature != nil && signature.input != f.signature.input {
					throw DKParsingError("Compose: inner has unexpected signature", self)
				}
				if intermediateType != nil && f.signature.output != intermediateType! {
					throw DKParsingError("Compose: inner has unexpected signature", self)
				}
				if inner != nil {
					throw DKParsingError("Compose: inner set twice", self)
				}
				inner = f
				intermediateType = f.signature.output
			}
			// First we try to parse a argument keywords
			let keywords: Set<String> = ["first", "then"]
			while outer == nil || inner == nil {
				let keyword = maybeIdent()
				var isInner: Bool
				if keyword != nil && keywords.contains(keyword!) {
					accept()
					try expectReservedWord(":")
					isInner = keyword == "first"
				} else {
					isInner = outer != nil
				}
				let sig = isInner ? innerSig() : outerSig()
				let f = try parseFunction(sig)
				try (isInner ? setInner : setOuter)(f)
				if outer == nil || inner == nil {
					try expectReservedWord(",")
				}
			}
			return DKFunctionComposition(outer: outer!, inner: inner!)
		}
		fatalError()
	}
	func parseGen(_ s: String, _ signature: DKTypeSignature!) throws -> DKFunction {
		if signature == nil {
			throw DKParsingError("Function sink or generator needs a signature", self)
		}
		let itemType = DKFunctionGenerator.canBeGeneratorAndItemType(signature)
		if itemType == nil {
			throw DKParsingError("Generator has wrong signature \(signature)", self)
		}
		let name = try parseIdent()
		// This is totally hackish
		var params: JSON = JSON.null
		if peekReservedWord(",") {
			accept()
			let num = try parseNumber()
			params = .integer(Int(num))
		}
		return DKFunctionGenerator(uniquingTable, name: name, params: params, itemType: itemType!)
	}
	func parseFunctionProjection(_ structType: DKTypeStruct) throws -> DKFunction {
		try expectReservedWord(".")
		if token == nil {
			throw DKParsingError("Premature end for projection", self)
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
			throw DKParsingError("Field improper for \(structType)", self)
		}
		accept()
		return DKFunctionProjection(structType: structType, fieldIndex: fieldIndex!, uniquingTable)
	}
}
