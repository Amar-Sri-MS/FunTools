//
//  SimulationSamples.swift
//
//  Created by Bertrand Serlet on 12/29/15.
//  Copyright © 2016 Fungible Inc. All rights reserved.
//

// Record samples
// The model is that time starts at 0
// samples are recorded at always increasing (or equal) dates
// When there are too many samples, the earlier samples get scaled
// Client can also request scaling the samples

protocol SimulationScaledSamples: class {
    // enables avoiding redisplay when nothing changed
    var generation: Int { get }
    // Number of samples (grouped by scale)
    var numScaledSamples: Int { get }
    // Copy of all the scaled samples.  The API makes a copy in order to be thread safe.  Not guaranteed to match numScaledSamples
    func copyAllScaledSamples() -> [SimulationSamples.RangeAndAvg]
    // Overall range, either specified initially, or grown automatically
    var overallRange: ClosedRange<Double>? { get }
    // Actual range.  May be contained in overallRange, when overallRange is specified; or equal to spanningRange when automatic
    var range: ClosedRange<Double>? { get }
    var averageValue: Double { get }
    var lastValue: Double { get }
    var title: String { get }
    var titleExtras: (SimulationScaledSamples) -> String { get set }
    // Request to increase the scale
    func compress(_ factor: Int)
    func toJSON() -> JSON // Return JSON.null when none
}

extension SimulationScaledSamples {
    var minValue: Double { return range?.lowerBound ?? 0.0 }
    var maxValue: Double { return range?.upperBound ?? 0.0 }
}

class SimulationSamples: SimulationScaledSamples, CustomStringConvertible {
    struct RangeAndAvg {
        var range: ClosedRange<Double>?
        var avg: Double
        init(range: ClosedRange<Double>?, avg: Double) {
            self.range = range
            self.avg = avg
        }
        func add(_ other: RangeAndAvg) -> RangeAndAvg {
            if range == nil { return other }
            if other.range == nil { return self }
            return RangeAndAvg(range: range!.addBounds(other.range!), avg: avg + other.avg)
        }
        func toJSON() -> JSON {
            // We often have the same values so we compress that simply
            if range == nil {
                return JSON.array([])
            } else if range!.lowerBound == range!.upperBound && range!.upperBound == avg {
                return JSON.real(avg)
            } else {
                return JSON.array([
                    JSON.real(range!.lowerBound),
                    JSON.real(range!.upperBound),
                    JSON.real(avg)
                    ])
            }
        }
        init(fromJSON json: JSON) {
            switch json {
                case .real(let x):
                    range = x ... x
                    avg = x
                default:
                    let a = json.arrayValue
                    if a.count == 3 {
                        range = a[0].doubleValue ... a[1].doubleValue
                        avg = a[2].doubleValue
                    } else {
                        range = nil
                        avg = 0.0
                    }
            }
        }
    }

    var compressSamplesThreshold = 1000 // when more than 1000 individual samples force a compression
    var generation = 0
    var mutable = true
    let auto: Bool
    let title: String
    var titleExtras: (SimulationScaledSamples) -> String
    private var spanningRange: ClosedRange<Double>?

    fileprivate let lock = Lock()
    fileprivate var past = PastValues() // values since start + past.countScaled
    fileprivate var recent = RecentValues() // samples not yet compressed

    /*=============== PUBLIC ===============*/

