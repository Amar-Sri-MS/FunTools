#!/usr/bin/env python3
import pickle
import os
import sys
import collections

from bottle import request
from bottle import route
from bottle import run
from bottle import template
from bottle import static_file

# import models/vp_util
abs_app_dir_path = os.path.dirname(os.path.realpath(__file__))
abs_models_path = os.path.join(abs_app_dir_path, 'models')
sys.path.append(abs_models_path)
import vp_util

job_root = "data/jobs/"

@route('/')
def default():
    return template("list.tpl", jobs=os.listdir(job_root))

@route('/favicon.ico')
def static():
    return static_file('favicon.ico', root="static")

@route('/static/<name>')
def static(name):
    return static_file(name, root="static")

@route('/<job_id>')
def index(job_id):
    opt = get_query_opt(job_id=job_id)
    pd = get_pd(opt.job_id)
    return template("main.tpl", opt=opt, debug_build=pd.debug_build)

@route('/<job_id>/samples')
@route('/<job_id>/samples/<wu>')
def show_wus(job_id, wu=None):
    opt = get_query_opt(job_id=job_id, wu=wu)
    return show_samples(opt, wu=wu)

@route('/<job_id>/frames')
@route('/<job_id>/frames/<frame>')
def show_frames(job_id, frame=None):
    opt = get_query_opt(job_id=job_id, frame=frame)
    return show_samples(opt, frames_only=True)

@route('/<job_id>/vp/<vp>')
def show_wus(job_id, vp):
    opt = get_query_opt(job_id=job_id, vp=vp)
    return show_samples(opt, vp=vp)

@route('/<job_id>/util')
@route('/<job_id>/util/<vp>')
def show_util(job_id, vp=None):
    opt = get_query_opt(job_id=job_id, vp=vp)
    pd = get_pd(opt.job_id)
    rows = util.vp_util(opt, pd)
    sort_rows(opt, rows)
    return template("util.tpl", opt=opt, rows=rows)
    
def get_k_percentile(rows, sort_by, k):
    rows.sort(lambda x,y: cmp(x[sort_by], y[sort_by]))
    num_rows = len(rows)
    if k < 2:
        return rows
    if num_rows == 0:
        return rows
    if num_rows < k:
        dummy_row = [""] * len(rows[0])
        res = [dummy_row] * (k + 1)
        res[0] = rows[0]
        res[-1] = rows[-1]
        for i in range(1, num_rows - 1):
            j = int((i * 1.0 / (num_rows - 1)) * (k + 1))
            res[j] = rows[i]
        return res
    res = []
    res.append(rows[0])
    for i in range(1, k):
        inx = i * num_rows / k
        res.append(rows[inx])
    res.append(rows[-1])
    return res

@route('/<job_id>/wu_list')
@route('/<job_id>/wu_list/<colname>')
def show_wu_list(job_id, colname=None):
    opt = get_query_opt(job_id=job_id)
    if opt.sort_by is None:
        opt.sort_by = 0
        opt.sort_invert = True

    row_hdr = get_pd(opt.job_id).rows[0]
    menu_cols = row_hdr[3:] if len(row_hdr) > 3 else []
    hdr = ["count", "wu"]
    if colname:
        k = 10 # at 10% each
        hdr.append("low")
        for i in range(1, k):
            pct = i * 100 / k
            hdr.append("%s%%" % pct)
        hdr.append("high")
        col = row_hdr.index(colname)
        func = lambda n,rows: [len(rows), n] + [r[col] for r in get_k_percentile(rows, col, k)]
    else:
        func = lambda n,rows: [len(rows), n]
    rows = group_by(opt, "wu", func)
    rows.insert(0, hdr)
    return template("wu_list.tpl", opt=opt, rows=rows, menu_cols=menu_cols)


def show_samples(opt, wu=None, frames_only=False, vp=None):
    rows = get_rows(opt, wu, frames_only, vp)
    return template("samples.tpl", opt=opt, rows=rows)

class QueryOpt(object):
    def __init__(self):
        self.sort_by = None
        self.sort_invert = False
        self.show_all = False
        self.show_max = 25
        self.from_row = 0
        self.vp = None
        self.wu = None
        self.frame = None
        self.path = request.urlparts.path
        self.query = request.urlparts.query

    def replace_query(self, **kwargs):
        parts = [p for p in self.query.split("&") if p]
        for k,v in list(kwargs.items()):
            parts = [p for p in parts if not p.startswith(k + "=")]
            if v is not None:
                parts.append("%s=%s" % (k, v))
        return "&".join(parts)

    def is_wustack(self, arg0):
        return self.wustack_start <= arg0 < self.wustack_end

