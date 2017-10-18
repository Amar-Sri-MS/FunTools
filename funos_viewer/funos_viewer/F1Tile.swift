//
//  Tile.swift
//
//  Created by Bertrand Serlet on 1/10/16.
//  Copyright © 2016 Fungible Inc. All rights reserved.
//

// Data structure to hold (row, col) and to compute directions and movements

enum DNRouting: Int, CustomStringConvertible, EnumUIChoice {
    case xy
    case yx
    case northLast
    case deadlocky
    var description: String {
        return "\(self)"
    }
    static func allChoices() -> [String] {
        return ["xy", "yx", "northLast", "deadlocky"]
    }
    static func fromInt(_ index: Int) -> DNRouting {
        return DNRouting(rawValue: index)!
    }
}

struct Tile: Hashable {
    // Note that we allow row or col to be -1 or 4
    let row: Int
    let col: Int

    /*=============== CREATION ===============*/

    init(row r: Int, col c: Int) {
        assert(r >= -1 && r <= F1.numClusterRows)
        assert(c >= -1 && c <= F1.numClusterCols)
        row = r; col = c
    }
    init(cluster: Int) {
        assert(cluster >= 0 && cluster < F1.numClusters)
        if cluster < 3 {
            self.init(row: 0, col: cluster)
        } else if cluster < 5 {
            self.init(row: 1, col: cluster == 3 ? 0 : 2)
        } else {
            self.init(row: 2, col: cluster - 5)
        }
    }
    static var nameToRowColCache: [String: (row: Int, col: Int)] = [:]
    init(name: UnitName) {
        let r = Tile.nameToRowColCache[name]
        if r != nil {
            self.init(row: r!.row, col: r!.col)
            return
        }
        func numAfterPrefix(_ prefix: String, base: UInt8) -> Int {
            let len = prefix.utf8.count
            let rest = String(name.dropFirst(len))
            let digitChar = UInt8(rest.unichar0().value)
            return Int(digitChar.digitForBaseToInt(base))
        }
        if name.hasPrefix("NU") {
            self.init(row: -1, col: numAfterPrefix("NU", base: 10))
        } else if name.hasPrefix("HU") {
            let num = numAfterPrefix("HU", base: 10)
            assert(num < F1.numHUs)
            let left = num % 2 == 0
            self.init(row: num / 2, col: left ? -1 : F1.numClusterCols)
        } else if name.hasPrefix("Cluster") {
            let num = numAfterPrefix("Cluster", base: 16)
            self.init(cluster: num)
            assert(unitName == name) // temp check
        } else if name.hasPrefix("HBMBox") {
            if name == "HBMBox-1" {
                self.init(row: F1.numClusterRows, col: -1)
            } else {
                let num = numAfterPrefix("HBMBox", base: 10)
                assert(num >= -1 && num <= F1.numClusterCols)
                self.init(row: F1.numClusterRows, col: num)
            }
        } else if name == "CSU" {
            self.init(row: 1, col: 1)
        } else {
            fatalError()
        }
        Tile.nameToRowColCache[name] = (row, col)
    }

    /*=============== ACCESSORS ===============*/

    var rowCol: Int {
        // Only valid for tiles in the grid, i.e. clusters
        assert(isGridTile)
        return row == 0 ? col : row == 1 ? (col == 0 ? 3 : 4) : 5 + col
    }
    var isGridTile: Bool {
        return row >= 0 && row < 3 && col >= 0 && col < 3 && (row != 1 || col != 1)
    }
    var isHBMBox: Bool { return row == F1.numClusterRows }
    var isHU: Bool { return (col == -1 || col == F1.numClusterCols) && row != F1.numClusterRows }
    static func gridRowColAsString(_ rowCol: Int) -> String {
        return rowCol.description
    }
    var gridNumberAsString: String {
        assert(isGridTile)
        return Tile.gridRowColAsString(rowCol)
    }
    var unitName: UnitName {
        if isGridTile {
            return "Cluster" + gridNumberAsString
        }
        if row == -1 { return "NU\(col)" }
        if isHBMBox { return "HBMBox\(col)" }
        if row == 1 && col == 1 { return "CSU" }
        if isHU && (row >= 0 && row < F1.numHUsPerSide) {
            let num = 2 * row + (col == -1 ? 0 : 1)
            return "HU" + "\(num)"
        }
        fatalError()
    }
    var hashValue: Int { return row * 1021 /*prime*/ + col }