    init(title t: String, range: ClosedRange<Double>, _ titleExtras: @escaping (SimulationScaledSamples) -> String) {
        // Assume all samples are within given range
        assert(range.upperBound >= range.lowerBound)
        auto = false; spanningRange = range
        title = t
        self.titleExtras = titleExtras
    }
    init(title t: String, _ titleExtras: @escaping (SimulationScaledSamples) -> String) {
        // samples resize themselves
        auto = true
        spanningRange = nil
        title = t
        self.titleExtras = titleExtras
    }
    func record(_ date: Int, value: Double) {
        assert(date >= 0) // samples start always at 0
        if !mutable { return }
        lock.apply {
            recordNoLock(date, value: value)
            if past.count > compressSamplesThreshold {
                compressNoLock(2)
            }
        }
    }
    var scale: Int {
        return lock.apply { past.scale }
    }
    var numScaledSamples: Int {
        return lock.apply {
            past.count + (recent.isEmpty ? 0 : 1)
        }
    }
    func copyAllScaledSamples() -> [RangeAndAvg] {
        return lock.apply {
            return recent.isEmpty ? past.pastValues : past.pastValues + [recent.toRangeAndAvg]
        }
    }
    func compress(_ factor: Int) {
        lock.apply { compressNoLock(factor) }
    }
    var overallRange: ClosedRange<Double>? {
        return lock.apply { spanningRange }
    }
    var range: ClosedRange<Double>? {
        // Actual range.  May be contained in overallRange, when overallRange is specified; or equal to spanningRange when automatic
        return lock.apply { rangeNoLock }
    }
    var averageValue: Double {
        return lock.apply { averageValueNoLock }
    }
    var lastValue: Double {
        return lock.apply { recent.lastValue }
    }
    var mostRecentDate: Int {
        return lock.apply { past.countScaled + recent.numRecentValues - 1 }
    }
    func extendTo(_ date: Int) {
        let lastValue = lock.apply { recent.lastValue }
        record(date, value: lastValue)
    }
    var description: String {
        return "Samples [\(past.countScaled)+\(recent.numRecentValues)] range=\(range!) avg=\(averageValue)"
    }
    func toJSON() -> JSON {
        var dict: [String: JSON] = [:]
        if auto && spanningRange != nil {
            dict["min"] = JSON.real(spanningRange!.lowerBound)
            dict["max"] = JSON.real(spanningRange!.upperBound)
        }
        dict["past"] = past.toJSON()
        dict["recent"] = recent.toJSON()
        return JSON.dictionary(dict)
    }
    func restoreFromJSON(_ json: JSON) {
        let dict = json.dictionaryValue
        if dict["min"] != nil && dict["max"] != nil {
            spanningRange = dict["min"]!.doubleValue ... dict["max"]!.doubleValue
        }
        past = PastValues(fromJSON: dict["past"]!)
        recent = RecentValues(fromJSON: dict["recent"]!)
        mutable = false
    }

    /*=============== PRIVATE ===============*/

    private func recordNoLock(_ date: Int, value: Double) {
        generation += 1
        var adjusted = value
        if auto {
            // We ajust our current overall range
            if spanningRange == nil {
                spanningRange = value ... value
            } else {
                spanningRange = spanningRange!.union(value)
            }
        } else if spanningRange != nil {
            // we put a floor or ceiling on the value
            adjusted = spanningRange!.clampValueWithin(value)
        }
        let lastDate = past.countScaled + recent.numRecentValues - 1
        var offsetFromLast = date - lastDate
        if date < lastDate {
            // ignore that sample from the past
            return
        }
        recent.check(past.scale)
        if date == lastDate {
            // we are just replacing the last date
            recent.replaceLast(adjusted)
            return
        }
        while date - past.countScaled >= past.scale {
            // We need to add a scaled sample
            let complement = past.scale - recent.numRecentValues // number of samples to add
            recent.repeatLast(complement)
            past.addSample(recent.rangeAndSum)
            recent.reset()
            offsetFromLast -= complement
        }
        assert(offsetFromLast > 0)
        let toBeAutoFilled = Int(offsetFromLast - 1)
        assert(toBeAutoFilled >= 0)
        recent.repeatLast(toBeAutoFilled)
        if past.countScaled + recent.numRecentValues == date {
            recent.addANewValue(value)
        }
        if recent.numRecentValues == past.scale + 1 {
            past.addSample(recent.allButLastSample)
            recent.removeAllButLastSample()
        } else {
            assert(recent.numRecentValues <= past.scale)
        }
        recent.check(past.scale)
    }
    private func compressNoLock(_ factor: Int) {
        assert(factor >= 2)
        generation += 1
        if past.count == 0 && recent.isEmpty {
            past.scale *= factor
            return
        }
        recent.check(past.scale)
	var newNumRecentValues = recent.numRecentValues
	var newRangeAndSum = recent.rangeAndSum
        past.compress(factor, numRecentValues: &newNumRecentValues, rangeAndSum: &newRangeAndSum)
	recent.numRecentValues = newNumRecentValues
	recent.rangeAndSum = newRangeAndSum
        recent.check(past.scale)
    }
    private var rangeNoLock: ClosedRange<Double>? {
        if recent.rangeAndSum.range == nil {
            return past.pastRangeAndSum.range
        }
        if past.pastRangeAndSum.range == nil {
            return recent.rangeAndSum.range!
        }
        return past.pastRangeAndSum.range!.union(recent.rangeAndSum.range!)
    }
    private var averageValueNoLock: Double {
        let n = past.countScaled + recent.numRecentValues
        if n == 0 { return 0 }
        let sumValues = past.pastRangeAndSum.sum + recent.rangeAndSum.sum
        let avg = sumValues / Double(n)
        // We can have floating point errors that accumulate, so we force the avg to stay below max
        let r = rangeNoLock
        if r == nil { return avg }
        return r!.clampValueWithin(avg)
    }

