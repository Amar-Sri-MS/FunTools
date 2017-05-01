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


