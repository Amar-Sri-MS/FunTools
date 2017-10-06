//
//  DKFunctionFilter.swift
//  DataKit
//
//  Created by Bertrand Serlet on 8/22/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

class DKFunctionFilter: DKFunction {
	let predicate: DKFunction
	init(predicate: DKFunction) {
		assert(predicate.signature.isPredicate)
		self.predicate = predicate
	}
	var itemType: DKType { return predicate.signature.input[0] }
	var sequenceType: DKType { return itemType.makeSequence }
	var paramsType: DKTypeStruct { return DKTypeStruct(funcParamType: sequenceType) }
	override var signature: DKTypeSignature {
		return DKTypeSignature(input: paramsType, output: sequenceType)
	}
	class func canBeFilterAndPredicateSignature(_ type: DKType) -> DKTypeSignature! {
		if let signature = type as? DKTypeSignature {
			let seqType = signature.output
			if signature.numberOfArguments != 1 || !(signature.input[0] is DKTypeSequence) || (signature.input[0] != seqType) {
				return nil
			}
			let itemType = (seqType as! DKTypeSequence).sub
			return DKTypeSignature(input: DKTypeStruct(funcParamType: itemType), output: DKTypeInt.bool)
		}
		return nil
	}
	override var functionToJSONDict: [String: JSON] {
		return [
			"filter": predicate.functionToJSON
		]
	}
	override class func functionFromJSON(_ uniquingTable: DKTypeTable, _ dict: [String: JSON]) -> DKFunction! {
		let filter = dict["filter"]
		if filter == nil || !filter!.isDictionary { return nil }
		let p = DKFunction.functionFromJSON(uniquingTable, filter!.dictionaryValue)
		if p == nil { return nil }
		return DKFunctionFilter(predicate: p!)
	}
	override func evaluate(context: DKEvaluationContext, _ subs: [DKExpression]) -> DKValue {
		assert(subs.count == 1)
		let x = subs[0].evaluate(context: context)
		var output: DKMutableBitStream = DataAsMutableBitStream()
		func applyPredicate(_ item: DKValue) {
			let expr = item.asExpressionConstant
			let r = self.predicate.evaluate(context: context, [expr])
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
	override var description: String {
		return "filter(\(predicate))"
	}
	override var isInputGroupable: Bool {
		return true
	}
}
