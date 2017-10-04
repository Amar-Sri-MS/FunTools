//
//  DKParser.swift
//  DataKit
//
//  Created by Bertrand Serlet on 10/4/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

class DKParser {
	let lexer: Lexer
	var lexerState: LexerState
	var previousToken: LexerToken!  // kept for errors
	var currentToken: LexerToken! // current token
	var uniquingTable: DKTypeTable
	init(_ uniquingTable: DKTypeTable, _ input: String) {
		lexer = Lexer(input: input, lexingStyle: .Swift)
		lexerState = lexer.makeIterator()
		self.uniquingTable = uniquingTable
	}
	func parseJustType() throws -> DKType {
		let t = try parseType()
		try expectEOF()
		return t
	}
	func parseJustValue(_ type: DKType) throws -> DKValue {
		let v = try parseValue(type)
		try expectEOF()
		return v
	}
	func parseJustFunction(_ signature: DKTypeSignature!) throws -> DKFunction {
		let f = try parseFunction(signature)
		try expectEOF()
		return f
	}
}

/*=============== UTILITIES ===============*/

extension DKParser {
	var token: LexerToken! {
		if currentToken == nil {
			currentToken = lexerState.next()
			if currentToken != nil { previousToken = currentToken }
		}
		return currentToken
	}
	func accept() { currentToken = nil }
	func peekReservedWord(_ word: String) -> Bool {
		if token == nil { return false }
		switch token!.type {
			case let .reservedWord(s): return s == word
			case let .punctuation(ch):
				let s = String(ch)
				return s == word
			default: return false
		}
	}
	func expectReservedWord(_ word: String) throws {
		if token == nil {
			throw DKParsingError("Premature end expecting '\(word)'", token)
		}
		if !peekReservedWord(word) {
			throw DKParsingError("Expecting '\(word)' and got \(token!)", token)
		}
		accept()
	}
	func maybeIdent() -> String! {
		if token == nil { return nil }
		switch token!.type {
		case let .identifier(s): return s
		default: return nil
		}
	}
	func parseIdent() throws -> String {
		let s = maybeIdent()
		if s == nil {
			throw DKParsingError("Expected identifier", token)
		}
		accept()
		return s!
	}
	func parseNumber() throws -> UInt64 {
		if token == nil {
			throw DKParsingError("Expecting number", token)
		}
		switch token!.type {
		case let .natural(n):
			accept()
			return n
		default: throw DKParsingError("Expecting number", token)
		}
	}
	func expectEOF() throws {
		if token != nil {
			throw DKParsingError("Extraneous token", token)
		}
	}
}

/*=============== TYPES ===============*/

// A type is:
// - a predefined name like UInt8
// - a type constructor like Int(8)
// - a struct like (first: String, last: String) or (String, String)
// - a sequence like [String]
// - a signature like T -> U

