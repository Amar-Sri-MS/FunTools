//
//  CocoaExtras.swift
//
//  Created by Bertrand Serlet (bserlet@mac.com) on 12/10/15.
//  Copy and modify freely as long as you retain the file header
//    and provide modifications quarterly to the original author.
//

import AppKit

let theNotificationCenter = NotificationCenter.default

/*=============== GEOMETRY EXTRAS ===============*/

extension CGFloat: Algebraic {}

extension CGPoint: Topological {
    public func distance(to: CGPoint) -> CGFloat {
        return abs(x - to.x) + abs(y - to.y)
    }
    func distance(to other: CGRect) -> CGFloat {
        if other.contains(self) { return 0.0 }
        let x2 = other.origin.x
        let y2 = other.origin.y
        let x2b = x2 + other.size.width
        let y2b = y2 + other.size.height
        let left = x2b < x
        let right = x < x2
        let bottom = y2b < y
        let top = y < y2
        if top && left { return distance(to: CGPoint(x: x2b, y: y2)) }
        if left && bottom { return distance(to: CGPoint(x: x2b, y: y2b)) }
        if bottom && right { return distance(to: CGPoint(x: x2, y: y2b)) }
        if right && top { return distance(to: other.origin) }
        if left { return x - x2b }
        if right { return x2 - x }
        if bottom { return y - y2b }
        return y2 - y
    }
    func middle(_ other: CGPoint) -> CGPoint {
        return CGPoint(x: (x + other.x) / 2.0, y: (y + other.y) / 2.0)
    }
}

extension CGRect {
    var center: CGPoint {
        return CGPoint(x: origin.x + size.width / 2, y: origin.y + size.height / 2)
    }
    func distance(to other: CGRect) -> CGFloat {
        if intersects(other) { return 0.0 }
        let endx = origin.x + size.width
        let endy = origin.y + size.height
        let x2 = other.origin.x
        let y2 = other.origin.y
        let x2b = x2 + other.size.width
        let y2b = y2 + other.size.height
        let left = x2b < origin.x
        let right = endx < x2
        let bottom = y2b < origin.y
        let top = endy < y2
        if top && left { return CGPoint(x: origin.x, y: endy) ^ CGPoint(x: x2b, y: y2) }
        if left && bottom { return CGPoint(x: origin.x, y: origin.y) ^ CGPoint(x: x2b, y: y2b) }
        if bottom && right { return CGPoint(x: endx, y: origin.y) ^ CGPoint(x: x2, y: y2b) }
        if right && top { return CGPoint(x: endx, y: endy) ^ other.origin }
        if left { return origin.x - x2b }
        if right { return x2 - endx }
        if bottom { return origin.y - y2b }
        return y2 - endy
    }
}

extension CALayer {
    func containsLayer(_ candidate: CALayer) -> Bool {
        if self === candidate { return true }
        if sublayers == nil { return false }
        return sublayers!.any { $0.containsLayer(candidate) }
    }
    func removeAllSublayers() {
        while sublayers != nil && !sublayers!.isEmpty {
            let sub = sublayers!.first!
            sub.removeFromSuperlayer()
        }
    }
    func ancestorLayer() -> CALayer! {
        var parent = superlayer
        if parent == nil { return nil }
        while true {
            let gp = parent!.superlayer
            if gp == nil { return parent }
            parent = gp
        }
        fatalError()
    }
    func relativeToAbsoluteTransform() -> CGAffineTransform {
        // Only works for transalations
        let motherOfAllLayers = ancestorLayer()
        let absZero = motherOfAllLayers?.convert(CGPoint.zero, from: self)
        return CGAffineTransform(translationX: absZero!.x, y: absZero!.y)
    }
    func setBackgroundColorRecursive(_ color: CGColor, _ textColor: CGColor, _ depth: Int) {
        backgroundColor = color
        if let text = self as? CATextLayer {
            text.foregroundColor = textColor
        }
        if sublayers != nil && depth > 0 {
            for sub in sublayers! {
                sub.backgroundColor = color
                sub.setBackgroundColorRecursive(color, textColor, depth - 1)
            }
        }
    }
}

