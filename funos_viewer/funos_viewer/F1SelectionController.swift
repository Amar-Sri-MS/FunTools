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

    // Output TAB
    @IBOutlet var selectionInfo: NSTextView!
    @IBOutlet var selectionSamples: SimulationSamplesView!
    @IBOutlet var selectionQueuesText: NSTextView!

    // WUs TAB
    @IBOutlet var wusTable: NSTableView!

    // Misc Stats TAB
    @IBOutlet var inUseField: NSTextField!
    @IBOutlet var modulesInited: NSTextView!

    // Options TAB
    @IBOutlet var selectionRelativeHeat: NSButton!

    // IKV Raw TAB
    @IBOutlet var ikvContainer: NSTextField!
    @IBOutlet var ikvCount: NSTextField!
    @IBOutlet var ikvPuts: NSTextField!
    @IBOutlet var ikvGets: NSTextField!
    @IBOutlet var ikvDeletes: NSTextField!
    @IBOutlet var ikvRehash: NSTextField!

    // IKV TAB

    class WUInfo: NSObject {
        // we subclass NSObject to get valueForKeyPath
        var wu: String = ""
        var count: Int = 0
        var duration: Int = 0
        var avgDuration: Int { return count == 0 ? 0 : duration / count }
    }
    var allInfo: [WUInfo] = []

    var refreshTimer: Timer!
    let updateFrequency = 0.2
    unowned let document: F1SimDocument


    init(document: F1SimDocument) {
        self.document = document
        super.init()
        loadNib()
        selectionTabView.delegate = self
        wusTable.delegate = self
        wusTable.dataSource = self
        // The next two lines are a horrible hack.  Without them, for some reason you need to go to the WUs TAB twice before you get any display.  Makes no sense.
        async {
            self.selectionTabView.performSelector(onMainThread: #selector(NSTabView.selectNextTabViewItem), with: nil, waitUntilDone: true)
            self.selectionTabView.performSelector(onMainThread: #selector(NSTabView.selectPreviousTabViewItem), with: nil, waitUntilDone: false)
        }
    }
    // uncomment to debug leaks
//    deinit {
//        print("DESTROY F1SelectionController")
//    }
    let tabsToRefresh: Set<String> = ["WUs", "Misc Stats", "IKV Raw"]

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
            case "IKV Raw": doRefreshIKVRaw()
            default: break
        }
    }
    func updateAllInfo(counts: [String: JSON], durations: [String: JSON]) -> Bool {
        // returns whether the number of rows changed
        let allExisting: Set<String> = Set(allInfo.map { $0.wu })
        for i in 0 ..< allInfo.count {
            let info = allInfo[i]
            let key = info.wu
            if counts[key] == nil { continue }
            info.count = counts[key]!.integerValue
            info.duration = durations[key]?.integerValue ?? 0
        }
        let newKeysUnsorted = counts.keys.filter { !allExisting.contains($0) }
        if newKeysUnsorted.isEmpty { return false }
        let newKeys = newKeysUnsorted.sorted { counts[$0]!.integerValue > counts[$1]!.integerValue }
        for key in newKeys {
            let info = WUInfo()
            info.wu = key
            info.count = counts[key]!.integerValue
            info.duration = durations[key]?.integerValue ?? 0
            allInfo |= info
        }
        return true
    }
    func doRefreshWUs() {
        let counts = document.doF1Command("peek", "stats/wus/counts")?.dictionaryValue
        if counts == nil || counts!.isEmpty { return }
        let durations = document.doF1Command("peek", "stats/wus/durations")?.dictionaryValue
        if durations == nil || durations!.isEmpty { return }
        let newRows = updateAllInfo(counts: counts!, durations: durations!)
        if newRows { wusTable.noteNumberOfRowsChanged() }
        wusTable.reloadData()
    }
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
    func doRefreshIKVRaw() {
        let cont = ikvContainer!.stringValue
        let propsName = "stats/ikv/\(cont)"
        let stats = document.doF1Command("peek", propsName)?.dictionaryValue
        if stats == nil || stats!.isEmpty { return }
        for (ui, name) in [(ikvPuts!, "puts"), (ikvGets!, "gets"), (ikvDeletes!, "deletes"), (ikvRehash!, "rehash")] {
            ui.integerValue = stats![name]!.integerValue
        }
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
        let allInfoAsMutableArray = NSMutableArray(array: allInfo)
        allInfoAsMutableArray.sort(using: tableView.sortDescriptors)
        allInfo = allInfoAsMutableArray as! [F1SelectionController.WUInfo]
        tableView.reloadData()
    }
    func loadNib() {
        let ok = Bundle.main.loadNibNamed("F1SelectionWindow", owner: self, topLevelObjects: nil)
        assert(ok)
        let view = window.contentView!.subviews.first!
        assert(view == selectionTabView)
        selectionInfo.makeNonEditableFixedPitchOfSize(12.0)   // try to speedup display
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
    func clearSelectionTab() {
        let message = ""
        selectionInfo.string = message
        selectionQueuesText.string = message
        selectionRelativeHeat.isEnabled = false
    }
    @IBAction func fiddleWithOptions(_ sender: NSObject?) {
        document.noteSelectionChangedAndUpdate()
    }
}
