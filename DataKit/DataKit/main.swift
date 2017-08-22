//
//  main.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/21/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

DKType.selfTest()
DKExpression.selfTest()
DKBitAddress.selfTest()

let data = generateDataWithStudents(100)

let ts = studentsType()
var uniquingTable1 = DKTypeTable()
let tsShortcut = ts.toTypeShortcut(uniquingTable1)

print("Students type = \(tsShortcut)")

let filter: DKValueFuncFilter = filterJoe(uniquingTable1)

print("Students = \(data.debugDescription)")
printStudentsDataStream(data: data)

let regen = regenerateData(input: data)
printStudentsDataStream(data: regen)

assert(data == regen)
dumpFilterJoe(input: data, uniquingTable1)

try data.write(to: "/tmp/students.data")
try filter.valueToJSON(uniquingTable1).writeToFile("/tmp/students_filter.json")
try uniquingTable1.typeTableAsJSON.writeToFile("/tmp/students_type.json")

