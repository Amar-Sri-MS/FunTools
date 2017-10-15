//
//  Students.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/29/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

import Foundation

func generateRandomStudent(id: Int) -> [JSON] {
	// Generates values in the fields order
	let firstNames = ["Mary", "Patricia", "Linda", "Barbara", "Elizabeth", "Jennifer", "Maria", "Susan", "Margaret", "Dorothy", "Joe", "James", "John", "Robert", "Michael", "William", "David"]
	assert(firstNames.count == 17) // prime
	let lastNames = ["Smith", "Johnson", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Anderson", "Jackson", "White", "Martin", "Martinez"]
	assert(lastNames.count == 13) // prime
	let first = firstNames[id % firstNames.count]
	let last = lastNames[id % lastNames.count]
	let age = 16 + (id % 7)
	let graduated = id % 2 == 0
	let hasGrant = id % 3 == 0
	return [
		.string(first),
		.string(last),
		.integer(age),
		.bool(graduated),
		.bool(hasGrant),
		.integer(id)
	]
}

func studentType() -> DKTypeStruct {
	let fields = ["first_name", "last_name", "age", "graduated", "has_grant", "id"]
	let types = [DKType.string, DKType.string, DKTypeInt.uint8, DKType.bool, DKType.bool, DKTypeInt.uint32]
	return DKTypeStruct(subTypes: types, subNames: fields, packed: true, alignmentInBits: 32)
}

func generateDataWithStudents(_ uniquingTable: DKTypeTable, _ num: Int) -> Data {
	var data: DKMutableBitStream = DataAsMutableBitStream()
	let t = studentType()
	for id in 0 ..< num {
		data.pad(toByteAlign: 4)
		let studentArray = generateRandomStudent(id: id)
		let student = t.valueFromRawJSON(uniquingTable, .array(studentArray))!
		data.pad(toByteAlign: 4)
		student.append(to: &data)
	}
	return data.finishAndData()
}

func printStudentsDataStream(data: Data) {
	let t = studentType()
	var addr = DKBitAddress(data: data, bitOffset: 0)
	while true {
		addr.bitOffset = t.forceAlignBitOffset(addr.bitOffset)
		let v = t.fromAddressAndAdvance(&addr)
		if v == nil { break }
		print("Got: \(v!.description)")
	}
	print("OR as 1 value: ")
	let ts = studentType().makeSequence
	let students = ts.fromDataLazy(data)
	print("Got: \(students!.description)")

}

func regenerateData(input: Data) -> Data {
	var output: DKMutableBitStream = DataAsMutableBitStream()
	let ts = studentType().makeSequence
	let students = ts.fromDataLazy(input)
	students?.append(to: &output)
	return output.finishAndData()
}

func filterSpecificFirstOrLastName(_ uniquingTable: DKTypeTable, _ first: Bool, _ name: String) -> DKFunctionFilter {
	let t = studentType()
	let seq = DKTypeSequence(subType: t)
	let sig = DKTypeSignature(unaryArg: seq, output: seq)
	return try! DKParser.parseFunction(uniquingTable, "filter({ $0.\(first ? "first_name" : "last_name") == \"\(name)\" })", sig) as! DKFunctionFilter
}

var socket: Int32 = 0

extension String {
	var asOneLine: String {
		var t = replaceOccurrences("\n", " ").replaceOccurrences("\t", " ")
		while true {
			let u = t.replaceOccurrences("  ", " ")
			if u == t { return t }
			t = u
		}
	}
}

func sendToDPCServer(_ combined: JSON) {
	print("Combined: \(combined)")
	let str = combined.description.asOneLine
	print("Single line: \n\(str)")
	let r = dpcrun_command_with_subverb_and_arg(&socket, "datakit", "setup", str)
	let rs: String = r == nil ? "NOPE" : String(cString: r!)
	print("r = \(rs)")
	sleep(1)
	let r2 = dpcrun_command_with_subverb(&socket, "datakit", "run")
	let rs2: String = r2 == nil ? "NOPE" : String(cString: r2!)
	print("r = \(rs2)")
}

func registerGeneratorOfStudents(typeTable: DKTypeTable) {
	let t = studentType()
	var count = 0
	DKFunctionGenerator.registerItemGenerator(name: "Students") {
		if count >= $0.integerValue { return nil }
		let studentArray = generateRandomStudent(id: count)
		let student = t.valueFromRawJSON(typeTable, .array(studentArray))!
		count += 1
		return student
	}

}
func registerGeneratorOfRandomInts(typeTable: DKTypeTable) {
	var count = 0
	DKFunctionGenerator.registerItemGenerator(name: "Students") {
		if count >= $0.integerValue { return nil }
		let i = UInt64.random() % 1_000_000
		let new = DKValue.int(type: DKTypeInt.uint64, intValue: i)
		count += 1
		return new
	}
}

let pipe0 = "map(logger())"

let pipe0b = "map((Student) -> () | logger())"

let pipe1 = "compose(" +
	"map((Student) -> () | logger()), " +
	"filter({ $0.first_name == \"Joe\"})" +
")"

let pipe2 = "compose(" +
	"map((Student) -> () | logger()), " +
	"compose(" +
	"filter((Student) -> Bool | { $0.first_name == \"Joe\"}), " +
	"filter({ $0.last_name == \"Smith\"})" +
	")" +
")"

//let pipeFullNames = "compose(" +
//	"map((String) -> () | logger()), " +
//	"map((Student) -> String | { $0.first_name + \"_\" + $0.last_name })" +
//")"

func studentsTestNew() {
	let pipeString = pipe2
	let t = studentType()
	let typeTable = DKTypeTable()
	registerGeneratorOfStudents(typeTable: typeTable)
	let generator = DKFunctionGenerator(typeTable, name: "Students", params: 1000, itemType: t)
	let seq = DKTypeSequence(subType: t)
	let sig = DKTypeSignature(unaryArg: seq, output: .void)
	let sc = t.toTypeShortcut(typeTable)
	let pipeline = try! DKParser.parseFunction(typeTable, pipeString.replaceOccurrences("Student", sc), sig)
	print("pipeline = \(pipeline)")
	let flowGraphGen = DKFlowGraphGen(typeTable, generator, pipeline)
	let r = flowGraphGen.generate()
	for fifo in r.fifos {
		print("\(fifo.sugaredDescription(typeTable))")
	}
	let j = flowGraphGen.flowGraphToJSON
	print("flow graph as JSON: \n\(j)")
	sendToDPCServer(j)
}

func studentsTest() {
	studentsTestNew()
}
