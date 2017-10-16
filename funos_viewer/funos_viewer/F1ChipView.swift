//
//  NSChipView.swift
//
//  Created by Bertrand Serlet on 12/7/15.
//  Copyright © 2016 Fungible Inc. All rights reserved.
//

import AppKit

/*=============== NS CHIP EXTRAS ===============*/

// SN wires should be at least 5 pixels wide.
let MINIMUM_SN_WIDTH : CGFloat = 5.0
//  7/1000 of screen width, on average.
let SCALED_SN_WIDTH : Double = 0.007


extension CALayer {
    func makeBoxAndAdd2Text(_ unitName: UnitName) {
        let text = CATextLayer()
        let text2 = CATextLayer()
        name = unitName
        backgroundColor = .white
        borderWidth = 1.0
        borderColor = .black
        text.contentsScale = contentsScale
        text.string = unitName
        text.fontSize = 12.0
        text.font = NSFont.boldSystemFont(ofSize: text.fontSize)
        text.foregroundColor = .blue
        text.alignmentMode = "left"
        addSublayer(text)
        text2.contentsScale = contentsScale
        text2.string = ""
        text2.fontSize = 12.0
        text2.font = NSFont.userFixedPitchFont(ofSize: text2.fontSize) // use fixed pitch so that the display is more stable
        text2.foregroundColor = .black
        text2.alignmentMode = "left"
        text2.isWrapped = true
        addSublayer(text2)
    }
    func updateBoxDimensions(_ gray: Bool = false) {
        let text = sublayers![0] as! CATextLayer
        let text2 = sublayers![1] as! CATextLayer
        text.frame = CGRect(x: 3, y: bounds.height - 17, width: min(150.0, bounds.width - 6), height: 16)
        text2.frame = CGRect(x: 3, y: 3, width: bounds.width - 6, height: bounds.height - 18)
        backgroundColor = gray ? .veryLightGray : .white
    }
    func makeOrUpdateBoxWith2Texts(_ update: Bool, unitName: UnitName, gray: Bool = false) {
        if !update {
            makeBoxAndAdd2Text(unitName)
        }
        updateBoxDimensions(gray)
    }
    func makeOrUpdateQueueStyleBox(_ update: Bool, dir: CardinalDirection, incoming: Bool, isDN: Bool) {
        // Dir points to the exit of the box
        // incoming determines the arrow direction
        let props = [1, 1, 1, 2]
        let bigIndex: Int
        switch dir {
            case .north: addAbutYSublayers(update, proportions: props); bigIndex = 3
            case .south: addAbutYSublayers(update, proportions: props.reversed()); bigIndex = 0
            case .east: addAbutXSublayers(update, proportions: props); bigIndex = 3
            case .west: addAbutXSublayers(update, proportions: props.reversed()); bigIndex = 0
        }
        let big = sublayers![bigIndex]
        let shape = update ? big.sublayers![0] as! CAShapeLayer : CAShapeLayer()
        let side = dir == .east || dir == .west
        let flip = (dir == .west || dir == .south) != incoming
        let path = CGPath.isosceleTriangle(big.bounds.size, sideWays: side, flip: flip)
        shape.path = path
        shape.frame = big.frame
        if !update {
            big.addSublayer(shape)
            for l in sublayers! {
                l.borderColor = .gray
                l.borderWidth = 0.5
            }
            shape.fillColor = isDN ? CGColor.green.lighter : CGColor.blue.lighter
            shape.strokeColor = isDN ? CGColor.green.darker : CGColor.blue.darker
            backgroundColor = .white
            borderWidth = 0.75
            borderColor = .black
        }
    }
    func addCenterBox(_ layers: ChipLayers, update: Bool, unitName: UnitName, gray: Bool = false) {
        let sub = update ? sublayers![0] : CALayer()
        sub.frame = CGRect(x: bounds.minX + round((bounds.width - bounds.width) / 2.0), y: bounds.minY + round((bounds.height - bounds.height) / 2.0), width: bounds.width, height: bounds.height)
        if !update {
            sub.contentsScale = contentsScale
            addSublayer(sub)
        }
        sub.makeOrUpdateBoxWith2Texts(update, unitName: unitName, gray: gray)
        if !update && !unitName.isEmpty { layers.units[unitName] = sub }
    }
    func addCluster(_ layers: ChipLayers, update: Bool, numCores: Int, clusterNum: Int) {
        let thin: CGFloat = 0.25
        borderWidth = 2.0
        addAbutXSublayers(update, proportions: 60, 20) // 40 for the L2$ and BAM
        let tile = Tile(cluster: clusterNum)
        let u = tile.unitName
        let clusterAndCores = sublayers![0]
        clusterAndCores.addAbutYSublayers(update, proportions: 6, 2, 5, 6)
        let coresRow0 = clusterAndCores.sublayers![0]
        let blockCopy = clusterAndCores.sublayers![1]
        let cluster = clusterAndCores.sublayers![2]
        let coresRow1 = clusterAndCores.sublayers![3]
        cluster.borderWidth = thin
        cluster.makeOrUpdateBoxWith2Texts(update, unitName: u)
        if !update { layers.units[u] = cluster }
        let blockCopyName = "BlockCopy\(clusterNum)"
        blockCopy.borderWidth = thin
        blockCopy.makeOrUpdateBoxWith2Texts(update, unitName: blockCopyName)
        if !update {
            let text = blockCopy.sublayers![0] as! CATextLayer
            text.fontSize = 8.0
            layers.units[blockCopyName] = blockCopy
        }
        var cnum: Int = 0
        for row in [coresRow0, coresRow1] {
            row.addSplitXSublayers(update, numSplit: (numCores + 1) / 2)
            for i in 0 ..< ((numCores + 1) / 2) {
                let coreNum = CoreNumber(rowCol: clusterNum, coreNum: UInt4(cnum))
                let coreName = "Core" + coreNum.description
                cnum += 1
                let coreAndVPs = row.sublayers![i]
                coreAndVPs.backgroundColor = .white
                coreAndVPs.addAbutYSublayers(update, proportions: 1, 1, 1, 1, 2)
                let core = coreAndVPs.sublayers![4]
                core.makeOrUpdateBoxWith2Texts(update, unitName: coreName)
                coreAndVPs.borderWidth = 0.75
                if !update { 
                    layers.units[coreName] = core
                    for i in 0 ..< 4 {
                        let vpName = "VP\(coreNum.description).\(i)"
                        let vp = coreAndVPs.sublayers![i]
                        if !update {
                            let text = CATextLayer()
                            vp.name = vpName
                            vp.backgroundColor = .white
                            vp.borderWidth = 0.0
                            text.contentsScale = vp.contentsScale
                            text.string = vpName
                            text.fontSize = 3.0
                            text.font = NSFont.boldSystemFont(ofSize: text.fontSize)
                            text.foregroundColor = .gray
                            text.alignmentMode = "left"
                            vp.addSublayer(text)
                        }
                        let text = vp.sublayers![0] as! CATextLayer
                        text.frame = CGRect(x: 3, y: vp.bounds.height - 16, width: min(150.0, vp.bounds.width+4), height: 16)
                        backgroundColor = .white
                        layers.units[vpName] = vp
                        vp.borderWidth = thin
                    }
                    let text = core.sublayers![0] as! CATextLayer
                    text.truncationMode = "start"
                    text.fontSize = 8.0
                    core.borderWidth = thin
                }
            }
        }
        let a = "BAM" + Tile.gridRowColAsString(clusterNum)
        let BMAndL2 = sublayers![1]
        BMAndL2.borderWidth = thin
        BMAndL2.addAbutYSublayers(update, proportions: 1, 1)
        let alloc = BMAndL2.sublayers![0]
        alloc.borderWidth = thin
        alloc.makeOrUpdateBoxWith2Texts(update, unitName: a, gray: false)
        if !update { layers.units[a] = alloc }
        let l2 = "L2$" + Tile.gridRowColAsString(clusterNum)
        let l2layer = BMAndL2.sublayers![1]
        l2layer.borderWidth = thin
        l2layer.makeOrUpdateBoxWith2Texts(update, unitName: l2, gray: false)
        if !update { layers.units[l2] = l2layer }
    }
    func addCSU(_ layers: ChipLayers, update: Bool) {
        backgroundColor = .white
        borderWidth = 2.0
        borderColor = .black
        addAbutYSublayers(update, proportions: 2, 30, 10)
        let csu = sublayers![2]
        let directoriesAndSpace = sublayers![1]
        directoriesAndSpace.addAbutXSublayers(update, proportions: 1, 30, 1)
        let directories = directoriesAndSpace.sublayers![1]
        assert(F1.numDirectories % 2 == 0) // only know how to handle even numbers
        directories.addAbutYSublayers(update, proportions: 1, 1)
        var i = 0
        for dirRow in directories.sublayers!.reversed() {
            dirRow.addAbutXSublayers(update, proportions: [Int](repeating: 1, count: F1.numDirectories / 2))
            for d in dirRow.sublayers! {
                d.makeOrUpdateBoxWith2Texts(update, unitName: "Dir\(i)")
                d.borderWidth = 0.5
                layers.units["Dir\(i)"] = d
                let text = d.sublayers![0] as! CATextLayer
                text.fontSize = 8.0
                i += 1
            }
        }
        csu.makeOrUpdateBoxWith2Texts(update, unitName: "CSU")
        if !update {
            layers.units["CSU"] = csu
        }
    }
    func addCenterGrid(_ layers: ChipLayers, update: Bool, numCores: Int) {
        addAbutYSublayers(update, proportions: 10, 3, 10, 3, 10)
        var cc = 0
        for i in [4, 2, 0] {
            let tranche = sublayers![i]
            tranche.addAbutXSublayers(update, proportions: 10, 3, 10, 3, 10)
            for j in [0, 2, 4] {
                let cluster = tranche.sublayers![j]
                if i == 2 && j == 2 {
                    layers.units["CSU"] = cluster
                    cluster.addCSU(layers, update: update)
                } else {
                    layers.units["PC\(cc)"] = cluster
                    cluster.addCluster(layers, update: update, numCores: numCores, clusterNum: cc)
                    cc += 1
                }
            }
        }
        // Order of adding to sublayers is important, SN and DN must be last in that order
        if !update {
            makeSNFabric(layers)
            makeCNFabric(layers)
        }
        drawSNFabric(layers, selected: false)
        drawCNFabric(layers, selected: false)
        let fabric = addDNFabric(layers, update: update, selected: false)
        if !update { layers.units["DN"] = fabric }
    }
    
