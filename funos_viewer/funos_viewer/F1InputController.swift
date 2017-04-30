//
//  F1InputController.swift
//
//  Created by Bertrand Serlet on 5/20/16.
//  Copyright © 2016 Fungible Inc. All rights reserved.
//

import AppKit

class F1InputController: NSObject {
    @IBOutlet var window: NSWindow!
    @IBOutlet var view: NSView!

    var tabView: NSTabView!
    @IBOutlet var numRegisteredCommands: NSTextField!
    @IBOutlet var fiboArg: NSTextField!
    @IBOutlet var keyPath: NSTextField!
    @IBOutlet var pokeValue: NSTextField!
    @IBOutlet var testName: NSTextField!
    @IBOutlet var repeatCheckbox: NSButton!

    var parametersToControls = MappingOfParametersToControls()

    unowned let document: F1SimDocument

    init(document: F1SimDocument) {
        self.document = document
        super.init()
        loadNib()
    }
    // uncomment to debug leaks
//    deinit {
//        print("DESTROY F1InputController")
//    }
    func loadNib() {
        let ok = Bundle.main.loadNibNamed("F1InputWindow", owner: self, topLevelObjects: nil)
        assert(ok)
        assert(view != nil)
        tabView = view.subviews.first as! NSTabView
    }
    func firstF1Setup() {
        let json = document.doF1Command("help")
        if json != nil {
            let num = json!.dictionaryValue.count
            numRegisteredCommands.intValue = Int32(num)
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

    func addUIForAllParameters() {
        let defaultParameters = FunChipSimulationParameters()
        let bounds = tabView.bounds
        for tabID in SimulationParametersTabs {
            let tabItem = tabView.tabViewItem(at: tabID+1)
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

}
