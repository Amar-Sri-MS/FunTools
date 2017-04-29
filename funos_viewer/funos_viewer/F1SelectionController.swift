//
//  F1SelectionController.swift
//
//  Created by Bertrand Serlet on 5/20/16.
//  Copyright © 2016 Fungible Inc. All rights reserved.
//

import AppKit

class F1SelectionController: NSObject {
    @IBOutlet var window: NSWindow!
    @IBOutlet var selectionTabView: NSTabView!
    @IBOutlet var selectionInfo: NSTextView!
    @IBOutlet var selectionSamples: SimulationSamplesView!
    @IBOutlet var selectionMessagesText: NSTextView!
    @IBOutlet var selectionQueuesText: NSTextView!
    @IBOutlet var selectionRelativeHeat: NSButton!

    unowned let document: F1SimDocument

    init(document: F1SimDocument) {
        self.document = document
        super.init()
        loadNib()
    }
    // uncomment to debug leaks
//    deinit {
//        print("DESTROY F1SelectionController")
//    }
    func loadNib() {
        let ok = Bundle.main.loadNibNamed("F1SelectionView", owner: self, topLevelObjects: nil)
        assert(ok)
        let view = window.contentView!.subviews.first!
        assert(view == selectionTabView)
        selectionInfo.makeNonEditableFixedPitchOfSize(12.0)   // try to speedup display
        selectionMessagesText.makeNonEditableFixedPitchOfSize(12.0)
        selectionQueuesText.makeNonEditableFixedPitchOfSize(12.0)
        clearSelectionTab()
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
    func reinstantiateLayoutConstraints() {
        let superView = selectionTabView.superview!
        selectionTabView.removeConstraints(selectionTabView.constraints)
        selectionTabView.translatesAutoresizingMaskIntoConstraints = false
        superView.addConstraint(NSLayoutConstraint(item: superView, attribute: .top, relatedBy: .equal, toItem: selectionTabView, attribute: .top, multiplier: 1.0, constant: -4.0))
        superView.addConstraint(NSLayoutConstraint(item: superView, attribute: .bottom, relatedBy: .equal, toItem: selectionTabView, attribute: .bottom, multiplier: 1.0, constant: 3.0))
        superView.addConstraint(NSLayoutConstraint(item: superView, attribute: .trailing, relatedBy: .equal, toItem: selectionTabView, attribute: .trailing, multiplier: 1.0, constant: 2.0))
        superView.addConstraint(NSLayoutConstraint(item: document.chipView, attribute: .trailing, relatedBy: .equal, toItem: selectionTabView, attribute: .leading, multiplier: 1.0, constant: -4.0))
        let width = selectionTabView.bounds.width
        selectionTabView.addConstraint(NSLayoutConstraint(item: selectionTabView, attribute: .width, relatedBy: .equal, toItem: nil, attribute: .notAnAttribute, multiplier: 1.0, constant: width))
        selectionTabView.needsLayout = true
        selectionTabView.delegate = document
    }

}