    @discardableResult func addDNFabric(_ layers: ChipLayers, update: Bool, selected: Bool) -> CALayer {
        let fabric = update ? layers.units["DN"]! : CALayer()
        if selected { assert(update) }
        var z: CGFloat = -100.0
        var i = 0
        let width = Double(bounds.width)
        let height = Double(bounds.height)
        if !update {
            fabric.name = "DN"
            fabric.contentsScale = contentsScale
            addSublayer(fabric)
        } else {
            if selected { z = -z } // make it pop when selected
        }
        for (num, boxX) in [(-1, -0.03), (0, 0.13), (1, 0.46), (2, 0.795), (3, 0.96)] {
            let sub = update ? fabric.sublayers![i] : CALayer()
            i += 1
            sub.frame = CGRect(x: boxX * width, y: -0.07 * height, width: 0.06 * width, height: 0.06 * height)
            sub.borderWidth = 0.5
            sub.borderColor = .black
            sub.backgroundColor = .white
            if !update {
                fabric.addSublayer(sub)
                layers.units["HBMBox\(num)"] = sub
            }
        }
        fabric.zPosition = z
        let WW = 0.025          // width of a bus
        func makeOrUpdateWire(_ horiz: Bool, relX: Double, relY: Double, relLen: Double, name: UnitName) {
            // All Doubles express a proportion
            let width = bounds.width
            let height = bounds.height
            let start = CGPoint(x: CGFloat(relX) * width, y: CGFloat(relY) * height)
            let length = CGFloat(relLen) * (horiz ? width : height)
            let thickness = CGFloat(height) * CGFloat(WW)
            let sub: BusWiring = update ? fabric.sublayers![i] as! BusWiring : BusWiring()
            i += 1
            sub.setDimensions123Segments(horiz, start: start, length: length, thickness: thickness)
            sub.fillColor = selected ? CGColor.green.darker : .green
            sub.strokeColor = sub.fillColor!.blendWithBlack(0.25)
            if !update {
                sub.unitName = name
                layers.DNSegments[name] = sub
                // Prevent animations when displaying heat
                sub.preventAnimations()
                fabric.addSublayer(sub)
            }
            sub.zPosition = z
        }
        let ROW_WIDTH = 0.333   // in proportion
        let BAND1 = 0.144
        let BAND2 = 0.176
        // First the horizontal wires
        for row in 0 ... F1.numClusterRows {
            let isHBMBoxRow = row == 0
            let xp = isHBMBoxRow ? 0.0 : -0.02
            let rheight = ROW_WIDTH
            let roffset = rheight * (isHBMBoxRow ? -0.64 : Double(row - 1))
            let buses = [(CardinalDirection.east, BAND1 + roffset), (CardinalDirection.west, BAND2 + roffset)]
            for (dir, yp) in buses {
                var xp2 = xp
                let PERP = 0.015
                let tn: (Int) -> String = { Tile(row: F1.numClusterRows - row, col: $0).unitName }
                let segments: [(Int, Double)] = isHBMBoxRow
                    ? [(-1, 0.160), (0, 0.333), (1, 0.332), (2, 0.153 + 0.014)]
                    : [(-1, 0.173), (0, 0.320), (1, 0.320), (2, 0.173 + 0.014)]
                for (source, len) in segments {
                    let relLen = (1.0 - xp * 2) * len
                    let sourceName = dir == .east ? tn(source) : tn(source+1)
                    let name = "DNLink\(sourceName)To\(dir)"
                    makeOrUpdateWire(true, relX: xp2, relY: yp - WW / 2.0 + PERP, relLen: relLen, name: name)
                    xp2 += relLen
                }
            }
        }
        // Then the vertical ones
        for col in [0, 1, 2] {
            let yp = -0.09
            let rwidth = ROW_WIDTH
            let roffset = rwidth * Double(col)
            let buses = [(CardinalDirection.north, BAND1 + roffset), (CardinalDirection.south, BAND2 + roffset)]
            for (dir, xp) in buses {
                var yrel = yp
                let tn: (Int) -> String = { Tile(row: $0, col: col).unitName }
                for (source, len) in [(4, 0.045), (3, 0.179), (2, 0.283), (1, 0.283), (0, 0.173)] {
                    let segH = (1.0 - yp * 2) * len
                    var sourceName: UnitName
                    if dir != CardinalDirection.north {
                        sourceName = tn(source-1)
                    } else if source == 4 {
                        sourceName = ["HBM1", "HBM3", "HBM6"][col]
                    } else {
                        sourceName = tn(source)
                    }
                    let name = "DNLink\(sourceName)To\(dir)"
                    makeOrUpdateWire(false, relX: xp - WW / 2.0, relY: yrel, relLen: segH, name: name)
                    yrel += segH
                }
            }
        }
        return fabric
    }
    
