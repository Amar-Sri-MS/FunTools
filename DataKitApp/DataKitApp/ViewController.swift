//
//  ViewController.swift
//  DataKitApp
//
//  Created by Bertrand Serlet on 10/8/17.
//  Copyright © 2017 Bertrand Serlet. All rights reserved.
//

import Cocoa

// The app logic is here

let predefArray = [
	("all", "map(logger())"),
	("", ""),
	("all ints (typed)", "map((UInt64) -> () | logger())"),
	("all * 100", "compose(\n" +
		"    first: map((UInt64) -> UInt64 | { $0 * 100 }),\n" +
		"    then: map(logger())\n" +
	")"),
	("all smaller than 10000", "compose(\n" +
		"    first:  filter((UInt64) -> Bool | { $0 < 10000}),\n" +
		"    then: map(logger())\n" +
	")"),
	("more complex", "compose(\n" +
		"    first: compose(\n" +
		"        first: filter((UInt64) -> Bool | { $0 < 100000}),\n" +
		"        then: map((UInt64) -> UInt64 | { $0 * 1000 + 42})\n" +
		"    ),\n" +
		"    then: map(logger())\n" +
		")"),
	("", ""),
	("all Students (typed)", "map((Student) -> () | logger())"),
	("all Joes", "compose(\n" +
		"    first: filter((Student) -> Bool | { $0.first_name == \"Joe\"}), \n" +
		"    then: map(logger())\n" +
	")"),
	("all Joe Smith", "compose(\n" +
		"    first: compose(\n" +
		"        first: filter((Student) -> Bool | { $0.last_name == \"Smith\"}),\n" +
		"        then: filter((Student) -> Bool | { $0.first_name == \"Joe\"})),\n" +
		"    then: map(logger())\n" +
	")")
]

class ViewController: NSViewController, NSTextViewDelegate {
	@IBOutlet var sourcePopUp: NSPopUpButton!
	@IBOutlet var transformation: NSTextView!
	@IBOutlet var predefs: NSPopUpButton!
	@IBOutlet var numFifos: NSTextField!
	@IBOutlet var status: NSTextField!
	@IBOutlet var generatedJSON: NSTextView!
	@IBOutlet var commandToF1: NSTextField!

	let typeTable = DKTypeTable()
	var isStudents: Bool {
		return sourcePopUp.indexOfSelectedItem >= 2
	}
	func baseType() -> DKType {
		return isStudents ? studentType() : DKTypeInt.uint64
	}
	func generator() -> DKFunctionGenerator {
		let num = sourcePopUp.indexOfSelectedItem & 1 == 0 ? 100 : 1000
		return DKFunctionGenerator(typeTable, name: isStudents ? "Students" : "RandomInts", params: .integer(num), itemType: baseType())
	}
	func pipelineString() -> String {
		let pipeline = transformation.string
		if isStudents {
			let sc = baseType().toTypeShortcut(typeTable)
			return pipeline.replaceOccurrences("Student", sc)
		} else {
			return pipeline
		}
	}
	func flowGraphGenerator() throws -> DKFlowGraphGen {
		let sig = DKTypeSignature(unaryArg: DKTypeSequence(subType: baseType()), output: .void)
		let pipeString = pipelineString()
		let pipeline = try DKParser.parseFunction(typeTable, pipeString, sig)
		generatedJSON.string = pipeline.description
		return DKFlowGraphGen(typeTable, generator(), pipeline)
	}
	override func viewDidLoad() {
		super.viewDidLoad()
		let bigFont = NSFont(name: "Menlo", size: 16)
		transformation.font = bigFont
		generatedJSON.font = bigFont
		registerGeneratorOfStudents(typeTable: typeTable)
		transformation.delegate = self
		predefs.removeAllItems()
		predefs.addItems(withTitles: predefArray.map { $0.0 })
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
		reset()
	}
	@IBAction func predefChanged(_ sender: NSObject?) {
		let i = predefs.indexOfSelectedItem
		let text = predefArray[i].1
		if text == "" { return }
		reset()
		transformation.string = text
	}
	// Returns the string as one line
	func checkAndJSON() -> String! {
		do {
			let flowGraphGen = try flowGraphGenerator()
			let r = flowGraphGen.generate()
			numFifos.integerValue = r.fifos.count
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

