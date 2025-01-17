//
//  DKParserForType.swift
//  DataKit
//
//  Created by Bertrand Serlet on 10/5/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// A type is:
// - a predefined name like UInt8
// - a type constructor like Int(8), Compressed<[Student]>(deflate)
// - a struct like (first: String, last: String) or (String, String)
// - a sequence like [String]
// - a signature like (T1, T2) -> U

extension DKParser {
	func parseType() throws -> DKType {
		if token == nil {
			throw DKParsingError("Malformed type, no token found", self)
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
		throw DKParsingError("Malformed type, unexpected token", self)
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
			if params.count != 1 || !params[0].isInteger {
				throw DKParsingError("For type constructor \(typeName), improper parameters \(params)", self)
			}
			let numBits = UInt8(params[0].integerValue)
			return DKTypeInt.shared(signed: typeName == "Int", numBits: numBits)
		}
		if typeName == "Compressed" {
			try expectReservedWord("<")
			let base = try parseType()
			try expectReservedWord(">")
			let params = try parseTypeParameters()
			if params.count != 1 || !params[0].isString {
				throw DKParsingError("For type constructor \(typeName), improper parameters \(params)", self)
			}
			let compMethod = params[0].stringValue
			return DKTypeAnnotated(base: base, compressed: compMethod)
		}
		// Is it an alias?
		let sc = uniquingTable.aliasFor(typeName)
		let j: JSON = .string(sc == nil ? typeName : sc!)
		let t = j.toDKType(uniquingTable)
		if t == nil {
			throw DKParsingError("Unknown predefined type '\(typeName)'", self)
		}
		return t!
	}
	func parseTypeParameters() throws -> [JSON] {
		try expectReservedWord("(")
		let params = try parseJSONList(butoir: ")")
		try expectReservedWord(")")
		return params
	}
	func parseTypeSequence() throws -> DKTypeSequence {
		try expectReservedWord("[")
		let t = try parseType()
		try expectReservedWord("]")
		return DKTypeSequence(t)
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
					throw DKParsingError("Expecting field name", self)
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

