//
//  DKValueStream.swift
//  DataKit
//
//  Created by Bertrand Serlet on 9/13/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

protocol DKValueStream {
	init(itemType: DKType)
	var itemType: DKType { get }
}

extension DKValueStream {
	var sequenceType: DKTypeSequence { return DKTypeSequence(subType: itemType) }
}

class DKValueStreamSource: DKValueStream {
	var itemType: DKType
	required init(itemType: DKType) {
		self.itemType = itemType
	}
}

class DKValueStreamDest: DKValueStream {
	var itemType: DKType
	required init(itemType: DKType) {
		self.itemType = itemType
	}
}
