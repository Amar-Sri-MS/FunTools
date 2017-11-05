//
//  TopLikeController.swift
//  funos_viewer
//
//  Created by Bertrand Serlet on 7/16/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

import AppKit

class TopLikeController: NSObject {
	@IBOutlet var window: NSWindow!
	var refreshTimer: Timer!
	let updateFrequency = 0.2

	@IBOutlet var wusTable: NSTableView!

	var wusInfo = WUInfoDataSource()

	override init() {
		super.init()
		let ok = Bundle.main.loadNibNamed(NSNib.Name(rawValue: "TopLikeWindow"), owner: self, topLevelObjects: nil)
		assert(ok)
		wusTable.dataSource = wusInfo
		wusTable.reloadData()
		show()
	}
	@objc func refresh() {
		if !window.isVisible {
			refreshTimer?.invalidate()
			return
		}
		let counts = document.doF1Command("peek", "stats/wus/counts")?.dictionaryValue
		if counts == nil || counts!.isEmpty { return }
		let durations = document.doF1Command("peek", "stats/wus/durations")?.dictionaryValue
		if durations == nil || durations!.isEmpty { return }
		wusInfo.updateAllInfo(counts: counts!, durations: durations!)
		wusTable.reloadData()
	}
	func show() {
		window.makeKeyAndOrderFront(nil)
		refreshTimer = Timer.scheduledTimer(withTimeInterval: updateFrequency, repeats: true, block: { _ in
			self.performSelector(onMainThread: #selector(TopLikeController.refresh), with: nil, waitUntilDone: false)
		})
	}
	var document: F1SimDocument {
		return NSApp.theDocument!
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
		func descriptionForKey(_ key: String) -> String {
			// The code at the end used to work but is broken with Swift4
			if key == "wu" { return wu.description }
			if key == "count" { return count.description }
			if key == "duration" { return duration.description }
			if key == "avgDuration" { return avgDuration.description }
			print("*** Key not implemented \(key)")
			fatalErrorNYI()
			// return (value(forKey: key) as! NSObject).description
		}
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
		return info.descriptionForKey(tableColumn!.identifier.rawValue)
	}

	func tableView(_ tableView: NSTableView, sortDescriptorsDidChange oldDescriptors: [NSSortDescriptor]) {
		resort(tableView.sortDescriptors)
		tableView.reloadData()
	}
	
}

