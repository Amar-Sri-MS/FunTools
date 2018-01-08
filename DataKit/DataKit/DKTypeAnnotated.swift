//
//  DKTypeAnnotated.swift
//  DataKit
//
//  Created by Bertrand Serlet on 12/25/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// Denotes a type with different layout based on some annotation
// Example: Compressed

class DKTypeAnnotated: DKType {
	let base: DKType
	let annotation: JSON

	// ===============  CREATION ===============

	init(base: DKType, annotation: JSON) {
		assert(annotation.isDictionary)
		self.base = base
		self.annotation = annotation
	}
	convenience init(base: DKType, compressed method: String) {
		self.init(base: base, annotation: .dictionary(["compression": .string(method)]))
	}
	override func requiredAlignmentInBits() -> UInt64! {
		return 8
	}

	// ===============  TO/FROM JSON ===============

	override func typeToRawJSON(_ uniquingTable: DKTypeTable) -> JSON {
		let dict: [String: JSON] = [
			"genre": "annotated",
			"base": base.toTypeShortcut(uniquingTable).toJSON,
			"annotation": annotation,
		]
		return .dictionary(dict)
	}
	override class func typeFromJSON(_ uniquingTable: DKTypeTable, _ j: JSON) -> DKType? {
		let dict = j.dictionaryValue
		if dict["genre"] != "annotated" { return nil }
		let base = dict["base"]?.toDKType(uniquingTable)
		if base == nil { return nil }
		let ann = dict["annotation"]
		if ann == nil { return nil }
		return DKTypeAnnotated(base: base!, annotation: ann!)
	}

	// ===============  MISC ===============

	var isCompressedType: Bool {
		return annotation.dictionaryValue["compression"] != nil
	}
	var compressionMethod: String! {
		return annotation.dictionaryValue["compression"]?.stringValue
	}

	override func subclassableSugaryDescription(_ uniquingTable: DKTypeTable) -> String {
		if isCompressedType {
			let baseStr = base.sugaredDescription(uniquingTable)
			return "Compressed<\(baseStr)>(\(compressionMethod!))"
		}
		return super.subclassableSugaryDescription(uniquingTable)
	}

}