    /*=============== PRIVATE SUBTYPES ===============*/

    fileprivate struct RangeAndSum {
        var range: ClosedRange<Double>? = nil
        var sum: Double = 0.0
        init() {}
        init(range: ClosedRange<Double>?, sum: Double) {
            self.range = range; self.sum = sum
        }
        func toRangeAndAvg(_ scale: Int) -> RangeAndAvg {
            return RangeAndAvg(range: range, avg: sum / Double(scale))
        }
        mutating func addInPlace(_ other: RangeAndSum) {
            range = range == nil ? other.range : (other.range == nil ? range : range!.union(other.range!))
            sum += other.sum
        }
        mutating func add1InPlace(_ value: Double) {
            range = range == nil ? value ... value : range!.union(value)
            sum += value
        }
        mutating func addRepeatedInPlace(_ r: RangeAndAvg, scale: Int) {
            range = range == nil ? r.range : (r.range == nil ? range! : range!.union(r.range!))
            sum += r.avg * Double(scale)
        }
        mutating func forceSumWithin(_ numValues: Int) {
            if range == nil { return }
            let scaled = range!.scale(Double(numValues))
            sum = scaled.clampValueWithin(sum)
        }
        func toJSON() -> JSON {
            // We often have the same values so we compress that simply
            if range == nil {
                return JSON.array([])
            } else if range!.lowerBound == range!.upperBound && range!.upperBound == sum {
                return JSON.real(sum)
            } else {
                return JSON.array([
                    JSON.real(range!.lowerBound),
                    JSON.real(range!.upperBound),
                    JSON.real(sum)
                    ])
            }
        }
        init(fromJSON json: JSON) {
            switch json {
            case .real(let x):
                range = x ... x
                sum = x
            default:
                let a = json.arrayValue
                if a.count == 3 {
                    range = a[0].doubleValue ... a[1].doubleValue
                    sum = a[2].doubleValue
                }
            }
        }
    }
    fileprivate struct PastValues {
        // values corresponding to start ..< start + past.countScaled
        var scale: Int = 1
        var pastValues: [RangeAndAvg] = []
        // We also maintain min, max and sum for pastValues
        var pastRangeAndSum = RangeAndSum()
        var count: Int { return pastValues.count }
        var countScaled: Int { return pastValues.count * scale }
        init() {}
        mutating func addSample(_ sample: RangeAndSum) {
            pastValues |= sample.toRangeAndAvg(scale)
            pastRangeAndSum.addInPlace(sample)
            // to avoid floating point errors accumulating we max out
            pastRangeAndSum.forceSumWithin(countScaled)
        }
        mutating func compress(_ factor: Int, numRecentValues: inout Int, rangeAndSum: inout RangeAndSum) {
            let old = pastValues
            var new: [RangeAndAvg] = []
            for i in 0 ..< (old.count / factor) {
                var sum = 0.0
                var bounds: ClosedRange<Double>? = nil
                for j in i * factor ..< (i+1) * factor {
                    sum += old[j].avg
                    let oldr = old[j].range
                    if oldr != nil {
                        if bounds == nil {
                            bounds = oldr!
                        } else {
                            bounds = bounds!.union(oldr!)
                        }
                    }
                }
                let avg = sum / Double(factor)
                new |= RangeAndAvg(range: bounds, avg: avg)
            }
            for j in (old.count / factor) * factor ..< old.count {
                let v = old[j]
                numRecentValues += scale
                rangeAndSum.addRepeatedInPlace(v, scale: scale)
            }
            pastValues = new
            scale *= factor
        }
        func toJSON() -> JSON {
            var dict: [String: JSON] = [:]
            dict["scale"] = JSON.integer(scale)
            let array: [JSON] = runLengthEncodedArray(pastValues.map { $0.toJSON() })
            dict["values"] = JSON.array(array)
            return JSON.dictionary(dict)
        }
        init(fromJSON json: JSON) {
            let dict = json.dictionaryValue
            scale = dict["scale"]!.integerValue
            pastValues = runLengthArrayDecoded(dict["values"]!.arrayValue).map { RangeAndAvg(fromJSON: $0) }
            // reestablish the cache
            for v in pastValues {
                let sample: RangeAndSum = RangeAndSum(range: v.range, sum: v.avg * Double(scale))
                pastRangeAndSum.addInPlace(sample)
            }
        }
    }
    fileprivate struct RecentValues {
        var numRecentValues = 0 // between 1 and scale (included), also can be 0 when no sample yet
        var lastValue = 0.0
        var rangeAndSum = RangeAndSum() // sum of all recent values, including lastValue
        var isEmpty: Bool { return numRecentValues == 0 }
        var toRangeAndAvg: RangeAndAvg {
            assert(numRecentValues != 0)
            return RangeAndAvg(range: rangeAndSum.range, avg: rangeAndSum.sum / Double(numRecentValues))
        }
        init() { }
        mutating func replaceLast(_ value: Double) {
            if rangeAndSum.range == nil {
                rangeAndSum.range = value...value
            } else {
                rangeAndSum.range = rangeAndSum.range!.union(value...value)
            }
            rangeAndSum.sum += value - lastValue  // adjust sum
            lastValue = value
        }
        mutating func repeatLast(_ num: Int) {
            numRecentValues += num
            rangeAndSum.sum += lastValue * Double(num)
        }
        mutating func reset() {
            numRecentValues = 0
            rangeAndSum = RangeAndSum(range: lastValue ... lastValue, sum: 0.0)
        }
        mutating func addANewValue(_ value: Double) {
            rangeAndSum.add1InPlace(value)
            numRecentValues += 1
            lastValue = value
        }
        var allButLastSample: RangeAndSum {
            let sum = rangeAndSum.sum - lastValue
            return RangeAndSum(range: rangeAndSum.range, sum: sum)
        }
        mutating func removeAllButLastSample() {
            numRecentValues = 1
            rangeAndSum = RangeAndSum(range: lastValue ... lastValue, sum: lastValue)
        }
        func check(_ scale: Int) {
            assert(numRecentValues >= 0 && numRecentValues <= scale)
        }
        func toJSON() -> JSON {
            var dict: [String: JSON] = [:]
            dict["num"] = JSON.integer(numRecentValues)
            dict["last"] = JSON.real(lastValue)
            dict["ras"] = rangeAndSum.toJSON()
            return JSON.dictionary(dict)
        }
        init(fromJSON json: JSON) {
            let dict = json.dictionaryValue
            numRecentValues = dict["num"]!.integerValue
            lastValue = dict["last"]!.doubleValue
            rangeAndSum = RangeAndSum(fromJSON: dict["ras"]!)
        }
    }
}

