//
//  F1Definitions.swift
//  funos_viewer
//
//  Created by Bertrand Serlet on 4/23/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

import Foundation
import AppKit

typealias ClockCycle = Int32 // It's not important what this is, as long it's not Int to catch errors

typealias ActivityID = String

typealias UnitName = String

/*=============== ENUMERATIONS SHOWN IN THE UI ===============*/

protocol EnumUIChoice: Equatable {
    static func allChoices() -> [String]
    static func fromInt(_ index: Int) -> Self // needed because can't generically use init(rawValue:...)
}

extension EnumUIChoice {
    static func fromChoice(_ choice: String) -> Self {
        let index = allChoices().index(of: choice)!
        return Self.fromInt(index)
    }
}

/*=============== DIRECTION ===============*/

enum CardinalDirection: Int, CustomStringConvertible {
    // Note: some code depends on the ordering of these
    case north = 0
    case east
    case south
    case west
    var description: String {
        switch self {
        case .north: return "North"
        case .east: return "East"
        case .south: return "South"
        case .west: return "West"
        }
    }
    static func all() -> [CardinalDirection] {
        return [.north, .east, .south, .west]
    }
    var opposite: CardinalDirection {
        switch self {
        case .north: return .south
        case .east: return .west
        case .south: return .north
        case .west: return .east
        }
    }
    var rotateClockWise: CardinalDirection {
        switch self {
        case .north: return .east
        case .east: return .south
        case .south: return .west
        case .west: return .north
        }
    }
    var rotateCounterClockWise: CardinalDirection {
        switch self {
        case .north: return .west
        case .east: return .north
        case .south: return .east
        case .west: return .south
        }
    }
}

/*=============== MISC ===============*/

let clockCyclesFormatter: StatisticsCustomValuePrettyPrinter = { v in "\(v.round2)c" }
let twoDecimalsFormatter: StatisticsCustomValuePrettyPrinter = { v in "\(v.round2)" }


class F1Block: CustomStringConvertible, Hashable, Equatable, Comparable {

    /*=============== SET UP   ===============*/

    // Each simulation unit must have a different name (unique across the entire chip)
    var name: UnitName {
        fatalErrorMustBeImplementedBySubclass()
    }
    // top level units have their stats listed; others are private
    var topLevel = true
    var container: F1Block! { return nil }

    /*=============== SIMULATION  ===============*/

    // This state is managed by the simulation

    var stats: Statistics = Statistics(locked: true)
    var samples: SimulationScaledSamples!

    var now: Int { return 0 }
    var simulationLineWidth: Int { return 33 }
    func noteStateChanged() {
        // Should be called whenever the state of the simulation unit changes
        // in order to record samples
        recordAllSamples()
    }
    func recordAllSamples() {
        if let s = samples as? SimulationSamples {
            s.record(Int(now), value: takeSample())
        }
    }
    func takeSample() -> Double { return 0.0 } // should be subclassed

    var description: String { return name }
    var skipZerosForUnitStatsDescription: Bool { return true } // overridable
    func unitStatsDescriptionWithIndent(_ level: Int, maximumLineLength: Int) -> String {
        // Overridable
        return stats.descriptionWithIndent(level, indentStructuredKeys: true, skipZeroKeys: skipZerosForUnitStatsDescription, maximumLineLength: maximumLineLength)
    }

    func simulationInfoMiniSummary() -> String {
        // Overridable
        // What is shown in the text box in the chip view
        // Also gets reproduced in the selection summary
        // Should NOT be \n terminated
        return ""
    }

    // Displays mini threshold data for the unit's box itself.
    // Text should not be \n terminated.
    // Subclasses should override.
    func simulationInfoMiniThroughput() -> String {
        return ""
    }

    // Generates text for the "Sigma" summary tab in the selection
    // detail window.
    func simulationInfoFullSummary() -> String {
        if stats.isEmpty { return name }
        let mini = simulationInfoMiniSummary()
        let statsDesc = unitStatsDescriptionWithIndent(0, maximumLineLength: simulationLineWidth)
        return name + "\n\n" + (mini.isEmpty ? "" : mini + "\n\n") + statsDesc
    }

    // Generates text for the "Msgs" tab in the selection detail window.
    func simulationInfoMessaging() -> String {
        return name
    }

    // Generates text for the "Queues" tab in the selection detail window.
    func simulationInfoQueues() -> String {
        let num = numberOfMessagesInAllHWQueues()
        return name + "\n\n" + "NumMessagesInAllQueues: \(num)"
    }
    func numberOfMessagesInAllHWQueues() -> Int { return 0 }

