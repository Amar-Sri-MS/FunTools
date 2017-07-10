//
//  MallocWindowController.swift
//  funos_viewer
//
//  Created by Bertrand Serlet on 7/9/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

import AppKit

class MallocWindowController: NSObject {
	@IBOutlet var window: NSWindow!

	var refreshTimer: Timer!
	let updateFrequency = 0.2

	@IBOutlet var mallocInfoTable: NSTableView!
	@IBOutlet var mallocCachesTable: NSTableView!

	var mallocInfoSource = MallocRegionsDataSource()
	var mallocCachesSource = MallocCachesDataSource()

	override init() {
		super.init()
		let ok = Bundle.main.loadNibNamed("MallocWindow", owner: self, topLevelObjects: nil)
		assert(ok)
		show()
		mallocInfoTable.dataSource = mallocInfoSource
		mallocCachesTable.dataSource = mallocCachesSource
	}

	func show() {
		window.makeKeyAndOrderFront(nil)
		refreshTimer = Timer.scheduledTimer(withTimeInterval: updateFrequency, repeats: true, block: { _ in
			self.performSelector(onMainThread: #selector(F1SelectionController.refresh), with: nil, waitUntilDone: false)
		})
	}
	func refresh() {
		if !window.isVisible {
			refreshTimer?.invalidate()
			return
		}
		refreshAgentInfo()
		refreshCachesInfo()
	}
	func refreshAgentInfo() {
		let regions = document.doF1Command("peek", "stats/malloc_agent/regions")?.arrayValue
		if regions == nil || regions!.isEmpty { return }
		if mallocInfoSource.updateAllInfo(regions!) {
			mallocInfoTable.reloadData()
		}
	}
	func refreshCachesInfo() {
		let perVP = document.doF1Command("peek", "stats/malloc_caches")?.dictionaryValue
		if perVP == nil || perVP!.isEmpty { return }
		if mallocCachesSource.updateAllInfo(perVP!) {
			mallocCachesTable.reloadData()
		}
	}

	var document: F1SimDocument {
		return NSApp.theDocument!
	}

}

/*=============== MALLOC AGENT DATA SOURCE ===============*/

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

/*=============== MALLOC CACHES DATA SOURCE ===============*/

class MallocCachesDataSource: NSObject, NSTableViewDataSource {
	class SummaryVPInfo: NSObject {
		// we subclass NSObject to get valueForKeyPath
		var name: String = ""
		var bytesAvail: UInt64 = 0
		var numAvail = 0
		var maxAvail = 0
		var numAllocHits = 0
		var numAllocMisses = 0
		var numRecycleHits = 0
		var numRecycleMisses = 0
		var replenished = 0
		var kbAvail: Int { return Int(bytesAvail >> UInt64(10)) }
		var percentFull: Double {
			return (maxAvail == 0 ? 0.0 : Double(numAvail) / Double(maxAvail) * 100.0).round1
		}
	}
	var allVPs: [String: JSON] = [:]
	var allInfo: [SummaryVPInfo] = [] // sorted by name

	func updateAllInfo(_ vps: [String: JSON]) -> Bool {
		// returns whether something changed
		if (vps == allVPs) { return false }
		allVPs = vps
		allInfo = []
		for (name, dict) in vps {
			let summary = SummaryVPInfo()
			summary.name = name
			let cached: [JSON] = dict["cached"]?.arrayValue ?? [] // array of entries e.g. {"avail": 10, "lcs": 6, "max": 3}
			for j in cached {
				let d = j.dictionaryValue
				let lcs = d["lcs"]?.integerValue ?? 0
				let avail = d["avail"]?.integerValue ?? 0
				let max = d["max"]?.integerValue ?? 0
				if (lcs != 0) && (max != 0) {
					summary.bytesAvail += UInt64(avail) << lcs
					summary.numAvail += avail
					summary.maxAvail += max
				}
			}
			summary.numAllocHits = dict["alloc_hit"]?.integerValue ?? 0
			summary.numAllocMisses = dict["alloc_miss"]?.integerValue ?? 0
			summary.numRecycleHits = dict["recycle_hit"]?.integerValue ?? 0
			summary.numRecycleMisses = dict["recycle_miss"]?.integerValue ?? 0
			summary.replenished = dict["replenished"]?.integerValue ?? 0
			allInfo.append(summary)
		}
		allInfo.sort { $0.name < $1.name }
		return true
	}
	var total: SummaryVPInfo {
		let total = SummaryVPInfo()
		total.name = "Total"
		for summary in allInfo {
			total.bytesAvail += summary.bytesAvail
			total.numAvail += summary.numAvail
			total.maxAvail += summary.maxAvail
			total.numAllocHits += summary.numAllocHits
			total.numAllocMisses += summary.numAllocMisses
			total.numRecycleHits += summary.numRecycleHits
			total.numRecycleMisses += summary.numRecycleMisses
			total.replenished += summary.replenished
		}
		return total
	}

	func numberOfRows(in tableView: NSTableView) -> Int {
		return allInfo.count + 1
	}

	func tableView(_ tableView: NSTableView, objectValueFor tableColumn: NSTableColumn?, row: Int) -> Any? {
		let last = row >= allInfo.count
		let info = last ? total : allInfo[row]
		let ident = tableColumn!.identifier
		let value: Any? = info.value(forKeyPath: ident)
		return (value as! NSObject).description
	}
}

