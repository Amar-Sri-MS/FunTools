//
//  AppDelegate.swift
//  funos_viewer
//
//  Created by Bertrand Serlet on 4/18/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

import Cocoa

@NSApplicationMain
class AppDelegate: NSObject, NSApplicationDelegate {

    @IBOutlet weak var window: NSWindow!

    func applicationDidFinishLaunching(_ aNotification: Notification) {
        // Insert code here to initialize your application
        UserDefaults.standard.set(true, forKey: "NSConstraintBasedLayoutVisualizeMutuallyExclusiveConstraints")
        let docController = NSDocumentController.shared()
        let doc = F1SimDocument()
        docController.addDocument(doc)
    }

    func applicationWillTerminate(_ aNotification: Notification) {
        // Insert code here to tear down your application
    }


}

