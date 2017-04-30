//
//  F1SimDocument.swift
//
//  Created by Bertrand Serlet on 11/29/15.
//  Copyright © 2016 Fungible Inc. All rights reserved.
//

import AppKit

@objc class F1SimDocument: NSDocument, NSTabViewDelegate, NSWindowDelegate {
    @IBOutlet var chipView: NSChipView!
    var inputController: F1InputController! // All the parameters and such
    var selectionController: F1SelectionController! // Selection info

    var dateLastUpdate: Date!

    var socket: Int32 = 0;

    var window: NSWindow! { return chipView.window }
    
    override init() {
        super.init()
        self.loadNib()
        window.title = "F1 Viewer"
        window.delegate = self
    }
    func windowWillClose(_ notification: Notification) {
        window.delegate = nil
        // We need to force an explicit tear down, or else the document does not deinit
        inputController = nil
        selectionController = nil
    }
    var updateLock = Lock()
    var updateInProgress = false
    var cachedDNLinks: Set<F1Block>! = nil
    func reflectProgressOrSelectionChange() {
        chipView.updateHotCores {
            if chipView.selectedUnits.contains($0) { return nil }
            if $0.hasPrefix("Core") || $0.hasPrefix("Cluster") || $0.hasPrefix("BlockCopy") {
                return nil
            }
            return nil
        }
        if chipView.selectedUnits.contains("DN") {
            let relative = selectionController.isRelativeHeat
            if relative {
                let maximum = cachedDNLinks.maximize { $0.stats["MessagesEnqueued"] }
                if maximum == nil { return } // nothing has been active yet
            }
        }
        if chipView.selectedUnits.contains("SN") {
            let segmentStats = SNSegmentStats(networkName: "SN")
            var maxi: Double = 0
           if !segmentStats.isEmpty {
                if selectionController.isRelativeHeat {
                    maxi = segmentStats.maximize { $1}!.maximum
                }
                if maxi == 0.0 { return }
                chipView.updateHotSegments(networkName: "SN") {
                    (segmentStats[$0] ?? 0.0) / maxi
                }
            }
        }
        if chipView.selectedUnits.contains("CN") {
            let segmentStats = SNSegmentStats(networkName: "CN")
            var maxi: Double = 0
            if !segmentStats.isEmpty {
                if selectionController.isRelativeHeat {
                    maxi = segmentStats.maximize { $1}!.maximum
                }
                if maxi == 0.0 { return }
                chipView.updateHotSegments(networkName: "CN") {
                    (segmentStats[$0] ?? 0.0) / maxi
                }
            }
        }
    }
    
    // Gather statistics on use of the signalling or coherency network
    // in order to show level of activity on each link.
    func SNSegmentStats(networkName: UnitName) -> [String:Double]{
        return [:]
    }
    func noteMouseOverDNSegment(_ note: Notification) {
        if !chipView.selectedUnits.contains("DN") { return }
    }
    func noteMouseOverSNSegment(_ note: Notification) {
        if !chipView.selectedUnits.contains("SN") { return }
    }
    func noteSimulationProgressedAndUpdate() {
        updateLock.apply { updateInProgress = true }
        reflectProgressOrSelectionChange()
        noteSelectionChangedAndUpdate()
        updateLock.apply { updateInProgress = false }
    }
    
    func noteSimulationProgressed(_ note: Notification) {
        let now = Date()
        if updateLock.apply( { return updateInProgress }) {
            // update already in progress, we give up for now
            return
        }
        dateLastUpdate = now
        performSelector(onMainThread: #selector(F1SimDocument.noteSimulationProgressedAndUpdate), with: nil, waitUntilDone: false)
    }
    func tabView(_ tabView: NSTabView, didSelect tabViewItem: NSTabViewItem?) {
        noteSelectionChangedAndUpdate()
    }
    func noteSelectionChangedAndUpdate() {
        selectionController.clearSelectionTab()
    }
    func noteSelectionChanged(_ note: Notification) {
        performSelector(onMainThread: #selector(F1SimDocument.noteSelectionChangedAndUpdate), with: nil, waitUntilDone: false)
    }
    func loadNib() {
        if inputController != nil { return } // Already initialized
        let ok = Bundle.main.loadNibNamed("F1ChipWindow", owner: self, topLevelObjects: nil)
        assert(ok)
        let center = theNotificationCenter
        center.addObserver(self, selector: #selector(F1SimDocument.noteSelectionChanged(_:)), name: NSNotification.Name("SelectionChanged"), object: chipView)

        inputController = F1InputController(document: self)
//        inputController.reinstantiateLayoutConstraints()
        inputController.addUIForAllParameters()

        selectionController = F1SelectionController(document: self)

        window.makeKeyAndOrderFront(nil)
        chipView.translatesAutoresizingMaskIntoConstraints = false
        chipView.needsLayout = true
        inputController.firstF1Setup()
        // let winCon = NSWindowController(window: window)
        // Next line is very bizarre but without it NSDocumentController.sharedDocumentController().currentDocument does not work
//        addWindowController(winCon)
    }
    func doF1Command(_ verb: String, _ argsArray: [String]) -> JSON! {
        let debug = foilNeverExecutedWarnings
        let argsArray: String = argsArray.joinDescriptions(", ")
        let r = dpcrun_command(&socket, verb, "[\(argsArray)]")
        if r == nil {
            Swift.print("*** Error executing \(verb): nil ; socket=\(socket)")
            return nil
        }
        let str: String = String(cString: r!)
        if debug {
            Swift.print("command '\(verb)' returned '\(str)'")
        }
        return try? JSON(str)
    }
    func doF1Command(_ verb: String, _ args: String...) -> JSON! {
        return doF1Command(verb, args)
    }
    func doAndLogF1Command(_ verb: String, _ args: String...) {
        selectionController.selectionInfo.string = ""
        let json: JSON! = doF1Command(verb, args)
        selectionController.selectionInfo.string = json?.toJSONString() ?? ""
    }
    // Raise the window showing timelines for packets.
    @IBAction func doHelp(_ sender: NSObject?) {
        doAndLogF1Command("help")
    }

    @IBAction func doEnableCounters(_ sender: NSObject?) {
        doAndLogF1Command("enable_wdi")
    }
    @IBAction func doFibo(_ sender: NSObject?) {
        let n = inputController.fiboArg.intValue
        doAndLogF1Command("fibo", n.description)
    }

    @IBAction func doPeek(_ sender: NSObject?) {
        let key = inputController.keyPath.stringValue
        doAndLogF1Command("peek", key.quotedString())
    }
    @IBAction func doPoke(_ sender: NSObject?) {
        let key = inputController.keyPath.stringValue
        let value = inputController.pokeValue.stringValue
        doAndLogF1Command("poke", key.quotedString(), value.quotedString())
    }
    @IBAction func doFind(_ sender: NSObject?) {
        let key = inputController.keyPath.stringValue
        doAndLogF1Command("find", key.quotedString())
    }
    @IBAction func doExecuteTest(_ sender: NSObject?) {
        let isRepeat = inputController.repeatCheckbox.state != 0
        let testName = inputController.testName.stringValue
        isRepeat ? doAndLogF1Command("repeat", "10", "execute", testName) : doAndLogF1Command("execute", testName)
    }
    @IBAction func doAsyncTest(_ sender: NSObject?) {
        let testName = inputController.testName.stringValue
        doAndLogF1Command("async", testName)
    }

    @IBAction func fiddleWithOptions(_ sender: NSObject?) {
        noteSelectionChangedAndUpdate()
    }
}