extension CGFloat {
    func sizesInProportion(_ proportions: [Int]) -> [CGFloat] {
        let sum = proportions.reduce(0, +)
        assert(sum != 0)
        var remain = self
        var sizes: [CGFloat] = []
        for i in proportions.indices {
            if i == proportions.count - 1 {
                sizes |= remain
            } else {
                let s = CGFloat((Double(self) * Double(proportions[i]) / Double(sum)).round)
                sizes |= s
                remain -= s
            }
        }
        return sizes
    }
    func sizesWhenSplit(_ numSplit: Int) -> [CGFloat] {
        assert(numSplit > 0)
        var remain = self
        var sizes: [CGFloat] = []
        for i in 0 ..< numSplit {
            if i == numSplit - 1 {
                sizes |= remain
            } else {
                let s = CGFloat((Double(self) / Double(numSplit)).round)
                sizes |= s
                remain -= s
            }
        }
        return sizes
    }
}

extension CGRect {
    func abutXRectsInProportion(_ proportions: [Int]) -> [CGRect] {
        let sizes = width.sizesInProportion(proportions)
        var rects: [CGRect] = []
        var x = minX
        for i in sizes.indices {
            let s = sizes[i]
            rects |= CGRect(x: x, y: minY, width: s, height: height)
            x += s
        }
        return rects
    }
    func abutYRectsInProportion(_ proportions: [Int]) -> [CGRect] {
        let sizes = height.sizesInProportion(proportions)
        var rects: [CGRect] = []
        var y = minY
        for i in sizes.indices {
            let s = sizes[i]
            rects |= CGRect(x: minX, y: y, width: width, height: s)
            y += s
        }
        return rects
    }
}

extension CGColor {
    static var white: CGColor {
        return NSColor.white.cgColor
    }
    static var black: CGColor {
        return NSColor.black.cgColor
    }
    static var red: CGColor {
        return NSColor.red.cgColor
    }
    static var green: CGColor {
        return NSColor.green.cgColor
    }
    static var blue: CGColor {
        return NSColor.blue.cgColor
    }
    static var yellow: CGColor {
        return NSColor.yellow.cgColor
    }
    static var purple: CGColor {
        return NSColor.purple.cgColor
    }
    static var gray: CGColor {
        return black.blendWithWhite(0.5)
    }
    func blendWithWhite(_ whiteProportion: CGFloat) -> CGColor {
        let blended = NSColor(cgColor: self)!.blended(withFraction: whiteProportion, of: NSColor.white)!
        let noAlpha = blended.withAlphaComponent(1.0)
        return noAlpha.cgColor
    }
    func blendWithBlack(_ blackProportion: CGFloat) -> CGColor {
        let blended = NSColor(cgColor: self)!.blended(withFraction: blackProportion, of: NSColor.black)!
        let noAlpha = blended.withAlphaComponent(1.0)
        return noAlpha.cgColor
    }
    func blend(_ other: CGColor) -> CGColor {
        return NSColor(cgColor: self)!.blended(withFraction: 0.5, of: NSColor(cgColor: other)!)!.cgColor
    }
    var lighter: CGColor { return blendWithWhite(0.7) }
    var darker: CGColor { return blendWithBlack(0.05) }
    static var lightGray: CGColor {
        return NSColor.lightGray.cgColor
    }
    static var veryLightGray: CGColor {
        return black.blendWithWhite(0.94)
    }
    static var extremelyLightGray: CGColor {
        return black.blendWithWhite(0.97)
    }
    func invert() -> CGColor {
        return NSColor(cgColor: self)!.invert().cgColor
    }
    static func random() -> CGColor {
        let red = Double.random01()
        let green = Double.random01()
        let blue = Double.random01()
        return NSColor(calibratedRed: CGFloat(red), green: CGFloat(green), blue: CGFloat(blue), alpha: 0.0).cgColor
    }
}

