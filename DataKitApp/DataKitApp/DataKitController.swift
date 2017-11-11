//
//  DataKitController.swift
//  DataKitApp
//
//  Created by Bertrand Serlet on 11/10/17.
//  Copyright © 2017 Bertrand Serlet. All rights reserved.
//

import Foundation

class DataKitController {
	var isStudents = false
	var numGenerated = 100
	init() {
		registerGeneratorOfStudents(typeTable: typeTable)
		typeTable.noteAlias("Student", studentType())
	}
	let predefArray = [
		("all", "map(logger())"),
		("", ""),
		("all ints (typed)", "map((UInt64) -> () | logger())"),
		("all * 100", "compose(\n" +
			"    first: map((UInt64) -> UInt64 | { $0 * 100 }),\n" +
			"    then: map(logger())\n" +
			")"),
		("all smaller than 10000", "compose(\n" +
			"    first:  filter((UInt64) -> Bool | { $0 < 10000}),\n" +
			"    then: map(logger())\n" +
			")"),
		("more complex", "compose(\n" +
			"    first: compose(\n" +
			"        first: filter((UInt64) -> Bool | { $0 < 100000}),\n" +
			"        then: map((UInt64) -> UInt64 | { $0 * 1000 + 42})\n" +
			"    ),\n" +
			"    then: map(logger())\n" +
			")"),
		("", ""),
		("all Students (typed)", "map((Student) -> () | logger())"),
		("all Joes", "compose(\n" +
			"    first: filter((Student) -> Bool | { $0.first_name == \"Joe\"}), \n" +
			"    then: map(logger())\n" +
			")"),
		("all Joe Smith", "compose(\n" +
			"    first: compose(\n" +
			"        first: filter((Student) -> Bool | { $0.last_name == \"Smith\"}),\n" +
			"        then: filter((Student) -> Bool | { $0.first_name == \"Joe\"})),\n" +
			"    then: map(logger())\n" +
			")"),
		("all full names", "compose(\n" +
			"    first: map((Student) -> String | { $0.first_name+\" \"+$0.last_name}),\n" +
			"    then: map(logger())\n" +
			")")
	]
	let typeTable = DKTypeTable()
	func baseType() -> DKType {
		return isStudents ? studentType() : DKTypeInt.uint64
	}
	func generator() -> DKFunctionGenerator {
		return DKFunctionGenerator(typeTable, name: isStudents ? "Students" : "RandomInts", params: .integer(numGenerated), itemType: baseType())
	}
	func flowGraphGenerator(_ pipeline: String) throws -> (DKFlowGraphGen, String) {
		let sig = DKTypeSignature(unaryArg: DKTypeSequence(subType: baseType()), output: .void)
		var pipeStringCooked = pipeline
		if isStudents {
			let sc = baseType().toTypeShortcut(typeTable)
			pipeStringCooked = pipeline.replaceOccurrences("Student", sc)
		}
		let pipeline = try DKParser.parseFunction(typeTable, pipeStringCooked, sig)
		let fgg = DKFlowGraphGen(typeTable, generator(), pipeline)
		return (fgg, pipeline.description)
	}
}