    // Allocates the Core Animation layers for the SN fabric and
    // for the individual wires.
    func makeSNFabric(_ layers : ChipLayers) {
        let fabric = CALayer()
        fabric.name = "SN"
        fabric.contentsScale = contentsScale
        addSublayer(fabric)
        layers.units["SN"] = fabric
        var z: CGFloat = -10.0
        fabric.zPosition = z

        // Create one BusWiring object per connection.
        func makeWireLayer(name: String) {
            let sub = BusWiring()
            sub.unitName = name
            layers.SNSegments[name] = sub
            // Prevent animations when displaying heat
            sub.preventAnimations()
            fabric.addSublayer(sub)
        }
        
        for hostNumber in 0 ..< 6 {
            makeWireLayer(name: "HU\(hostNumber)")
        }
        for clusterNumber in 0..<8 {
            makeWireLayer(name: "Cluster\(clusterNumber)")
        }
        for nuNumber in 0..<3 {
            makeWireLayer(name: "NU\(nuNumber)")
        }
     }

     // Redraw the layer for the SN.
    func drawSNFabric(_ layers: ChipLayers, selected: Bool) {
        let fabric = layers.units["SN"]
        let width = bounds.size.width
        let height = bounds.size.height
        
        // Redraw one wire in the SN network.
        // horiz indicates that the line starts out horizontal.
        // If segment 2 is non-nil, then it represents a third
        // 90 degree turn, >0 if up/right, <0 if left/down.
        func updateWire(name: UnitName, startX: Double, startY: Double, startHoriz: Bool,
            len1: Double, len2: Double?, len3: Double?) {
             let sub : BusWiring = layers.SNSegments[name]!
            // All Doubles express a proportion
            // If segment2 exist, it's a 90 degree turn, >0 if up (or right)
            let start = CGPoint(x: CGFloat(startX) * width, y: CGFloat(startY) * height)
            let length1 = CGFloat(len1) * (startHoriz ? width : height)
            let thickness = max(MINIMUM_SN_WIDTH, 
                                width * CGFloat(SCALED_SN_WIDTH))

            let length2: CGFloat! = len2 == nil ? nil : CGFloat(len2!) * (startHoriz ? height : width)
            let length3: CGFloat! = len3 == nil ? nil : CGFloat(len3!) * (startHoriz ? width : height)
            sub.setDimensions123Segments(startHoriz, start: start, length: length1, segment2Length: length2, segment3Length: length3, thickness: thickness)
            sub.fillColor = selected ? CGColor.blue.darker : CGColor.blue.lighter
            sub.strokeColor = sub.fillColor!.blendWithBlack(0.25)
        }
        // First the pipes to the HUs.
        // Note that directions for lengths go the wrong way - negative is up/right (positive in Cocoa coordinate
        // system) and positive is left/down.
        // Spacing wires 0.02 apart seems to work for both small and large layouts.
        updateWire(name: "HU0",
                   startX: -0.012, startY: 0.61, startHoriz: true,
                   len1: 0.40, len2: -0.070, len3: nil)
        updateWire(name: "HU1",
                   startX: 1.0, startY: 0.61, startHoriz: true,
                   len1: -0.40, len2: -0.070, len3: nil)
        updateWire(name: "HU2",
                   startX: -0.012, startY: 0.6, startHoriz: true,
                   len1: 0.38, len2: -0.050, len3: nil)
        updateWire(name: "HU3",
                   startX: 1.0, startY: 0.6, startHoriz: true,
                   len1: -0.38, len2: -0.050, len3: nil)
        updateWire(name: "HU4",
                   startX: -0.012, startY: 0.308, startHoriz: true,
                   len1: 0.395, len2: 0.050, len3: nil)
        updateWire(name: "HU5",
                   startX: 1.012, startY: 0.308, startHoriz: true,
                   len1: -0.395, len2: 0.050, len3: nil)
        // Clusters.
        updateWire(name: "Cluster0",
                   startX: 0.23, startY: 0.663, startHoriz: false,
                   len1: -0.057, len2: 0.200, len3: -0.088)
        updateWire(name: "Cluster1",
                   startX: 0.53, startY: 0.617, startHoriz: false,
                   len1: 0.1, len2: nil, len3: nil)
        updateWire(name: "Cluster2",
                   startX: 0.57, startY: 0.663, startHoriz: false,
                   len1: -0.048, len2: -0.200, len3: -0.097)
        updateWire(name: "Cluster3",
                   startX: 0.265, startY: 0.4, startHoriz: true,
                   len1: 0.1, len2: nil, len3: nil)
        updateWire(name: "Cluster4",
                   startX: 0.62, startY: 0.4, startHoriz: true,
                   len1: 0.1, len2: nil, len3: nil)
        updateWire(name: "Cluster5",
                   startX: 0.24, startY: 0.256, startHoriz: false,
                   len1: 0.03, len2: 0.200, len3: 0.090)
        updateWire(name: "Cluster6",
                   startX: 0.535, startY: 0.25, startHoriz: false,
                   len1: 0.1, len2: nil, len3: nil)
        updateWire(name: "Cluster7",
                   startX: 0.57, startY: 0.256, startHoriz: false,
                   len1: 0.035, len2: -0.200, len3: 0.110)
        // NU's.
        updateWire(name: "NU0",
                   startX: 0.315, startY: 1.0, startHoriz: false,
                   len1: -0.44, len2: 0.065, len3: nil)
        updateWire(name: "NU1",
                   startX: 0.345, startY: 1.0, startHoriz: false,
                   len1: -0.4, len2: 0.045, len3: nil)
        updateWire(name: "NU2",
                   startX: 0.625, startY: 1.0, startHoriz: false,
                   len1: -0.4, len2: -0.050, len3: nil)
    }
    
