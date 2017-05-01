//
//  F1InputController.swift
//
//  Created by Bertrand Serlet on 5/20/16.
//  Copyright © 2016 Fungible Inc. All rights reserved.
//

import AppKit

class F1InputController: NSObject, NSOutlineViewDataSource {
    @IBOutlet var window: NSWindow!
    @IBOutlet var view: NSView!

    var tabView: NSTabView!

    // Commands TAB
    @IBOutlet var numRegisteredCommands: NSTextField!
    @IBOutlet var fiboArg: NSTextField!
    @IBOutlet var keyPath: NSTextField!
    @IBOutlet var pokeValue: NSTextField!
    @IBOutlet var testName: NSTextField!
    @IBOutlet var repeatCheckbox: NSButton!

    // Tests TAB
    @IBOutlet var tests: NSOutlineView!
    @IBOutlet var testName2: NSTextField!

    unowned let document: F1SimDocument

    init(document: F1SimDocument) {
        self.document = document
        super.init()
        loadNib()
        tests.dataSource = self
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

    func outlineView(_ outlineView: NSOutlineView, numberOfChildrenOfItem item: Any?) -> Int {
        if item == nil { return 2 }
        return 0
    }
    func outlineView(_ outlineView: NSOutlineView, isItemExpandable item: Any) -> Bool {
        return false
    }
    func outlineView(_ outlineView: NSOutlineView, child index: Int, ofItem item: Any?) -> Any {
        if item == nil {
            switch index {
            case 0: return "bstest" as NSString
            case 1: return "counter" as NSString
            default: return "???" as NSString
            }
        }
        return "Error" as NSString
    }
    func outlineView(_ outlineView: NSOutlineView, objectValueFor tableColumn: NSTableColumn?, byItem item: Any?) -> Any? {
        return item
    }
    func selectedTest() -> String {
        let row = tests.selectedRow
        return tests.item(atRow: row) as! String
    }
}
