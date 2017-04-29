//
//  SimulationParameters.swift
//
//  Created by Bertrand Serlet on 2/21/16.
//  Copyright © 2016 Fungible Inc. All rights reserved.
//

// Simulation Parameters capture a bunch of parameters to use for the simulation setup
// We store the values as JSON so that we can differentiate between, say, an Int and a Double
// And also for easy saving into a JSON file.

typealias SimulationParameterKey = String
typealias SimulationCategory = Int

protocol SimulationParameters: class, CustomStringConvertible {
    var name: String { get }
    var all: [SimulationParameterKey: JSON] { get set } // all the keys with their default

    var keysForFlowsUI: [SimulationParameterKey] { get } // keys shown in the UI
    var keysForConfigUI: [SimulationParameterKey] { get } // keys shown in the UI

    var keysToUILabels: [SimulationParameterKey: String] { get } // mapping for keys shown in the UI
    var toolTips: [SimulationParameterKey: String] { get } // toolTip shown in the UI
    var enumChoices: [SimulationParameterKey: [String]]! { get } // to indicate which keys are popup (nil if none)
}

let SimulationParametersTabs = 0 ... 1

extension SimulationParameters {
    subscript(key: SimulationParameterKey) -> Double { return all[key]!.doubleValue }
    subscript(key: SimulationParameterKey) -> Bool { return all[key]!.boolValue }
    subscript(key: SimulationParameterKey) -> String { return all[key]!.stringValue }
    subscript(key: SimulationParameterKey) -> Int { return all[key]!.integerValue }
    subscript(key: SimulationParameterKey) -> ClockCycle { return ClockCycle(all[key]!.integerValue) }
    subscript(key: SimulationParameterKey) -> UInt8 { return UInt8(all[key]!.integerValue) }
    subscript(key: SimulationParameterKey) -> UInt16 { return UInt16(all[key]!.integerValue) }
    func keysForTab(_ tabID: Int) -> [String] {
        return tabID == 0 ? keysForFlowsUI : keysForConfigUI
    }
    var allUILabels: [SimulationParameterKey] {
        return keysForFlowsUI + keysForConfigUI
    }
    func keyCategory(_ key: SimulationParameterKey) -> SimulationCategory {
        if keysForFlowsUI.index(of: key) != nil { return 0 }
        if keysForConfigUI.index(of: key) != nil { return 1 }
        fatalError()
    }
    func updateFromControl(_ key: SimulationParameterKey, control: SimulationParameterControl) -> Bool {
        // returns whether it differs
        let previous: JSON = all[key]!
        var json: JSON = JSON.null
        switch previous {
            case .null:
                break
            case .real:
                json = JSON.real(control.doubleValue)
            case .integer:
                json = JSON.integer(control.integerValue)
            case .bool:
                json = JSON.bool(control.boolValue)
            case .string:
                json = JSON.string(control.titleOfSelectedItem)
            default: fatalError()
        }
        all[key] = json
        return json != previous
    }
    func updateFromControls(_ table: [SimulationParameterKey: SimulationParameterControl], _ noteDiffersFromDefault: (SimulationParameterKey, SimulationParameterControl, Bool /*differs*/) -> Void) {
        for key in allUILabels {
            let control = table[key]!
            let differs = updateFromControl(key, control: control)
            noteDiffersFromDefault(key, control, differs)
        }
    }
    func updateFromJSONDictionary(_ table: [SimulationParameterKey: JSON]) {
        for (key, new) in table {
            if (all[key] == nil) {
                print("No such key '\(key)' in parameters.")
                assert(all[key] != nil)
            }
            let previous: JSON = all[key]!
            var json: JSON = JSON.null
            // Note that we maintain the type of previous rather than just copy new
            switch previous {
                case .null:
                    break // continues to be null
                case .real:
                    json = JSON.real(new.doubleValue)
                case .integer:
                    json = JSON.integer(new.integerValue)
                case .bool:
                    json = JSON.bool(new.boolValue)
                case .string:
                    json = JSON.string(new.stringValue)
                default: fatalError()
            }
            if json != JSON.null { all[key] = json }
        }
    }
    func toJSON() -> JSON {
        return JSON.dictionary(all)
    }
}

protocol SimulationParameterControl {
    var stringValue: String { get }
    var titleOfSelectedItem: String { get } // only used for enums
    var integerValue: Int { get }
    var doubleValue: Double { get }
    var boolValue: Bool { get }
    func setValueFromJSON(_ json: JSON)
}

extension JSON {
    var titleOfSelectedItem: String { fatalError() } // only used for enums
    func setValueFromJSON(_: JSON) { fatalError() }
}

extension JSON: SimulationParameterControl {
}
