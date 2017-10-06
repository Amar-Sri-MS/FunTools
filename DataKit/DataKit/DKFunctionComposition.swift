//
//  DKFunctionComposition.swift
//  DataKit
//
//  Created by Bertrand Serlet on 9/7/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// Composes inner: (T) -> U and outer: (U) -> V
// into composition(x) = outer(inner(x))

class DKFunctionComposition: DKFunction {
	let inner: DKFunction
	let outer: DKFunction
	init(outer: DKFunction, inner: DKFunction) {
		let isig = inner.signature
		let osig = outer.signature
		assert(osig.numberOfArguments == 1)
		assert(isig.output == osig[0])
		self.inner = inner
		self.outer = outer
	}
	override var signature: DKTypeSignature {
		return DKTypeSignature(input: inner.signature.input, output: outer.signature.output)
	}
	override var functionToJSONDict: [String: JSON] {
		return [
			"composition": [inner.functionToJSON, outer.functionToJSON]
		]
	}
	override class func functionFromJSON(_ uniquingTable: DKTypeTable, _ dict: [String: JSON]) -> DKFunction! {
		let c = dict["composition"]
		if c == nil || !c!.isArray { return nil }
		let a = c!.arrayValue
		if a.count != 2 { return nil }
		let inner = DKFunction.functionFromJSON(uniquingTable, a[0].dictionaryValue)
		if inner == nil { return nil }
		let outer = DKFunction.functionFromJSON(uniquingTable, a[1].dictionaryValue)
		if outer == nil { return nil }
		return DKFunctionComposition(outer: outer!, inner: inner!)
	}
	override func evaluate(context: DKEvaluationContext, _ subs: [DKExpression]) -> DKValue {
		let evaled: [DKExpression] = subs.map { $0.evaluate(context: context).asExpressionConstant }
		let r1 = inner.evaluate(context: context, evaled)
		if r1.type is DKTypeSequence && outer.isInputGroupable {
			if let valueSeq = r1 as? DKValueLazySequence {
				var output: DKMutableBitStream = DataAsMutableBitStream()
				valueSeq.forEach {
					let v2 = outer.evaluate(context: context, [DKExpressionConstant($0)])
					v2.append(to: &output)
				}
				let newInput = output.finishAndData()
				if outer.signature.output == .void {
					return DKValue.null
				} else if let seq = outer.signature.output as? DKTypeSequence {
					return DKValueLazySequence(itemType: seq.sub, data: newInput)
				} else {
					abort();
				}
			}
		}
		let expr2 = r1.asExpressionConstant
		return outer.evaluate(context: context, [expr2])
	}
	override var isInputGroupable: Bool {
		return inner.isInputGroupable && outer.isInputGroupable
	}
	override var description: String {
		return "composition(\(inner), \(outer))"
	}
}
