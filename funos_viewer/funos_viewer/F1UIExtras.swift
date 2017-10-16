//
//  NSUIExtras.swift
//
//  Created by Bertrand Serlet on 3/8/16.
//  Copyright © 2016 Fungible Inc. All rights reserved.
//

// UI Extras specific to NS chip

import AppKit

/*=============== QUARTZ CORE EXTRAS ===============*/

extension CGPath {
    static func isosceleTriangle(_ size: CGSize, sideWays: Bool, flip: Bool) -> CGPath {
        // if flip is false, points up
        let w: CGFloat = size.width
        let h: CGFloat = size.height
        let path = CGMutablePath()
        if sideWays {
            let x0 = w * (flip ? 0.67 : 0.33)
            path.move(to: CGPoint(x: x0, y: h * 0.33))
            path.addLine(to: CGPoint(x: x0, y: h * 0.67))
            path.addLine(to: CGPoint(x: w - x0, y: h * 0.5))
        } else {
            let y0 = h * (flip ? 0.67 : 0.33)
            path.move(to: CGPoint(x: w * 0.33, y: y0))
            path.addLine(to: CGPoint(x: w * 0.67, y: y0))
            path.addLine(to: CGPoint(x: w * 0.5, y: h - y0))
        }
        path.closeSubpath()
        return path.copy()!
    }
    static func wireFramePathForPoints(_ points: [CGPoint]) -> CGPath {
        let wireFramePath = CGMutablePath()
        if points.count == 0 { return wireFramePath }
        wireFramePath.move(to: points[0])
        for i in 1 ..< points.count {
            wireFramePath.addLine(to: points[i])
        }
        return wireFramePath
    }
    static func pathForWireFramePath(_ points: [CGPoint], transform: UnsafePointer<CGAffineTransform>?, thickness: CGFloat) -> CGPath {
        let wireFramePath = wireFramePathForPoints(points)
        return CGPath(__byStroking: wireFramePath, transform: transform, lineWidth: thickness, lineCap: CGLineCap.square, lineJoin: CGLineJoin.round, miterLimit: 0.5)!
    }
    static func pointsFor123Segments(_ horiz: Bool, start: CGPoint, length: CGFloat, segment2Length l2: CGFloat! = nil, segment3Length l3: CGFloat! = nil) -> [CGPoint] {
        // If segment2 exist, it's a 90 degres turn, >0 if up (or right)
        let end0 = CGPoint(x: start.x + (horiz ? length : 0.0), y: start.y + (horiz ? 0.0 : length))
        var points = [start, end0]
        if l2 == nil { return points }
        let end1 = CGPoint(x: end0.x + (horiz ? 0.0 : l2), y: end0.y + (horiz ? l2 : 0.0))
        points |= end1
        if l3 == nil { return points }
        let end2 = CGPoint(x: end1.x + (horiz ? l3 : 0.0), y: end1.y + (horiz ? 0.0 : l3))
        points |= end2
        return points
    }
}

extension NSFont {
    func sizeForString(_ string: String) -> CGSize {
        let maxSize = CGSize(width: 1E6, height: 1E6)
        return string.boundingRect(with: maxSize, options: [NSString.DrawingOptions.usesLineFragmentOrigin], attributes: [NSAttributedStringKey.font: self], context: nil).size
    }
}

