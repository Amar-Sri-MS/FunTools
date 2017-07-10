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
        let docController = NSDocumentController.shared()
        document = F1SimDocument()
        docController.addDocument(document)
    }

    func applicationWillTerminate(_ aNotification: Notification) {
        // Insert code here to tear down your application
    }

}

var mallocController: MallocWindowController! = nil

extension NSApplication {
	var theDocument: F1SimDocument! { return document }

	@IBAction func mallocWindow(_ sender: NSObject?) {
		if mallocController == nil {
			mallocController = MallocWindowController()
		}
		mallocController.show()
	}

}