extension DKParser {
	func parseType() throws -> DKType {
		if token == nil {
			throw DKParsingError("Malformed type, no token found", token)
		}
		let s = maybeIdent()
		if s != nil {
			accept()
			let t = try finishParsingPredefOrConstructor(s!)
			if t is DKTypeStruct {
				return try maybeMakeSignature(t as! DKTypeStruct)
			}
			return t
		}
		if peekReservedWord("(") {
			let t = try parseTypeStruct()
			return try maybeMakeSignature(t)
		}
		if peekReservedWord("[") {
			return try parseTypeSequence()
		}
		throw DKParsingError("Malformed type, unexpected token", token)
	}
	func maybeMakeSignature(_ base: DKTypeStruct) throws -> DKType {
		if peekReservedWord("->") {
			accept()
			let u = try parseType()
			let params = base.realignForFuncParams()
			return DKTypeSignature(input: params, output: u)
		}
		return base
	}
	func finishParsingPredefOrConstructor(_ typeName: String) throws -> DKType {
		if typeName == "Int" || typeName == "UInt" {
			let params = try parseTypeParameters()
			if params.count != 1 {
				throw DKParsingError("For type constructor \(typeName), improper parameters \(params)", token)
			}
			return DKTypeInt.shared(signed: typeName == "Int", numBits: UInt8(params[0]))
		}
		let j: JSON = .string(typeName)
		let t = j.toDKType(uniquingTable)
		if t == nil {
			throw DKParsingError("Unknown predefined type '\(typeName)'", token)
		}
		return t!
	}
	func parseTypeParameters() throws -> [Int] {
		var params: [Int] = []
		try expectReservedWord("(")
		while !peekReservedWord(")") {
			if token == nil {
				throw DKParsingError("Premature end in parameter list", token)
			}
			switch token!.type {
			case let .natural(i):
				accept()
				params |= Int(i)
			default:
				throw DKParsingError("Expecting number in parameter list", token)
			}
			if !peekReservedWord(",") {
				break
			}
			accept()
		}
		try expectReservedWord(")")
		return params
	}
	func parseTypeSequence() throws -> DKTypeSequence {
		try expectReservedWord("[")
		let t = try parseType()
		try expectReservedWord("]")
		return DKTypeSequence(subType: t)
	}
	func parseTypeStruct() throws -> DKTypeStruct {
		try expectReservedWord("(")
		var names: [String]! = nil
		var types: [DKType] = []
		let f = maybeIdent()
		if f != nil {
			// We could have ':' for a field name, or not, in which case we have a type
			accept()
			if peekReservedWord(":") {
				accept()
				names = [f!]
				let t = try parseType()
				types |= t
			} else {
				let t = try finishParsingPredefOrConstructor(f!)
				types |= t
			}
		} else if peekReservedWord(")") {
			accept()
			return DKTypeStruct.void
		} else {
			let t = try parseType()
			types |= t
		}
		while peekReservedWord(",") {
			accept()
			if names == nil {
				let t = try parseType()
				types |= t
			} else {
				let f = maybeIdent()
				if f == nil {
					throw DKParsingError("Expecting field name", token)
				}
				accept()
				try expectReservedWord(":")
				let t = try parseType()
				names! |= f!
				types |= t
			}
		}
		try expectReservedWord(")")
		return DKTypeStruct(subTypes: types, subNames: names)
	}
}

/*=============== VALUES ===============*/

// A value is:
// - a predefined name like nil, true, false
// - a number like 42
// - a string like "Donald"
// - a struct like ("Abraham", "Lincoln")
// - a sequence like [1, 2, 3]

// TODO: real, functions

extension DKParser {
	func parseValue(_ type: DKType) throws -> DKValue {
		if token == nil {
			throw DKParsingError("Expecting value", token)
		}
		switch token!.type {
		case let .natural(n):
			accept()
			return DKValueSimple(type: type, value: n)
		case let .stringLiteral(s):
			accept()
			if type != DKTypeString.string {
				throw DKParsingError("Parsed a string '\(s)' instead of a value of type \(type)", token)
			}
			return DKValueSimple(s)
		case let .identifier(s):
			accept()
			if s == "nil" {
				if type != DKType.void {
					throw DKParsingError("Parsed nil instead of a value of type \(type)", token)
				}
				return .null
			}
			if s == "true" || s == "false" {
				if type != DKTypeInt.bool {
					throw DKParsingError("Parsed a bool '\(s)' instead of a value of type \(type)", token)
				}
				return .bool(s == "true")
			}
			throw DKParsingError("Unexpect identifier '\(s)' for value", token)
		case let .reservedWord(s):
			if s == "(" {
				if !(type is DKTypeStruct) {
					throw DKParsingError("Parsing a struct not \(type)", token)
				}
				return try parseValueStruct(type as! DKTypeStruct)
			}
			if s == "[" {
				if !(type is DKTypeSequence) {
					throw DKParsingError("Parsing an array not \(type)", token)
				}
				return try parseValueSequence(type as! DKTypeSequence)
			}
			throw DKParsingError("Unexpected word '\(s)' for value", token)
		default:
			throw DKParsingError("Unexpected token for value", token)
		}
	}
	func parseValueStruct(_ type: DKTypeStruct) throws -> DKValue {
		try expectReservedWord("(")
		var jsons: [JSON] = []
		for t in type.subs {
			let v = try parseValue(t)
			jsons |= v.rawValueToJSON
			if peekReservedWord(")") { break }
			try expectReservedWord(",")
		}
		if jsons.count != type.subs.count {
			throw DKParsingError("Missing subvalues after \(jsons) for struct \(type)", token)
		}
		try expectReservedWord(")")
		return DKValueSimple(type: type, json: .array(jsons))
	}
	func parseValueSequence(_ type: DKTypeSequence) throws -> DKValue {
		try expectReservedWord("[")
		var jsons: [JSON] = []
		while !peekReservedWord("]") {
			let v = try parseValue(type.sub)
			jsons |= v.rawValueToJSON
			if peekReservedWord("]") { break }
			try expectReservedWord(",")
		}
		try expectReservedWord("]")
		return DKValueSimple(type: type, json: .array(jsons))
	}
}

