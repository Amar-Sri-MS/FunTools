//
//  F1SimDocument.swift
//
//  Created by Bertrand Serlet on 11/29/15.
//  Copyright © 2016 Fungible Inc. All rights reserved.
//

import AppKit

@objc class F1SimDocument: NSDocument, NSTabViewDelegate, NSWindowDelegate {
    // Simulation Parameters
    @IBOutlet var inputPlaceholder: NSView! // replaced after loading XIB file
    // Chip
    @IBOutlet var chipView: NSChipView!
    // Selection
    @IBOutlet var selectionPlaceholder: NSView! // replaced after loading XIB file

    var inputController: F1InputController! // All the parameters and such
    var selectionController: F1SelectionController! // Selection info

    var dateLastUpdate: Date!

    var socket: Int32 = 0;

    var window: FunSimWindow { return chipView.window as! FunSimWindow }
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
        let ipf = inputPlaceholder.frame
        inputPlaceholder.superview!.replaceSubview(inputPlaceholder, with: inputController.view)
        inputController.reinstantiateLayoutConstraints()
        inputController.view.frame = ipf
        inputController.addUIForAllParameters()

        selectionController = F1SelectionController(document: self)
        let scf = selectionPlaceholder.frame
        selectionPlaceholder.superview!.replaceSubview(selectionPlaceholder, with: selectionController.selectionTabView)
        // We need to add constraints back
        selectionController.reinstantiateLayoutConstraints()
        selectionController.selectionTabView.frame = scf

        window.makeKeyAndOrderFront(nil)
        // let winCon = NSWindowController(window: window)
        // Next line is very bizarre but without it NSDocumentController.sharedDocumentController().currentDocument does not work
//        addWindowController(winCon)
    }
    // Raise the window showing timelines for packets.
    @IBAction func doHelp(_ sender: NSObject?) {
        let r = dpcrun_command(&socket, "help", "[]")
        if r == nil {
            Swift.print("*** Error doing help")
        } else {
            let str: String = String(cString: r!)
            let json: JSON = try! JSON(str)
            Swift.print("output = \(json)")
        }
    }

    @IBAction func fiddleWithOptions(_ sender: NSObject?) {
        noteSelectionChangedAndUpdate()
    }
}
