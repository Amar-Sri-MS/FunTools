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
		return compress.compress
	}
	override var signature: DKTypeSignature {
		let bytes = DKTypeSequence(DKTypeInt.uint8)
		if compresses {
			// We compress into bytes
			return DKTypeSignature(input: compress.signature.input, output: bytes)
		} else {
			// We decompress from bytes
			return DKTypeSignature(unaryArg: bytes, output: compress.signature.output)
		}
	}
	var sequenceType: DKTypeSequence { return compress.base as! DKTypeSequence }
	override func sugaredDescription(_ uniquingTable: DKTypeTable) -> String {
		let typeStr = compresses ? "COMP" : "DECOMP"
		return "\(typeStr)#\(graphIndex)(t=\(compress.signature.sugaredDescription(uniquingTable)); method=\(compress.method))"
	}
	override func nodeToJSONDict(_ uniquingTable: DKTypeTable) -> [String: JSON] {
		return ["compressor": compress.functionToJSON]
	}
}