    /*=============== MOVING AROUND ===============*/

    func directionTo(_ routing: DNRouting, randomGenerator rg: (Int) -> Int, ultimateDest: Tile) -> CardinalDirection {
        // Return direction where to head, as well as a tweak for HBM, -1=>left; 0=>straight; +1=>right
        assert(self != ultimateDest)
        let debug = foilNeverExecutedWarnings   // row==0 && col==1 && ultimateDest.row==3 && ultimateDest.col==3
        if debug {
            print("directionTo self=\(self) to=\(ultimateDest)")
        }
        let rowd = ultimateDest.row - row
        let cold = ultimateDest.col - col
        // We dont expect NUs to talk to clusters via the other NUs, so we always go South as the first step
        if row == -1 { return .south } // first go South to avoid other NUs
        if isHBMBox {
            if col == -1 { return .east } // no choice
            if col == F1.numClusterCols { return .west } // no choice
            // else we let the general algorithm work
        }
        // We can go on the left and right edges
        if isHU {
            return col == -1 ? .east : .west // avoid edge
        }
        if ultimateDest.isHU {
            if rowd == 0 {
                return cold > 0 ? .east : .west
            }
            let neighbor = Tile(row: ultimateDest.row, col: ultimateDest.col == -1 ? 0 : F1.numClusterCols - 1)
            return directionTo(routing, randomGenerator: rg, ultimateDest: neighbor)
        }
        if ultimateDest.isHBMBox {
            if rowd == 0 {
                assert(row == F1.numClusterRows)
                return cold > 0 ? .east : .west
            }
            if cold == 0 {
                assert(rowd > 0)
                return .south
            }
            let uc = ultimateDest.col
            let (nr, nc) = uc == -1 ? (F1.numClusterRows, 0) : uc == F1.numClusterCols ? (F1.numClusterRows, F1.numClusterCols - 1) : (F1.numClusterRows - 1, uc)
            let neighbor = Tile(row: nr, col: nc)
            return directionTo(routing, randomGenerator: rg, ultimateDest: neighbor)
        }
        if routing == .xy || routing == .yx {
            if abs(rowd) < abs(cold) {
                // we first travel horizontally
                return cold > 0 ? .east : .west
            } else if abs(cold) < abs(rowd) {
                return rowd > 0 ? .south : .north
            } else {
                // Same distance
                if routing == .xy {
                    // We could be sophisticated and avoid the center, but for now, we favor North South
                    return rowd > 0 ? .south : .north
                } else {
                    return cold > 0 ? .east : .west
                }
            }
        } else if routing == .northLast {
            if rowd == 0 { return cold > 0 ? .east : .west }
            if cold == 0 { return rowd > 0 ? .south : .north }
            // We have a choice
            let choice1: CardinalDirection = cold > 0 ? .east : .west
            let choice2: CardinalDirection = rowd > 0 ? .south : .north
            // but if one of the choices is .North, then we pick the other
            if choice2 == .north { return choice1 }
            let r = rg(2)
            return r == 0 ? choice1 : choice2
        } else if routing == .deadlocky {
            if rowd == 0 { return cold > 0 ? .east : .west }
            if cold == 0 { return rowd > 0 ? .south : .north }
            // We have a choice
            let choice1: CardinalDirection = cold > 0 ? .east : .west
            let choice2: CardinalDirection = rowd > 0 ? .south : .north
            let r = rg(2)
            return r == 0 ? choice1 : choice2
        } else {
            fatalError()
        }
    }
    func directionTo(_ routing: DNRouting, randomGenerator rg: (Int) -> Int, ultimateDest: UnitName) -> CardinalDirection {
        let rowCol = Tile(name: ultimateDest)
        return directionTo(routing, randomGenerator: rg, ultimateDest: rowCol)
    }
    func next(_ direction: CardinalDirection) -> Tile! {
        var r = row; var c = col
        switch direction {
            case .north:
                if row == -1 { return nil }
                if isHU { return nil }
                if isHBMBox && (col == -1 || col == F1.numClusterCols) { return nil }
                r += -1
            case .east:
                if row == -1 { return nil }
                if col >= F1.numClusterCols { return nil }
                c += 1
            case .west:
                if row == -1 { return nil }
                if col <= -1 { return nil }
                c += -1
            case .south:
                if isHBMBox || isHU { return nil }
                r += 1
            }
        return Tile(row: r, col: c)
    }
    func next(_ routing: DNRouting, randomGenerator rg: (Int) -> Int, ultimateDest: Tile) -> Tile! {
        let dir = directionTo(routing, randomGenerator: rg, ultimateDest: ultimateDest)
        return next(dir)
    }
    func next(_ routing: DNRouting, randomGenerator rg: (Int) -> Int, ultimateDest: UnitName) -> UnitName! {
        return next(routing, randomGenerator: rg, ultimateDest: Tile(name: ultimateDest))?.unitName
    }
    static func numHops(_ routing: DNRouting, randomGenerator rg: (Int) -> Int, from: UnitName, _ to: UnitName) -> Int {
        let debug = foilNeverExecutedWarnings   // from == "Cluster1" && to.hasPrefix("HU3")
        if debug {
            print("HERE numHops from=\(from) to=\(to)")
        }
        let fromTile = Tile(name: from)
        let toTile = Tile(name: to)
        return numHops(routing, randomGenerator: rg, from: fromTile, toTile, debug: debug)
    }
    private static func numHops(_ routing: DNRouting, randomGenerator rg: (Int) -> Int, from: Tile, _ to: Tile, debug: Bool) -> Int {
        if from == to { return 0 }
        let dir = from.directionTo(routing, randomGenerator: rg, ultimateDest: to)
        if debug {
            print("NumHops: from=\(from) to=\(to) dir=\(dir)")
        }
        let nextTile = from.next(dir)!
        return 1 + numHops(routing, randomGenerator: rg, from: nextTile, to, debug: debug)
    }

