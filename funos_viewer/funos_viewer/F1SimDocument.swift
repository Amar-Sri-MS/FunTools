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
    var heatTimer: Timer!
    let updateFrequency = 0.2

    var window: NSWindow! { return chipView.window }
    
    override init() {
        super.init()
        self.loadNib()
        window.title = "F1 Viewer"
        window.delegate = self
        heatTimer = Timer.scheduledTimer(withTimeInterval: updateFrequency, repeats: true, block: { _ in
            self.performSelector(onMainThread: #selector(F1SimDocument.refreshHeat), with: nil, waitUntilDone: false)
        })
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
    func refreshHeat() {
        let perVP = doF1Command("peek", "stats/per_vp")?.dictionaryValue
        if perVP == nil || perVP!.isEmpty { return }
        var perCluster: [String: Int] = [:]
        var perCore: [String: Int] = [:]
        var sum = 0
        for vp in perVP!.keys {
            let clusterCoreVP = vp.substringAfter(2).split(at: ".").map { $0 }
            assert(clusterCoreVP.count == 3)
            let times = perVP![vp]!.dictionaryValue["wus_received"]!.integerValue
            let cluster = "Cluster\(clusterCoreVP[0])"
            let core = "Core\(clusterCoreVP[0]).\(clusterCoreVP[1])"
            perCluster[cluster] = (perCluster[cluster] ?? 0) + times
            perCore[core] = (perCore[core] ?? 0) + times
            sum += times
        }
        if sum == 0 { return }
//        Swift.print("clusters = \(perCluster) ; cores = \(perCore)")
        chipView.updateHotCores {
            if chipView.selectedUnits.contains($0) { return nil }
            if $0.hasPrefix("Core") {
                let num = perCore[$0] ?? 0
                return Double(num) / Double(sum)
            }
            if $0.hasPrefix("Cluster") {
                let num = perCluster[$0] ?? 0
                return Double(num) / Double(sum)
            }
            return nil
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

        selectionController = F1SelectionController(document: self)

        window.makeKeyAndOrderFront(nil)
        chipView.translatesAutoresizingMaskIntoConstraints = false
        chipView.needsLayout = true
        inputController.firstF1Setup()
        // let winCon = NSWindowController(window: window)
        // Next line is very bizarre but without it NSDocumentController.sharedDocumentController().currentDocument does not work
//        addWindowController(winCon)
    }
    func doF1Command( socket: inout Int32, _ verb: String, _ argsArray: [String]) -> JSON! {
        let debug = foilNeverExecutedWarnings
        let argsArray: String = argsArray.joinDescriptions(", ")
        var s = socket
        let r = dpcrun_command(&s, verb, "[\(argsArray)]")
        socket = s
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
        return doF1Command(socket: &socket, verb, args)
    }
    func log(string: String) {
        selectionController.selectionInfo.string = string
    }
    func doAndLogF1Command(_ verb: String, _ args: String...) {
        log(string: "");
        let json: JSON! = doF1Command(socket: &socket, verb, args)
        log(string: json?.toJSONString() ?? "")
    }
    func doAndLogF1CommandAsync(_ verb: String, _ args: String...) {
        log(string: "");
        async {
            var tempSocket: Int32 = 0
            let json: JSON! = self.doF1Command(socket: &tempSocket, verb, args)
            _ = Darwin.close(tempSocket)
            if json == nil { return }
            let str = json.toJSONString()
            self.performSelector(onMainThread: #selector(F1SimDocument.log), with: str, waitUntilDone: true)
        }
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

    @IBAction func doExecuteTest2(_ sender: NSObject?) {
        let testName = inputController.selectedTest()
        doAndLogF1CommandAsync("execute", testName)
    }
    @IBAction func doExecute10xTest2(_ sender: NSObject?) {
        let testName = inputController.selectedTest()
        doAndLogF1CommandAsync("repeat", "10", "execute", testName)
    }
    @IBAction func doAsyncTest2(_ sender: NSObject?) {
        let testName = inputController.selectedTest()
        doAndLogF1CommandAsync("async", testName)
    }

    @IBAction func fiddleWithOptions(_ sender: NSObject?) {
        noteSelectionChangedAndUpdate()
    }
}
