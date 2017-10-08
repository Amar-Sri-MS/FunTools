//
//  ViewController.swift
//  DataKitApp
//
//  Created by Bertrand Serlet on 10/8/17.
//  Copyright © 2017 Bertrand Serlet. All rights reserved.
//

import Cocoa

class ViewController: NSViewController, NSTextViewDelegate {
	@IBOutlet var sourcePopUp: NSPopUpButton!
	@IBOutlet var transformation: NSTextView!
	@IBOutlet var predefs: NSPopUpButton!
	@IBOutlet var numFifos: NSTextField!
	@IBOutlet var status: NSTextField!
	@IBOutlet var generatedJSON: NSTextView!

	let typeTable = DKTypeTable()
	var isStudents: Bool {
		return sourcePopUp.indexOfSelectedItem == 0
	}
	func baseType() -> DKType {
		return isStudents ? studentType() : DKTypeInt.uint64
	}
	func generator() -> DKFunctionGenerator {
		return DKFunctionGenerator(typeTable, name: isStudents ? "Students" : "RandomInts", params: 1000, itemType: baseType())
	}
	func pipelineString() -> String {
		let pipeline = transformation.string!
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
		transformation.font = NSFont(name: "Menlo", size: 16)
		generatedJSON.font = NSFont(name: "Menlo", size: 16)
		registerGeneratorOfStudents(typeTable: typeTable)
		transformation.delegate = self
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
	}
	@IBAction func sourceChanged(_ sender: NSObject?) {
		transformation.string = ""
		reset()
	}
	@IBAction func predefChanged(_ sender: NSObject?) {
		reset()
		var text: String = ""
		switch predefs.indexOfSelectedItem {
		case 0:
			text = "map(logger())"
		case 1:
			text = "map((Student) -> (): logger())"
		case 2:
			text = "compose(\n" +
				"    map((Student) -> (): logger()), \n" +
				"    filter({ $0.first_name == \"Joe\"})\n" +
				")"
		default:
			text = "compose(\n" +
				"    map((Student) -> (): logger()), \n" +
				"    compose(\n" +
				"        filter((Student) -> Bool: { $0.first_name == \"Joe\"}), \n" +
				"        filter({ $0.last_name == \"Smith\"})\n" +
				"    )\n" +
				")"
		}
		transformation.string = text
	}
	func checkAndJSON() -> String! {
		do {
			let flowGraphGen = try flowGraphGenerator()
			let r = flowGraphGen.generate()
			numFifos.integerValue = r.fifos.count
			let j = flowGraphGen.flowGraphToJSON
			let js = j.description
			generatedJSON.string = js
			return js
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
		let str = combined!.description.asOneLine
//		print("Single line: \n\(str)")
		let r = dpcrun_command_with_subverb_and_arg(&socket, "datakit", "setup", str)
		status.stringValue = r == nil ? "CAN'T CONNECT" : "OK"
	}
	@IBAction func run(_ sender: NSObject?) {
		let r2 = dpcrun_command_with_subverb(&socket, "datakit", "run")
		status.stringValue = r2 == nil ? "CAN'T CONNECT" : "OK"
	}
}

