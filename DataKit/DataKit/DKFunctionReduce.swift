//
//  DKFunctionReduce.swift
//  DataKit
//
//  Created by Bertrand Serlet on 9/17/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// Reduce a function 'each' (U, T) -> U, given an initial value
// For example if the initial value is 0 and each is +, just adds
// The signature of reduce is ([T]) -> U

class DKFunctionReduce: DKFunction {
	let initialValue: DKValue
	let each: DKFunction
	init(initialValue: DKValue, each: DKFunction) {
		assert(each.signature.numberOfArguments == 2)
		assert(each.signature.input[0] == each.signature.output)
		assert(each.signature.output == initialValue.type)
		self.each = each
		self.initialValue = initialValue
	}
	var inputValueType: DKType { return each.signature.output }
	var outputType: DKType { return each.signature.output }
	var inputItemType: DKType { return each.signature.input[1] }
	var inputSequenceType: DKType { return inputItemType.makeSequence }
	var paramsType: DKTypeStruct { return DKTypeStruct(funcParamType: inputSequenceType) }
	override var signature: DKTypeSignature {
		return DKTypeSignature(input: paramsType, output: outputType)
	}
	// Given the type of the overal reduce, infers the type of 'each' if possible
	class func canBeReduceSignature(_ reduceType: DKType) -> DKTypeSignature! {
		if let signature = reduceType as? DKTypeSignature {
			let valueType = signature.output
			if signature.numberOfArguments != 1 || !(signature.input[0] is DKTypeSequence) {
				return nil
			}
			let seqType = signature.input[0] as! DKTypeSequence
			let eachInputType = DKTypeStruct(funcParams: [valueType, seqType.sub])
			return DKTypeSignature(input: eachInputType, output: valueType)
		}
		return nil
	}
	override var functionToJSONDict: [String: JSON] {
		return [
			"reduce": each.functionToJSON,
			"initial": initialValue.rawValueToJSON
		]
	}
	override class func functionFromJSON(_ uniquingTable: DKTypeTable, _ dict: [String: JSON]) -> DKFunction! {
		let m = dict["reduce"]
		if m == nil || !m!.isDictionary { return nil }
		let e = DKFunction.functionFromJSON(uniquingTable, m!.dictionaryValue)
		if e == nil { return nil }
		let initial = dict["initial"]
		if initial == nil { return nil }
		let vtype = e!.signature.output
		let iv = vtype.valueFromRawJSON(uniquingTable, initial!)
		if (iv == nil) || (iv!.type != vtype) { return nil }
		return DKFunctionReduce(initialValue: iv!, each: e!)
	}
	override func evaluate(context: DKEvaluationContext, _ subs: [DKExpression]) -> DKValue {
		assert(subs.count == 1)
		let x = subs[0].evaluate(context: context)
		var value = initialValue
		func applyEach(_ item: DKValue) {
			let expr = item.asExpressionConstant
			value = each.evaluate(context: context, [DKExpressionConstant(value), expr])
		}
		if let explicit = x as? DKValueSimple {
			explicit.forEach(applyEach)
		} else if let valueSeq = x as? DKValueLazySequence {
			valueSeq.forEach(applyEach)
		} else {
			abort()
		}
		return value
	}
	override var description: String {
		return "reduce(\(initialValue.description), \(each))"
	}
}
