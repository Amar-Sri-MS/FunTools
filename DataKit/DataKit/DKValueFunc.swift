//
//  DKValueFunc.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/29/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// A function has a signature
// Currently we support only a finite number of "fixed" functions

class DKValueFunc: DKValue, DKValueIsEqualToOther {
	func isEqualTo(_ rhs: DKValue) -> Bool {
		fatalErrorMustBeImplementedBySubclass()
	}
	func prepareToEvaluate(context: DKEvaluationContext) {
		// nothing by default
	}
	var evaluator: DKNAryEvaluator {
		fatalErrorMustBeImplementedBySubclass()
	}
	class func fromRawJSON(_ uniquingTable: DKTypeTable, _ j: JSON) -> DKValueFunc! {
		for f in [DKValueFuncOperator.fromRawJSON, DKValueFuncProjection.fromRawJSON, DKValueFuncFilter.fromRawJSON, DKValueFuncClosure.fromRawJSON] {
			let v: DKValueFunc! = f(uniquingTable, j)
			if v != nil { return v }
		}
		return nil
	}
	var signature: DKTypeSignature {
		return type as! DKTypeSignature
	}
}

class DKValueFuncOperator: DKValueFunc {
	let oper: DKOperator
	let domainShortcut: DKType.Shortcut // derived from signature
	init(oper: DKOperator, _ uniquingTable: DKTypeTable) {
		// We make sure we have all the proper types
		domainShortcut = oper.baseType.toTypeShortcut(uniquingTable)
		self.oper = oper
	}
	override var type: DKType { return oper.signature }
	override func isEqualTo(_ rhs: DKValue) -> Bool {
		if let r = rhs as? DKValueFuncOperator {
			return oper == r.oper
		}
		return false
	}
	override var rawValueToJSON: JSON {
		var dict: [String: JSON] = [
			"op": .string(oper.op),
			"domain": domainShortcut.toJSON
		]
		if let a = oper as? DKAlgebraicOperator {
			dict["genre"] = .string("algebraic")
			dict["arity"] = .integer(a.arity)
		} else if let _ = oper as? DKComparisonOperator {
			dict["genre"] = .string("comparison")
		}
		return .dictionary(dict)
	}
	override class func fromRawJSON(_ uniquingTable: DKTypeTable, _ j: JSON) -> DKValueFuncOperator! {
		let dict = j.dictionaryValue
		if dict["op"] == nil { return nil }
		let op = dict["op"]!.stringValue
		let domain = dict["domain"]?.toDKType(uniquingTable)
		if domain == nil { return nil }
		if dict["genre"] == "algebraic" {
			let arity = dict["arity"]!.integerValue
			let oper = DKAlgebraicOperator(domain: domain!, op: op, arity: arity)
			return DKValueFuncOperator(oper: oper!, uniquingTable)
		} else if dict["genre"] == "comparison" {
			let oper = DKComparisonOperator(domain: domain!, op: op)
			return DKValueFuncOperator(oper: oper!, uniquingTable)
		} else {
			return nil
		}
	}
	override var evaluator: DKNAryEvaluator {
		return oper.evaluator
	}
	override var description: String {
		return oper.op
	}
	override func sugaredDescription(_ knowns: [DKType: String]) -> String {
		return oper.op
	}
}

class DKValueFuncProjection: DKValueFunc {
	let structType: DKTypeStruct
	let fieldIndex: Int
	let domainShortcut: DKType.Shortcut
	init(structType: DKTypeStruct, fieldIndex: Int, _ uniquingTable: DKTypeTable) {
		assert(fieldIndex < structType.count)
		self.structType = structType
		self.fieldIndex = fieldIndex
		domainShortcut = structType.toTypeShortcut(uniquingTable)
	}
	convenience init(structType: DKTypeStruct, fieldName: String, _ uniquingTable: DKTypeTable) {
		let i: Int? = structType[fieldName]
		assert(i != nil)
		self.init(structType: structType, fieldIndex: i!, uniquingTable)
	}
	override func isEqualTo(_ rhs: DKValue) -> Bool {
		if let r = rhs as? DKValueFuncProjection {
			return structType == r.structType && fieldIndex == r.fieldIndex
		}
		return false
	}
	override var type: DKType {
		let input = DKTypeStruct(funcParamType: structType, repeated: 1)
		return DKTypeSignature(input: input, output: structType[fieldIndex])
	}
	override var evaluator: DKNAryEvaluator {
		return {  context, subs in
			assert(subs.count == 1)
			let x = subs[0].evaluate(context: context)
			if let s = x as? DKValueLazyStruct {
				return s.subValueAt(self.fieldIndex)
			}
			if let structType = x.type as? DKTypeStruct {
				let j = x.rawValueToJSON.arrayValue
				return DKValueSimple(type: structType[self.fieldIndex], json: j[self.fieldIndex])
			}
			fatalError("*** Expecting a struct \(self.structType) instead got value \(x)")
		}
	}
	override var rawValueToJSON: JSON {
		let dict: [String: JSON] = [
			"projection": .integer(fieldIndex),
			"domain": domainShortcut.toJSON
		]
		return .dictionary(dict)
	}
	override class func fromRawJSON(_ uniquingTable: DKTypeTable, _ j: JSON) -> DKValueFunc! {
		let dict = j.dictionaryValue
		let p = dict["projection"]
		if p == nil { return nil }
		let t = dict["domain"]?.toDKType(uniquingTable) as? DKTypeStruct
		if t == nil { return nil }
		return DKValueFuncProjection(structType: t!, fieldIndex: p!.integerValue, uniquingTable)
	}
	var projectedFieldName: String {
		return structType.names == nil ? fieldIndex.description : structType.names![fieldIndex]
	}
	override var description: String {
		return "{ $0.\(projectedFieldName) }"
	}
}