extension CALayer {
    func preventAnimations() {
        actions = ["borderColor": NSNull(), "backgroundColor": NSNull()]
    }
    @objc func positionForAnimation() -> CGPoint {
        // When this layer is first used for the start of a SimulationMessageLayer, 
        // returns where the message layer should be positioned
        // Expressed in relative coordonates
        return bounds.center
    }
    func addTextInACircle(_ centerPosition: CGPoint, diameter: CGFloat, lineWidth: CGFloat, strikeColor: CGColor, fillColor: CGColor, textColor: CGColor, label: String, font: NSFont, fontSize: CGFloat) {
        let circleSize = CGSize(width: diameter, height: diameter)
        let circle = CAShapeLayer()
        let path = CGMutablePath()
        let base = CGPoint(x: centerPosition.x - diameter / 2.0, y: centerPosition.y - diameter / 2.0)
        let rect = CGRect(origin: base, size: circleSize)
        path.addEllipse(in: rect)
        circle.path = path
        circle.fillColor = fillColor
        circle.strokeColor = strikeColor
        circle.lineWidth = lineWidth
        circle.bounds = path.boundingBox
        circle.frame.size = circle.bounds.size
        circle.frame.origin = base
        addSublayer(circle)
        let text = CATextLayer()
        text.contentsScale = contentsScale
        text.string = label
        text.font = font
        text.fontSize = fontSize
        text.foregroundColor = textColor
        text.alignmentMode = "center"
        let textSize = font.sizeForString(label)
        let originx = centerPosition.x - diameter / 2.0
        let correction: CGFloat = /* textSize.height == 19 ? 13.0 : textSize.height == 13 ? 18.0 : */ -textSize.height + diameter
        let originy = centerPosition.y - textSize.height / 2.0 - correction
//        print("diam=\(diameter) textSize=\(textSize) fontSize=\(fontSize)")
        text.frame.origin = CGPoint(x: originx, y: originy)
        text.frame.size = circleSize
        addSublayer(text)

    }
    func addFlowPath(_ diameter: CGFloat, overallWidth: CGFloat, units: [String], strikeColor: CGColor, fillColor: CGColor, textColor: CGColor) {
        var adjustedDiam = diameter
        var adjustedArrowSize: CGFloat = 30.0
        let lineWidth: CGFloat = 2.0
        let xStart: CGFloat = lineWidth
        let yStart: CGFloat = lineWidth
        let width = overallWidth // - xStart
        assert(units.count >= 2)
        while adjustedDiam * CGFloat(units.count) + adjustedArrowSize * 0.4 * CGFloat(units.count-1) > width {
            adjustedDiam *= 0.8 // we do it that way so that several flows at are the same scale
            adjustedArrowSize *= 0.8
        }
        var fontSize: CGFloat = 24.0
        var font: NSFont = NSFont.boldSystemFont(ofSize: fontSize)
        while true {
            font = NSFont.boldSystemFont(ofSize: fontSize)
            let allFits = units.every {
                let textSize = font.sizeForString($0)
                return textSize.width < adjustedDiam * 0.80 && textSize.height < adjustedDiam * 0.80
            }
            if allFits || fontSize <= 8.0 {
//                print("fontSize=\(fontSize) diam=\(adjustedDiam)")
                break
            }
            fontSize -= 1.0
        }
        let intervalX = (width - adjustedDiam) / CGFloat(units.count - 1)
        // Draw the circles
        for i in units.indices {
            let base = CGPoint(x: xStart + adjustedDiam/2.0 + CGFloat(i) * intervalX, y: yStart + diameter/2.0 + 4.0)
            addTextInACircle(base, diameter: adjustedDiam, lineWidth: lineWidth, strikeColor: strikeColor, fillColor: fillColor, textColor: textColor, label: units[i], font: font, fontSize: fontSize)
        }
        let arrowSize: CGSize = CGSize(width: adjustedArrowSize, height: adjustedArrowSize)
        let arrowPath = CGPath.isosceleTriangle(arrowSize, sideWays: true, flip: false)
        for i in 0 ..< units.count-1 {
            let line = CAShapeLayer()
            let path = CGMutablePath()
            let base = CGPoint(x: xStart + CGFloat(i) * intervalX + adjustedDiam, y: yStart + diameter / 2.0 + lineWidth)
            path.move(to: base)
            path.addLine(to: CGPoint(x: base.x + intervalX - adjustedDiam, y: base.y))
            line.path = path
            line.strokeColor = CGColor.red.darker
            line.lineWidth = lineWidth
            line.bounds = path.boundingBox
            line.frame.size = line.bounds.size
            line.frame.origin = base
            addSublayer(line)
            let arrow = CAShapeLayer()
            let abounds = arrowPath.boundingBox
            let abaseX: CGFloat = xStart + base.x + intervalX - adjustedDiam - abounds.size.width - lineWidth - 1.0
            let abaseY = yStart + base.y - abounds.size.height / 2.0 - lineWidth
            let abase = CGPoint(x: abaseX, y: abaseY)
            arrow.path = arrowPath
            arrow.strokeColor = CGColor.red.darker
            arrow.fillColor = CGColor.red.darker
            arrow.bounds = abounds
            arrow.frame.size = arrow.bounds.size
            arrow.frame.origin = abase
            addSublayer(arrow)
        }
    }
}

