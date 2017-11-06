//
//  DKTypeTable.swift
//  DataKit
//
//  Created by Bertrand Serlet on 8/16/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// A type table defines a context for types
// It is fundamentally a dictionary mapping the shortcuts to the raw JSON of the type

class DKTypeTable {
	typealias Shortcut = DKType.Shortcut
	var shortcuts: [Shortcut: JSON] = [:]
	var aliases: [String: Shortcut] = [:]
	init() {
	}
	subscript(sc: Shortcut) -> JSON? {
		get { return shortcuts[sc] }
		set(value) {
			let old = shortcuts[sc];
			if old != nil {
				assert(old == value)
			} else {
				shortcuts[sc] = value
			}
		}
	}
	func noteAlias(_ name: String, _ sc: Shortcut) {
		assert(aliases[name] == nil)
		aliases[name] = sc
	}
	func noteAlias(_ name: String, _ type: DKType) {
		let sc = type.toTypeShortcut(self)
		noteAlias(name, sc)
	}
	func aliasFor(_ name: String) -> Shortcut? {
		return aliases[name]
	}
	func aliasForShortcut(_ sc: Shortcut) -> String? {
		return aliases.keysForValue(sc).first
	}
	var typeTableAsJSON: JSON {
		var dict = shortcuts
		for (alias, shortcut) in aliases {
			dict[alias] = .string(shortcut)
		}
		return .dictionary(dict)
	}
}
