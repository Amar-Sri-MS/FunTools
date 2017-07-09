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
		setupSelectionInfo()
		setupWUsTable()
		resetIKVSamples()
		setupMallocTable()
		selectionTabView.delegate = self
		selectionRelativeHeat.isEnabled = false
		// The next two lines are a horrible hack.  Without them, for some reason you need to go to the WUs TAB twice before you get any display.  Makes no sense.
		async {
			self.selectionTabView.performSelector(onMainThread: #selector(NSTabView.selectNextTabViewItem), with: nil, waitUntilDone: true)
			self.selectionTabView.performSelector(onMainThread: #selector(NSTabView.selectPreviousTabViewItem), with: nil, waitUntilDone: false)
		}
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
	let tabsToRefresh: Set<String> = ["WUs", "Misc Stats", "Malloc"]

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
			case "WUs": doRefreshWUs()
			case "Misc Stats": doRefreshMiscStats()
			case "IKV": doRefreshIKV()
			case "Malloc": doRefreshMalloc()
			default: break
		}
	}
	func updateSelectionTabForUnit(_ unit: F1Block) {
		// Note that unit can be a single unit or a group of units
		switch (selectionTabView.selectedTabViewItem!.identifier! as AnyObject).description {
		case "0":
			selectionInfo.setStringPreservingSelection(unit.simulationInfoFullSummary())
		case "1": break
		case "2":
			selectionQueuesText.setStringPreservingSelection(unit.simulationInfoQueues())
		case "3":
			selectionRelativeHeat.isEnabled = unit.name == "DN" || unit.name == "SN"
		default: fatalError()
		}
		selectionTabView.needsDisplay = true
		unit.noteStateChanged() // we force taking a new sample
	}

	/*=============== OUTPUT ===============*/

	@IBOutlet var selectionInfo: NSTextView!
	@IBOutlet var selectionQueuesText: NSTextView!

	func setupSelectionInfo() {
		selectionInfo.makeNonEditableFixedPitchOfSize(12.0)   // try to speedup display
		selectionQueuesText.makeNonEditableFixedPitchOfSize(12.0)
		clearSelectionTab()
	}

	func clearSelectionTab() {
		selectionInfo.string = ""
		selectionQueuesText.string = ""
	}

	/*=============== WUS ===============*/

	@IBOutlet var wusTable: NSTableView!

	var wusInfo = WUInfoDataSource()

	func setupWUsTable() {
		wusTable.dataSource = wusInfo
	}

	func doRefreshWUs() {
		let counts = document.doF1Command("peek", "stats/wus/counts")?.dictionaryValue
		if counts == nil || counts!.isEmpty { return }
		let durations = document.doF1Command("peek", "stats/wus/durations")?.dictionaryValue
		if durations == nil || durations!.isEmpty { return }
		wusInfo.updateAllInfo(counts: counts!, durations: durations!)
		wusTable.reloadData()
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

	/*=============== MALLOC ===============*/
	@IBOutlet var mallocInfoTable: NSTableView!

	var mallocInfoSource = MallocRegionsDataSource()

	func setupMallocTable() {
		mallocInfoTable.dataSource = mallocInfoSource
	}
	func doRefreshMalloc() {
		let regions = document.doF1Command("peek", "stats/malloc_agent/regions")?.arrayValue
		if regions == nil || regions!.isEmpty { return }
		if mallocInfoSource.updateAllInfo(regions!) {
			mallocInfoTable.reloadData()
		}
	}

}

/*=============== WUs DATA SOURCE ===============*/

class WUInfoDataSource: NSObject, NSTableViewDataSource {
	class WUInfo: NSObject {
		// we subclass NSObject to get valueForKeyPath
		var wu: String = ""
		var count: Int = 0
		var duration: Int = 0	// usecs
		var avgDuration: Int { return count == 0 ? 0 : duration / count }
	}
	
	var allInfo: [WUInfo] = []

	func updateAllInfo(counts: [String: JSON], durations: [String: JSON]) {
		let allExisting: Set<String> = Set(allInfo.map { $0.wu })
		for i in 0 ..< allInfo.count {
			let info = allInfo[i]
			let key = info.wu
			if counts[key] == nil { continue }
			info.count = counts[key]!.integerValue
			info.duration = ((durations[key]?.integerValue ?? 0) + 500) / 1000
		}
		let newKeysUnsorted = counts.keys.filter { !allExisting.contains($0) }
		if newKeysUnsorted.isEmpty { return }
		let newKeys = newKeysUnsorted.sorted { counts[$0]!.integerValue > counts[$1]!.integerValue }
		for key in newKeys {
			let info = WUInfo()
			info.wu = key
			info.count = counts[key]!.integerValue
			info.duration = ((durations[key]?.integerValue ?? 0) + 500) / 1000
			allInfo |= info
		}
	}

