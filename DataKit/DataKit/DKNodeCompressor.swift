//
//  DKNodeCompressor.swift
//  DataKit
//
//  Created by Bertrand Serlet on 12/31/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// A Compressor node is really like a Fifo, except it is implemented in datakit as 2 VPs and a HW accelerator

class DKNodeCompressor: DKNode {
	let compress: DKFunctionCompress
	init(label: Int, compress: DKFunctionCompress) {
		let base = compress.base
		assert(base is DKTypeSequence) // we restrict for now to sequences
		self.compress = compress
		super.init(label)
	}
	var compresses: Bool {
		return compress.compresses
	}
	override var signature: DKTypeSignature {
		return compress.signature
	}
	override func sugaredDescription(_ uniquingTable: DKTypeTable) -> String {
		let typeStr = compresses ? "COMP" : "DECOMP"
		return "\(typeStr)#\(graphIndex)(t=\(compress.signature.sugaredDescription(uniquingTable)); method=\(compress.method))"
	}
	override func nodeToJSONDict(_ uniquingTable: DKTypeTable) -> [String: JSON] {
		return ["compressor_node": compress.functionToJSON]
	}
}

