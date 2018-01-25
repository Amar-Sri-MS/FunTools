//
//  DKFunctionCompress.swift
//  DataKit
//
//  Created by Bertrand Serlet on 12/25/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// Expresses the explicit compression or decompression of data

class DKFunctionCompress: DKFunction {
	let base: DKType	// Uncompressed type
	let shortcut: DKType.Shortcut	// cache
	let compresses: Bool // false means de-compression
	let method: String
	init(_ uniquingTable: DKTypeTable, base: DKType, compress: Bool, method: String) {
		self.base = base
		shortcut = base.toTypeShortcut(uniquingTable)
		self.compresses = compress
		self.method = method
	}
	override var signature: DKTypeSignature {
		let compressed = DKType.byteSequence
		if compresses {
			return DKTypeSignature(input: DKTypeStruct(funcParamType: base), output: compressed)
		} else {
			return DKTypeSignature(input: DKTypeStruct(funcParamType: compressed), output: base)
		}
	}
	override var functionToJSONDict: [String: JSON] {
		return [
			"compression": .bool(compresses),
			"base": shortcut.toJSON,
			"method": .string(method)
		]
	}
	override class func functionFromJSON(_ uniquingTable: DKTypeTable, _ dict: [String: JSON]) -> DKFunction! {
		let g = dict["compression"]
		if g == nil || !g!.isBool { return nil }
		let b = g! == JSON.bool(true)
		let t = dict["base"]?.toDKType(uniquingTable)
		if t == nil { return nil }
		let m = dict["method"]
		if m == nil || !m!.isString { return nil }
		return DKFunctionCompress(uniquingTable, base: t!, compress: b, method: m!.stringValue)
	}
	override var description: String {
		if compresses {
			return "compress(\(method.quotedString()))"
		} else {
			return "decompress(\(method.quotedString()))"
		}
	}
	class func canBeSignature(signature: DKTypeSignature, compress: Bool) -> Bool {
		if signature.numberOfArguments != 1 {
			return false
		}
		if compress {
			return signature.output == DKType.byteSequence
		} else {
			return signature.input[0] == DKType.byteSequence
		}
	}
	override var isInputGroupable: Bool {
		return true
	}
}
