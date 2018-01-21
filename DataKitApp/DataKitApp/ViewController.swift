//
//  ViewController.swift
//  DataKitApp
//
//  Created by Bertrand Serlet on 10/8/17.
//  Copyright © 2017 Bertrand Serlet. All rights reserved.
//

import Cocoa

// The app logic is here

class ViewController: NSViewController, NSTextViewDelegate {
	@IBOutlet var sourcePopUp: NSPopUpButton!
	@IBOutlet var transformation: NSTextView!
	@IBOutlet var predefs: NSPopUpButton!
	@IBOutlet var numFifos: NSTextField!
	@IBOutlet var status: NSTextField!
	@IBOutlet var generatedJSON: NSTextView!
	@IBOutlet var commandToF1: NSTextField!

	var dk = DataKitController()

	var isStudents: Bool {
		return sourcePopUp.indexOfSelectedItem >= 3
	}
	var isSequentialInts: Bool {
		return sourcePopUp.indexOfSelectedItem == 2
	}
	override func viewDidLoad() {
		super.viewDidLoad()
		let bigFont = NSFont(name: "Menlo", size: 16)
		transformation.font = bigFont
		generatedJSON.font = bigFont
		transformation.delegate = self
		predefs.removeAllItems()
		predefs.addItems(withTitles: dk.predefArray.map { $0.0 })
//		let sep = NSMenuItem.separator()
//		for i in 0 ..< predefs.numberOfItems where predefs.item(at: i)!.title == sep.title {
//			predefs.itemArray[i] = sep
//		}
	}

	override var representedObject: Any? {
		didSet {
		// Update the view, if already loaded.
		}
	}
	func reset() {
		generatedJSON.string = ""
		numFifos.stringValue = ""
		status.stringValue = ""
		commandToF1.stringValue = ""
	}
	@IBAction func sourceChanged(_ sender: NSObject?) {
		let nums = [100, 1000, 1000 /* sequential ints */, 100, 1000, 10_000, 100_000]
		dk.numGenerated = nums[sourcePopUp.indexOfSelectedItem]
		dk.isStudents = isStudents
		dk.isSequentialInts = isSequentialInts
		reset()
	}
	@IBAction func predefChanged(_ sender: NSObject?) {
		let i = predefs.indexOfSelectedItem
		let text = dk.predefArray[i].1
		if text == "" { return }
		reset()
		transformation.string = text
	}
	// Returns the string as one line
	func checkAndJSON() -> String! {
		do {
			let (flowGraphGen, str) = try dk.flowGraphGenerator(transformation.string)
			generatedJSON.string = str
			let graph = flowGraphGen.generate().graph
			numFifos.integerValue = graph.nodes.count
			let j = flowGraphGen.flowGraphToJSON
			let js = j.description
			generatedJSON.string = js
			let oneLine = js.description.asOneLine
			commandToF1.stringValue = "datakit setup \(oneLine)"
			return oneLine
		} catch let error {
			generatedJSON.string = "*** Error parsing: \(error)"
			return nil
		}
	}
	public func textView(_ textView: NSTextView, shouldChangeTextInRanges affectedRanges: [NSValue], replacementStrings: [String]?) -> Bool {
		reset()
		return true
	}
	@IBAction func check(_ sender: NSObject?) {
		_ = checkAndJSON()
	}
	@IBAction func setup(_ sender: NSObject?) {
		let combined = checkAndJSON()
		if combined == nil { return }
		let r = dpcrun_command_with_subverb_and_arg(&socket, "datakit", "setup", combined!)
		status.stringValue = r == nil ? "CAN'T CONNECT" : "OK"
	}
	@IBAction func run(_ sender: NSObject?) {
		commandToF1.stringValue = "datakit run"
		let r2 = dpcrun_command_with_subverb(&socket, "datakit", "run")
		status.stringValue = r2 == nil ? "CAN'T CONNECT" : "OK"
	}
}

