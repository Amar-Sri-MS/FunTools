import collections

class Bucket(object):
    def __init__(self):
        self.idle = 0
        self.busy = 0

def vp_util(opt, pd):
    header = pd.rows[0]
    rows = pd.rows[1:]

    assert header[0] == "timestamp"
    assert header[1] == "vp"
    assert header[2] == "wu"
    assert header[3] == "cycles", header
    vp_bucket = collections.defaultdict(Bucket)
    for r in rows:
        if opt.vp and r[1] != opt.vp:
            continue

        is_idle = r[2] == "wuh_idle"

        start = r[0]
        end = start + (r[3]*2/16)*10

        bucket_no = r[0] / 1000000
        next_bucket = (bucket_no + 1) * 1000000

        while next_bucket <= end:
            if is_idle:
                vp_bucket[r[1], bucket_no].idle += next_bucket - start
            else:
                vp_bucket[r[1], bucket_no].busy += next_bucket - start
            start = next_bucket
            bucket_no += 1
            next_bucket += 1000000

        if is_idle:
            vp_bucket[r[1], bucket_no].idle += end - start
        else:
            vp_bucket[r[1], bucket_no].busy += end - start

    first_bucket = min(r[0] for r in rows) / 1000000
    last_bucket = max(r[0] for r in rows) / 1000000
    if opt.vp:
        vps = [opt.vp]
    else:
        vps = sorted(set(r[1] for r in rows))
    result = [("vp", "time_bucket", "utilization")]
    for vp in vps:
        for b in range(first_bucket, last_bucket+1):
            known = vp_bucket[vp, b].idle + vp_bucket[vp, b].busy
            assert known <= 1000000
            if known != 1000000:
                util = "known %s" % known
            else:
                used = vp_bucket[vp, b].idle
                util = (used * 1000) / 1000000
                util = "%s.%s" % (util/10, util%10)
            result.append((vp, b, util))
    return result