/*=============== REPRESENTATION OF A BUS ===============*/

class BusWiring: CAShapeLayer {
    var unitName: UnitName! = nil
    var points: [CGPoint]!
    override init() { super.init() }
    required init?(coder aDecoder: NSCoder) {
        super.init(coder: aDecoder)
    }
    override init(layer: Any) {
        super.init(layer: layer)
        if let o2 = layer as? BusWiring {
            unitName = o2.unitName
        }
    }
    
    // Draws a line segment for one of the networks.  Each line has three segments at right angles.
    func setDimensions123Segments(_ horiz: Bool, start: CGPoint, length: CGFloat, segment2Length l2: CGFloat! = nil, segment3Length l3: CGFloat! = nil, thickness: CGFloat) {
        // If segment2 exist, it's a 90 degres turn, >0 if up (or right)
        points = CGPath.pointsFor123Segments(horiz, start: start, length: length, segment2Length: l2, segment3Length: l3)
        path = CGPath.pathForWireFramePath(points, transform: nil, thickness: thickness)
        bounds = (path?.boundingBox)!
        frame = NSRect(x: start.x, y: start.y, width: horiz ? length : thickness, height: horiz ? thickness : length)
    }
    override func contains(_ p: CGPoint) -> Bool {
        // This needs to be overridden so that clicks work
        return path!.__containsPoint(transform: nil, point: p, eoFill: true)
    }
    var startPoint: CGPoint { return points.first! }
    var endPoint: CGPoint { return points.last! }
    override func positionForAnimation() -> CGPoint {
        if points.count > 2 { return points[points.count / 2] }
        return startPoint.middle(endPoint)
    }
    func distance(to p: CGPoint) ->(dist: CGFloat, startIsClosest: Bool) {
        let ds = startPoint ^ p
        let de = endPoint ^ p
        return ds < de ? (ds, true) : (de, false)
    }
    func asPositionAnimation(_ inOrder: Bool, transform: UnsafePointer<CGAffineTransform>) -> CAKeyframeAnimation {
        let animation = CAKeyframeAnimation(keyPath: "position")
        animation.path = CGPath.pathForWireFramePath(inOrder ? points : points.reversed(), transform: transform, thickness: 1.0)
        animation.repeatCount = 1
        return animation
    }
}

/*=============== REPRESENTATION OF A MESSAGE IN TRANSIT ===============*/

enum AnimationShapeStyle {
    case packet // NU -> HU
    case `switch` // NU -> NU
    case packetViaHBM // NU -> HBM -> HU
    case commandLeft // HU Left -> NU
    case commandRight // HU Right-> NU
    case DMA
    case WUL
}