    // Allocates the Core Animation layers for the CN fabric and
    // for the individual wires.
    func makeCNFabric(_ layers : ChipLayers) {
        let fabric = CALayer()
        fabric.name = "CN"
        fabric.contentsScale = contentsScale
        addSublayer(fabric)
        layers.units["CN"] = fabric
        var z: CGFloat = -10.0
        fabric.zPosition = z
        
        // Create one BusWiring object per connection.
        func makeWireLayer(name: String) {
            let sub = BusWiring()
            sub.unitName = name
            layers.CNSegments[name] = sub
            // Prevent animations when displaying heat
            sub.preventAnimations()
            fabric.addSublayer(sub)
        }
        
        for clusterNumber in 0..<8 {
            makeWireLayer(name: "Cluster\(clusterNumber)")
        }
    }
    
    // Redraw the layer for the Coherency Network.
    func drawCNFabric(_ layers: ChipLayers, selected: Bool) {
        let fabric = layers.units["CN"]
        let width = bounds.size.width
        let height = bounds.size.height
        
        // Redraw one wire in the CN network.
        // horiz indicates that the line starts out horizontal.
        // If segment 2 is non-nil, then it represents a third
        // 90 degree turn, >0 if up/right, <0 if left/down.
        func updateWire(name: UnitName, startX: Double, startY: Double, startHoriz: Bool,
                        len1: Double, len2: Double?, len3: Double?) {
            let sub : BusWiring = layers.CNSegments[name]!
            // All Doubles express a proportion
            // If segment2 exist, it's a 90 degree turn, >0 if up (or right)
            let start = CGPoint(x: CGFloat(startX) * width, y: CGFloat(startY) * height)
            let length1 = CGFloat(len1) * (startHoriz ? width : height)
            let thickness = max(MINIMUM_SN_WIDTH, 
                                width * CGFloat(SCALED_SN_WIDTH))
            
            let length2: CGFloat! = len2 == nil ? nil : CGFloat(len2!) * (startHoriz ? height : width)
            let length3: CGFloat! = len3 == nil ? nil : CGFloat(len3!) * (startHoriz ? width : height)
            sub.setDimensions123Segments(startHoriz, start: start, length: length1, segment2Length: length2, segment3Length: length3, thickness: thickness)
            sub.fillColor = selected ? CGColor.yellow.darker : CGColor.yellow.lighter
            sub.strokeColor = sub.fillColor!.blendWithBlack(0.25)
        }
         // Clusters.
        updateWire(name: "Cluster0",
                   startX: 0.25, startY: 0.663, startHoriz: false,
                   len1: -0.048, len2: 0.200, len3: -0.092)
        updateWire(name: "Cluster1",
                   startX: 0.55, startY: 0.617, startHoriz: false,
                   len1: 0.1, len2: nil, len3: nil)
        updateWire(name: "Cluster2",
                   startX: 0.59, startY: 0.663, startHoriz: false,
                   len1: -0.060, len2: -0.190, len3: -0.095)
        updateWire(name: "Cluster3",
                   startX: 0.265, startY: 0.44, startHoriz: true,
                   len1: 0.1, len2: nil, len3: nil)
        updateWire(name: "Cluster4",
                   startX: 0.62, startY: 0.44, startHoriz: true,
                   len1: 0.1, len2: nil, len3: nil)
        updateWire(name: "Cluster5",
                   startX: 0.22, startY: 0.256, startHoriz: false,
                   len1: 0.070, len2: 0.200, len3: 0.067)
        updateWire(name: "Cluster6",
                   startX: 0.55, startY: 0.25, startHoriz: false,
                   len1: 0.1, len2: nil, len3: nil)
        updateWire(name: "Cluster7",
                   startX: 0.59, startY: 0.256, startHoriz: false,
                   len1: 0.068, len2: -0.190, len3: 0.087)
    }
    