    func error(_ str: String) {
        print("*** \(now): @\(name) \(str)")
    }
    func fixupKeysForMultipleSelection(_ stats: StatisticsByMerging) {
        // Override this for unit types that can display stats for multiple units
    }
    func samplesToJSON() -> JSON {
        // Return JSON.null if empty
        if samples == nil { return JSON.null }
        return samples.toJSON()
    }
    func samplesRestoreFromJSON(_ json: JSON) {
        if json == JSON.null { return }
        (samples as? SimulationSamples)?.restoreFromJSON(json)
    }

    // We implement Hashable so that units hash
    var hashValue: Int { return name.hashValue }

    static func ==(lhs: F1Block, rhs: F1Block) -> Bool {
        if lhs === rhs { return true }
        return lhs.name == rhs.name
    }
    static func <(lhs: F1Block, rhs: F1Block) -> Bool {
        return lhs.name < rhs.name
    }
    
}


enum GeneralMode: Int, EnumUIChoice {
    case normal = 0
    case dnUnitTestNone     // No packets generated at all.
    case dnUnitTest1        // 1 Ping over DN from NU0 to Cluster7 and back
    case dnUnitTest10       // 10 Ping over DN from NU0 to Cluster7
    case blockCopyBMToBM   // CSU requests block copy test
    case blockCopyHBMToBM  // CSU requests block copy test
    case blockCopyBMToHBM   // CSU requests block copy test
    case blockCopyHBMToHBM  // CSU requests block copy test
    var description: String {
        return GeneralMode.allChoices()[rawValue]
    }
    static func allChoices() -> [String] {
        return ["Normal", "DNUnitTestNone", "DNUnitTest1", "DNUnitTest10", "BlockCopyBMToBM", "BlockCopyHBMToBM", "BlockCopyBMToHBM", "BlockCopyHBMToHBM"]
    }
    static func fromInt(_ index: Int) -> GeneralMode {
        return GeneralMode(rawValue: index)!
    }
}

enum LoadGeneratorMode: Int, EnumUIChoice {
    case normal = 0
    case dnCol2Half     // 50% load on the last column of DN
    case core6_3_Busy   // Put 50% load on all VPs of a core
    case cluster6_Busy  // Put 50% load of all VPs of a cluster
    var description: String {
        return LoadGeneratorMode.allChoices()[rawValue]
    }
    static func allChoices() -> [String] {
        return ["Normal", "DNCol2Half", "Core6_3_Busy", "Cluster6_Busy"]
    }
    static func fromInt(_ index: Int) -> LoadGeneratorMode {
        return LoadGeneratorMode(rawValue: index)!
    }
}