class DKValueFuncFilter: DKValueFunc {
	let predicate: DKValueFunc
	init(predicate: DKValueFunc) {
		assert(predicate.signature.isPredicate)
		self.predicate = predicate
	}
	var itemType: DKType { return predicate.signature.input[0] }
	var sequenceType: DKType { return DKTypeSequence(subType: itemType) }
	var paramsType: DKTypeStruct { return DKTypeStruct(funcParamType: sequenceType, repeated: 1) }
	override var type: DKType {
		return DKTypeSignature(input: paramsType, output: sequenceType)
	}
	override var rawValueToJSON: JSON {
		let dict: [String: JSON] = [
			"filter": predicate.rawValueToJSON
		]
		return .dictionary(dict)
	}
	override class func fromRawJSON(_ uniquingTable: DKTypeTable, _ j: JSON) -> DKValueFunc! {
		let dict = j.dictionaryValue
		let filter = dict["filter"]
		if filter == nil { return nil }
		let p = DKValueFunc.fromRawJSON(uniquingTable, filter!)
		if p == nil { return nil }
		return DKValueFuncFilter(predicate: p!)
	}
	override func prepareToEvaluate(context: DKEvaluationContext) {
		print("SHOULD PREPARE STREAM PAIR")
	}
	override var evaluator: DKNAryEvaluator {
		return {  context, subs in
			assert(subs.count == 1)
			let x = subs[0].evaluate(context: context)
			var output: DKMutableBitStream = DataAsMutableBitStream()
			func applyPredicate(_ item: DKValue) {
				let expr = DKExpressionConstant(item)
				let r = self.predicate.evaluator(context, [expr])
				let b = r.boolValue
				if b {
					item.append(to: &output)
				}
			}
			if let explicit = x as? DKValueSimple {
				explicit.forEach(applyPredicate)
			} else if let valueSeq = x as? DKValueLazySequence {
				valueSeq.forEach(applyPredicate)
			} else {
				abort()
			}
			print("*** WRONG HERE: Input should be created right away")
			let newInput = output.finishAndData()
			return DKValueLazySequence(itemType: self.itemType, data: newInput)
		}
	}
	override var description: String {
		return "filter(\(predicate))"
	}
	override func sugaredDescription(_ knowns: [DKType: String]) -> String {
		return "filter(\(predicate.sugaredDescription(knowns)))"
	}
}

// Create a closure that requires parameters of type params
// When evaluating, binds each argument to $0, $1, ...
class DKValueFuncClosure: DKValueFunc {
	let structParams: DKTypeStruct
	let body: DKExpression
	let paramsShortcut: DKType.Shortcut	// derived
	let bodyJSON: JSON	// we compute the expression serialization at creation type to avoid needing to create types later
	init(structParams: DKTypeStruct, body: DKExpression, _ uniquingTable: DKTypeTable) {
		self.structParams = structParams
		self.body = body
		paramsShortcut = structParams.toTypeShortcut(uniquingTable)
		bodyJSON = body.expressionToJSON(uniquingTable)
	}
	convenience init(params: [DKType], body: DKExpression, _ uniquingTable: DKTypeTable) {
		self.init(structParams: DKTypeStruct(funcParams: params), body: body, uniquingTable)
	}
	override var type: DKType { return DKTypeSignature(input: structParams, output: body.type) }
	override var rawValueToJSON: JSON {
		let dict: [String: JSON] = [
			"closure": .string(paramsShortcut),
			"body": bodyJSON
		]
		return .dictionary(dict)
	}
	override class func fromRawJSON(_ uniquingTable: DKTypeTable, _ j: JSON) -> DKValueFunc! {
		let dict = j.dictionaryValue
		let structParams = dict["closure"]?.toDKType(uniquingTable) as? DKTypeStruct
		if structParams == nil { return nil }
		let body = dict["body"]?.toDKExpression(uniquingTable)
		if body == nil { return nil }
		return DKValueFuncClosure(structParams: structParams!, body: body!, uniquingTable)
	}
	override var evaluator: DKNAryEvaluator {
		return {  context, subs in
			assert(subs.count == self.structParams.subs.count)
			let evaluated = subs.map { $0.evaluate(context: context) }
			let newContext = context.newContextWith(values: evaluated)
			return self.body.evaluate(context: newContext)
		}
	}
	override var description: String {
		let p = structParams.subs.joinDescriptions(", ")
		return "{ (\(p)) -> \(body.type) in \(body) }"
	}
	override func sugaredDescription(_ knowns: [DKType: String]) -> String {
		let p = structParams.subs.joinDescriptions(", ") {
			$0.sugaredDescription(knowns)
		}
		return "{ (\(p)) -> \(body.type.sugaredDescription(knowns)) in \(body.sugaredDescription(knowns).desc) }"
	}
}