/*=============== FUNCTIONS ===============*/

// A function may be given a signature, or have an explicit type: <signature> | <body>
// The body can be:
// - an operator like + - * / && || ^ ! | < > == != <= >=
// - a projection like .first_name
// - a functional constructor like filter(<predicate>) or map(.first_name) or compose(<f1>, <f2>)
//TODO
// - a closure

extension DKParser {
	func parseFunction(_ signature: DKTypeSignature!) throws -> DKFunction {
		var sig = signature
		if sig == nil {
			let t = try parseType()
			if !(t is DKTypeSignature) {
				throw DKParsingError("Function type is not a signature \(t)", token)
			}
			sig = t as? DKTypeSignature
			try expectReservedWord("|")
		}
		return try parseFunctionBody(sig!)
	}
	func parseFunctionBody(_ signature: DKTypeSignature) throws -> DKFunction {
		if token == nil {
			throw DKParsingError("Parsing function: premature end", token)
		}
		switch token!.type {
		case let .identifier(s):
			return try parseFunctionConstructor(s, signature)
		case let .punctuation(ch):
			if ch == "." {
				return try parseProjection(signature)
			}
			let s = String(ch)
			if DKOperator.allOperatorStrings.contains(s) {
				accept()
				return try! parseOperatorFunction(s, signature)
			}
			throw DKParsingError("Function can't start with punctuation \(s) - signature \(signature)", token)
		case let .reservedWord(s):
			if DKOperator.allOperatorStrings.contains(s) {
				accept()
				return try! parseOperatorFunction(s, signature)
			}
			throw DKParsingError("Function can't start with word \(s) - signature \(signature)", token)
		default: throw DKParsingError("Unknown function", token)
		}
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

/*=============== PARSING ERROR ===============*/

public struct DKParsingError: Error, CustomStringConvertible {
	let message: String
	let position: LexerPosition
	let line: LexerLine
	init(_ m: String, _ token: LexerToken?) {
		message = m
		position = token?.range.lowerBound ?? "".unicodeScalars.startIndex
		line = token?.line ?? 0
	}
	public var description: String {
		return "*** Parsing error: \(message) at line: \(line)"
	}
}

/*=============== TEST ===============*/

extension DKParser {
	class func selfTest() {
		let uniquingTable = DKTypeTable()
		for s in ["Bool", "Void", "UInt8", "Int(32)", "UInt(64)", "()", "(first: String, last: String)", "(first: String)", "(String, UInt8)", "[UInt8]", "(UInt32, String) -> UInt32"] {
			let parser = DKParser(uniquingTable, s)
			let t = try! parser.parseJustType()
			print(">>> Parsed string '\(s)' => '\(t)'")
		}
		for (ts, s) in [("()", "nil"), ("Bool", "true"), ("Bool", "false"), ("Int64", "42"), ("String", "\"Donald\""), ("(first: String, last: String, age: UInt8)", "(\"Jo\", \"Y\", 21)"), ("[UInt64]", "[1, 2, 3]")] {
			let parser = DKParser(uniquingTable, ts)
			let t = try! parser.parseJustType()
			let parser2 = DKParser(uniquingTable, s)
			let v = try! parser2.parseJustValue(t)
			assert(v.type == t)
			print(">>> Parsed type \(t) and value \(v)")
		}
		let f = try! DKParser(uniquingTable, "((first: String, last: String, age: UInt8)) -> String | .last").parseJustFunction(nil)
		print("Projection = \(f) of type \(f.signature)")
	}
}
