//
//  F1SimDocument.swift
//
//  Created by Bertrand Serlet on 11/29/15.
//  Copyright © 2016 Fungible Inc. All rights reserved.
//

import AppKit

extension String {
	func toCCV() -> [String]? {
		let ccv = String(dropFirst(2).dropLast(4)).split(at: ":").map { $0 }
		return ccv.count == 3 ? ccv : nil
	}
}

@objc class F1SimDocument: NSDocument, NSTabViewDelegate, NSWindowDelegate {
	@IBOutlet var chipView: NSChipView!
	var inputController: F1InputController! // All the parameters and such

	var dateLastUpdate: Date!

	var socket: Int32 = 0;
	var heatTimer: Timer!
	let updateFrequency = 0.2
	var clustersGreyedOut = false

	var window: NSWindow! { return chipView.window }

	override init() {
		super.init()
		self.loadNib()
		window.title = "F1 Viewer"
		window.delegate = self
		heatTimer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true, block: { _ in
			self.performSelector(onMainThread: #selector(F1SimDocument.refreshHeat), with: nil, waitUntilDone: false)
		})
	}
	func windowWillClose(_ notification: Notification) {
		window.delegate = nil
		// We need to force an explicit tear down, or else the document does not deinit
		inputController = nil
	}
	var updateLock = Lock()
	var updateInProgress = false
	var cachedDNLinks: Set<F1Block>! = nil
	func grayOutClustersAndCores() {
		let allVPs = doF1Command("peek", "config/all_vps")?.arrayValue
		if allVPs != nil && !allVPs!.isEmpty {
			var clustersSeen: Set<String> = []
			var coresSeen: Set<String> = []
			for faddr in allVPs! {
				let clusterCoreVP = faddr.stringValue.toCCV()!
				let cluster = "Cluster\(clusterCoreVP[0])"
				clustersSeen.insert(cluster)
				let core = "Core\(clusterCoreVP[0]).\(clusterCoreVP[1])"
				coresSeen.insert(core)
			}

			for i in 0 ..< F1.numClusters {
				if !clustersSeen.contains("Cluster\(i)") {
					let layer: CALayer = chipView.layers.units["PC\(i)"]!
					layer.setBackgroundColorRecursive(.extremelyLightGray, .lightGray, 4)
				} else {
					for j in 0 ..< 6 {
						let core = "Core\(i).\(j)"
						if !coresSeen.contains(core) {
							let layer: CALayer = chipView.layers.units[core]!
							layer.setBackgroundColorRecursive(.extremelyLightGray, .lightGray, 1)
						}
					}
				}
			}
			let layer: CALayer = chipView.layers.units["CSU"]!
			layer.setBackgroundColorRecursive(.extremelyLightGray, .lightGray, 4)
		}
	}
	@objc func refreshHeat() {
		if !clustersGreyedOut {
			// One-time for now; we may want to make it more dynamic based on a timer
			grayOutClustersAndCores()
			clustersGreyedOut = true
		}
		let allVPs = doF1Command("peek", "stats/per_vp")?.dictionaryValue
		if allVPs == nil || allVPs!.isEmpty { return }
		var perCluster: [String: Int] = [:]
		var perCore: [String: Int] = [:]
		var perVP: [String: Int] = [:]
		var sum = 0
		for faddr in allVPs!.keys {
			let ccv = faddr.toCCV()
			if ccv == nil { continue }
			let times = allVPs![faddr]!.dictionaryValue["wus_received"]!.integerValue
			let cluster = "Cluster\(ccv![0])"
			let core = "Core\(ccv![0]).\(ccv![1])"
			let vp = "VP\(ccv![0]).\(ccv![1]).\(ccv![2])"
			perCluster[cluster] = (perCluster[cluster] ?? 0) + times
			perCore[core] = (perCore[core] ?? 0) + times
			perVP[vp] = times
			sum += times
		}
		if sum == 0 { return }
		//        Swift.print("clusters = \(perCluster) ; cores = \(perCore)")
		chipView.updateHotCores {
			if chipView.selectedUnits.contains($0) { return nil }
			if $0.hasPrefix("VP") {
				let core = "Core\($0.substring(2 ..< 3))"
				let num = perVP[$0] ?? 0
				return Double(num) / Double(max(perCore[core] ?? 0, 1))
			} else if $0.hasPrefix("Core") {
				let cluster = "Cluster\($0.substring(4 ..< 5))"
				let thisCluster = perCluster[cluster] ?? 0
				let num = perCore[$0] ?? 0
				return Double(num) / Double(max(thisCluster, 1))
			} else if $0.hasPrefix("Cluster") {
				let num = perCluster[$0] ?? 0
				return Double(num) / Double(sum)
			}
			return nil
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
	@objc func noteSimulationProgressedAndUpdate() {
		updateLock.apply { updateInProgress = true }
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
	@objc func noteSelectionChangedAndUpdate() {
		(NSApp as! ViewerApp).clearConsole()
	}
	@objc func noteSelectionChanged(_ note: Notification) {
		performSelector(onMainThread: #selector(F1SimDocument.noteSelectionChangedAndUpdate), with: nil, waitUntilDone: false)
	}
	func loadNib() {
		if inputController != nil { return } // Already initialized
		let ok = Bundle.main.loadNibNamed(NSNib.Name(rawValue: "F1ChipWindow"), owner: self, topLevelObjects: nil)
		assert(ok)
		let center = theNotificationCenter
		center.addObserver(self, selector: #selector(F1SimDocument.noteSelectionChanged(_:)), name: NSNotification.Name("SelectionChanged"), object: chipView)

		inputController = F1InputController(document: self)

		window.makeKeyAndOrderFront(nil)
		chipView.translatesAutoresizingMaskIntoConstraints = false
		chipView.needsLayout = true
		inputController.firstF1Setup()
		// let winCon = NSWindowController(window: window)
		// Next line is very bizarre but without it NSDocumentController.sharedDocumentController().currentDocument does not work
		//        addWindowController(winCon)
	}
	func doF1Command( socket: inout Int32, _ verb: String, _ argsArray: [String]) -> JSON! {
		let debug = foilNeverExecutedWarnings
		let argsArray: String = argsArray.joinDescriptions(", ")
		let argsStr = "[\(argsArray)]"
		var s = socket
		if debug {
			Swift.print("=== COMMAND: \(verb) \(argsStr)")
		}
		let r = dpcrun_command(&s, verb, argsStr) // probably leaks here
		socket = s
		if r == nil {
			Swift.print("*** Error executing \(verb): nil ; socket=\(socket)")
			return nil
		}
		//		Swift.print("Executed command '\(verb)'")
		let str: String = String(cString: r!)
		if debug {
			Swift.print("command '\(verb)' returned '\(str)'")
		}
		let j = try? JSON(str)
		if j == nil {
			return nil
		}
		if j!.dictionaryValue["tid"] != nil && j!.dictionaryValue["result"] != nil {
			return j!.dictionaryValue["result"]
		}
		return j
	}
	func doF1Command(_ verb: String, _ args: String...) -> JSON! {
		return doF1Command(socket: &socket, verb, args)
	}
	@objc func log(string: String) {
		(NSApp as! ViewerApp).setConsole(string)
	}
	func doAndLogF1Command(_ verb: String, _ args: String...) {
		log(string: "")
		let json: JSON! = doF1Command(socket: &socket, verb, args)
		log(string: json?.toJSONString() ?? "")
	}
	func doAndLogF1CommandAsync(_ verb: String, _ args: String...) {
		log(string: "");
		async {
			var tempSocket: Int32 = 0
			let json: JSON! = self.doF1Command(socket: &tempSocket, verb, args)
			_ = Darwin.close(tempSocket)
			if json == nil { return }
			let str = json.toJSONString()
			self.performSelector(onMainThread: #selector(F1SimDocument.log), with: str, waitUntilDone: true)
		}
	}
	// Raise the window showing timelines for packets.
	@IBAction func doHelp(_ sender: NSObject?) {
		let arg = inputController.helpArg.stringValue
		if arg.isEmpty {
			doAndLogF1Command("help")
		} else {
			doAndLogF1Command("help", arg)
		}
	}
	@IBAction func doFibo(_ sender: NSObject?) {
		let n = inputController.fiboArg.intValue
		doAndLogF1Command("fibo", n.description)
	}
	@IBAction func doGeneric(_ sender: NSObject?) {
		let verb = inputController.genericVerb.stringValue
		let arg = inputController.genericArg.stringValue
		doAndLogF1Command(verb, arg)
	}
	@IBAction func doEnableCounters(_ sender: NSObject?) {
		doAndLogF1Command("enable_counters")
	}

	@IBAction func doPeek(_ sender: NSObject?) {
		let key = inputController.keyPath.stringValue
		doAndLogF1Command("peek", key.quotedString())
	}
	@IBAction func doPoke(_ sender: NSObject?) {
		let key = inputController.keyPath.stringValue
		let value = inputController.pokeValue.stringValue
		let isNumber = (Int(value) != nil) || (value.hasPrefix("0x") && (Int(value.substringAfter("0x"), radix: 16) != nil))
		doAndLogF1Command("poke", key.quotedString(), isNumber ? value: value.quotedString())
	}
	@IBAction func doFind(_ sender: NSObject?) {
		let key = inputController.keyPath.stringValue
		doAndLogF1Command("find", key.quotedString())
	}

	@IBAction func doExecuteTest2(_ sender: NSObject?) {
		let testName = inputController.selectedTest()
		let arg1 = inputController.testArg1.stringValue
		let arg2 = inputController.testArg2.stringValue
		if arg1.isEmpty {
			doAndLogF1CommandAsync("execute", testName)
		} else if arg2.isEmpty {
			doAndLogF1CommandAsync("execute", testName, arg1)
		} else {
			doAndLogF1CommandAsync("execute", testName, arg1, arg2)
		}
	}
	@IBAction func doExecute10xTest2(_ sender: NSObject?) {
		let testName = inputController.selectedTest()
		let arg1 = inputController.testArg1.stringValue
		let arg2 = inputController.testArg2.stringValue
		if arg1.isEmpty {
			doAndLogF1CommandAsync("repeat", "10", "execute", testName)
		} else if arg2.isEmpty {
			doAndLogF1CommandAsync("repeat", "10", "execute", testName, arg1)
		} else {
			doAndLogF1CommandAsync("repeat", "10", "execute", testName, arg1, arg2)
		}
	}
	@IBAction func doAsyncTest2(_ sender: NSObject?) {
		let testName = inputController.selectedTest()
		let arg1 = inputController.testArg1.stringValue
		let arg2 = inputController.testArg2.stringValue
		if arg1.isEmpty {
			doAndLogF1CommandAsync("async", testName)
		} else if arg2.isEmpty {
			doAndLogF1CommandAsync("async", testName, arg1)
		} else {
			doAndLogF1CommandAsync("async", testName, arg1, arg2)
		}
	}

	// IKV TAB
	var truthLock = Lock()
	var truth: Set<UInt64> = []

	@IBAction func doCreateIKVStore(_ sender: NSObject?) {
		log(string: "");
		let json = doF1Command("ikvdemo", "create_and_open", inputController.paramsAsString)
		let container = json?.dictionaryValue["ikv_container"]?.integerValue
		if container != nil {
			inputController.ikvContainer = container
			truth = []
			let vapp = NSApp as! ViewerApp
			let ikvController = vapp.ikvController
			ikvController?.ikvContainer.stringValue = container!.description
			ikvController?.startIKVTimer()
		}
		log(string: json?.toJSONString() ?? "")
	}
	func doAndLogIKVCommandAsync(_ subverb: String, _ ikvValues: [UInt64], _ whenDone: VoidBlock! = nil) {
		let params = inputController.paramsAsString
		let args: [String] = [subverb, params, "[" + ikvValues.joinDescriptions(", ") + "]"]
		log(string: "")
		async {
			var tempSocket: Int32 = 0
			let json: JSON! = self.doF1Command(socket: &tempSocket, "ikvdemo", args)
			_ = Darwin.close(tempSocket)
			if json == nil { return }
			let str = json.toJSONString()
			self.performSelector(onMainThread: #selector(F1SimDocument.log), with: str, waitUntilDone: true)
			(NSApp as! ViewerApp).ikvController.performSelector(onMainThread: #selector(IKVController.doRefreshIKV), with: nil, waitUntilDone: true)
			whenDone?()
		}
	}
	func randomValue() -> UInt64 {
		return (UInt64.random() % 9_000_000) + 1_000_000 // low probability of collision
	}
	@IBAction func doIKVPut(_ sender: NSObject?) {
		let repeatCount = inputController.ikvRepeat!.integerValue
		let ikvValues: [UInt64] = (0 ..< repeatCount).map { _ in randomValue() }
		doAndLogIKVCommandAsync("put", ikvValues) {
			self.truthLock.apply { self.truth.formUnion(ikvValues) }
		}
	}
	func pickExistingNAtRandom(_ n: Int) -> [UInt64] {
		let truthAsArray = truthLock.apply { self.truth.map { $0 } }
		var ikvValues: [UInt64] = []
		while ikvValues.count < n {
			ikvValues |= truthAsArray.randomElement()
		}
		return ikvValues
	}
	@IBAction func doIKVGet(_ sender: NSObject?) {
		let repeatCount = inputController.ikvRepeat!.integerValue
		if truth.isEmpty { return }
		doAndLogIKVCommandAsync("get", pickExistingNAtRandom(repeatCount))
	}
	func do1PutAnd10Get() {
		let sema1 = Semaphore()
		let newValue = randomValue()
		doAndLogIKVCommandAsync("put", [newValue]) {
			self.truthLock.apply { _ = self.truth.insert(newValue) }
			sema1.signal()
		}
		sema1.wait()
		let sema2 = Semaphore()
		doAndLogIKVCommandAsync("get", pickExistingNAtRandom(10)) {
			sema2.signal()
		}
		sema2.wait()
	}
	@IBAction func doIKVPutAnd10Get(_ sender: NSObject?) {
		let repeatCount = inputController.ikvRepeat!.integerValue
		async {
			for _ in 0 ..< repeatCount {
				self.do1PutAnd10Get()
			}
		}
	}
	@IBAction func doIKVDelete(_ sender: NSObject?) {
		let repeatCount = inputController.ikvRepeat!.integerValue
		let n = min(repeatCount, truthLock.apply { self.truth.count })
		if n == 0 { return }
		let truthAsArray = truthLock.apply { self.truth.map { $0 } }
		let toDelete = truthAsArray.prefix(n).map {$0 }
		// Remove from truth first
		truthLock.apply { self.truth.formSymmetricDifference(toDelete) }
		doAndLogIKVCommandAsync("delete", toDelete)
	}
	func doPutsThenDeletes(ikvValues: [UInt64]) {
		let sema1 = Semaphore()
		doAndLogIKVCommandAsync("put", ikvValues) {
			self.truthLock.apply { self.truth.formUnion(ikvValues) }
			sema1.signal()
		}
		sema1.wait()
		let sema2 = Semaphore()
		// Remove from truth first
		truthLock.apply { self.truth.formSymmetricDifference(ikvValues) }
		doAndLogIKVCommandAsync("delete", ikvValues) {
			sema2.signal()
		}
		sema2.wait()
	}
	@IBAction func doIKVPutThenDelete(_ sender: NSObject?) {
		let repeatCount = inputController.ikvRepeat!.integerValue
		let ikvValues: [UInt64] = (0 ..< repeatCount).map { _ in randomValue() }
		async {
			self.doPutsThenDeletes(ikvValues: ikvValues)
		}
	}
	@IBAction func noteIKVParamsChanged(_ sender: NSObject?) {
		//        inputController.noteIKVParamsChanged()
	}

	@IBAction func fiddleWithOptions(_ sender: NSObject?) {
		noteSelectionChangedAndUpdate()
	}
}

