//
//  DKFlowGraphGen.swift
//  DataKit
//
//  Created by Bertrand Serlet on 9/13/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

class DKFlowGraphGen {
	let uniquingTable: DKTypeTable
	let gen: DKFunctionGenerator
	let fun: DKFunction
	init(_ uniquingTable: DKTypeTable, _ gen: DKFunctionGenerator, _ fun: DKFunction) {
		// We check the function takes 1 argument compatible with the generator
		// And produces no output
		// As we would not know what to do with the output
		assert(fun.signature.numberOfArguments == 1)
		assert(fun.signature[0] == gen.signature.output)
		assert(fun.signature.output == DKType.void)
		self.uniquingTable = uniquingTable
		self.gen = gen
		self.fun = fun
	}
	func optimize(fifos: inout [DKFifo]) -> Bool {
		// Currently, this optimization is pointless
		for i in 1 ..< fifos.count - 1 {
			if fifos[i].predicateOnInput == nil && fifos[i+1].predicateOnInput == nil && fifos[i].toAppend == .gatherByBatch {
				print("Optimize away fifo #\(i)")
				fifos.remove(at: i)
				_ = optimize(fifos: &fifos) // try again
				return true
			}
		}
		return false
	}
	func generate() -> (fifos: [DKFifo], lastFunc: DKFunction) {
		// Start with a fifo for the output of the generator
		let fifo = DKFifo(label: 0, itemType: gen.itemType)
		var fifos: [DKFifo] = [fifo]
		let lastFunc = generate(fun, &fifos)
		let opt = optimize(fifos: &fifos)
		if opt {
			print("Fifo optimized, now: \(fifos)")
		}
		var compact = false
		while compact {
			compact = false
		}
		return (fifos, lastFunc)
	}
	func generate(_ fun: DKFunction, _ fifos: inout [DKFifo]) -> DKFunction {
		func addFifo(_ t: DKType) -> DKFifo {
			let fifo = DKFifo(label: fifos.count, itemType: t)
			fifos |= fifo
			return fifo
		}
		if let filter = fun as? DKFunctionFilter {
			var lastFifo = fifos.last!
			let t = filter.itemType
			if lastFifo.toAppend != .all || lastFifo.predicateOnInput != nil {
				// make a new fifo
				lastFifo = addFifo(t)
			}
			lastFifo.predicateOnInput = filter.predicate
			return DKFunctionGatherFromFifo(uniquingTable, fifos.count - 1, t)
		} else if let comp = fun as? DKFunctionComposition {
			// First apply inner
			let genInner = generate(comp.inner, &fifos)
			if (genInner is DKFunctionGatherFromFifo) && comp.outer.isInputGroupable {
				// Instead of composing the functions, we specify that the last Fifo gathers
				fifos.last!.toAppend = .gatherByBatch
				let t = (genInner.signature.output as! DKTypeSequence).sub
				_ = addFifo(t)	// we ignore for now the (trivial) result
				return generate(comp.outer, &fifos)
			} else {
				let genOuter = generate(comp.outer, &fifos)
				return DKFunctionComposition(outer: genOuter, inner: genInner)
			}
		} else {
			let prev = DKFunctionGatherFromFifo(uniquingTable, fifos.count - 1, fifos.last!.itemType)
			return DKFunctionComposition(outer: fun, inner: prev)
		}
	}
	var flowGraphToJSON: JSON {
		let r = generate()
		let dict: [String: JSON] = [
			"types": uniquingTable.typeTableAsJSON,
			"fifos": .array(r.fifos.map { $0.fifoToJSON(uniquingTable) }),
			"generator": gen.functionToJSON,
			"fun": fun.functionToJSON,
			"last_fun": r.lastFunc.functionToJSON
		]
		return .dictionary(dict)
	}
}
