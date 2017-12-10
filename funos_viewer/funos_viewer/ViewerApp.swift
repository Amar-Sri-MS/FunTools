//
//  ViewerApp.swift
//  funos_viewer
//
//  Created by Bertrand Serlet on 7/16/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

import Cocoa


class ViewerApp: NSApplication {
	@IBOutlet var shortCuts: NSPanel!

	var consoleController: ConsoleController!
	@IBAction func consoleWindow(_ sender: NSObject?) {
		if consoleController == nil {
			consoleController = ConsoleController()
		}
		consoleController.show()
	}

	var topLikeController: TopLikeController!
	@IBAction func topLikeWindow(_ sender: NSObject?) {
		if topLikeController == nil {
			topLikeController = TopLikeController()
		}
		topLikeController.show()
	}

	var miscController: MiscWindowController! = nil
	@IBAction func miscWindow(_ sender: NSObject?) {
		if miscController == nil {
			miscController = MiscWindowController()
		}
		miscController.show()
	}

	var mallocController: MallocWindowController! = nil
	@IBAction func mallocWindow(_ sender: NSObject?) {
		if mallocController == nil {
			mallocController = MallocWindowController()
		}
		mallocController.show()
	}

	var ikvController: IKVController! = nil
	@IBAction func ikvWindow(_ sender: NSObject?) {
		if ikvController == nil {
			ikvController = IKVController()
		}
		ikvController.show()
	}

	func clearConsole() {
		if consoleController == nil {
			consoleController = ConsoleController()
		}
		consoleController.clearSelectionTab()
	}
	func setConsole(_ string: String) {
		if consoleController == nil {
			consoleController = ConsoleController()
		}
//		consoleController.selectionInfo.string = string
		consoleController.window.viewsNeedDisplay = true
	}

}
