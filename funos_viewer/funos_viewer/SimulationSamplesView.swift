//
//  SimulationSamplesView.swift
//
//  Created by Bertrand Serlet on 12/30/15.
//  Copyright © 2016 Fungible Inc. All rights reserved.
//

import AppKit

// A way to display samples.

class SimulationSamplesViewSpan: NSObject {
    var span: Double = 0.0
    init(_ s: Double) { span = s }
}

extension CALayer {
    func updateSamplesSize(_ newWidth: CGFloat, _ newHeight: CGFloat) {
        let oldw = bounds.width
        let oldh = bounds.height
        frame = CGRect(x: 0, y:0, width: newWidth, height: newHeight)
        if sublayers != nil && !sublayers!.isEmpty {
            let sx = newWidth / oldw
            let sy = newHeight / oldh
            for l in sublayers! {
                let rect = l.frame
                let rect2 = CGRect(x: rect.origin.x * sx, y: rect.origin.y * sy, width: rect.width * sx, height: rect.height * sy)
                l.frame = rect2
            }
        }
    }

    func makeOrUpdateSamples(_ ss: SimulationScaledSamples) {
        let width: CGFloat = 2.0
        let height = bounds.height
        let maxNumBars = Int(bounds.width / width)
        var allSamples = ss.copyAllScaledSamples() // inefficient but thread-safe
        let overallRange: ClosedRange<Double>? = ss.overallRange
        if overallRange == nil { return }
        let overallSpan = overallRange!.span
        if overallSpan <= 0.0 { return }
        var tryIncremental = true
        if contents == nil {
            tryIncremental = false
            contents = SimulationSamplesViewSpan(overallSpan)
        } else if (contents as! SimulationSamplesViewSpan).span != overallSpan {
            tryIncremental = false
            (contents as! SimulationSamplesViewSpan).span = overallSpan
        }
        func calibrate(_ value: Double) -> CGFloat {
            if overallRange == nil { return 0.0}
            var v = (value - overallRange!.lowerBound) / overallSpan
            v = min(1.0, v)
            v = max(v, 0.0)
            v = v * 0.9 // leave some margin
            return CGFloat(v) * height
        }
        func subSetFrame(_ sub: CALayer, index: Int) {
            let sample = allSamples[index]
            if sample.range == nil { return }
            let x = width * CGFloat(index)
            let hmin: CGFloat = calibrate(sample.range!.lowerBound)
            let havg: CGFloat = calibrate(sample.avg)
            let hmax: CGFloat = calibrate(sample.range!.upperBound)
            sub.removeAllSublayers()
            let smin = CALayer()
            smin.frame = CGRect(x: x, y: 0, width: width, height: hmin)
            smin.backgroundColor = SimulationSamplesView.colorForMinValue
            sub.addSublayer(smin)
            if havg != hmin {
                let savg = CALayer()
                savg.frame = CGRect(x: x, y: hmin, width: width, height: havg - hmin)
                savg.backgroundColor = SimulationSamplesView.colorForAvgValue
                sub.addSublayer(savg)
            }
            if hmax != havg {
                let smax = CALayer()
                smax.frame = CGRect(x: x, y: havg, width: width, height: hmax - havg)
                smax.backgroundColor = SimulationSamplesView.colorForMaxValue
                sub.addSublayer(smax)
            }
        }
        if tryIncremental && (allSamples.count <= maxNumBars) && sublayers != nil && sublayers!.count != 0 && sublayers!.count <= allSamples.count {
            // incrementally add new bars
            if !sublayers!.isEmpty {
                let i = sublayers!.count - 1
                let sub = sublayers![i]
                subSetFrame(sub, index: i)
            }
            for i in sublayers!.count ..< allSamples.count {
                let sub = CALayer()
                subSetFrame(sub, index: i)
                addSublayer(sub)
            }
        } else {
            while ss.numScaledSamples > maxNumBars {
                ss.compress(2)
            }
            allSamples = ss.copyAllScaledSamples() // inefficient but thread-safe
            removeAllSublayers()
            for i in allSamples.indices {
                let sub = CALayer()
                subSetFrame(sub, index: i)
                addSublayer(sub)
            }
        }
    }
}

class SimulationSamplesView: NSView {
    static let colorForMinValue: CGColor = CGColor.blue.lighter
    static let colorForMaxValue: CGColor = CGColor.purple.blendWithWhite(0.1)
    static let colorForAvgValue: CGColor = colorForMinValue.blend(colorForMaxValue)
    private var samples: SimulationScaledSamples!
    private var lastGeneration = 0
    func setupLayer(_ size: CGSize) {
        wantsLayer = true
        layer!.removeAllSublayers()
        let textLayer = CATextLayer()
        textLayer.contentsScale = layer!.contentsScale
        textLayer.string = "Usage history"
        textLayer.fontSize = 12.0
        textLayer.font = NSFont.systemFont(ofSize: textLayer.fontSize)
        textLayer.foregroundColor = CGColor.black
        textLayer.alignmentMode = "left"
        textLayer.frame = CGRect(x: 3, y: size.height - 17, width: size.width - 6, height: 16)
        textLayer.transform = CATransform3DMakeTranslation(0, 0, +1)
        layer!.addSublayer(textLayer)
        let samplesLayer = CALayer()
        samplesLayer.frame = CGRect(x: 2, y: 0, width: size.width + 11, height: size.height - 16)
        samplesLayer.backgroundColor = CGColor.white
        samplesLayer.borderWidth = 0.5
        layer!.addSublayer(samplesLayer)
    }
    override init(frame: NSRect) {
        super.init(frame: frame)
        setupLayer(frame.size)
    }
    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setupLayer(frame.size)
    }
    override var fittingSize: NSSize { return frame.size }
    func setSamples(_ ss: SimulationScaledSamples!) {
        if samples == nil && ss == nil {
            // no change
            return
        }
        if samples != nil && ss != nil && samples === ss && lastGeneration == ss.generation {
            // no change
            return
        }
        let textLayer = layer!.sublayers![0] as! CATextLayer
        let samplesLayer = layer!.sublayers![1]
        if ss == nil || ss.numScaledSamples == 0 {
            samples = nil
            lastGeneration = 0
            textLayer.string = "Usage history"
            samplesLayer.removeAllSublayers()
        } else {
            let incremental = samples != nil && samples === ss
            let title = ss.title
            let titleExtras = ss.titleExtras(ss)
            let text = titleExtras.isEmpty ? "\(title):" : "\(title) (\(titleExtras)):"
            textLayer.string = text
            if samples != nil {
                lastGeneration = samples.generation
            }
            if !incremental {
                samples = ss
                samplesLayer.removeAllSublayers()
            }
            samplesLayer.makeOrUpdateSamples(samples)
        }
    }
}

