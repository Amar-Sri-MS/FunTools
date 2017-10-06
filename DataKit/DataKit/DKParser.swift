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
	func parseJustValue(_ type: DKType!) throws -> DKValue {
		let v = try parseValue(type)
		try expectEOF()
		return v
	}
	func parseJustFunction(_ signature: DKTypeSignature!) throws -> DKFunction {
		let f = try parseFunction(signature)
		try expectEOF()
		return f
	}
	func parseJustExpression(_ type: DKType!) throws -> DKExpression {
		let e = try parseExpression(type, [])
		try expectEOF()
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
			throw DKParsingError("Premature end expecting '\(word)'", token)
		}
		if !peekReservedWord(word) {
			throw DKParsingError("Expecting '\(word)' and got \(token!)", token)
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

/*=============== PARSING ERROR ===============*/

public struct DKParsingError: Error, CustomStringConvertible {
	let message: String
	let position: LexerPosition
	let line: LexerLine
	init(_ m: String, _ token: LexerToken?) {
		message = m
		position = token?.range.lowerBound ?? "".unicodeScalars.startIndex
		line = token?.line ?? 0
//		print("Creating parsing error \(self)")
	}
	public var description: String {
		return "*** Parsing error: \(message) at line: \(line)"
	}
}

