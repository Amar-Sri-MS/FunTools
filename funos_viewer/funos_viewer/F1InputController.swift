//
//  F1InputController.swift
//
//  Created by Bertrand Serlet on 5/20/16.
//  Copyright © 2016 Fungible Inc. All rights reserved.
//

import AppKit

class F1InputController: NSObject, NSOutlineViewDataSource, NSTabViewDelegate {
	@IBOutlet var window: NSWindow!
	@IBOutlet var view: NSView!

	var tabView: NSTabView!

	// Commands TAB
	@IBOutlet var numRegisteredCommands: NSTextField!
	@IBOutlet var helpArg: NSTextField!
	@IBOutlet var fiboArg: NSTextField!
	@IBOutlet var genericVerb: NSTextField!
	@IBOutlet var genericArg: NSTextField!

	@IBOutlet var keyPath: NSTextField!
	@IBOutlet var pokeValue: NSTextField!

	// Tests TAB
	@IBOutlet var tests: NSOutlineView!
	@IBOutlet var testArg1: NSTextField!
	@IBOutlet var testArg2: NSTextField!

	// IKV TAB
	@IBOutlet var sizeClass: NSMatrix!
	@IBOutlet var logPageSize: NSTextField!
	@IBOutlet var pageCacheKB: NSTextField!
	@IBOutlet var ikvRepeat: NSTextField!
	var ikvContainer: Int! // token from the back-end

	var numWUs: Int!
	var topLevelWUs: [String]!

	unowned let document: F1SimDocument

	init(document: F1SimDocument) {
		self.document = document
		super.init()
		loadNib()
		tests.dataSource = self
		tabView.delegate = self
	}
	// uncomment to debug leaks
	//    deinit {
	//        print("DESTROY F1InputController")
	//    }
	func loadNib() {
		let ok = Bundle.main.loadNibNamed(NSNib.Name(rawValue: "F1InputWindow"), owner: self, topLevelObjects: nil)
		assert(ok)
		assert(view != nil)
		tabView = view.subviews.first as! NSTabView
	}
	func firstF1Setup() {
		let json = document.doF1Command("help")
		if json != nil {
			let num = json!.dictionaryValue.count
			numRegisteredCommands.intValue = Int32(num)
		}
	}
	public func tabView(_ tabView: NSTabView, willSelect tabViewItem: NSTabViewItem?) {
		computeTopLevelWUs()
	}
	func computeTopLevelWUs() {
		if numWUs != nil { return }
		//        print("Fetching WU Handlers")
		let wus = document.doF1Command("peek", "config/wu_handlers")?.dictionaryValue
		if wus == nil || wus!.isEmpty {
			// use the default, for now
			topLevelWUs = ["bstest", "snake", "wuctest", "nvme"]
		} else {
			numWUs = wus!.count
			topLevelWUs = wus!.compactMap {
				if $1.dictionaryValue.isEmpty { return nil }
				let attrs = $1.dictionaryValue["attrs"]?.integerValue ?? 0
				// FIXME: 16 below...
				let isTopLevel = (attrs & 16 /* WU_ATTR_TOP_LEVEL */) != 0
				return isTopLevel ? $0 : nil
			}
			//            print("TopLevel WUs: \(topLevelWUs!)")
			topLevelWUs = topLevelWUs.sorted()
			tests.tableColumns.last?.headerCell.stringValue = "TESTS (\(topLevelWUs.count)/\(numWUs!))"
			tests.reloadData()
		}

	}
	func outlineView(_ outlineView: NSOutlineView, numberOfChildrenOfItem item: Any?) -> Int {
		if topLevelWUs == nil { computeTopLevelWUs() }
		if item == nil { return topLevelWUs.count }
		return 0
	}
	func outlineView(_ outlineView: NSOutlineView, isItemExpandable item: Any) -> Bool {
		return false
	}
	func outlineView(_ outlineView: NSOutlineView, child index: Int, ofItem item: Any?) -> Any {
		if item == nil {
			return topLevelWUs[index]
		}
		return "Error" as NSString
	}
	func outlineView(_ outlineView: NSOutlineView, objectValueFor tableColumn: NSTableColumn?, byItem item: Any?) -> Any? {
		return item
	}
	func selectedTest() -> String {
		let row = tests.selectedRow
		return tests.item(atRow: row) as! String
	}

	func gatherParameters() -> JSON {
		var dict: [String: JSON] = [:]
		switch sizeClass.selectedRow {
		case 0: dict["size_param"] = "small"
		case 1: dict["size_param"] = "large"
		default: dict["size_param"] = "mix"
		}
		var logPageSizeInt = logPageSize.integerValue
		if logPageSizeInt < 12 || logPageSizeInt > 16 {
			logPageSizeInt = 12
			logPageSize.integerValue = logPageSizeInt
		}
		dict["log_page_size"] = JSON.integer(logPageSizeInt)
		var pageCacheKBInt = pageCacheKB?.integerValue ?? 100
		if pageCacheKBInt < 1 || pageCacheKBInt > 10_000 {
			pageCacheKBInt = 100
			pageCacheKB.integerValue = pageCacheKBInt
		}
		dict["pages_cache_size"] = JSON.integer(pageCacheKBInt * 1024)
		var cmdRepeat = ikvRepeat.integerValue
		if cmdRepeat < 1 || cmdRepeat > 10_000 {
			cmdRepeat = 100
			ikvRepeat.integerValue = cmdRepeat
		}
		dict["command_repeat"] = JSON.integer(cmdRepeat)
		if ikvContainer != nil { dict["ikv_container"] = JSON.integer(ikvContainer!) }
		return JSON.dictionary(dict)
	}
	var paramsAsString: String {
		return gatherParameters().description
	}
}
