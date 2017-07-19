//
//  ConsoleController.swift
//  funos_viewer
//
//  Created by Bertrand Serlet on 7/16/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

import AppKit

class ConsoleController: NSObject {
	@IBOutlet var window: NSWindow!
	@IBOutlet var selectionInfo: NSTextView!

	override init() {
		super.init()
		let ok = Bundle.main.loadNibNamed("ConsoleWindow", owner: self, topLevelObjects: nil)
		assert(ok)
		show()
		setupSelectionInfo()
	}
	func show() {
		window.makeKeyAndOrderFront(nil)
	}
	func setupSelectionInfo() {
		selectionInfo.makeNonEditableFixedPitchOfSize(12.0)   // try to speedup display
		clearSelectionTab()
	}
	func clearSelectionTab() {
		selectionInfo.string = ""
	}
}