/*=============== SAMPLES COMBINING OTHER SAMPLES ===============*/

class SimulationCombinedSamples: SimulationScaledSamples, CustomStringConvertible {
    let subs: [SimulationSamples]
    let normalize: Bool
    init(subs: [SimulationSamples], normalize n: Bool) {
        // normalize means we divide by the number of subs
        assert(!subs.isEmpty)
        self.subs = subs
        normalize = n
    }
    var lastSubGenerations = [Int]()
    var lastGeneration = 0
    var generation: Int {
        let newGenerations = subs.map { $0.generation }
        if newGenerations == lastSubGenerations { return lastGeneration }
        lastSubGenerations = newGenerations
        lastGeneration += 1
        return lastGeneration
    }
    func compressAllAtSameScale() {
        let scale = subs.maximize( { $0.scale })!.maximum
        for sub in subs {
            while sub.scale < scale {
                sub.compress(2)
                assert(sub.scale <= scale) // must all be powers of 2
            }
        }
    }
    var numScaledSamples: Int {
        compressAllAtSameScale()
        return subs.maximize( { $0.numScaledSamples })!.maximum
    }
    var overallRange: ClosedRange<Double>? {
        let sum = subs.reduce(0.0 ... 0.0) {
            return $1.overallRange == nil ? $0 : $0.addBounds($1.overallRange!)
        }
        return normalize ? sum.scale(1.0 / Double(subs.count)) : sum
    }
    var range: ClosedRange<Double>? {
        let sum = subs.reduce(0.0 ... 0.0) {
            if $1.range == nil || $1.range!.isEmpty { return $0 } // this can happen for empty samples
            return $0.addBounds($1.range!)
        }
        return normalize ? sum.scale(1.0 / Double(subs.count)) : sum
    }
    var averageValue: Double {
        let sum = subs.reduce(0.0) { $0 + $1.averageValue }
        return normalize ? sum / Double(subs.count) : sum
    }
    var lastValue: Double {
        return subs[0].lastValue
    }
    var title: String {
        return subs.first!.title
    }
    var titleExtras: (SimulationScaledSamples) -> String {
        get {
            return subs.first!.titleExtras
        }
        set {
            fatalError()
        }
    }
    func compress(_ factor: Int) {
        subs.forEach { $0.compress(factor) }
    }
    func copyAllScaledSamples() -> [SimulationSamples.RangeAndAvg] {
        // First we compress what is not at the same compression level
        compressAllAtSameScale()
        // We extend all the subs not at the latest
        let maxMostRecentDate = subs.maximize( { $0.mostRecentDate })!.maximum
        if maxMostRecentDate < 0 { return [] } // empty
        for sub in subs {
            if sub.mostRecentDate != maxMostRecentDate {
                sub.extendTo(maxMostRecentDate)
//                assert(sub.mostRecentDate == maxMostRecentDate)
            }
        }
        if subs[0].numScaledSamples == 0 { return [] }
        // gather all the samples
        var sums: [SimulationSamples.RangeAndAvg] = []
        for sub in subs {
            let these = sub.copyAllScaledSamples()
            if sums.count == 0 {
                sums = these
            } else {
//                assert(these.count == sums.count)
                sums = zip(sums, these).map { $0.0.add($0.1) }
            }
        }
        if !normalize { return sums }
        let s = 1.0 / Double(subs.count)
        return sums.map { SimulationSamples.RangeAndAvg(range: ($0.range == nil ? nil : $0.range!.scale(s)), avg: $0.avg * s) }
    }
    var description: String {
        return "Samples from \(subs.count) units" + (normalize ? ", normalized" : "")
    }
    func toJSON() -> JSON { return JSON.null }
}

