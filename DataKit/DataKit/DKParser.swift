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
	class func parseType(_ uniquingTable: DKTypeTable, _ input: String) throws -> DKType {
		let parser = DKParser(uniquingTable, input)
		let t = try parser.parseType()
		try parser.expectEOF()
		return t
	}
	class func parseValue(_ uniquingTable: DKTypeTable, _ input: String, _ type: DKType!) throws -> DKValue {
		let parser = DKParser(uniquingTable, input)
		let v = try parser.parseValue(type)
		try parser.expectEOF()
		return v
	}
	class func parseFunction(_ uniquingTable: DKTypeTable, _ input: String, _ signature: DKTypeSignature! = nil) throws -> DKFunction {
		let parser = DKParser(uniquingTable, input)
		let f = try parser.parseFunction(signature)
		try parser.expectEOF()
		return f
	}
	class func parseExpression(_ uniquingTable: DKTypeTable, _ input: String, _ type: DKType! = nil) throws -> DKExpression {
		let parser = DKParser(uniquingTable, input)
		let e = try parser.parseExpression(type, [])
		try parser.expectEOF()
		return e
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
			throw DKParsingError("Premature end expecting '\(word)'", self)
		}
		if !peekReservedWord(word) {
			throw DKParsingError("Expecting '\(word)' and got \(token!)", self)
		}
		accept()
	}
	func peekAnyPunctuationOrReservedWord() -> String! {
		if token == nil { return nil }
		switch token!.type {
		case let .reservedWord(s): return s
		case let .punctuation(ch): return String(ch)
		default: return nil
		}
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
			throw DKParsingError("Expected identifier", self)
		}
		accept()
		return s!
	}
	func parseNumber() throws -> UInt64 {
		if token == nil {
			throw DKParsingError("Expecting number", self)
		}
		switch token!.type {
		case let .natural(n):
			accept()
			return n
		default: throw DKParsingError("Expecting number", self)
		}
	}
	private func parseJSONNumber() throws -> JSON {
		switch token!.type {
			case let .natural(i):
				accept()
				return .integer(Int(Int64(bitPattern: i)))
			case .realPositive(let d):
				accept()
				return .real(d)
			default:
				throw DKParsingError("Error parsing JSON", self)
		}
	}
	private func parseJSONString() throws -> JSON {
		switch token!.type {
			case .stringLiteral(let s):
				accept()
				return .string(s)
			case .identifier(let s):
				accept()
				return .string(s)
			default:
				throw DKParsingError("Error parsing JSON", self)
		}
	}
	private func parseJSONWithSpecial(_ str: String) throws -> JSON {
		switch str {
			case "+":
				accept();
				return try parseJSONNumber()
			case "-":
				accept()
				let n = try parseJSONNumber()
				return n.isReal ? .real(-n.doubleValue) : .integer(-n.integerValue)
			case "(":
				accept()
				let array = try parseJSONList(butoir: ")")
				try expectReservedWord(")")
				return .array(array)
			case "{":
				accept()
				let dict = try parseJSONPairs(butoir: "}")
				try expectReservedWord("}")
				return .dictionary(dict)
			default:
				throw DKParsingError("Error parsing JSON", self)
		}
	}
	func parseJSON() throws -> JSON {
		switch token!.type {
			case .natural, .realPositive:
				return try parseJSONNumber()
			case .stringLiteral, .identifier:
				return try parseJSONString()
			case .punctuation(let ch):
				let s = String(ch)
				return try parseJSONWithSpecial(s)
			case .reservedWord(let s):
				return try parseJSONWithSpecial(s)
			default:
				throw DKParsingError("Error parsing JSON", self)
		}
	}
	// parse a comma-separated list of JSON expressions; butoir is not accepted
	func parseJSONList(butoir: String) throws -> [JSON] {
		var list: [JSON] = []
		while !peekReservedWord(butoir) {
			if token == nil {
				throw DKParsingError("Premature end in JSON list", self)
			}
			list |= try parseJSON()
			if !peekReservedWord(",") {
				break
			}
			accept()
		}
		return list
	}
	func parseJSONPairs(butoir: String) throws -> [String: JSON] {
		var dict: [String: JSON] = [:]
		while !peekReservedWord(butoir) {
			if token == nil {
				throw DKParsingError("Premature end in JSON list", self)
			}
			let keyj = try parseJSONString()
			let key = keyj.stringValue
			try expectReservedWord(":")
			let value = try parseJSON()
			dict[key] = value
			if !peekReservedWord(",") {
				break
			}
			accept()
		}
		return dict
	}
	func expectEOF() throws {
		if token != nil {
			throw DKParsingError("Extraneous token", self)
		}
	}
}

/*=============== PARSING ERROR ===============*/

public struct DKParsingError: Error, CustomStringConvertible {
	let message: String
	let position: LexerPosition
	let line: LexerLine
	let parser: DKParser
	let tokenRange: Range<LexerPosition>!	// nil => at end
	init(_ m: String, _ parser: DKParser) {
		self.parser = parser
		message = m
		let token = parser.token
		position = token?.range.lowerBound ?? "".unicodeScalars.startIndex
		line = token?.line ?? 0
		tokenRange = token?.range
//		print("Creating parsing error \(self)")
	}
	public var description: String {
		let rest: String = tokenRange == nil ? "<EOF>" : parser.lexer.originalString(from: tokenRange!.lowerBound)
		let start = rest.truncate(50)
		let more = start == rest ? "" : "..."
		return "*** Parsing error: \(message) at line: \(line) starting with: '\(start)\(more)'"
	}
}

