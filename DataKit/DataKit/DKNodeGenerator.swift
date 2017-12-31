//
//  DKNodeGenerator.swift
//  DataKit
//
//  Created by Bertrand Serlet on 11/12/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

class DKNodeGenerator: DKNode {
	let maker: DKFunction
	let max: Int
	override var signature: DKTypeSignature {
		return DKTypeSignature(input: .void, output: maker.signature.output)
	}
	init(graphIndex: Int, maker: DKFunction, max: Int) {
		self.maker = maker
		self.max = max
		super.init(graphIndex)
	}
	override func sugaredDescription(_ uniquingTable: DKTypeTable) -> String {
		return "GENERATOR#\(graphIndex)(t=\(signature.sugaredDescription(uniquingTable)); maker=\(maker.description))"
	}
	override func nodeToJSONDict(_ uniquingTable: DKTypeTable) -> [String: JSON] {
		let dict: [String: JSON] = [
			"maker": maker.functionToJSON,
			"max": .integer(max)
			]
		return dict
	}

}
