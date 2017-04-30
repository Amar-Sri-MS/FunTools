//
//  F1SelectionController.swift
//
//  Created by Bertrand Serlet on 5/20/16.
//  Copyright © 2016 Fungible Inc. All rights reserved.
//

import AppKit

class F1SelectionController: NSObject, NSTabViewDelegate, NSTableViewDelegate, NSTableViewDataSource {
    @IBOutlet var window: NSWindow!
    @IBOutlet var selectionTabView: NSTabView!
    @IBOutlet var selectionInfo: NSTextView!
    @IBOutlet var selectionSamples: SimulationSamplesView!
    @IBOutlet var selectionMessagesText: NSTextView!
    @IBOutlet var selectionQueuesText: NSTextView!
    @IBOutlet var selectionRelativeHeat: NSButton!

    @IBOutlet var wusTable: NSTableView!

    var wuTimer: Timer!
    unowned let document: F1SimDocument

    init(document: F1SimDocument) {
        self.document = document
        super.init()
        loadNib()
        selectionTabView.delegate = self
        wusTable.delegate = self
        wusTable.dataSource = self
    }
    // uncomment to debug leaks
//    deinit {
//        print("DESTROY F1SelectionController")
//    }
    public func tabView(_ tabView: NSTabView, didSelect tabViewItem: NSTabViewItem?) {
//        print("Received notification tabView changed to \(tabViewItem!.label)")
        if tabViewItem!.label == "WUs" {
            wuTimer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true, block: { _ in
                self.performSelector(onMainThread: #selector(F1SelectionController.refreshWU), with: nil, waitUntilDone: false)
            })
        }
    }
    func refreshWU() {
        let tabViewItem = selectionTabView.selectedTabViewItem
        if tabViewItem != nil && tabViewItem!.label == "WUs" {
            doRefreshWUs()
        } else {
            wuTimer?.invalidate()
        }
    }
    struct WUInfo {
        var wu: String = ""
        var count: Int = 0
        var duration: Int = 0
    }
    var allInfo: [WUInfo] = []
    func textFieldAt(atColumn col: Int, row: Int) -> NSTextField! {
        return wusTable.view(atColumn: col, row: row, makeIfNecessary: false) as? NSTextField
    }
    func doRefreshWUs() {
        let counts = document.doF1Command("peek", "stats/wus/counts")?.dictionaryValue
        if counts == nil || counts!.isEmpty { return }
        let durations = document.doF1Command("peek", "stats/wus/durations")?.dictionaryValue
        if durations == nil || durations!.isEmpty { return }
        let allExisting: Set<String> = Set(allInfo.map { $0.wu })
        for i in 0 ..< allInfo.count {
            var info = allInfo[i]
            let key = info.wu
            if counts![key] == nil { continue }
            info.count = counts![key]!.integerValue
            info.duration = durations![key]?.integerValue ?? 0
            allInfo[i] = info
        }
        var newRows = false
        for key in counts!.keys where !allExisting.contains(key) {
            var info = WUInfo()
            info.wu = key
            info.count = counts![key]!.integerValue
            info.duration = durations![key]?.integerValue ?? 0
            allInfo |= info
            newRows = true
        }
//        if newRows {
//            wusTable.noteNumberOfRowsChanged()
//        } else {
            wusTable.reloadData()
//        }
    }
    func numberOfRows(in tableView: NSTableView) -> Int {
        return allInfo.count
    }
    func tableView(_ tableView: NSTableView, objectValueFor tableColumn: NSTableColumn?, row: Int) -> Any? {
        let info = allInfo[row]
        switch tableColumn!.title {
            case "WU name": return info.wu
            case "count": return info.count.description
            case "duration": return info.duration.description
            case "avg duration":
                let d = info.count == 0 ? 0.0 : Double(info.duration) / Double(info.count)
                return d.round2.description
            default: fatalError("identifier = \(tableColumn!.title)")
        }
    }
    func loadNib() {
        let ok = Bundle.main.loadNibNamed("F1SelectionWindow", owner: self, topLevelObjects: nil)
        assert(ok)
        let view = window.contentView!.subviews.first!
        assert(view == selectionTabView)
        selectionInfo.makeNonEditableFixedPitchOfSize(12.0)   // try to speedup display
        selectionMessagesText.makeNonEditableFixedPitchOfSize(12.0)
        selectionQueuesText.makeNonEditableFixedPitchOfSize(12.0)
        clearSelectionTab()
        window.makeKeyAndOrderFront(nil)
    }
    var isRelativeHeat: Bool { return selectionRelativeHeat.boolValue }

    func updateSelectionTabForUnit(_ unit: F1Block) {
        // Note that unit can be a single unit or a group of units
        switch (selectionTabView.selectedTabViewItem!.identifier! as AnyObject).description {
        case "0":
            selectionInfo.setStringPreservingSelection(unit.simulationInfoFullSummary())
            selectionSamples.setSamples(unit.samples)
        case "1":
            selectionMessagesText.setStringPreservingSelection(unit.simulationInfoMessaging())
        case "2":
            selectionQueuesText.setStringPreservingSelection(unit.simulationInfoQueues())
        case "3":
            selectionRelativeHeat.isEnabled = unit.name == "DN" || unit.name == "SN"
        default: fatalError()
        }
        selectionTabView.needsDisplay = true
        unit.noteStateChanged() // we force taking a new sample
    }
    func clearSelectionTab() {
        let message = ""
        selectionInfo.string = message
        selectionMessagesText.string = message
        selectionQueuesText.string = message
        selectionRelativeHeat.isEnabled = false
    }
    @IBAction func fiddleWithOptions(_ sender: NSObject?) {
        document.noteSelectionChangedAndUpdate()
    }
}