/*=============== CORE ANIMATION EXTRAS ===============*/

extension CALayer {
    func addAbutXSublayers(_ update: Bool, proportions: [Int]) {
        let sizes = bounds.width.sizesInProportion(proportions)
        var x = bounds.minX
        for i in sizes.indices {
            let s = sizes[i]
            let sub = update ? sublayers![i] : CALayer()
            sub.frame = CGRect(x: x, y: bounds.minY, width: s, height: bounds.height)
            x += s
            if !update {
                sub.contentsScale = contentsScale
                addSublayer(sub)
            }
        }
    }
    func addAbutXSublayers(_ update: Bool, proportions: Int...) {
        addAbutXSublayers(update, proportions: proportions)
    }
    func addAbutYSublayers(_ update: Bool, proportions: [Int]) {
        let sizes = bounds.height.sizesInProportion(proportions)
        var y = bounds.minY
        for i in sizes.indices {
            let s = sizes[i]
            let sub = update ? sublayers![i] : CALayer()
            sub.frame = CGRect(x: bounds.minX, y: y, width: bounds.width, height: s)
            y += s
            if !update {
                sub.contentsScale = contentsScale
                addSublayer(sub)
            }
        }
    }
    func addAbutYSublayers(_ update: Bool, proportions: Int...) {
        addAbutYSublayers(update, proportions: proportions)
    }
    func addSplitXSublayers(_ update: Bool, numSplit: Int) {
        let sizes = bounds.width.sizesWhenSplit(numSplit)
        var x = bounds.minX
        for i in sizes.indices {
            let s = sizes[i]
            let sub = update ? sublayers![i] : CALayer()
            sub.frame = CGRect(x: x, y: bounds.minY, width: s, height: bounds.height)
            x += s
            if !update {
                sub.contentsScale = contentsScale
                addSublayer(sub)
            }
        }
    }
    func scaleFrameOrigin(_ xratio: CGFloat, _ yratio: CGFloat) {
        var new = frame.origin
        new.x *= xratio
        new.y *= yratio
        frame.origin = new
    }
}

/*=============== APPKIT EXTRAS ===============*/

extension NSColor {
    func invert() -> NSColor {
        let cc = usingColorSpace(NSColorSpace.genericRGB)!
        return NSColor(red: 1.0 - cc.redComponent, green: 1.0 - cc.greenComponent, blue: 1.0 - cc.blueComponent, alpha: cc.alphaComponent)
    }
}

extension NSTextView {
    func makeNonEditableFixedPitchOfSize(_ fontSize: CGFloat) {
        isAutomaticSpellingCorrectionEnabled = false
        isEditable = false
        font = NSFont.userFixedPitchFont(ofSize: 12.0)  // try to speedup display
    }
    func setStringPreservingSelection(_ str: String) {
        if string == str { return } // no change
        let range = selectedRange()
        string = str
        setSelectedRange(range)
        scrollRangeToVisible(range)
    }
}
extension NSText {
    convenience init(nonSelectableText text: String, frame: NSRect) {
        self.init(frame: frame)
        isSelectable = false
        isEditable = false
        alignment = NSTextAlignment.left
        drawsBackground = false
        string = text
    }
}

extension NSTextField {
    func setJSONValue(_ json: JSON) {
        switch json {
        case let .integer(i): integerValue = i
        case let .real(r): doubleValue = r
        case let .bool(b): stringValue = b ? "true" : "false"
        case .null: stringValue = "null"
        case let .string(s): stringValue = s
        case let .array(a): stringValue = "[\(a.count) items]"
        case let .dictionary(d): stringValue = "{\(d.count) items}"
        }
    }
}
