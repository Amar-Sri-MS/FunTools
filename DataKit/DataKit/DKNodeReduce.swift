//
//  DKNodeReduce.swift
//  DataKit
//
//  Created by Bertrand Serlet on 9/13/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// Node that "absorbs" a stream of [T] and produces a value of type U
class DKNodeReduce: DKNode {
	let reducer: DKFunctionReduce
	var finalFunc: DKFunction!	// function to apply to the result
	init(label: Int, reduce: DKFunctionReduce) {
		self.reducer = reduce
		super.init(label)
	}
	var sequenceType: DKTypeSequence { return DKTypeSequence(reducer.inputItemType) }
	var outputType: DKType {
		return finalFunc == nil ? reducer.outputType : finalFunc.signature.output
	}
	override var signature: DKTypeSignature {
		return DKTypeSignature(unaryArg: sequenceType, output: outputType)
	}
	override func sugaredDescription(_ uniquingTable: DKTypeTable) -> String {
		let item = reducer.inputItemType.sugaredDescription(uniquingTable)
		let valueType = reducer.outputType
		let ini = reducer.initialValue.description
		return "FIFO#\(graphIndex)(initial=\(ini), u=\(valueType), t=\(item), final=\(finalFunc?.description ?? ""); each=\(reducer.each.description))"
	}
	override func nodeToJSONDict(_ uniquingTable: DKTypeTable) -> [String: JSON] {
		var dict: [String: JSON] = [
			"reducer": reducer.functionToJSON,
			]
		if finalFunc != nil {
			dict["final"] = finalFunc.functionToJSON
		}
		return dict
	}
	func compose(outer fun: DKFunction) {
		if finalFunc == nil {
			assert(fun.signature.numberOfArguments == 1)
			assert(fun.signature.input[0] == reducer.outputType)
			finalFunc = fun
		} else {
			finalFunc = DKFunctionComposition(outer: fun, inner: finalFunc!)
		}
	}
}
