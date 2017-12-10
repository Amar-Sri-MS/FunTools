//
//  DKFlowGraphGen.swift
//  DataKit
//
//  Created by Bertrand Serlet on 9/13/17.
//  Copyright © 2017 Fungible. All rights reserved.
//

class DKFlowGraph {
	let uniquingTable: DKTypeTable
	var nodes: [DKNode]
	init(_ uniquingTable: DKTypeTable, _ generator: DKNodeGenerator) {
		self.uniquingTable = uniquingTable
		nodes = [generator]
	}
	func optimize() -> Bool {
		// Currently, this optimization is pointless
		if nodes.count < 2 { return false }
		for i in 1 ..< nodes.count - 1 {
			if let fifo = nodes[i] as? DKNodeFifo {
				if let next = nodes[i+1] as? DKNodeFifo {
					if fifo.hasDefaultBehavior && next.predicateOnInput == nil {
						print("Optimize away fifo #\(i)")
						nodes.remove(at: i)
						_ = optimize() // try again
						return true
					}
				}
			}
		}
		return false
	}
	func generate(_ fun: DKFunction) -> DKFunction {
		func addFifo(_ t: DKType) {
			let fifo = DKNodeFifo(label: nodes.count, itemType: t)
			nodes |= fifo
		}
		func addReduceNode(_ r: DKFunctionReduce) {
			let node = DKNodeReduce(label: nodes.count, reduce: r)
			nodes |= node
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
			let genInner = generate(comp.inner)
			if (genInner is DKFunctionGatherFromFifo) && comp.outer.isInputGroupable {
				// Instead of composing the functions, we specify that the last Fifo gathers
				let t = (genInner.signature.output as! DKTypeSequence).sub
				addFifo(t)	// we ignore for now the (trivial) result
				return generate(comp.outer)
			} else if (genInner is DKFunctionGetFromReduceNode) {
				// We just compose the value coming from inner to outer
				return DKFunctionComposition(outer: comp.outer, inner: genInner)
			} else {
				let genOuter = generate(comp.outer)
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
		} else if let reduce = fun as? DKFunctionReduce {
			if !(nodes.last! is DKNodeFifo) {
				let t = reduce.inputItemType
				addFifo(t)
			}
			addReduceNode(reduce)
			return DKFunctionGetFromReduceNode(uniquingTable, nodes.count - 1, reduce.outputType)
		} else {
			if nodes.last is DKNodeReduce {
				let reduceNode = nodes.last as! DKNodeReduce
				reduceNode.compose(outer: fun)
				return DKFunctionGetFromReduceNode(uniquingTable, nodes.count - 1, fun.signature.output)
			} else if nodes.last is DKNodeFifo {
				let prev = DKFunctionGatherFromFifo(uniquingTable, nodes.count - 1, nodes.last!.itemType)
				return DKFunctionComposition(outer: fun, inner: prev)
			} else {
				fatalErrorNYI()
			}
		}
	}
	func flowGraphToJSONDict(_ dict: inout [String: JSON]) {
		for i in nodes.indices {
			assert(nodes[i].graphIndex == i)
		}
		dict["nodes"] = .array(nodes.map { $0.nodeToJSON(uniquingTable) })
		// we do the table last, in case something got added there
		dict["types"] = uniquingTable.typeTableAsJSON
	}
}

class DKFlowGraphGen {
	let uniquingTable: DKTypeTable
	let fun: DKFunction
	let maker: DKFunction
	let max: Int
	init(_ uniquingTable: DKTypeTable, _ maker: DKFunction, _ max: Int, _ fun: DKFunction) {
		// We check the function takes 1 argument compatible with the generator
		// And produces no output
		// As we would not know what to do with the output
		assert(fun.signature.numberOfArguments == 1)
		assert(fun.signature[0] == maker.signature.output.makeSequence)
		assert(fun.signature.output == DKType.void)
		self.uniquingTable = uniquingTable
		self.maker = maker
		self.max = max
		self.fun = fun
	}
	func generate() -> (graph: DKFlowGraph, lastFunc: DKFunction) {
		let generator = DKNodeGenerator(graphIndex: 0, maker: maker, max: max)
		let graph: DKFlowGraph = DKFlowGraph(uniquingTable, generator)
		let lastFunc: DKFunction = graph.generate(fun)
		let opt = graph.optimize()
		if opt {
			print("Fifo optimized, now: \(graph.nodes)")
		}
		return (graph, lastFunc)
	}
	var flowGraphToJSON: JSON {
		let (graph, lastFunc) = generate()
		var dict: [String: JSON] = [
			"fun": fun.functionToJSON,
			"last_fun": lastFunc.functionToJSON
		]
		graph.flowGraphToJSONDict(&dict)
		return .dictionary(dict)
	}
}
