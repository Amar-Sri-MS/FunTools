//
//  DKParserForValue.swift
//  DataKit
//
//  Created by Bertrand Serlet on 10/5/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// A value is:
// - a predefined name like nil, true, false
// - a number like 42
// - a string like "Donald"
// - a struct like ("Abraham", "Lincoln")
// - a sequence like [1, 2, 3]

// TODO: real, functions

extension DKParser {
	func parseValue(_ type: DKType!) throws -> DKValue {
		if token == nil {
			throw DKParsingError("Expecting value", self)
		}
		switch token!.type {
		case let .natural(n):
			accept()
			return DKValueSimple(type: type ?? DKTypeInt.uint64, value: n)
		case let .stringLiteral(s):
			accept()
			if type != nil && type! != .string {
				throw DKParsingError("Parsed a string '\(s)' instead of a value of type \(type)", self)
			}
			return DKValueSimple(s.unquotedString(LexingStyle.JSON))
		case let .identifier(s):
			accept()
			if s == "nil" {
				if type != DKType.void {
					throw DKParsingError("Parsed nil instead of a value of type \(type)", self)
				}
				return .null
			}
			if s == "true" || s == "false" {
				if type != nil && type! != .bool {
					throw DKParsingError("Parsed a bool '\(s)' instead of a value of type \(type)", self)
				}
				return .bool(s == "true")
			}
			throw DKParsingError("Unexpect identifier '\(s)' for value", self)
		case let .reservedWord(s):
			if s == "(" {
				if type != nil && !(type is DKTypeStruct) {
					throw DKParsingError("Parsing a struct not \(type)", self)
				}
				return try parseValueStruct(type as? DKTypeStruct)
			}
			if s == "[" {
				if type != nil && !(type is DKTypeSequence) {
					throw DKParsingError("Parsing an array not \(type)", self)
				}
				return try parseValueSequence(type as? DKTypeSequence)
			}
			throw DKParsingError("Unexpected word '\(s)' for value", self)
		case let .punctuation(ch):
			if ch != "-" {
				throw DKParsingError("Unexpected punctuation for value", self)
			}
			accept()
			let n = try parseNumber()
			return DKValueSimple(type: type ?? DKTypeInt.int64, value: -Int64(bitPattern: n))
		default:
			throw DKParsingError("Unexpected token for value", self)
		}
	}
	func parseValueStruct(_ type: DKTypeStruct!) throws -> DKValue {
		try expectReservedWord("(")
		var jsons: [JSON] = []
		if type != nil {
			for t in type.subs {
				let v = try parseValue(t)
				jsons |= v.rawValueToJSON
				if peekReservedWord(")") { break }
				try expectReservedWord(",")
			}
			if jsons.count != type.subs.count {
				throw DKParsingError("Missing subvalues after \(jsons) for struct \(type)", self)
			}
			try expectReservedWord(")")
			return DKValueSimple(type: type, json: .array(jsons))
		} else {
			var types: [DKType] = []
			while !peekReservedWord(")") {
				let v = try parseValue(nil)
				jsons |= v.rawValueToJSON
				types |= v.type
				if peekReservedWord(")") { break }
				try expectReservedWord(",")
			}
			try expectReservedWord(")")
			return DKValueSimple(type: DKTypeStruct(subTypes: types, subNames: nil), json: .array(jsons))
		}
	}
	func parseValueSequence(_ type: DKTypeSequence!) throws -> DKValue {
		try expectReservedWord("[")
		var jsons: [JSON] = []
		var t = type?.sub
		while !peekReservedWord("]") {
			let v = try parseValue(t)
			if t == nil { t = v.type }
			jsons |= v.rawValueToJSON
			if peekReservedWord("]") { break }
			try expectReservedWord(",")
		}
		try expectReservedWord("]")
		if t == nil {
			throw DKParsingError("Need a type to parse an empty sequence of values", self)
		}
		return DKValueSimple(type: DKTypeSequence(subType: t!), json: .array(jsons))
	}
}
