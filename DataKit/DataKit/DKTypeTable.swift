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
	var shortcuts: [DKType.Shortcut: JSON]
	init() {
		shortcuts = [:]
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
	var typeTableAsJSON: JSON {
		return .dictionary(shortcuts)
	}
}