class GeneralSimulationParameters: SimulationParameters {
    var name: String { return "General" }
    var all: [SimulationParameterKey: JSON] = [
        // Flows
        "NU->BM->HU": true,
        "num100GbE": 1.5,
        "NU->BM->NU": true,
        "route100GbE": 1.5,
        "HU->BM->NU": true,
        "bandwidthPushed": 2.0, // times 100 * Gb
        "NU->BM->HBM->BM->HU": true,
        "packetsViaHBMx100Gb": 1.5,
        // Other
        "randomize": true,
        "useVPBlockCopy": true,
        "mode": "Normal",
        "unitTestRepeat": false,
        "loadGenerator": "Normal",
        ]
    var keysForFlowsUI: [SimulationParameterKey] { return [
        "NU->BM->HU", "num100GbE",
        "NU->BM->NU", "route100GbE",
        "HU->BM->NU", "bandwidthPushed",
        "NU->BM->HBM->BM->HU", "packetsViaHBMx100Gb",
        ]
    }
    var keysForConfigUI: [SimulationParameterKey] { return ["mode", "unitTestRepeat", "loadGenerator", "randomize", "useVPBlockCopy"] }
    var keysForCommandsUI: [SimulationParameterKey] { return [] }
    var keysToUILabels: [SimulationParameterKey: String] {
        return [
            "NU->BM->HU": "Simple network to host",
            "num100GbE": "packets x 100Gb",
            "NU->BM->NU": "Switch/Route functionality",
            "route100GbE": "packets x 100Gb",
            "HU->BM->NU": "Command buffers egress",
            "bandwidthPushed": "buffers x 100Gb",
            "NU->BM->HBM->BM->HU": "Network to host via HBM",
            "packetsViaHBMx100Gb": "packets x 100Gb",
            "randomize": "randomize",
            "useVPBlockCopy": "useVPBlockCopy",
            "mode": "mode",
            "unitTestRepeat": "repeat unit test",
            "loadGenerator": "load generator",
        ]
    }
    var toolTips: [SimulationParameterKey: String] {
        return [
            "NU->BM->HU": "Packets are delivered to NU and egress at HU",
            "num100GbE": "Control the rate of packets delivered from NU to thehost; 0 is OK and means no packets",
            "NU->BM->NU": "Packets at delivered at a random NU, are stored in BM, and sent by another NU",
            "route100GbE": "Control the rate of packets switched from 1 NU to another; 0 is OK",
            "HU->BM->NU": "Command buffers ring a doorbell then the commands are gathered then the buffers are fetched and egressed to NU",
            "bandwidthPushed": "Bandwith pushed by the HostGenerator to the HUs; 0 OK",
            "NU->BM->HBM->BM->HU": "Packets are delivered to NU and egress at HU; They are stored to HBM, and after some delay fetched from HBM",
            "packetsViaHBMx100Gb": "Bandwidth pushed to NU that must be stored then fetched from HBM",
            "randomize": "Randomize packet generation vs. a simple cycling of choices.  Also when true processing times are randomized (between 0.5x and 1.5x)",
            "useVPBlockCopy": "Uses code to do a block copy vs. use accelerator",
            "mode": "Normal simulation mode vs. unit tests",
            "unitTestRepeat": "Repeat unit test 10 times",
            "loadGenerator": "Send 1 Ping between NU2 and HBM7 and back every other cycle",
        ]
    }
    var enumChoices: [SimulationParameterKey: [String]]! {
        return ["mode": GeneralMode.allChoices(), "loadGenerator": LoadGeneratorMode.allChoices()]
    }

    var randomize: Bool { return self["randomize"] }
    var useVPBlockCopy: Bool { return self["useVPBlockCopy"] }
    var mode: GeneralMode { return .fromChoice(self["mode"]) }
    var unitTestRepeat: Bool { return self["unitTestRepeat"] }
    var loadGenerator: LoadGeneratorMode { return .fromChoice(self["loadGenerator"]) }
    var num100GbE: Double { return all["NU->BM->HU"]!.boolValue ? self["num100GbE"] : 0.0 }
    var route100GbE: Double { return all["NU->BM->NU"]!.boolValue ? self["route100GbE"] : 0.0 }
    var bandwidthPushed: Double { return all["HU->BM->NU"]!.boolValue ? self["bandwidthPushed"] : 0.0 }
    var packetsViaHBMx100Gb: Double { return all["NU->BM->HBM->BM->HU"]!.boolValue ? self["packetsViaHBMx100Gb"] : 0.0 }

    var description: String { return "\(all)" }
}

struct FunChipSimulationParameters {
    var general = GeneralSimulationParameters()
    var allParametersWithUI: [SimulationParameters] {
        return [general]
    }

    func updateFromJSON(_ json: JSON) {
        for params in allParametersWithUI {
            let subjson = json.dictionaryValue[params.name]
            if subjson != nil {
                params.updateFromJSONDictionary(subjson!.dictionaryValue)
            }
        }
    }
    func toJSON() -> JSON {
        var dict: [String: JSON] = [:]
        let base = FunChipSimulationParameters()
        for (params, defs) in zip(allParametersWithUI, base.allParametersWithUI) {
            let paramsJSON = params.toJSON()
            let defsJSON = defs.toJSON()
            var nonTrivial: [String: JSON] = [:]
            for (k, j) in paramsJSON.dictionaryValue {
                let jd = defsJSON.dictionaryValue[k]
                if j != jd {
                    nonTrivial[k] = j
                }
            }
            if !nonTrivial.isEmpty {
                dict[params.name] = JSON.dictionary(nonTrivial)
            }
        }
        return JSON.dictionary(dict)
    }
    func fixupAfterReadingFromUI() {
        // all the special cases...

    }
}

class FunSimWindow: NSWindow {
    var shiftDepressed = false
    var noteShiftKeyChanged: VoidBlock!
    override func sendEvent(_ theEvent: NSEvent) {
        let shift = theEvent.modifierFlags.contains(NSEventModifierFlags.shift) // shift key
        if shift != shiftDepressed {
            shiftDepressed = shift
            noteShiftKeyChanged?()
        }
        super.sendEvent(theEvent)
    }

}