    /*=============== ENUMERATION ===============*/

    static func allClusters() -> [Tile] {
        var array = [Tile]()
        for row in 0 ..< F1.numClusterRows {
            for col in 0 ..< F1.numClusterCols {
                if row == 1 && col == 1 { continue }
                array |= Tile(row: row, col: col)
            }
        }
        return array
    }
    static func allHBMBoxes() -> [Tile] {
        return (-1 ... F1.numClusterCols).map { Tile(name: "HBMBox\($0)") }
    }
    static func allNUs() -> [Tile] {
        let all = 0 ..< F1.numNUs
        return all.map { Tile(name: "NU\($0)") }
    }
    static func allHUs() -> [Tile] {
        let all = 0 ..< F1.numHUs
        return all.map { Tile(name: "HU\($0)") }
    }
    static func allUnits() -> [Tile] {
        var all: [Tile] = [Tile(name: "CSU")]
        all += allClusters()
        all += allNUs()
        all += allHBMBoxes()
        all += allHUs()
        return all
    }
    static func allClusterNames() -> [UnitName] {
        return allClusters().map { $0.unitName }
    }
    static func allUnitNames() -> [UnitName] {
        return allUnits().map { $0.unitName }
    }
    var NUNumberForCluster: Int {
        assert(F1.numNUs == 3)
        return col
    }

    /*=============== MISC ===============*/

    static func ==(lhs: Tile, rhs: Tile) -> Bool {
        return (lhs.row == rhs.row) && (lhs.col == rhs.col)
    }
}