    func addNU(_ layers: ChipLayers, update: Bool, num: Int) {
        let props = [9, 5, 1, 1]
        let reverse = num != 0
        addAbutXSublayers(update, proportions: reverse ? props.reversed() : props)
        func layerAt(_ index: Int) -> CALayer { return sublayers![reverse ? 3 - index : index] }
        let n = "NU\(num)"
        let NU = layerAt(0)
        NU.makeOrUpdateBoxWith2Texts(update, unitName: n)
        let a = "NUA$\(num)"
        let NUAllocCache = layerAt(1)
        NUAllocCache.makeOrUpdateBoxWith2Texts(update, unitName: a)
        layerAt(2).makeOrUpdateQueueStyleBox(update, dir: .south, incoming: false, isDN: true)
        layerAt(3).makeOrUpdateQueueStyleBox(update, dir: .south, incoming: false, isDN: false)
        if !update {
            layers.units[n] = NU
            layers.units[a] = NUAllocCache
            let outDNQ = "NUWritesQ\(num)"
            layerAt(2).name = outDNQ
            layers.units[outDNQ] = layerAt(2)
            let outSNQ = "NUOutgoingWUQ\(num)"
            layerAt(3).name = outSNQ
            layers.units[outSNQ] = layerAt(3)
        }
    }
    func addHU(_ layers: ChipLayers, update: Bool, num: Int) {
        addAbutYSublayers(update, proportions: 1, 5)
        let HU = sublayers![1]
        let n = "HU\(num)"
        HU.makeOrUpdateBoxWith2Texts(update, unitName: n)
        let a = "HUA$\(num)"
        let HUAllocCache = sublayers![0]
        HUAllocCache.makeOrUpdateBoxWith2Texts(update, unitName: a)
        if !update {
            layers.units[n] = HU
            layers.units[a] = HUAllocCache
        }
    }
    func addLeftOrRight(_ layers: ChipLayers, update: Bool, left: Bool) {
        assert(F1.numHUsPerSide == 3)
        addAbutYSublayers(update, proportions: 1, 30, 1, 30, 1, 30, 1)
        for i in 0 ..< F1.numHUsPerSide {
            let HUGroup = sublayers![2 * i + 1]
            HUGroup.addHU(layers, update: update, num: 2 * (F1.numHUsPerSide - i - 1) + (left ? 0 : 1))
        }
        zPosition = +1.0    // no idea why this is needed?!?
    }
    func addNUs(_ layers: ChipLayers, update: Bool) {
        assert(F1.numNUs == 3)
        addAbutXSublayers(update, proportions: 11, 30, 1, 30, 1, 30, 11)
        for i in 0 ..< F1.numNUs {
            let NUGroup = sublayers![2*i + 1]
            NUGroup.addNU(layers, update: update, num: i)
        }
    }
    func addHBMs(_ layers: ChipLayers, update: Bool) {
        assert(F1.numHBMs == 8)
        addAbutXSublayers(update, proportions: 20, 2, 15, 15, 2, 15, 15, 2, 15, 15, 2, 20)
        for i in 0 ..< F1.numHBMs {
            let position = [0, 2, 3, 5, 6, 8, 9, 11][i]
            let HBM = sublayers![position]
            let name = "HBM\(i)"
            HBM.makeOrUpdateBoxWith2Texts(update, unitName: name, gray: false)
            if !update { layers.units[name] = HBM }
        }
        zPosition = +5.0    // no idea why this is needed?!?
    }
    func addChip(_ layers: ChipLayers, update: Bool, numCores: Int) {
        addAbutYSublayers(update, proportions: 1, 1, 20, 1)
        let NUs = sublayers![3]
        let hcore = sublayers![2]
        let HBMs = sublayers![0]
        NUs.addNUs(layers, update: update)
        hcore.addAbutXSublayers(update, proportions: 1, 20, 1)
        let left = hcore.sublayers![0]
        left.addLeftOrRight(layers, update: update, left: true)
        let right = hcore.sublayers![2]
        right.addLeftOrRight(layers, update: update, left: false)
        let coreWithSpace = hcore.sublayers![1]
        coreWithSpace.addAbutXSublayers(update, proportions: 1, 80, 1)
        let core2 = coreWithSpace.sublayers![1]
        core2.addAbutYSublayers(update, proportions: 1, 80, 1)
        let core = core2.sublayers![1]
        core.addCenterGrid(layers, update: update, numCores: numCores)
        HBMs.addHBMs(layers, update: update)
    }
    func addOverallLayer(_ layers: ChipLayers, update: Bool, numCores: Int) {
        addAbutXSublayers(update, proportions: 1, 80, 1)
        let hlayer = sublayers![1]
        hlayer.addAbutYSublayers(update, proportions: 1, 80, 1)
        let chip = hlayer.sublayers![1]
        chip.addChip(layers, update: update, numCores: numCores)
    }
}

