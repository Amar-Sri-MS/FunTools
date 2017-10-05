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
			print(">>> Parsed string '\(s)' => '\(t)'")
		}

		print("\nParsing values...")
		for (ts, s) in [("()", "nil"), ("Bool", "true"), ("Bool", "false"), ("Int64", "42"), ("String", "\"Donald\""), ("\(sc)", "(\"Jo\", \"Y\", 21)"), ("[UInt64]", "[1, 2, 3]")] {
			let parser = DKParser(uniquingTable, ts)
			let t = try! parser.parseJustType()
			let parser2 = DKParser(uniquingTable, s)
			let v = try! parser2.parseJustValue(t)
			assert(v.type == t)
			print(">>> Parsed type \(t) and value \(v)")
		}

		print("\nParsing functions...")
		for s in [
			"(\(sc)) -> String : .last",
			"(UInt8, UInt8) -> UInt8 : +",
			"(\(sc)) -> Bool: { true }"
			] {
				let f = try! DKParser(uniquingTable, s).parseJustFunction(nil)
				print(">>> Function '\(s)' is parsed as '\(f)' of type '\(f.signature)'")
		}

		print("\nParsing expressions...")
		for s in ["42", "(69)", "(12, 34)"] {
			let e = try! DKParser(uniquingTable, s).parseJustExpression(nil)
			print(">>> Expression '\(s)' is parsed as '\(e)' of type '\(e.type)'")
		}
		print("\nParsing tests done!\n")
		exit(0)

	}
}
