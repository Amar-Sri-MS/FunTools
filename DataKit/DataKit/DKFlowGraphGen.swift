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
	func addFifoNode(_ t: DKType) {
		let fifo = DKNodeFifo(label: nodes.count, itemType: t)
		nodes |= fifo
	}
	var gatherFromLast: DKFunction {
		return DKFunctionGatherFromNode(uniquingTable, nodes.last!)
	}
	// Generate takes the node graph we have so far and a function to compute
	// and transforms it into a more complex node graph but a simpler function
	func generate(_ fun: DKFunction) -> DKFunction {
		switch fun {
		case let filter as DKFunctionFilter:
			return generateForFilter(filter)
		case let comp as DKFunctionComposition:
			return generateForComposition(comp)
		case let map as DKFunctionMap:
			return generateForMap(map)
		case let reduce as DKFunctionReduce:
			return generateForReduce(reduce)
		case let compress as DKFunctionCompress:
			return generateForCompress(compress)
		default:
			print("Falling into default case for node graph generation with \(fun)")
			if nodes.last is DKNodeReduce {
				let reduceNode = nodes.last as! DKNodeReduce
				print("We compose the result of reduce node: \(reduceNode) with outer fun: \(fun) [A]")
				reduceNode.compose(outer: fun)
				return gatherFromLast
			} else if nodes.last is DKNodeFifo {
				let prev = gatherFromLast
				return DKFunctionComposition(outer: fun, inner: prev)
			} else {
				fatalErrorNYI()
			}
		}
	}
	func generateForFilter(_ filter: DKFunctionFilter) -> DKFunction {
		// If the last node is a fifo and does not have a filter yet, we add it to that node
		// else we insert a fifo
		var lastFifo = nodes.last!
		let t = filter.itemType
		let appliesPredicate = (lastFifo is DKNodeFifo) && !(lastFifo as! DKNodeFifo).hasDefaultBehavior
		if !(lastFifo is DKNodeFifo) || appliesPredicate {
			// make a new fifo
			addFifoNode(t)
			lastFifo = nodes.last!
		}
		assert((lastFifo as! DKNodeFifo).predicateOnInput == nil)
		(lastFifo as! DKNodeFifo).predicateOnInput = filter.predicate
		return gatherFromLast
	}
	func generateForComposition(_ comp: DKFunctionComposition) -> DKFunction {
		// First apply inner
		let genInner = generate(comp.inner)
		if (genInner is DKFunctionGatherFromNode) && ((genInner as! DKFunctionGatherFromNode).valueType is DKTypeSequence) && comp.outer.isInputGroupable {
			// Instead of composing the functions, we specify that the last Fifo gathers - this is an optimization
			let t = ((genInner as! DKFunctionGatherFromNode).valueType as! DKTypeSequence).sub
			addFifoNode(t)	// we ignore for now the (trivial) result
			return generate(comp.outer)
		} else if (genInner is DKFunctionGatherFromNode) && nodes.last is DKNodeReduce {
			let reduceNode = nodes.last as! DKNodeReduce
//			print("We compose the result of reduce node: \(reduceNode) with outer fun: \(comp.outer) [B]")
			reduceNode.compose(outer: comp.outer)
			return gatherFromLast
		} else {
			// We actually compose the values
			// That means gathering all items of a sequence
			let s = genInner is DKFunctionGatherFromNode ? (genInner as! DKFunctionGatherFromNode).valueType.description : "Not_a_gather"
			print("Will gather values coming for \(genInner) to apply \(comp.outer) genInner.value=\(s)")
			// THIS IS PROBABLY BOGUS
			return DKFunctionComposition(outer: comp.outer, inner: genInner)
		}
	}
	func generateForMap(_ map: DKFunctionMap) -> DKFunction {
		// We make sure we come out of a fifo
		if !(nodes.last! is DKNodeFifo) {
			let t = map.inputItemType
			addFifoNode(t)
		}
		(nodes.last! as! DKNodeFifo).compose(outer: map.each)
		if map.each is DKFunctionLogger {
			// No point in returning anything
			return map.each
		}
		return gatherFromLast
	}
	func generateForReduce(_ reduce: DKFunctionReduce) -> DKFunction {
		// We make sure we come out of a fifo
		if !(nodes.last! is DKNodeFifo) {
			let t = reduce.inputItemType
			addFifoNode(t)
		}
		let node = DKNodeReduce(label: nodes.count, reduce: reduce)
		nodes |= node
		return gatherFromLast
	}
	func generateForCompress(_ compress: DKFunctionCompress) -> DKFunction {
		assert(compress.signature.numberOfArguments == 1)
		let inputType = compress.signature.input[0]
		if !(nodes.last! is DKNodeFifo) {
			assert(inputType is DKTypeSequence)
			let itemType = (inputType as! DKTypeSequence).sub
			addFifoNode(itemType)
		}
		let node = DKNodeCompressor(label: nodes.count, compress: compress)
		nodes |= node
		return gatherFromLast
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
		let graph = generate().graph
		var dict: [String: JSON] = [:]
		graph.flowGraphToJSONDict(&dict)
		return .dictionary(dict)
	}
}
