//
//  Students.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/29/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

import Foundation

func generateRandomStudent(id: Int) -> JSON {
	let firstNames = ["Mary", "Patricia", "Linda", "Barbara", "Elizabeth", "Jennifer", "Maria", "Susan", "Margaret", "Dorothy", "Joe", "James", "John", "Robert", "Michael", "William", "David"]
	assert(firstNames.count == 17) // prime
	let lastNames = ["Smith", "Johnson", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Anderson", "Jackson", "White", "Martin", "Martinez"]
	assert(lastNames.count == 13) // prime
	let first = firstNames[id % firstNames.count]
	let last = lastNames[id % lastNames.count]
	let age = 16 + (id % 7)
	let graduated = id % 2 == 0
	let hasGrant = id % 3 == 0
	let dict: [String: JSON] = [
		"first_name": .string(first),
		"last_name": .string(last),
		"age": .integer(age),
		"graduated": .bool(graduated),
		"has_grant": .bool(hasGrant),
		"id": .integer(id)
	]
	return .dictionary(dict)
}

func studentType() -> DKTypeStruct {
	let fields = ["first_name", "last_name", "age", "graduated", "has_grant", "id"]
	let types = [DKTypeString.string, DKTypeString.string, DKTypeInt.uint8, DKTypeInt.bool, DKTypeInt.bool, DKTypeInt.uint32]
	return DKTypeStruct(subTypes: types, subNames: fields, packed: true, alignmentInBits: 32)
}

func studentsType() -> DKTypeSequence {
	return DKTypeSequence(subType: studentType())
}

func generateDataWithStudents(_ num: Int) -> Data {
	var data = DataAsMutableBitStream()
	for id in 0 ..< num {
		data.pad(toByteAlign: 4)
		let student = generateRandomStudent(id: id)
		let dict = student.dictionaryValue
		let first = dict["first_name"]!.stringValue
		data.appendString(first)
		let last = dict["last_name"]!.stringValue
		data.appendString(last)
		let age = UInt8(dict["age"]!.integerValue)
		data.append(age)
		let g = dict["graduated"]!.boolValue
		let hg = dict["has_grant"]!.boolValue
		let bits: UInt8 = (g ? 1 : 0) + (hg ? 2 : 0)
		data.append(bits)
		let id32 = UInt32(id)
		data.pad(toByteAlign: 4)
		data.append(id32)
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
	let students = ts.fromDataLazy(data)
	students?.append(to: &output)
	return output.finishAndData()
}

func filterJoe(_ uniquingTable: DKTypeTable) -> DKValueFuncFilter {
	let t = studentType()
	let studentFirstName: DKValueFunc = DKValueFuncProjection(structType: t, fieldName: "first_name", uniquingTable)
	let v0 = DKExpressionVariable(index: 0, type: t)
	let expressionGetFirstName = DKExpressionFuncCall(fun: studentFirstName, arguments: [v0])
	let isEqualFunc: DKValueFunc = DKValueFuncOperator(oper: DKComparisonOperator(domain: DKTypeString.string, op: "==")!, uniquingTable)
	let kJoe: DKExpressionConstant = "Joe"
	let expressionFirstIsJoe: DKExpression = DKExpressionFuncCall(fun: isEqualFunc, arguments: [expressionGetFirstName, kJoe])
	let funcFirstIsJoe: DKValueFunc = DKValueFuncClosure(params: [t], body: expressionFirstIsJoe, uniquingTable)
	return DKValueFuncFilter(predicate: funcFirstIsJoe)
}

func generateFullName(_ uniquingTable: DKTypeTable) -> DKValueFuncClosure {
	let t = studentType()
	let v0 = DKExpressionVariable(index: 0, type: t)
	let studentFirstName: DKValueFunc = DKValueFuncProjection(structType: t, fieldName: "first_name", uniquingTable)
	let expressionGetFirstName = DKExpressionFuncCall(fun: studentFirstName, arguments: [v0])
	let studentLastName: DKValueFunc = DKValueFuncProjection(structType: t, fieldName: "last_name", uniquingTable)
	let expressionGetLastName = DKExpressionFuncCall(fun: studentLastName, arguments: [v0])
	let kSpace: DKExpressionConstant = "_"
	let oper = DKAlgebraicOperator(domain: DKTypeString.string, op: "|", arity: 3)!
	let catted = DKValueFuncOperator(oper: oper, uniquingTable)
	let expressionFullName: DKExpression = DKExpressionFuncCall(fun: catted, arguments: [expressionGetFirstName, kSpace, expressionGetLastName])
	return DKValueFuncClosure(params: [t], body: expressionFullName, uniquingTable)
}

func dumpFilterJoe(input: Data, _ uniquingTable: DKTypeTable) {
	let ts = studentsType()
	let t = studentType()
	let knowns = [t: "Student"]
	let filterFunc = filterJoe(uniquingTable)
	print("Filter = \(filterFunc.sugaredDescription(knowns))")
	let students = ts.fromDataLazy(data)
	let con = DKEvaluationContext()
	filterFunc.prepareToEvaluate(context: con)
	let filtered = filterFunc.evaluator(con, [DKExpressionConstant(students!)])
	print("Filtered Joes: \(filtered.description)")
	let fullNameGen = generateFullName(uniquingTable)
	print("Generate full name = \(fullNameGen.sugaredDescription(knowns))")
	for student in filtered as! DKValueLazySequence {
		let full = fullNameGen.evaluator(con, [DKExpressionConstant(student)])
		print("-> \(full.stringValue)")
	}
}
