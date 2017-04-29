//
//  F1InputController.swift
//
//  Created by Bertrand Serlet on 5/20/16.
//  Copyright © 2016 Fungible Inc. All rights reserved.
//

import AppKit

class F1InputController: NSObject {
    @IBOutlet var view: NSView!
    var tabView: NSTabView!

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
        let ok = Bundle.main.loadNibNamed("F1InputView", owner: self, topLevelObjects: nil)
        assert(ok)
        assert(view != nil)
        tabView = view.subviews.first as! NSTabView
    }
    func reinstantiateLayoutConstraints() {
//        let superView = selectionTabView.superview!
//        selectionTabView.removeConstraints(selectionTabView.constraints)
//        selectionTabView.translatesAutoresizingMaskIntoConstraints = false
//        superView.addConstraint(NSLayoutConstraint(item: superView, attribute: .top, relatedBy: .equal, toItem: selectionTabView, attribute: .top, multiplier: 1.0, constant: -4.0))
//        superView.addConstraint(NSLayoutConstraint(item: superView, attribute: .bottom, relatedBy: .equal, toItem: selectionTabView, attribute: .bottom, multiplier: 1.0, constant: 3.0))
//        superView.addConstraint(NSLayoutConstraint(item: superView, attribute: .trailing, relatedBy: .equal, toItem: selectionTabView, attribute: .trailing, multiplier: 1.0, constant: 2.0))
//        superView.addConstraint(NSLayoutConstraint(item: document.chipView, attribute: .trailing, relatedBy: .equal, toItem: selectionTabView, attribute: .leading, multiplier: 1.0, constant: -4.0))
//        let width = selectionTabView.bounds.width
//        selectionTabView.addConstraint(NSLayoutConstraint(item: selectionTabView, attribute: .width, relatedBy: .equal, toItem: nil, attribute: .notAnAttribute, multiplier: 1.0, constant: width))
//        selectionTabView.needsLayout = true
//        selectionTabView.delegate = document
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
