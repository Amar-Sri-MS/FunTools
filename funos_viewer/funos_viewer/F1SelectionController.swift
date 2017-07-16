//
//  F1SelectionController.swift
//
//  Created by Bertrand Serlet on 5/20/16.
//  Copyright © 2016 Fungible Inc. All rights reserved.
//

import AppKit

class F1SelectionController: NSObject, NSTabViewDelegate {
	@IBOutlet var window: NSWindow!
	@IBOutlet var selectionTabView: NSTabView!
	var refreshTimer: Timer!
	let updateFrequency = 0.2
	unowned let document: F1SimDocument

	init(document: F1SimDocument) {
		self.document = document
		super.init()
		loadNib()
		resetIKVSamples()
		selectionTabView.delegate = self
		selectionRelativeHeat.isEnabled = false
	}

	func loadNib() {
		let ok = Bundle.main.loadNibNamed("F1SelectionWindow", owner: self, topLevelObjects: nil)
		assert(ok)
		let view = window.contentView!.subviews.first!
		assert(view == selectionTabView)
		window.makeKeyAndOrderFront(nil)
	}


	// uncomment to debug leaks
	//    deinit {
	//        print("DESTROY F1SelectionController")
	//    }
	let tabsToRefresh: Set<String> = ["Misc Stats"]

