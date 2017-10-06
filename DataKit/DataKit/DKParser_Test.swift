//
//  DKParser_Test.swift
//  DataKit
//
//  Created by Bertrand Serlet on 10/5/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

extension DKParser {
	class func selfTest() {
		let uniquingTable = DKTypeTable()
		let parser = DKParser(uniquingTable, "(first: String, last: String, age: UInt8)")
		let studentType = try! parser.parseJustType()
		let sc = studentType.toTypeShortcut(uniquingTable)

		print("\nParsing types...")
		for s in ["Bool", "Void", "UInt8", "Int(32)", "UInt(64)", "()", "(first: String, last: String)", "(first: String)", "(String, UInt8)", "[UInt8]", "(UInt32, String) -> UInt32"] {
			let parser = DKParser(uniquingTable, s)
			let t = try! parser.parseJustType()
			print(">>> Parsed type string '\(s)' => '\(t.sugaredDescription(uniquingTable))'")
		}

		print("\nParsing values...")
		for (ts, s) in [
			("()", "nil"), ("Bool", "true"), ("Bool", "false"), ("Int64", "42"),
			("Int64", "-99"), ("Int64", "- 101"),
			("String", "\"Donald\""), ("\(sc)", "(\"Jo\", \"Y\", 21)"),
			("[UInt64]", "[1, 2, 3]")] {
			let parser = DKParser(uniquingTable, ts)
			let t = try! parser.parseJustType()
			let parser2 = DKParser(uniquingTable, s)
			let v = try! parser2.parseJustValue(t)
			assert(v.type == t)
			print(">>> Parsed '\(ts)' and '\(s)' as type \(t.sugaredDescription(uniquingTable)) and value \(v)")
		}

		print("\nParsing functions...")
		for s in [
			"(\(sc)) -> String : .last",
			"(UInt8, UInt8) -> UInt8 : +",
			"(\(sc)) -> Bool: { true }",
			"(\(sc)) -> Bool: { true || false }",
			"(\(sc)) -> Bool: { true == false }",
			"(\(sc)) -> \(sc): { $0 }",
			"(UInt64) -> Bool: { $0 == 42 }",
			"(\(sc)) -> String: { $0.first }",
			"(\(sc)) -> String: { $0.last }",
			"(\(sc)) -> Bool: { $0.last == \"Joe\"}",
			"(\(sc)) -> Bool: { $0.first == $0.last }",
			"([\(sc)]) -> [\(sc)]: filter( { true })",
			"([\(sc)]) -> [String]: map(.first)",
			"(UInt32, UInt32, UInt32) -> UInt32 : { $0 + $1 + $2 }",
			"(UInt32, UInt32, UInt32) -> UInt32 : { $0 * $1 + $2 }",
			"(UInt32, UInt32, UInt32) -> UInt32 : { $0 + $1 * $2 }",
			"((Int8) -> Int8: -)"
			] {
				let f = try! DKParser(uniquingTable, s).parseJustFunction(nil)
				print(">>> Function '\(s)' is parsed as '\(f)' of type '\(f.signature.sugaredDescription(uniquingTable))'")
		}

		print("\nParsing expressions...")
		for s in [
			"42", "(69)", "(12, 34)",
			"-42", "- 42", "-(42)",
			"(UInt64, UInt64, UInt64) -> UInt64 : *(3, 4, 5)"
			] {
			let e = try! DKParser(uniquingTable, s).parseJustExpression(nil)
			print(">>> Expression '\(s)' is parsed as '\(e.sugaredDescription(uniquingTable).desc)' of type '\(e.type.sugaredDescription(uniquingTable))'")
		}
		print("\nParsing tests done!\n")
		exit(0)

	}
}
