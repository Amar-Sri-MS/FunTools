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
	func parseType() throws -> DKType {
		let t = try parseTypeInternal()
		if token == nil { return t }
		throw DKParsingError("Malformed type, after \(t)", token)
	}
}

/*=============== PRIVATE IMPLEMENTATION ===============*/

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
	func parseIdent() -> String! {
		if token == nil { return nil }
		switch token!.type {
		case let .identifier(s): return s
		default: return nil
		}
	}
	func parseTypeInternal() throws -> DKType {
		// A type is:
		// - a predefined name like UInt8
		// - a type constructor like Int(8)
		// - a struct like (first: String, last: String) or (String, String)
		// - a sequence like [String]
		// - a signature like T -> U
		if token == nil {
			throw DKParsingError("Malformed type, no token found", token)
		}
		let s = parseIdent()
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
			let u = try parseTypeInternal()
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
		let t = try parseTypeInternal()
		try expectReservedWord("]")
		return DKTypeSequence(subType: t)
	}
	func parseTypeStruct() throws -> DKTypeStruct {
		try expectReservedWord("(")
		var names: [String]! = nil
		var types: [DKType] = []
		let f = parseIdent()
		if f != nil {
			// We could have ':' for a field name, or not, in which case we have a type
			accept()
			if peekReservedWord(":") {
				accept()
				names = [f!]
				let t = try parseTypeInternal()
				types |= t
			} else {
				let t = try finishParsingPredefOrConstructor(f!)
				types |= t
			}
		} else if peekReservedWord(")") {
			accept()
			return DKTypeStruct.void
		} else {
			let t = try parseTypeInternal()
			types |= t
		}
		while peekReservedWord(",") {
			accept()
			if names == nil {
				let t = try parseTypeInternal()
				types |= t
			} else {
				let f = parseIdent()
				if f == nil {
					throw DKParsingError("Expecting field name", token)
				}
				accept()
				try expectReservedWord(":")
				let t = try parseTypeInternal()
				names! |= f!
				types |= t
			}
		}
		try expectReservedWord(")")
		return DKTypeStruct(subTypes: types, subNames: names)
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
		for s in ["Bool", "UInt8", "Int(32)", "UInt(64)", "()", "(first: String, last: String)", "(first: String)", "(String, UInt8)", "[UInt8]", "(UInt32, String) -> UInt32"] {
			let parser = DKParser(uniquingTable, s)
			let t = try! parser.parseType()
			print("String '\(s)' => '\(t)'")
		}
	}
}
