//
//  DKNode.swift
//  DataKit
//
//  Created by Bertrand Serlet on 11/12/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

class DKNode: CustomStringConvertible {
	var itemType: DKType
	let graphIndex: Int
	init(_ graphIndex: Int, itemType: DKType) {
		self.itemType = itemType
		self.graphIndex = graphIndex
	}
	func sugaredDescription(_ uniquingTable: DKTypeTable) -> String {
		fatalErrorMustBeImplementedBySubclass()
	}
	var description: String {
		return sugaredDescription(DKTypeTable())
	}
	func nodeToJSONDict(_ uniquingTable: DKTypeTable) -> [String: JSON] {
		fatalErrorMustBeImplementedBySubclass()
	}
	func nodeToJSON(_ uniquingTable: DKTypeTable) -> JSON {
		var dict: [String: JSON] = nodeToJSONDict(uniquingTable)
		dict["graph_index"] = .integer(graphIndex)
		return .dictionary(dict)
	}
}