// This class denotes a message in transit
// It contains a unit, and a message in addition to a shape layer
class SimulationMessageLayer: CAShapeLayer {
    var at: F1Block!
    override init() { super.init() }
    override init(layer: Any) {
        super.init(layer: layer)
        if let o2 = layer as? SimulationMessageLayer {
            at = o2.at
        }
    }
    required init?(coder aDecoder: NSCoder) {
        super.init(coder: aDecoder)
    }
    static func new(_ style: AnimationShapeStyle, color: CGColor) -> SimulationMessageLayer {
        switch style {
            case .packet:
                return .smallPointedTriangle(color, pointsUp: false)
            case .switch:
                return .smallRect(color)
            case .packetViaHBM:
                return .smallCircle(color)
            case .commandLeft:
                return .smallPointedTriangle(color, pointsLeft: true)
            case .commandRight:
                return .smallPointedTriangle(color, pointsLeft: false)
            case .DMA:
                return .smallCircle(color)
            case .WUL:
                return .smallCircle(color)
        }
    }
    override var name: String? {
        get {
            return "@\(at.name): XXX"
        }
        set(x) {
            fatalError("Can't set name \(x!)")
        }
    }
    private static func smallPointedTriangle(_ fillColor: CGColor, pointsUp: Bool) -> SimulationMessageLayer {
        let layer = SimulationMessageLayer()
        let size = CGSize(width: 30.0, height: 40.0)
        layer.path = CGPath.isosceleTriangle(size, sideWays: false, flip: !pointsUp)
        layer.fillColor = fillColor
        layer.strokeColor = fillColor.blendWithBlack(0.25)
        layer.bounds = (layer.path?.boundingBox)!
        return layer
    }
    private static func smallPointedTriangle(_ fillColor: CGColor, pointsLeft: Bool) -> SimulationMessageLayer {
        let layer = SimulationMessageLayer()
        let size = CGSize(width: 30.0, height: 40.0)
        layer.path = CGPath.isosceleTriangle(size, sideWays: true, flip: !pointsLeft)
        layer.fillColor = fillColor
        layer.strokeColor = fillColor.blendWithBlack(0.25)
        layer.bounds = (layer.path?.boundingBox)!
        return layer
    }
    private static func smallRect(_ fillColor: CGColor) -> SimulationMessageLayer {
        let layer = SimulationMessageLayer()
        let rect = CGRect(x: 0.0, y: 0.0, width: 10.0, height: 10.0)
        layer.path = CGPath(rect: rect, transform: nil)
        layer.fillColor = fillColor
        layer.strokeColor = fillColor.blendWithBlack(0.25)
        layer.bounds = (layer.path?.boundingBox)!
        return layer
    }
    private static func smallRoundedRect(_ fillColor: CGColor) -> SimulationMessageLayer {
        let layer = SimulationMessageLayer()
        let rect = CGRect(x: 0.0, y: 0.0, width: 10.0, height: 10.0)
        layer.path = CGPath(roundedRect: rect, cornerWidth: 3.5, cornerHeight: 3.5, transform: nil)
        layer.fillColor = fillColor
        layer.strokeColor = fillColor.blendWithBlack(0.25)
        layer.bounds = (layer.path?.boundingBox)!
        return layer
    }
    private static func smallCircle(_ fillColor: CGColor) -> SimulationMessageLayer {
        let layer = SimulationMessageLayer()
        let rect = CGRect(x: 0.0, y: 0.0, width: 12.0, height: 12.0)
        let path = CGMutablePath()
        path.__addEllipse(transform: nil, rect: rect)
        layer.path = path
        layer.fillColor = fillColor
        layer.strokeColor = fillColor.blendWithBlack(0.25)
        layer.bounds = (layer.path?.boundingBox)!
        return layer
    }
}

/*=============== APPKIT EXTRAS ===============*/

extension NSControl {
    func makeOrResetBold(_ bold: Bool) {
        if font == nil { return }
        let fontSize = font!.pointSize
        font = bold ? NSFont.boldSystemFont(ofSize: fontSize) : NSFont.systemFont(ofSize: fontSize)
    }
    var titleOfSelectedItem: String { fatalError() }
    func setValueFromJSON(_ json: JSON) {
        switch json {
            case .null: break
            case .bool(let b): stringValue = b ? "true" : "false"
            case .integer(let i): integerValue = i
            case .real(let d): doubleValue = d
            case .string(let s): stringValue = s
            default: stringValue = description
        }
    }
    @objc var boolValue: Bool {
        return !(integerValue == 0)
    }
}

extension NSButton {
    override var boolValue: Bool {
        return state.rawValue == 1
    }
}

