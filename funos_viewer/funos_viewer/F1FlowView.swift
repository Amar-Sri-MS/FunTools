//
//  F1FlowView.swift
//
//  Created by Bertrand Serlet on 5/12/16.
//  Copyright © 2016 Fungible Inc. All rights reserved.
//

import AppKit

class F1FlowView: NSControl {
    func setupLayer(_ rect: NSRect, flowDesc: String) {
        let units = flowDesc.components(separatedBy: "->")
        assert(units.count >= 2)
        wantsLayer = true
        layer!.addFlowPath(rect.height - 8.0, overallWidth: rect.width - 20.0, units: units, strikeColor: CGColor.blue.darker, fillColor: .white, textColor: CGColor.blue.darker)
    }
    init(frame: NSRect, flowDesc: String) {
        super.init(frame: frame)
        setupLayer(frame, flowDesc: flowDesc)
    }
    override init(frame: NSRect) {
        super.init(frame: frame)
        setupLayer(frame, flowDesc: "A->B")
    }
    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setupLayer(frame, flowDesc: "A->B")
    }
    override var isEnabled: Bool {
        get {
            return super.isEnabled
        }
        set(x) {
            super.isEnabled = x
            layer!.opacity = x ? 1.0 : 0.5
        }
    }
}