/*=============== MISC ===============*/

func runLengthEncodedArray(_ values: [JSON]) -> [JSON] {
    // values can not be dictionaries
    var coded: [JSON] = []
    var previous: JSON = JSON.null
    var times = 0
    for j in values {
        assert(!j.isDictionary)
        if times == 0 {
            previous = j
            times = 1
        } else if previous == j {
            times += 1
        } else if times == 1 {
            coded |= previous
            previous = j
        } else {
            coded |= JSON.dictionary(["\(times)": previous])
            previous = j
            times = 1
        }
    }
    if times == 0 {
    } else if times == 1 {
        coded |= previous
    } else {
        coded |= JSON.dictionary(["\(times)": previous])
    }
    return coded
}

func runLengthArrayDecoded(_ coded: [JSON]) -> [JSON] {
    var decoded = [JSON]()
    for j in coded {
        if j.isDictionary {
            let (key, value) = j.dictionaryValue.first!
            let times = key.toInt64(.JSON)!
            for _ in 0 ..< times {
                decoded |= value
            }
        } else {
            decoded |= j
        }
    }
    return decoded
}

/*=============== TEST ===============*/

func samplesTest() throws {
    var samples = SimulationSamples(title: "test", range: 0.0 ... 1.0) { _ in "" }
    for i: Int in 42 ..< 42 + 100 {
        samples.record(i, value: 17.0)
    }
    assert(samples.range!.lowerBound == 17.0)
    assert(samples.range!.upperBound == 17.0)
    assert(samples.averageValue == 17.0)
    assert(samples.numScaledSamples == 100)
    samples.compress(3)
    assert(samples.range!.lowerBound == 17.0)
    assert(samples.range!.upperBound == 17.0)
    assert(samples.averageValue == 17.0)
    assert(samples.numScaledSamples == 34)

    samples = SimulationSamples(title: "test", range: 0.0 ... 1.0) { _ in "" }
    for i: Int in 42 ..< 42 + 100 {
        samples.record(i, value: i % 2 == 0 ? 13.0 : 14.0)
    }
    assert(samples.range!.lowerBound == 13.0)
    assert(samples.range!.upperBound == 14.0)
    assert(abs(samples.averageValue - 13.5) <= 0.13 / 2.0)
    assert(samples.numScaledSamples == 100)

    samples = SimulationSamples(title: "test", range: 0.0 ... 1.0) { _ in "" }
    samples.past.scale = 2
    for i: Int in 42 ..< 42 + 100 {
        samples.record(i, value: i % 2 == 0 ? 13.0 : 14.0)
    }
    assert(samples.range!.lowerBound == 13.0)
    assert(samples.range!.upperBound == 14.0)
    assert(abs(samples.averageValue - 13.5) <= 0.13 / 2.0)
    assert(samples.numScaledSamples == 50)

    samples = SimulationSamples(title: "test", range: 0.0 ... 1.0) { _ in "" }
    samples.past.scale = 2
    samples.record(1, value: 1.0)
    samples.record(1, value: 2.0)
    assert(samples.range!.lowerBound == 1.0)
    assert(samples.range!.upperBound == 2.0)
    assert(samples.averageValue == 2.0)
    assert(samples.numScaledSamples == 1)
    samples.record(2, value: 2.0)
    assert(samples.range!.lowerBound == 1.0)
    assert(samples.range!.upperBound == 2.0)
    assert(samples.averageValue == 2.0)
    assert(samples.numScaledSamples == 1)
    samples.record(101, value: 2.0)
    assert(samples.range!.lowerBound == 1.0)
    assert(samples.range!.upperBound == 2.0)
    assert(samples.averageValue == 2.0)
    assert(samples.numScaledSamples == 51)

    print("Samples test done")
}
