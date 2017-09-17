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
	let types = [DKTypeString.string, DKTypeString.string, DKTypeInt.uint8, DKTypeInt.bool, DKTypeInt.bool, DKTypeInt.uint32]
	return DKTypeStruct(subTypes: types, subNames: fields, packed: true, alignmentInBits: 32)
}

func studentsType() -> DKTypeSequence {
	return DKTypeSequence(subType: studentType())
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
	let ts = studentsType()
	let students = ts.fromDataLazy(data)
	print("Got: \(students!.description)")

}

func regenerateData(input: Data) -> Data {
	var output: DKMutableBitStream = DataAsMutableBitStream()
	let ts = studentsType()
	let students = ts.fromDataLazy(input)
	students?.append(to: &output)
	return output.finishAndData()
}

func filterSpecificFirstOrLastName(_ uniquingTable: DKTypeTable, _ first: Bool, _ name: String) -> DKFunctionFilter {
	let t = studentType()
	let studentFirstName: DKFunction = DKFunctionProjection(structType: t, fieldName: first ? "first_name" : "last_name", uniquingTable)
	let v0 = DKExpressionVariable(index: 0, type: t)
	let expressionGetFirstName = DKExpressionFuncCall(fun: studentFirstName, arguments: [v0])
	let isEqualFunc: DKFunction = DKFunctionOperator(oper: DKComparisonOperator(domain: DKTypeString.string, op: "==")!, uniquingTable)
	let k = DKExpressionConstant(.string(name))
	let expressionFirstIsJoe: DKExpression = DKExpressionFuncCall(fun: isEqualFunc, arguments: [expressionGetFirstName, k])
	let funcFirstIsJoe: DKFunction = DKFunctionClosure(params: [t], body: expressionFirstIsJoe, uniquingTable)
	return DKFunctionFilter(predicate: funcFirstIsJoe)
}

func generateFullName(_ uniquingTable: DKTypeTable) -> DKFunctionClosure {
	let t = studentType()
	let v0 = DKExpressionVariable(index: 0, type: t)
	let studentFirstName: DKFunction = DKFunctionProjection(structType: t, fieldName: "first_name", uniquingTable)
	let expressionGetFirstName = DKExpressionFuncCall(fun: studentFirstName, arguments: [v0])
	let studentLastName: DKFunction = DKFunctionProjection(structType: t, fieldName: "last_name", uniquingTable)
	let expressionGetLastName = DKExpressionFuncCall(fun: studentLastName, arguments: [v0])
	let kSpace: DKExpressionConstant = "_"
	let oper = DKAlgebraicOperator(domain: DKTypeString.string, op: "|", arity: 3)!
	let catted = DKFunctionOperator(oper: oper, uniquingTable)
	let expressionFullName: DKExpression = DKExpressionFuncCall(fun: catted, arguments: [expressionGetFirstName, kSpace, expressionGetLastName])
	return DKFunctionClosure(params: [t], body: expressionFullName, uniquingTable)
}

func dumpFilter(input: Data, _ uniquingTable: DKTypeTable, _ name: String) {
	let ts = studentsType()
	let t = studentType()
	let knowns = [t: "Student"]
	let filterFunc = filterSpecificFirstOrLastName(uniquingTable, true, name)
	print("Filter = \(filterFunc.sugaredDescription(knowns))")
	let students = ts.fromDataLazy(input)
	let con = DKEvaluationContext()
	let filtered = filterFunc.evaluate(context: con, [students!.asExpressionConstant])
	print("Filtered: \(filtered.description)")
	let fullNameGen = generateFullName(uniquingTable)
	print("Generate full name = \(fullNameGen.sugaredDescription(knowns))")
	for student in filtered as! DKValueLazySequence {
		let full = fullNameGen.evaluate(context: con, [student.asExpressionConstant])
		print("-> \(full.stringValue)")
	}
}

var socket: Int32 = 0

func sendToDPCServer(_ combined: JSON) {
	print("Combined: \(combined)")
	let str = combined.description.replaceOccurrences("\n", " ")
	print("Single line: \n\(str)")
	let r = dpcrun_command_with_subverb_and_arg(&socket, "datakit", "setup", str)
	let rs: String = r == nil ? "NOPE" : String(cString: r!)
	print("r = \(rs)")
	sleep(1)
	let r2 = dpcrun_command_with_subverb(&socket, "datakit", "run")
	let rs2: String = r2 == nil ? "NOPE" : String(cString: r2!)
	print("r = \(rs2)")
}

func studentsTest() {
	let ts = studentsType()
	let t = studentType()
	let typeTable = DKTypeTable()

	var count = 0
	DKFunctionGenerator.registerItemGenerator(name: "Students") {
		if count >= $0.integerValue { return nil }
		let studentArray = generateRandomStudent(id: count)
		let student = t.valueFromRawJSON(typeTable, .array(studentArray))!
		count += 1
		return student
	}
	let generator = DKFunctionGenerator(typeTable, name: "Students", params: 100, itemType: t)
	let con = DKEvaluationContext()
	let students = generator.evaluate(context: con, [])
	var bs: DKMutableBitStream = DataAsMutableBitStream()
	students.append(to: &bs)
	let data1 = bs.finishAndData()

	let data = generateDataWithStudents(typeTable, 100)
	assert(data1 == data)

	let tsShortcut = ts.toTypeShortcut(typeTable)

	print("Students type = \(tsShortcut)")

	let name = "Mary"
	let filter: DKFunctionFilter = filterSpecificFirstOrLastName(typeTable, true, name)

	print("Students = \(data.debugDescription)")
	printStudentsDataStream(data: data)

	let regen = regenerateData(input: data)
	printStudentsDataStream(data: regen)

	let students2 = ts.fromDataLazy(data1)
	let logger = DKFunctionSink(typeTable, name: "logger", itemType: t)
	print("Log should start here")
	let result = logger.evaluate(context: con, [students2!.asExpressionConstant])
	print("Log finished - result = \(result)")
	let knowns = [studentType(): "Student"]

	assert(data == regen)
	dumpFilter(input: data, typeTable, name)

	try! data.write(to: "/tmp/students.data")
	try! generator.functionToJSON.writeToFile("/tmp/students_generator.json")
	try! filter.functionToJSON.writeToFile("/tmp/students_filter.json")
	try! logger.functionToJSON.writeToFile("/tmp/students_logger.json")
	try! typeTable.typeTableAsJSON.writeToFile("/tmp/students_types.json")

	let combined: JSON = .dictionary([
		"type_table": typeTable.typeTableAsJSON,
		"generator": generator.functionToJSON,
		"filter": filter.functionToJSON,
		"sink": logger.functionToJSON
	])
	sendToDPCServer(combined)
	print("\n")

	if true {
		let lastIsSmith = filterSpecificFirstOrLastName(typeTable, false, "Smith")
		let pipeline = DKFunctionComposition(outer: logger, inner: DKFunctionComposition(outer: lastIsSmith, inner: filter))
		print("Signature of pipeline: \(pipeline.signature)")
		let combined2: JSON = .dictionary([
			"type_table": typeTable.typeTableAsJSON,
			"generator": generator.functionToJSON,
			"pipeline": pipeline.functionToJSON
			])
		let flowGraphGen = DKFlowGraphGen(typeTable, generator, pipeline)
		let r = flowGraphGen.generate()
		for fifo in r.fifos {
			print("\(fifo.sugaredDescription(knowns))")
		}
		let j = flowGraphGen.flowGraphToJSON
		print("flow graph as JSON: \n\(j)")

		//		sendToDPCServer(combined2)
	}

}

