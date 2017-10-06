//
//  DKValueFunc.swift
//  DataKit
//
//  Created by Bertrand Serlet on 7/29/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

// A function has a signature

class DKValueFunc: DKValue, DKValueIsEqualToOther {
	let fun: DKFunction
	init(_ fun: DKFunction) { self.fun = fun }
	func isEqualTo(_ rhs: DKValue) -> Bool {
		if let f = rhs as? DKValueFunc {
			return fun == f.fun
		}
		return false
	}
	override var type: DKType { return fun.signature }
	override var rawValueToJSON: JSON {
		return fun.functionToJSON
	}
	class func fromRawJSON(_ uniquingTable: DKTypeTable, _ j: JSON) -> DKValueFunc! {
		if !j.isDictionary { return nil }
		let fun = DKFunction.functionFromJSON(uniquingTable, j.dictionaryValue)
		return fun == nil ? nil : DKValueFunc(fun!)
	}
	override var description: String {
		return fun.description
	}
}

