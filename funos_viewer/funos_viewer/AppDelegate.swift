//
//  AppDelegate.swift
//  funos_viewer
//
//  Created by Bertrand Serlet on 4/18/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

import Cocoa

fileprivate var document: F1SimDocument!

@NSApplicationMain class AppDelegate: NSObject, NSApplicationDelegate {

    func applicationDidFinishLaunching(_ aNotification: Notification) {
        // Insert code here to initialize your application
        UserDefaults.standard.set(true, forKey: "NSConstraintBasedLayoutVisualizeMutuallyExclusiveConstraints")
        let docController = NSDocumentController.shared
        document = F1SimDocument()
        docController.addDocument(document)
	let ok = Bundle.main.loadNibNamed(NSNib.Name(rawValue: "Buttons"), owner: NSApp, topLevelObjects: nil)
	assert(ok)
	(NSApp as! ViewerApp).shortCuts.makeKeyAndOrderFront(nil)
    }

    func applicationWillTerminate(_ aNotification: Notification) {
        // Insert code here to tear down your application
    }

}

extension NSApplication {
	var theDocument: F1SimDocument! { return document }
}
