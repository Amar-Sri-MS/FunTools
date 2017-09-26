//
//  DKGenC.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/22/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// Currently unused

class DKGenC {
	var knownTypes: [String: DKType]
	init() {
		knownTypes = ["Bool": DKTypeInt.bool, "UInt8": DKTypeInt.byte]
	}
	func findKnownType(_ type: DKType) -> String? {
		return knownTypes.keysForValue(type).first
	}
	func toC(_ type: DKType, level: Int = 0) -> String {
		let known = findKnownType(type)
		if known != nil { return known! }
		// TODO: Need to avoid this...
		if let s = type as? DKTypeStruct {
			return s.toC(context: self, level: level)
		}
		if let s = type as? DKTypeArray {
			return s.toC(context: self, level: level)
		}
		fatalErrorNYI()
	}
}

extension DKTypeStruct {
	func toC(context: DKGenC, level: Int) -> String {
		let spaces = String.spaces(4 * level)
		var str = "struct {\n"
		for (i, sub) in subs.enumerated() {
			let name = names == nil ? "$\(i)" : names[i]
			str += spaces + "    " + context.toC(sub, level: level + 1) + " " + name + ";\n"
		}
		str += spaces + "}"
		return str
	}
}

extension DKTypeArray {
	func toC(context: DKGenC, level: Int) -> String {
		var str = context.toC(sub, level: level)
		str += numItems == nil ? "[]" : "[\(numItems!)]"
		return str
	}

}
