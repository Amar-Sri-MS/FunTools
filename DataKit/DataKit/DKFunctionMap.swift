//
//  DKFunctionMap.swift
//  DataKit
//
//  Created by Bertrand Serlet on 9/17/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// Maps a function 'each' (T) -> U to a sequence.
// The signature of the map is ([T]) -> [U] 
// except when U is () (then the signature is ([T]) -> ())
class DKFunctionMap: DKFunction {
	let each: DKFunction
	init(each: DKFunction) {
		assert(each.signature.numberOfArguments == 1)
		self.each = each
	}
	var inputItemType: DKType { return each.signature.input[0] }
	var outputItemType: DKType { return each.signature.output }
	var inputSequenceType: DKType { return inputItemType.makeSequence }
	var outputSequenceType: DKType { return outputItemType.makeSequence }
	var paramsType: DKTypeStruct { return DKTypeStruct(funcParamType: inputSequenceType) }
	override var signature: DKTypeSignature {
		return DKTypeSignature(input: paramsType, output: outputSequenceType)
	}
	class func canBeMapAndPredicateSignature(_ type: DKType) -> DKTypeSignature! {
		if let signature = type as? DKTypeSignature {
			let outputSequenceType = signature.output
			if signature.numberOfArguments != 1 || !(signature.input[0] is DKTypeSequence) {
				return nil
			}
			let inputItemType = (signature.input[0] as! DKTypeSequence).sub
			if outputSequenceType == DKType.void {
				return DKTypeSignature(input: DKTypeStruct(funcParamType: inputItemType), output: DKType.void)
			}
			if let s = outputSequenceType as? DKTypeSequence {
				let outputItemType = s.sub
				return DKTypeSignature(input: DKTypeStruct(funcParamType: inputItemType), output: outputItemType)
			} else {
				return nil
			}
		}
		return nil
	}
	override var functionToJSONDict: [String: JSON] {
		return [
			"map": each.functionToJSON
		]
	}
	override class func functionFromJSON(_ uniquingTable: DKTypeTable, _ dict: [String: JSON]) -> DKFunction! {
		let m = dict["map"]
		if m == nil || !m!.isDictionary { return nil }
		let e = DKFunction.functionFromJSON(uniquingTable, m!.dictionaryValue)
		if e == nil { return nil }
		return DKFunctionMap(each: e!)
	}
	override func evaluate(context: DKEvaluationContext, _ subs: [DKExpression]) -> DKValue {
		assert(subs.count == 1)
		let x = subs[0].evaluate(context: context)
		var output: DKMutableBitStream = DataAsMutableBitStream()
		func applyEach(_ item: DKValue) {
			let expr = item.asExpressionConstant
			let r = each.evaluate(context: context, [expr])
			r.append(to: &output)
		}
		if let explicit = x as? DKValueSimple {
			explicit.forEach(applyEach)
		} else if let valueSeq = x as? DKValueLazySequence {
			valueSeq.forEach(applyEach)
		} else {
			abort()
		}
		let newInput = output.finishAndData()
		return DKValueLazySequence(itemType: outputItemType, data: newInput)
	}
	override var description: String {
		return "map(\(each))"
	}
	override var isInputGroupable: Bool {
		return true
	}
}
