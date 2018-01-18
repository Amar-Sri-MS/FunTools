//
//  IKVController.swift
//  funos_viewer
//
//  Created by Bertrand Serlet on 7/16/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

import AppKit

class IKVController: NSObject {
	@IBOutlet var window: NSWindow!

	var refreshTimer: Timer!
	let updateFrequency = 0.2

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

	override init() {
		super.init()
		let ok = Bundle.main.loadNibNamed(NSNib.Name(rawValue: "IKVWindow"), owner: self, topLevelObjects: nil)
		assert(ok)
		resetIKVSamples()
		show()
	}

	func show() {
		window.makeKeyAndOrderFront(nil)
		refreshTimer = Timer.scheduledTimer(withTimeInterval: updateFrequency, repeats: true, block: { _ in
			self.performSelector(onMainThread: #selector(IKVController.refresh), with: nil, waitUntilDone: false)
		})
	}
	@objc func refresh() {
		if !window.isVisible {
			refreshTimer?.invalidate()
			return
		}
		doRefreshIKV()
	}

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
			self.performSelector(onMainThread: #selector(IKVController.doRefreshIKV), with: nil, waitUntilDone: false)
		})
	}

	@objc func doRefreshIKV() {
		let cont = ikvContainer!.stringValue
		let propsName = "stats/ikv/\(cont)"
		let stats = document.doF1Command("peek", propsName)?.dictionaryValue
		if stats == nil || stats!.isEmpty || ikvStartDate == nil { return }
		print("STATS=\(stats)")
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

	var document: F1SimDocument {
		return NSApp.theDocument!
	}

}