/*=============== NS CHIP EXTRAS ===============*/

typealias CALayerChangeFunc = (CALayer) -> Void

// Color bands to show an equalizer-like display
// say the latest is sample X[n]
// If you keep 1:
//      last recorded = X[n-1] => show X[n]-X[n-1]
// If you keep 2:
//      lasts recorded: X[n-2],X[n-1] => show X[n]-X[n-1]+X[n-1]-X[n-2] = X[n] - X[n-2]
// If you keep all:
//      just keep X[n] and show X[n] - 0

//let hotnessBands = [2, 1000] // 1000 and above treated as infinite

class ChipLayers {
    var units: [UnitName: CALayer] = [:]
    var unitHotness: [UnitName: [[Double]]] = [:]
    var unitHotnessLayers: [UnitName: [CALayer]] = [:]
    var DNSegments: [UnitName: BusWiring] = [:]
    var SNSegments: [UnitName: BusWiring] = [:]
    var CNSegments: [UnitName: BusWiring] = [:]
}

class NSChipView: NSView {
    let layers = ChipLayers()
    var selectedUnits: Set<UnitName> = []
    var numCores: Int = 6
    override func resize(withOldSuperviewSize oldSize: NSSize) {
        // Swift.print("In resizeWithOldSuperviewSize oldSize=\(oldSize) frame=\(frame) layer.bounds=\(layer!.bounds)")
        let newSize = superview!.bounds.size
        if oldSize == newSize { return }
        let deltax = newSize.width - oldSize.width
        let deltay = newSize.height - oldSize.height
        frame.size.width += deltax
        frame.size.height += deltay
        layer!.addOverallLayer(layers, update: true, numCores: numCores)
        setSelection(selectedUnits)
        let center = theNotificationCenter
        center.post(name: Notification.Name(rawValue: "Resized"), object: self)
        let (xratio, yratio) = (1.0 / (1.0 - deltax / frame.size.width), 1.0 / (1.0 - deltay / frame.size.height))
        if animationLayer.sublayers != nil {
            animationLayer.sublayers!.forEach { $0.scaleFrameOrigin(xratio, yratio) }
        }
        unitNameToLayerCache.removeAll(keepingCapacity: true)
//        for (_, ls) in layers.unitHotnessLayers {
//            for l in ls {
//                l.removeFromSuperlayer()
//            }
//        }
//        layers.unitHotnessLayers = [:]
        setupTrackingAreas()
    }
    func setupTrackingAreas() {
        while !trackingAreas.isEmpty {
            removeTrackingArea(trackingAreas.first!)
        }
        let options: NSTrackingArea.Options = NSTrackingArea.Options.mouseEnteredAndExited.union(NSTrackingArea.Options.mouseMoved).union(NSTrackingArea.Options.activeAlways)
        let trackingArea = NSTrackingArea(rect: bounds, options: options, owner: self, userInfo: nil)
        addTrackingArea(trackingArea)
    }
    func setupLayer(_ frame: NSRect) {
        wantsLayer = true
        layerContentsRedrawPolicy = .beforeViewResize
        layer!.removeAllSublayers()
        layer!.addOverallLayer(layers, update: false, numCores: numCores)
        layer!.addSublayer(CALayer()) // animation layer
        animationLayer.zPosition = +1000.0
        setupTrackingAreas()
    }
    var animationLayer: CALayer { return layer!.sublayers!.last! }
    func unitNameToLayerForAnimation1(_ unit: F1Block) -> CALayer! {
        let name = unit.name
        let l = layers.units[name]
        if l != nil { return l }
        if name.hasPrefix("DN") {
            return layers.DNSegments[name]
        }
        if name.hasPrefix("SN") {
            if name.hasPrefix("SNSourceLink") {
                return layers.SNSegments[name.substringAfter("SNSourceLink")]
            }
            if name.hasPrefix("SNDestLink") {
                return layers.SNSegments[name.substringAfter("SNDestLink")]
            }
            if name.hasPrefix("SNSourceQ") || name.hasPrefix("SNCrossQ") {
                return layers.units["CSU"]
            }
            return layers.SNSegments[name]
        }
        if name.hasPrefix("CN") {
            if name.hasPrefix("CNSourceLink") {
                return layers.CNSegments[name.substringAfter("CNSourceLink")]
            }
            if name.hasPrefix("CNDestLink") {
                return layers.CNSegments[name.substringAfter("CNDestLink")]
            }
            if name.hasPrefix("CNSourceQ") || name.hasPrefix("CNCrossQ") {
                return layers.units["CSU"]
            }
            return layers.CNSegments[name]
        }
        if name.hasPrefix("VP") {
            return layers.units["Core" + name.substring(2..<5)]
        }
        return nil
    }
    func unitNameToLayerForAnimation(_ unit: F1Block) -> CALayer {
        let name = unit.name
        let r = unitNameToLayerCache[name]
        if r != nil { return r! }
        var l = unitNameToLayerForAnimation1(unit)
        if l == nil {
            l = unitNameToLayerForAnimation1(unit.container!)
        }
        if l == nil {
            fatalError("*** No layer for name=\(name)")
        }
        unitNameToLayerCache[name] = l
        return l!
    }
    var unitNameToLayerCache: [UnitName: CALayer] = [:]
    override init(frame: NSRect) {
        super.init(frame: frame)
        setupLayer(frame)
    }
    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setupLayer(frame)
    }
    func unitNameForPoint(_ point: NSPoint) -> String! {
        var hitLayer = layer!.hitTest(point)
        while true {
            if hitLayer == nil { return nil }
//            Swift.print("Got hitLayer with bounds \(hitLayer!.bounds) name=\(hitLayer!.name)")
            if hitLayer!.name != nil { return hitLayer!.name }
//            Swift.print("To superlayer of hitLayer with bounds \(hitLayer!.bounds)")
            hitLayer = hitLayer!.superlayer
        }
    }
    override func acceptsFirstMouse(for theEvent: NSEvent?) -> Bool { return false }
    func setSelection(_ new: Set<UnitName>) {
        let doSelect: [UnitName: CALayerChangeFunc] = [
            "DN": { $0.superlayer!.addDNFabric(self.layers, update: true, selected: true) },
            "SN": { $0.superlayer!.drawSNFabric(self.layers, selected: true) },
            "CN": { $0.superlayer!.drawCNFabric(self.layers, selected: true) },
            "*":  { $0.backgroundColor = .yellow }
        ]
        let doDeselect: [UnitName: CALayerChangeFunc] = [
            "DN": { $0.superlayer!.addDNFabric(self.layers, update: true, selected: false) },
            "SN": { $0.superlayer!.drawSNFabric(self.layers, selected: false) },
            "CN": { $0.superlayer!.drawCNFabric(self.layers, selected: false) },
            "*":  { $0.backgroundColor = .white }
        ]
        let same = new == selectedUnits
        for u in selectedUnits {
            let layer = layers.units[u]!
            let fun: CALayerChangeFunc! = doDeselect[u] ?? doDeselect["*"]
            fun(layer)
            // Special hack to show the portion of DN under the left and right
            if u == "DN" {
                for i in -1 ... F1.numClusterCols {
                    layers.units["HBMBox\(i)"]!.opacity = 1.0
                }
            }
        }
        for u in new {
            let layer = layers.units[u]!
            let fun: CALayerChangeFunc! = doSelect[u] ?? doSelect["*"]
            fun(layer)
            // Special hack to show the portion of DN under the left and right
            if u == "DN" {
                for i in -1 ... F1.numClusterCols {
                    layers.units["HBMBox\(i)"]!.opacity = 0.5
                }
            }
        }
        selectedUnits = new
        if !same {
            let center = theNotificationCenter
            center.post(name: Notification.Name(rawValue: "SelectionChanged"), object: self)
        }
    }
    func updateUnitSummaries( _ info: (UnitName) -> String!) {
        for (name, layer) in layers.units {
            let str = info(name)
            if str == nil { continue }
            let text2 = layer.sublayers?[1] as? CATextLayer
            if text2 == nil { continue }
            text2!.string = str
        }
    }
    func updateHotCores( _ info: (UnitName) -> Double!) {
        for (name, layer) in layers.units {
//            let thisHotnessBand = name.hasPrefix("Core") ? hotnessBands : [1000]
//            let nbands = thisHotnessBand.count
            let heat = info(name)
            if heat == nil { continue }
//            var hotnessLayers = layers.unitHotnessLayers[name]
//            if hotnessLayers == nil {
//                let size = layer.bounds.size
//                let hband = size.height / CGFloat(nbands)
//                hotnessLayers = []
//                for band in 0 ..< nbands {
//                    let l = CALayer()
//                    l.frame = CGRect(x: 0, y: size.height - CGFloat(band + 1) * hband, width: size.width, height: hband)
//                    l.zPosition = -100
//                    layer.addSublayer(l)
//                    hotnessLayers! |= l
//                }
//                layers.unitHotnessLayers[name] = hotnessLayers
//            }
//            var hotness = layers.unitHotness[name] ?? [[Double]](repeating:[Double](), count: nbands)
//            for band in 0 ..< nbands {
//                // first record the last heat
//                var samples = hotness[band]
//                let maxToKeep = thisHotnessBand[band]
//                if maxToKeep >= 1000 {
//                    samples = [heat!]
//                } else {
//                    samples |= heat!
//                    while samples.count > maxToKeep {
//                        samples.remove(at: 0)
//                    }
//                }
//                hotness[band] = samples
////                let heatToDisplay = maxToKeep >= 1000 ? samples.last! : samples.last! - samples[0]
////                 let heatToDisplay = maxToKeep >= 1000 ? samples.last! : samples.miniMax().maximum
////                let heatToDisplay = maxToKeep >= 1000 ? samples.last! : samples.reduce(0.0) { $0 + $1 } / Double(samples.count)
//                let heatToDisplay = samples.last!
////                if name == "Core0.0" {
////                    Swift.print("For \(name) band #\(band) heatToDisplay=\(heatToDisplay) hotness=\(samples)")
////                }
////                let hotLayer = hotnessLayers![band]
//                let rounded = CGFloat(1.0 - heatToDisplay.round2)  // to make sure always the same
//                let previous = hotLayer.backgroundColor
//                let new = CGColor.red.blendWithWhite(rounded)
//                if previous != new {
//                    hotLayer.backgroundColor = new
//                }
//            }
//            layers.unitHotness[name] = hotness
            let heatToDisplay = min(1.0, max(0.0, heat!))
            let rounded = CGFloat(1.0 - heatToDisplay.round2)  // to make sure always the same
            let previous = layer.backgroundColor
            let new = CGColor.red.blendWithWhite(rounded)
            if previous != new {
                layer.backgroundColor = new
            }
        }
    }
    func updateHotSegments(networkName: UnitName, _ info: (UnitName) -> Double) {
        var segments : [UnitName: BusWiring] = layers.DNSegments
        switch (networkName) {
        case "DN":
            segments = layers.DNSegments
        case "SN":
            segments = layers.SNSegments
        case "CN":
            segments = layers.CNSegments
        default:
            assert(1==0)
        }
        
        for (name, segment) in segments {
            let v = info(name)
            let capped = v < 0.0 ? 0.0 : v > 1.0 ? 1.0 : v
            let color = CGColor.red.blendWithWhite(CGFloat(1.0 - capped))
            segment.fillColor = color
        }
    }
    func glow(_ unitNames: [UnitName], at: CFTimeInterval) {
//        let animation = CABasicAnimation(keyPath: "transform.scale")
        CATransaction.begin()
        let animation = CABasicAnimation(keyPath: "borderWidth")
//        animation.beginTime = at
        animation.toValue = 4.0
        animation.duration = 1.0
        animation.autoreverses = true
        let animation2 = CABasicAnimation(keyPath: "borderColor")
//        animation2.beginTime = at
        animation2.toValue = CGColor.yellow
        animation2.duration = 1.0
        animation2.autoreverses = true
        for name in unitNames {
            let unitLayer = layers.units[name]
            if unitLayer == nil { continue }
            let convertedTime = unitLayer!.convertTime(CACurrentMediaTime(), from: nil) + at
            animation.beginTime = convertedTime
            animation2.beginTime = convertedTime
            unitLayer!.add(animation, forKey: nil)
            unitLayer!.add(animation2, forKey: nil)
        }
        CATransaction.commit()
    }
    func xformForCentering(_ unitName: UnitName) -> CATransform3D {
        let unitLayer = layers.units[unitName]!
        let center: CGPoint = layer!.bounds.center
        let lcenter: CGPoint = unitLayer.bounds.center
        let lcenter2 = layer!.convert(lcenter, from: unitLayer)
        let scale: CGFloat = 2.0
        var xform: CATransform3D = CATransform3DMakeTranslation(center.x - lcenter2.x, center.y - lcenter2.y, 0.0)
        xform = CATransform3DConcat(xform, CATransform3DMakeScale(scale, scale, 1.0))
        xform = CATransform3DConcat(xform, CATransform3DMakeTranslation(center.x * (1.0 - scale), center.y * (1.0 - scale), 0.0))
        return xform
    }
    var lastMatches: NSMutableArray! = nil
    func isOver(isDN: Bool, point: NSPoint) -> Bool {
        if !bounds.contains(point) || layer == nil {
            lastMatches = nil
            return false
        }
        let matches = NSMutableArray()
        for (n, segment) in (isDN ? layers.DNSegments : layers.SNSegments) {
            let p = layer!.convert(point, to: segment)
            if segment.contains(p) {
                matches.add(n)
            }
        }
        if matches.count == 0 {
            lastMatches = nil
        } else if matches != lastMatches {
            let center = theNotificationCenter
            let userInfo: [String : Any] = ["name": matches]
            let note = Notification(name: Notification.Name(isDN ? "MouseOverDN" : "MouseOverSN"), object: self, userInfo: userInfo)
            center.post(note)
            lastMatches = matches
        }
        return matches.count != 0
    }
    func notifyMouseOver(_ pointInWindow: NSPoint) {
        let point = convert(pointInWindow, from: window!.contentView!)
        let l = animationLayer.hitTest(point)
        if l != nil {
            Swift.print("Animated message \(l!.name!)")
            return
        }
        _ = isOver(isDN: true, point: point) || isOver(isDN: false, point: point)
    }
    override func mouseMoved(with theEvent: NSEvent) {
        let pointInWindow = theEvent.locationInWindow
        notifyMouseOver(pointInWindow)
    }
    override func mouseEntered(with theEvent: NSEvent) {
        let pointInWindow = theEvent.locationInWindow
        notifyMouseOver(pointInWindow)
    }
    override func mouseExited(with theEvent: NSEvent) {
        let pointInWindow = theEvent.locationInWindow
        notifyMouseOver(pointInWindow)
    }
    override func mouseDown(with theEvent: NSEvent) {
        let pointInWindow = theEvent.locationInWindow
        let point = convert(pointInWindow, from: window!.contentView!)
        if !bounds.contains(point) { return }
        var unitName = unitNameForPoint(point)
        if unitName == nil || (unitName?.isEmpty)! || layers.units[unitName!] == nil {
            // Gross hack for SN and DN
            for special in ["SN", "DN", "CN"] {
                let specialLayer = layers.units[special]
                if specialLayer == nil { continue }
                let p2 = specialLayer!.convert(point, from: layer!)
                if specialLayer!.hitTest(p2) != nil {
                    unitName = specialLayer!.name
                    break
                }
            }
        }
        if unitName != nil && !(unitName?.isEmpty)! && layers.units[unitName!] != nil {
            Swift.print("Selecting \(unitName!)")
            setSelection(Set([unitName!]))
            //            if theEvent.clickCount == 2 {
            //                let option = theEvent.modifierFlags.contains(NSEventModifierFlags.AlternateKeyMask)
            //                let center: CGPoint = layer!.bounds.center
            //                layer!.transform = xformForCentering(unitName)
            //            }
        } else {
            setSelection([])
        }
    }
}
