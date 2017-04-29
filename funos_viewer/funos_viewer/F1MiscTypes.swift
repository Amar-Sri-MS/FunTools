//
//  MiscTypes.swift
//
//  Created by Bertrand Serlet on 1/30/16.
//  Copyright © 2016 Fungible Inc. All rights reserved.
//

let logBlockSize: UInt8 = 6   // 64B
let blockSize: UInt64 = UInt64(1) << logBlockSize // use for displacements
let blockNumBytes: Int = 1 << logBlockSize      // use for byte counts

// Geometric and logical parameters
struct F1Geometry {
    let numClusters = 8    // We use var rather than let for now, to avoid warnings
    let numNUs = 3
    let numHUsPerSide = 3
    let numHUs = 6
    let numHBMs = 8
    let numClusterRows = 3
    let numClusterCols = 3
    let numDirectories = 4  // in CSU
}
let F1: F1Geometry = F1Geometry()

let F1GroupsOfUnits: [UnitName: Int] = [
    "NU": F1.numNUs,
    "NUA$": F1.numNUs,
    "NUWritesQ": F1.numNUs,
    "NUOutgoingWUQ": F1.numNUs,
    "Cluster": F1.numClusters,
    "BAM": F1.numClusters,
    "L2$": F1.numClusters,
    "HBM": F1.numHBMs,
    "HU": F1.numHUs,
]

typealias Bytes = [UInt8]   // For arbitrary arrays, not necessarily multiple of cache lines
typealias BlockData = [UInt8]    // 64B
let blockDataAllZeros: BlockData = BlockData(repeating: 0, count: blockNumBytes)

extension Collection where Self.Index == Int, Self.IndexDistance == Int, Self.Iterator.Element == UInt64 {
    var asBytes: Bytes {
        var bytes: Bytes = []
        for word in self {
            var w = word
            for _ in 0 ..< 8 {
                bytes |= UInt8(w & 0xff)
                w >>= 8
            }
        }
        return bytes
    }
}

/*=============== CORES ===============*/

struct CoreNumber: Hashable, CustomStringConvertible {
    let bits: Int   // really: 4+3 bits
    init(rowCol: Int, coreNum: UInt3) {
        assert(rowCol >= 0 && rowCol < F1.numClusters)
        assert(coreNum < 8)
        bits = rowCol << 3 | Int(coreNum)
    }
    var rowCol: Int { return bits >> 3 }
    var coreNum: UInt3 { return UInt3(bits & 7) }
    var hashValue: Int { return bits }
    var description: String {
        return Tile.gridRowColAsString(rowCol) + "." + coreNum.description
    }
    var unitName: UnitName { return "Core" + description }
    static func ==(lhs: CoreNumber, rhs: CoreNumber) -> Bool {
        return lhs.bits == rhs.bits
    }
}

/*=============== VPS ===============*/

struct VPNumber: Hashable, CustomStringConvertible {
    let bits: Int   // really: 4+3+2 bits but to allow some room we use 4+3+4
    init(rawBits: Int) {
        assert(rawBits >= 0 && rawBits < 2048)
        bits = rawBits
    }
    init(rowCol: Int, coreNum: UInt3, VPNum: UInt4) {
        assert(rowCol >= 0 && rowCol < F1.numClusters)
        assert(coreNum < 8)
        assert(VPNum < 16)
        bits = rowCol << 7 | Int(coreNum) << 4 | Int(VPNum)
    }
    init(rowCol: Int, coreNum: Int, VPNum: Int) {
        assert(rowCol >= 0 && rowCol < F1.numClusters)
        assert(coreNum >= 0 && coreNum < 8)
        assert(VPNum >= 0 && VPNum < 16)
        bits = rowCol << 7 | Int(coreNum) << 4 | Int(VPNum)
    }
    init(vp00AtRowCol rowCol: Int) {
        assert(rowCol >= 0 && rowCol < F1.numClusters)
        bits = rowCol << 7
    }
    init(vp10AtRowCol rowCol: Int) {
        assert(rowCol >= 0 && rowCol < F1.numClusters)
        bits = rowCol << 7 | 1 << 4
    }
    var rowCol: Int { return bits >> 7 }
    var coreNum: UInt3 { return UInt3((bits >> 4) & 7) }
    var VPNum: UInt4 { return UInt4(bits & 15) }
    var coreNumber: CoreNumber { return CoreNumber(rowCol: rowCol, coreNum: coreNum) }
    var hashValue: Int { return bits }
    var description: String { return Tile.gridRowColAsString(rowCol) + "." + coreNum.description + "." + VPNum.description
    }
    var unitName: UnitName { return "VP" + description }
    var isSpecialVP: Bool { return (coreNum == 0 || coreNum == 1) && VPNum == 0 }
    var isDoorbellVP: Bool { return coreNum == 1 && VPNum == 0 }
    static func ==(lhs: VPNumber, rhs: VPNumber) -> Bool {
        return lhs.bits == rhs.bits
    }
}

