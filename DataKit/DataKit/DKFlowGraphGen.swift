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
	func optimize(nodes: inout [DKNode]) -> Bool {
		// Currently, this optimization is pointless
		if nodes.count < 2 { return false }
		for i in 1 ..< nodes.count - 1 {
			if let fifo = nodes[i] as? DKNodeFifo {
				if let next = nodes[i+1] as? DKNodeFifo {
					if fifo.hasDefaultBehavior && next.predicateOnInput == nil {
						print("Optimize away fifo #\(i)")
						nodes.remove(at: i)
						_ = optimize(nodes: &nodes) // try again
						return true
					}
				}
			}
		}
		return false
	}
	func generate() -> (nodes: [DKNode], lastFunc: DKFunction) {
		// Start with a fifo for the output of the generator
		let fifo = DKNodeFifo(label: 0, itemType: gen.itemType)
		var nodes: [DKNode] = [fifo]
		let lastFunc = generate(fun, &nodes)
		let opt = optimize(nodes: &nodes)
		if opt {
			print("Fifo optimized, now: \(nodes)")
		}
		var compact = false
		while compact {
			compact = false
		}
		return (nodes, lastFunc)
	}
	func generate(_ fun: DKFunction, _ nodes: inout [DKNode]) -> DKFunction {
		func addFifo(_ t: DKType) {
			let fifo = DKNodeFifo(label: nodes.count, itemType: t)
			nodes |= fifo
		}
		if let filter = fun as? DKFunctionFilter {
			var lastFifo = nodes.last!
			let t = filter.itemType
			let appliesPredicate = (lastFifo is DKNodeFifo) && !(lastFifo as! DKNodeFifo).hasDefaultBehavior
			if !(lastFifo is DKNodeFifo) || appliesPredicate {
				// make a new fifo
				addFifo(t)
				lastFifo = nodes.last!
			}
			(lastFifo as! DKNodeFifo).predicateOnInput = filter.predicate
			return DKFunctionGatherFromFifo(uniquingTable, nodes.count - 1, t)
		} else if let comp = fun as? DKFunctionComposition {
			// First apply inner
			let genInner = generate(comp.inner, &nodes)
			if (genInner is DKFunctionGatherFromFifo) && comp.outer.isInputGroupable {
				// Instead of composing the functions, we specify that the last Fifo gathers
				let t = (genInner.signature.output as! DKTypeSequence).sub
				addFifo(t)	// we ignore for now the (trivial) result
				return generate(comp.outer, &nodes)
			} else {
				let genOuter = generate(comp.outer, &nodes)
				return DKFunctionComposition(outer: genOuter, inner: genInner)
			}
		} else if let map = fun as? DKFunctionMap {
			if !(nodes.last! is DKNodeFifo) {
				let t = map.inputItemType
				addFifo(t)
			}
			(nodes.last! as! DKNodeFifo).compose(outer: map.each)
			if map.each is DKFunctionLogger {
				// No point in returning anything
				return map.each
			}
			return DKFunctionGatherFromFifo(uniquingTable, nodes.count - 1, map.each.signature.output)
		} else {
			let prev = DKFunctionGatherFromFifo(uniquingTable, nodes.count - 1, nodes.last!.itemType)
			return DKFunctionComposition(outer: fun, inner: prev)
		}
	}
	var flowGraphToJSON: JSON {
		let r = generate()
		for i in r.nodes.indices {
			assert(r.nodes[i].graphIndex == i)
		}
		var dict: [String: JSON] = [
			"nodes": .array(r.nodes.map { $0.nodeToJSON(uniquingTable) }),
			"generator": gen.functionToJSON,
			"fun": fun.functionToJSON,
			"last_fun": r.lastFunc.functionToJSON
		]
		// we do the table last, in case something got added there
		dict["types"] = uniquingTable.typeTableAsJSON
		return .dictionary(dict)
	}
}
