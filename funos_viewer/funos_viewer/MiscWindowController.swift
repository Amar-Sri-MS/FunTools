//
//  MiscWindowController.swift
//  funos_viewer
//
//  Created by Bertrand Serlet on 7/16/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

import AppKit

class MiscWindowController: NSObject {
	@IBOutlet var window: NSWindow!

	var refreshTimer: Timer!
	let updateFrequency = 0.2

	@IBOutlet var inUseField: NSTextField!
	@IBOutlet var modulesInited: NSTextView!

	override init() {
		super.init()
		let ok = Bundle.main.loadNibNamed(NSNib.Name(rawValue: "MiscWindow"), owner: self, topLevelObjects: nil)
		assert(ok)
		show()
	}
	func show() {
		window.makeKeyAndOrderFront(nil)
		refreshTimer = Timer.scheduledTimer(withTimeInterval: updateFrequency, repeats: true, block: { _ in
			self.performSelector(onMainThread: #selector(MiscWindowController.refresh), with: nil, waitUntilDone: false)
		})
	}

	@objc func refresh() {
		if !window.isVisible {
			refreshTimer?.invalidate()
			return
		}
		let wustacks = document.doF1Command("peek", "stats/wustacks")?.dictionaryValue
		let inUse = wustacks?["in_use"]?.integerValue
		if inUse != nil {
			inUseField.integerValue = inUse!
		}
		let modules = document.doF1Command("peek", "config/modules_inited")?.arrayValue
		let modulesStr = modules?.joinDescriptions(", ")
		if modulesStr != nil {
			modulesInited.string = modulesStr!
		}
	}
	var document: F1SimDocument {
		return NSApp.theDocument!
	}
}

