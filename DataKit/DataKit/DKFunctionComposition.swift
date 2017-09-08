//
//  DKFunctionComposition.swift
//  DataKit
//
//  Created by Bertrand Serlet on 9/7/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// Composes fun1: (T) -> U and fun2: (U) -> V
// into composition(x) = fun2(fun1(x))

class DKFunctionComposition: DKFunction {
	let fun1: DKFunction
	let fun2: DKFunction
	init(_ fun1: DKFunction, _ fun2: DKFunction) {
		let sig1 = fun1.signature
		let sig2 = fun2.signature
		assert(sig2.numberOfArguments == 1)
		assert(sig1.output == sig2[0])
		self.fun1 = fun1
		self.fun2 = fun2
	}
	override var signature: DKTypeSignature {
		return DKTypeSignature(input: fun1.signature.input, output: fun2.signature.output)
	}
	override var functionToJSON: [String: JSON] {
		return [
			"composition": [.dictionary(fun1.functionToJSON), .dictionary(fun2.functionToJSON)]
		]
	}
	override class func functionFromJSON(_ uniquingTable: DKTypeTable, _ dict: [String: JSON]) -> DKFunction! {
		let c = dict["composition"]
		if c == nil || !c!.isArray { return nil }
		let a = c!.arrayValue
		if a.count != 2 { return nil }
		let f1 = DKFunction.functionFromJSON(uniquingTable, a[0].dictionaryValue)
		if f1 == nil { return nil }
		let f2 = DKFunction.functionFromJSON(uniquingTable, a[1].dictionaryValue)
		if f2 == nil { return nil }
		return DKFunctionComposition(f1!, f2!)
	}
	override func evaluate(context: DKEvaluationContext, _ subs: [DKExpression]) -> DKValue {
		assert(subs.count == 1)
		let x = subs[0].evaluate(context: context)
		func compose(_ item: DKValue) -> DKValue {
			let expr = DKExpressionConstant(item)
			let r1 = self.fun1.evaluate(context: context, [expr])
			let expr2 = DKExpressionConstant(r1)
			return self.fun2.evaluate(context: context, [expr2])
		}
		if !fun2.isInputGroupable || x is DKValueSimple {
			return compose(x)
		} else if let valueSeq = x as? DKValueLazySequence {
			var output: DKMutableBitStream = DataAsMutableBitStream()
			valueSeq.forEach {
				compose($0).append(to: &output)
			}
			let newInput = output.finishAndData()
			if fun2.signature.output == .void {
				return DKValue.null
			} else if let seq = fun2.signature.output as? DKTypeSequence {
				return DKValueLazySequence(itemType: seq.sub, data: newInput)
			} else {
				abort();
			}
		} else {
			abort()
		}
	}
	override func sugaredDescription(_ knowns: [DKType: String]) -> String {
		return "composition(\(fun1.sugaredDescription(knowns)), \(fun2.sugaredDescription(knowns)))"
	}
}