	func resort(_ sortDescriptors: [NSSortDescriptor]) {
		let allInfoAsMutableArray = NSMutableArray(array: allInfo)
		allInfoAsMutableArray.sort(using: sortDescriptors)
		allInfo = allInfoAsMutableArray as! [WUInfo]
	}

	func numberOfRows(in tableView: NSTableView) -> Int {
		return allInfo.count
	}

	func tableView(_ tableView: NSTableView, objectValueFor tableColumn: NSTableColumn?, row: Int) -> Any? {
		let info = allInfo[row]
		let value: Any? = info.value(forKeyPath: tableColumn!.identifier)
		return (value as! NSObject).description
	}

	func tableView(_ tableView: NSTableView, sortDescriptorsDidChange oldDescriptors: [NSSortDescriptor]) {
		resort(tableView.sortDescriptors)
		tableView.reloadData()
	}

}

/*=============== MALLOC DATA SOURCE ===============*/

class MallocRegionsDataSource: NSObject, NSTableViewDataSource {
	class SummaryRegionInfo: NSObject {
		// we subclass NSObject to get valueForKeyPath
		var numRegions: Int = 0
		var listLogRegionSizes: String = ""
		var sumRegionSizesInBytes: UInt64 = 0
		var sumWastedInBytes: UInt64 = 0
		var numAllocs = 0
		var numFrees = 0
		var numInUse = 0
		var sumInUseSizesInBytes: UInt64 = 0
		var sumRegionSizes: Double {
			return (Double(sumRegionSizesInBytes) / 1024.0 / 1024.0).round1
		}
		var percentInUse: Double {
			return (sumRegionSizesInBytes == 0 ? 0.0 : Double(sumInUseSizesInBytes + sumWastedInBytes) / Double(sumRegionSizesInBytes) * 100.0).round1
		}
	}
	var allRegions: [JSON] = []
	var allInfo: [Int: SummaryRegionInfo] = [:] // logChunkSize -> Summary

	func updateAllInfo(_ regions: [JSON]) -> Bool {
		// returns whether something changed
		if (regions == allRegions) { return false }
		allRegions = regions
		allInfo = [:]
		for region in regions {
			let lcs = region.dictionaryValue["log_chunk_size"]!.integerValue
			let summary = allInfo[lcs] ?? SummaryRegionInfo()
			summary.numRegions += 1
			let lrs = region.dictionaryValue["log_region_size"]!.integerValue
			summary.listLogRegionSizes += (summary.listLogRegionSizes.isEmpty ? "" : " ") + lrs.description
			summary.sumRegionSizesInBytes = UInt64(1) << lrs
			let w = region.dictionaryValue["wasted_size"]!.integerValue
			summary.sumWastedInBytes += UInt64(w)
			let na = region.dictionaryValue["num_alloc"]!.integerValue
			summary.numAllocs += na
			let nf = region.dictionaryValue["num_free"]!.integerValue
			summary.numFrees += nf
			let niu = region.dictionaryValue["num_in_use"]!.integerValue
			summary.numInUse += niu
			summary.sumInUseSizesInBytes += UInt64(niu) << lcs
			allInfo[lcs] = summary
		}
		return true
	}

	var total: SummaryRegionInfo {
		let total = SummaryRegionInfo()
		for (_, summary) in allInfo {
			total.numRegions += summary.numRegions
			total.sumRegionSizesInBytes += summary.sumRegionSizesInBytes
			total.sumWastedInBytes += summary.sumWastedInBytes
			total.numAllocs += summary.numAllocs
			total.numFrees += summary.numFrees
			total.numInUse += summary.numInUse
			total.sumInUseSizesInBytes += summary.sumInUseSizesInBytes
		}
		return total
	}

	func numberOfRows(in tableView: NSTableView) -> Int {
		return allInfo.count + 1
	}

	func tableView(_ tableView: NSTableView, objectValueFor tableColumn: NSTableColumn?, row: Int) -> Any? {
		let last = row >= allInfo.count
		let lcss = allInfo.keys.sorted()
		let ident = tableColumn!.identifier
//		print("Got identifier '\(ident)'")
		if (ident == "logChunk") {
			return last ? "Total" : lcss[row].description
		} else {
			let info = last ? total : allInfo[lcss[row]]!
			let value: Any? = info.value(forKeyPath: ident)
			return (value as! NSObject).description
		}
	}

}