	public func tabView(_ tabView: NSTabView, willSelect tabViewItem: NSTabViewItem?) {
		//        print("Received willSelect notification tabView changed to \(tabViewItem!.label)")
		if tabsToRefresh.contains(tabViewItem!.label) {
			doRefresh(tabViewItem!.label)
		}
	}
	public func tabView(_ tabView: NSTabView, didSelect tabViewItem: NSTabViewItem?) {
		//        print("Received didSelect notification tabView changed to \(tabViewItem!.label)")
		if tabsToRefresh.contains(tabViewItem!.label) {
			refreshTimer = Timer.scheduledTimer(withTimeInterval: updateFrequency, repeats: true, block: { _ in
				self.performSelector(onMainThread: #selector(F1SelectionController.refresh), with: nil, waitUntilDone: false)
			})
		} else if tabViewItem!.label == "IKV" {
			doRefreshIKV()
		}
	}
	func refresh() {
		let tabViewItem = selectionTabView.selectedTabViewItem
		if tabViewItem != nil && tabsToRefresh.contains(tabViewItem!.label) {
			doRefresh(tabViewItem!.label)
		} else {
			refreshTimer?.invalidate()
		}
	}
	func doRefresh(_ label: String) {
		switch label {
			case "Misc Stats": doRefreshMiscStats()
			case "IKV": doRefreshIKV()
			default: break
		}
	}
	func updateSelectionTabForUnit(_ unit: F1Block) {
		// Note that unit can be a single unit or a group of units
		switch (selectionTabView.selectedTabViewItem!.identifier! as AnyObject).description {
		case "1": break
		case "3":
			selectionRelativeHeat.isEnabled = unit.name == "DN" || unit.name == "SN"
		default: fatalError()
		}
		selectionTabView.needsDisplay = true
		unit.noteStateChanged() // we force taking a new sample
	}

	/*=============== MISC ===============*/

	@IBOutlet var inUseField: NSTextField!
	@IBOutlet var modulesInited: NSTextView!

	func doRefreshMiscStats() {
		let wustacks = document.doF1Command("peek", "stats/wustacks")?.dictionaryValue
		let inUse = wustacks?["in_use"]?.integerValue
		if inUse != nil {
			inUseField.integerValue = inUse!
		}
		let modules = document.doF1Command("peek", "config/modules_inited")?.arrayValue
		let modulesStr = modules?.joinDescriptions(", ")
		if modulesStr != nil {
			modulesInited.string = modulesStr
		}
	}

	/*=============== OPTIONS (CURRENTLY UNUSED) ===============*/

	@IBOutlet var selectionRelativeHeat: NSButton!

	var isRelativeHeat: Bool { return selectionRelativeHeat.boolValue }

	@IBAction func fiddleWithOptions(_ sender: NSObject?) {
		document.noteSelectionChangedAndUpdate()
	}

	/*=============== IKV ===============*/

	@IBOutlet var ikvContainer: NSTextField!

	@IBOutlet var ikvPuts: NSTextField!
	@IBOutlet var ikvGets: NSTextField!
	@IBOutlet var ikvDeletes: NSTextField!

	var ikvCountSamples: SimulationSamples!
	@IBOutlet var ikvCountSamplesView: SimulationSamplesView!

	var ikvCapacitySamples: SimulationSamples!
	@IBOutlet var ikvCapacitySamplesView: SimulationSamplesView!

	var ikvSpaceAmplificationSamples: SimulationSamples!
	@IBOutlet var ikvSpaceAmplificationSamplesView: SimulationSamplesView!

	@IBOutlet var ikvResizing: NSTextField!
	@IBOutlet var ikvResizes: NSTextField!
	@IBOutlet var ikvRehash: NSTextField!
	@IBOutlet var ikvTombs: NSTextField!
	@IBOutlet var ikvReclaim: NSTextField!
	@IBOutlet var ikvPagereads: NSTextField!
	@IBOutlet var ikvPagewrites: NSTextField!
	@IBOutlet var ikvKeywait: NSTextField!
	@IBOutlet var ikvPagewait: NSTextField!

	var ikvStartDate: Date!  // to substract to now
	var ikvTimer: Timer!    // We start the timer whenever we have an IKV

	let maxSpaceAmp = 5.0

	func resetIKVSamples() {
		ikvCountSamples = SimulationSamples(title: "Count") { Int($0.lastValue).description }
		ikvCountSamples.record(0, value: 0.0)
		ikvCountSamplesView.setSamples(ikvCountSamples!)

		ikvCapacitySamples = SimulationSamples(title: "Capacity") { String(numberOfBytes: $0.lastValue) }
		ikvCapacitySamples.record(0, value: 0.0)
		ikvCapacitySamplesView.setSamples(ikvCapacitySamples!)

		ikvSpaceAmplificationSamples = SimulationSamples(title: "Space Amplification (capped at \(Int(maxSpaceAmp))x)", range: 0.0 ... maxSpaceAmp ) {
			let range = $0.range
			if range == nil { return "" }
			let mini = range!.lowerBound.round1
			let maxi = range!.upperBound.round1
			return "min:\(mini)x,max:\(maxi)x"
		}
		ikvSpaceAmplificationSamples.record(0, value: maxSpaceAmp)
		ikvSpaceAmplificationSamplesView.setSamples(ikvSpaceAmplificationSamples!)
		
	}

	func startIKVTimer() {
		resetIKVSamples()
		ikvTimer?.invalidate()
		ikvStartDate = Date()
		ikvTimer = Timer.scheduledTimer(withTimeInterval: updateFrequency, repeats: true, block: { _ in
			self.performSelector(onMainThread: #selector(F1SelectionController.doRefreshIKV), with: nil, waitUntilDone: false)
		})
	}

	func doRefreshIKV() {
		let cont = ikvContainer!.stringValue
		let propsName = "stats/ikv/\(cont)"
		let stats = document.doF1Command("peek", propsName)?.dictionaryValue
		if stats == nil || stats!.isEmpty || ikvStartDate == nil { return }
		let now = Int((Date() - ikvStartDate!) * 20.0)
		let list: [(ui: NSTextField?, name: String, samples: SimulationSamples?)] = [
			(ikvPuts, "puts", nil),
			(ikvGets, "gets", nil),
			(ikvDeletes, "deletes", nil),
			(nil, "count", ikvCountSamples),
			(nil, "capacity", ikvCapacitySamples),
			(ikvResizing, "resizing", nil),
			(ikvResizes, "resizes", nil),
			(ikvRehash, "rehash", nil),
			(ikvTombs, "tombs", nil),
			(ikvReclaim, "reclaim", nil),
			(ikvPagereads, "pagereads", nil),
			(ikvPagewrites, "pagewrites", nil),
			(ikvKeywait, "keywait", nil),
			(ikvPagewait, "pagewait", nil)
		]
		for (ui, name, samples) in list {
			let s = stats![name]
			if s != nil {
				let v = s!.integerValue
				if ui != nil {
					ui!.integerValue = v
				}
				if samples != nil && ikvStartDate != nil {
					samples!.record(now, value: Double(v))
				}
			}
		}
		ikvResizing!.stringValue = ikvResizing.boolValue ? "true" : "false"
		let capacityDouble = Double(stats!["capacity"]?.integerValue ?? 0)
		let inUseDouble = Double((stats!["count"]?.integerValue ?? 0) * 256)
		let spaceAmp = min(capacityDouble / max(inUseDouble, 1.0), maxSpaceAmp)
		ikvSpaceAmplificationSamples!.record(now, value: spaceAmp)

		ikvCountSamplesView.setSamples(ikvCountSamples!)
		ikvCapacitySamplesView.setSamples(ikvCapacitySamples!)
		ikvSpaceAmplificationSamplesView.setSamples(ikvSpaceAmplificationSamples!)
	}

}

