//
//  F1SimDocument.swift
//
//  Created by Bertrand Serlet on 11/29/15.
//  Copyright © 2016 Fungible Inc. All rights reserved.
//

import AppKit

@objc class F1SimDocument: NSDocument, NSTabViewDelegate, NSWindowDelegate {
    // Simulation Parameters
    @IBOutlet var parameters: NSTabView!
    // Chip
    @IBOutlet var chipView: NSChipView!
    // Selection
    @IBOutlet var selectionPlaceholder: NSView! // replaced after loading XIB file

    var selectionController: F1SelectionController! // Selection info

    var parametersToControls = MappingOfParametersToControls()
    var dateLastUpdate: Date!

    var window: FunSimWindow { return chipView.window as! FunSimWindow }
    override init() {
        super.init()
        self.loadNib()
        window.title = ""
        window.delegate = self
    }
    func windowWillClose(_ notification: Notification) {
        window.delegate = nil
        // We need to force an explicit tear down, or else the document does not deinit
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
    func parametersFromUI() -> FunChipSimulationParameters {
        let allParameters = FunChipSimulationParameters()
        let bold = parametersToControls.makeBoldForParameters(allParameters)
        // Mark all the TABs in bold if necessary
        for tabID in SimulationParametersTabs {
            let tabItem = parameters.tabViewItem(at: tabID+1)
            let title = tabItem.label
            if bold.contains(tabID) && !title.hasSuffix("!") {
                tabItem.label = title + "!"
            } else if !bold.contains(tabID) && title.hasSuffix("!") {
                tabItem.label = title.breakAt("!").before
            }
        }
        // Then, all the speciall cases...
        allParameters.fixupAfterReadingFromUI()
        return allParameters
    }
    func addUIForAllParameters() {
        let defaultParameters = FunChipSimulationParameters()
        let bounds = parameters.bounds
        for tabID in SimulationParametersTabs {
            let tabItem = parameters.tabViewItem(at: tabID+1)
            let boxContent = tabItem.view!
            var y: CGFloat = bounds.height - 79.0
            let width = bounds.size.width - 14.0
            var keyView: NSView! = nil
            for parameters in defaultParameters.allParametersWithUI {
                let keys = parameters.keysForTab(tabID)
                if keys.isEmpty { continue }
                let name = parameters.name
                let (section, t) = createParameterSection(parameters, startWithSectionLabel: tabID != 0, keys: keys, width: width, y: y, keyView: &keyView)
                let height = section.bounds.size.height
                y -= height - 7.0 // tighten things a bit
                boxContent.addSubview(section)
                parametersToControls.mergeInCategory(name, t: t)
            }
        }
    }
    func createParameterSection(_ parameters: SimulationParameters, startWithSectionLabel: Bool, keys: [SimulationParameterKey], width: CGFloat, y: CGFloat, keyView: inout NSView!) -> (view: NSView, map: [SimulationParameterKey: SimulationParameterControl]) {
        let frame = NSRect(x: -8.0, y: y, width: width, height: 0)
        let view = NSBox(frame: frame)
        view.borderType = .noBorder
        view.titlePosition = .noTitle
        view.autoresizingMask = NSAutoresizingMaskOptions.viewMinYMargin
        let y = startWithSectionLabel ? view.addParameterSectionName(parameters) : 0.0
        let t = view.addParameterSection(parameters, yStart: y, keys: keys, keyView: &keyView)
        view.sizeToFit()
        return (view, t)
    }
    static var cascadeOrigin = NSZeroPoint
    func loadNib() {
        if selectionController != nil { return } // Already initialized
        let ok = Bundle.main.loadNibNamed("F1ChipWindow", owner: self, topLevelObjects: nil)
        assert(ok)
        let center = theNotificationCenter
        center.addObserver(self, selector: #selector(F1SimDocument.noteSelectionChanged(_:)), name: NSNotification.Name("SelectionChanged"), object: chipView)
        addUIForAllParameters()

        selectionController = F1SelectionController(document: self)
        let scf = selectionPlaceholder.frame
        selectionPlaceholder.superview!.replaceSubview(selectionPlaceholder, with: selectionController.selectionTabView)
        // We need to add constraints back
        selectionController.reinstantiateLayoutConstraints()
        selectionController.selectionTabView.frame = scf

        F1SimDocument.cascadeOrigin = window.cascadeTopLeft(from: F1SimDocument.cascadeOrigin)
        window.makeKeyAndOrderFront(nil)
        let winCon = NSWindowController(window: window)
        winCon.shouldCascadeWindows = true  // does not seem to work
        // Next line is very bizarre but without it NSDocumentController.sharedDocumentController().currentDocument does not work
        addWindowController(winCon)
    }
    override func write(to url: URL, ofType typeName: String) throws {
    }
    override func save(_ sender: Any?) {
        saveAs(sender)
    }
    override func saveAs(_ sender: Any?) {
    }
    // Raise the window showing timelines for packets.
    @IBAction func doHelp(_ sender: NSObject?) {
        dpcclient_test();
    }

    @IBAction func fiddleWithOptions(_ sender: NSObject?) {
        noteSelectionChangedAndUpdate()
    }
}