def get_query_opt(**kwargs):
    opt = QueryOpt()
    if request.query.sort_by:
        opt.sort_by = int(request.query.sort_by)
    if request.query.sort_invert:
        opt.sort_invert = bool(int(request.query.sort_invert))
    if request.query.show_all:
        opt.show_all = bool(int(request.query.show_all))
    if request.query.from_row:
        opt.from_row = int(request.query.from_row)
    if request.query.vp:
        opt.vp = int(request.query.vp)
    if request.query.show_max:
        opt.show_max = int(request.query.show_max)
        if opt.show_max <= 0:
            opt.show_max = 1000*1000
    for k,v in list(kwargs.items()):
        setattr(opt, k, v)
    return opt

job_to_perf_data = {}

class PerfData(object):
    pass

def read_pd_from_file(fname):
    with open(fname, "r") as f:
        pd = pickle.load(f)
    assert pd.rows[0][0] == "timestamp"
    vp_to_rows = collections.defaultdict(list)
    assert pd.rows[0][1] == "vp"
    for r in pd.rows[1:]:
        vp_to_rows[r[1]].append(r)
    assert pd.rows[0][3] == "cycles"
    new_rows = []
    for vp, rows in vp_to_rows.items():
        new_rows.append(rows[0] + ("unknown",))
        for i in range(1, len(rows)):
            dispatch_time = rows[i][0] - rows[i-1][0]
            dispatch_cycles = dispatch_time*16/10
            dispatch_cycles -= rows[i-1][3]
            new_rows.append(rows[i] + (dispatch_cycles,))
    new_rows.sort(cmp=lambda x,y: cmp(x[0], y[0]))
    new_rows.insert(0, pd.rows[0] + ("dispatch_cycles",))
    pd.rows = new_rows

    return pd

def get_pd(job_id):
    pd = job_to_perf_data.get(job_id)
    if not pd:
        fname = os.path.join(job_root, job_id, "perf.data")
        pd = read_pd_from_file(fname)
        job_to_perf_data[job_id] = pd
    return pd

def sort_rows(opt, rows):
    if opt.sort_by is not None:
        sort_by = opt.sort_by
        if not opt.sort_invert:
            c = lambda x,y: cmp(x[sort_by], y[sort_by])
        else:
            c = lambda x,y: cmp(y[sort_by], x[sort_by])
        rows.sort(cmp=c)
    return rows

def get_rows(opt, wu, frames_only, vp):
    pd = get_pd(opt.job_id)

    opt.wustack_start = pd.wustack_start
    opt.wustack_end = pd.wustack_end

    header = pd.rows[0]
    rows = pd.rows[1:]

    if vp is not None:
        assert header[1] == "vp", header
        rows = [r for r in rows if r[1] == vp]
    if wu:
        assert header[2] == "wu", header
        rows = [r for r in rows if r[2] == wu]
    if frames_only:
        assert header[8] == "arg0", header
        rows = [r for r in rows if pd.wustack_start <= r[8] < pd.wustack_end]
    if opt.frame:
        arg0 = int(opt.frame, 16)
        assert pd.wustack_start <= arg0 < pd.wustack_end, (pd.wustack_start, arg0, pd.wustack_end)
        assert len(opt.frame) == 16
        prefix = int(opt.frame,16) >> 12
        assert header[8] == "arg0", header
        rows = [r for r in rows if prefix == (r[8] >> 12)]

    sort_rows(opt, rows)
    return [header] + rows

def group_by(opt, col, operate_fn):
    pd = get_pd(opt.job_id)
    header = pd.rows[0]
    rows = pd.rows[1:]

    assert col in header
    i = header.index(col)

    groups = collections.defaultdict(list)
    for r in rows:
        groups[r[i]].append(r)
    result = []
    for k,rows in list(groups.items()):
        result.append(operate_fn(k, rows))
    sort_rows(opt, result)
    return result

###
##  so we can act as a library
#
if (__name__ == "__main__"):
    if (len(sys.argv) == 2):
        job_root = sys.argv[1]
        print("Using job root %s" % job_root)

    run(host='0.0.0.0', port=8585, debug=True)
