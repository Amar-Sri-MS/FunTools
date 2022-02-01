#!/usr/bin/python3

import sys
import subprocess
import json
import time
import os

dpcsh_path = os.getenv('DPCSH', 'dpcsh')

def dpcsh_cmd(cmd):
  cmd = [dpcsh_path, '-Q', cmd]
  output = subprocess.check_output(cmd)
  j_output = json.loads(output)
  return j_output['result']

def vp_usage_info():
  data = dpcsh_cmd('peek stats/funtop/vp_usage')
  res = {}
  for (clstr, clstr_v) in data.items():
    for (core, core_v) in clstr_v.items():
      for (vp, vp_v) in core_v.items():
        ccv = '%s.%s.%s' % (clstr.split('_')[1], core.split('_')[1], vp.split('_')[1])
        v = vp_v['usage_percent']
        if v:
          res[ccv] = v
  return (res, data)

def top_wu_info():
  data = dpcsh_cmd('debug top_wus 200 100 0.001 0 false')
  res = {}
  for d in data:
    (faddr, ccv) = d['VP'].split(']')[0].split('[')
    ccv = ccv.replace('CCV', '')
    vp_v = { 'wu_list' : {} }
    vp_v['faddr'] = faddr
    for w in d['top_wus']:
      wu = w['WU']
      del w['WU']
      vp_v['wu_list'][wu] = w
    res[ccv] = vp_v
  return res

def top_wu_info_delta(res1, res2, vp_info):
  res = {}
  for (ccv, vp_v1) in res1.items():
    vp_v2 = res2.get(ccv, None)
    if not vp_v2:
      continue
    vp_v = dict(vp_v1)
    vp_v['wu_list'] = {}
    top_wu = vp_v['wu_list']
    tot_usecs = 0
    for (wu, w1) in vp_v1['wu_list'].items():
      w2 = vp_v2['wu_list'].get(wu, None)
      if not w2:
        continue
      count_diff = w2['count'] - w1['count']
      usecs_diff = w2['sum_usecs'] - w1['sum_usecs']
      tot_usecs += usecs_diff
      if count_diff:
        w = dict(w2)
        w['count_diff'] = count_diff
        w['usecs_diff'] = usecs_diff
        top_wu[wu] = w
    if len(top_wu):
      res[ccv] = vp_v
      vp_v['vp_percent'] = vp_info[0].get(ccv, 0)
    for (wu, w) in vp_v['wu_list'].items():
      w['wu_percent'] = int(w['usecs_diff'] * vp_v['vp_percent'] / tot_usecs)
      w['avg_nsecs']  = int(w['usecs_diff'] * 1000 / w['count_diff'])
  return res

def top_wu_sort_vp_count_diff(data, group_by_vp=False):
  tbl = []

  if group_by_vp:
    vp_per = {ccv:vp_v['vp_percent'] for (ccv, vp_v) in data.items()}
    ccv_list = sorted(vp_per, key=vp_per.get, reverse=True)
  else:
    ccv_list = data.keys()

  for ccv in ccv_list:
    vp_v = data[ccv]
    vp_res = []
    for (wu, w) in vp_v['wu_list'].items():
      r = [vp_v['faddr'], ccv, vp_v['vp_percent'], w['wu_percent'], wu, w['count_diff'], w['usecs_diff'], w['avg_nsecs']]
      vp_res.append(r)
    vp_res = sorted(vp_res, key=lambda e: e[6], reverse=True)
    if group_by_vp:
      for v in vp_res[1:]:
        v[0] = ''
        v[1] = ''
        v[2] = ''
    tbl += vp_res

  if group_by_vp:
    tbl = [r for r in tbl if r[3] > 0]
  else:
    tbl = sorted(tbl, key=lambda e: e[6], reverse=True)

  hdr = ['VP', 'FADDR', 'VP%', 'WU%', 'WU', '+count', '+usecs', 'avg_nsecs']
  return (tbl, hdr)

import curses

class MyCurses:
  def __init__(self):
    self.group_by_vp = False
    self.fmt = '{0[0]:<10} {0[1]:<6} {0[2]:>3} {0[3]:>3}  {0[4]:<40} {0[5]:>15} {0[6]:>15} {0[7]:>15}'

    self.cur_line = 0
    self.start_row = 0
    self.start_col = 0

    self.scr = curses.initscr()

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)

    # hide cursor
    try:
      curses.curs_set(0)
    except:
      pass
    # don't echo character input
    curses.noecho()
    self.scr.keypad(True)
    self.scr.clear()

    self.w1 = self.scr

  def group_toggle(self):
    self.group_by_vp = not self.group_by_vp
    self.start_row = 0
    self.start_col = 0
    self.cur_line = 0

  def fit_line(self, s, shift=False, fill=False):
    scol = self.start_col if shift else 0
    if fill: 
      s += ' ' * (scol + self.num_cols - 2 - len(s))
    s = s[scol:scol + self.num_cols - 2]
    return s

  def update_top_summary(self, top_summary):
    self.num_rows, self.num_cols = self.scr.getmaxyx()
    self.scr.move(0, 0)

    self.top_summary = top_summary
    for s in self.top_summary:
      s = s[:self.num_cols] + '\n'
      self.w1.addstr(s)

    # 1 line tbl hdr, 1 line for status
    self.wu_win_n = self.num_rows - len(self.top_summary) - 2
    if self.cur_line > self.wu_win_n:
      self.cur_line = self.wu_win_n

  def update_hdr_line(self, hdr):
    s = self.fmt.format(tuple(hdr))
    s = self.fit_line(s, shift=True, fill=True)
    self.w1.addstr(s + ' \n', curses.color_pair(1))

  def update_status_bar(self, s):
    self.w1.move(self.num_rows - 1,0)
    self.w1.move(self.num_rows - 1, 0)
    #s += '\t\t%s (%s %s) %s/%s %s' % (self.cur_line, self.start_row, self.start_col, self.wu_win_n, self.wu_n, len(self.wu_tbl))
    s = self.fit_line(s, fill=True)
    self.w1.insstr(s, curses.color_pair(1))

  def refresh_wu_tbl(self):
    end_row = min(self.start_row + self.wu_win_n, self.wu_n)
    wu_tbl = self.wu_tbl[self.start_row:end_row]
    n = len(wu_tbl)
    self.cur_line = min(self.cur_line, n - 1)

    for i in range(n):
      self.w1.move(i + len(self.top_summary) + 1,0)
      s = wu_tbl[i]
      if i == self.cur_line:
        s = self.fit_line(s, shift=True, fill=True) + ' \n'
        self.w1.addstr(s, curses.color_pair(2))
      else:
        s = self.fit_line(s, shift=True) + '\n'
        self.w1.addstr(s)

    self.scr.clrtobot()

  def update_wu_tbl(self, res):
    wu_tbl = [self.fmt.format(tuple(r)) for r in res]
    self.wu_tbl = wu_tbl
    self.wu_n = len(self.wu_tbl)
    self.refresh_wu_tbl()

  def handle_key_input(self, ch):
    if ch == curses.KEY_UP:
      if self.cur_line == 0:
        self.start_row = max(self.start_row - 1, 0)
      else:
        self.cur_line -= 1
      assert self.cur_line >= 0 and self.cur_line <= self.wu_win_n - 1
      return True
    if ch == curses.KEY_PPAGE:
      for i in range(self.wu_win_n):
        self.handle_key_input(curses.KEY_UP)
      return True

    if ch == curses.KEY_DOWN:
      if self.cur_line == self.wu_win_n - 1:
        if self.start_row + self.cur_line < self.wu_n - 1:
          self.start_row = self.start_row + 1
      else:
        self.cur_line += 1
      assert self.cur_line >= 0 and self.cur_line <= self.wu_win_n - 1
      return True
    if ch == curses.KEY_NPAGE:
      for i in range(self.wu_win_n):
        self.handle_key_input(curses.KEY_DOWN)
      return True

    if ch == curses.KEY_LEFT:
      self.start_col = max(self.start_col - 5 , 0)
      return True

    if ch == curses.KEY_RIGHT:
      self.start_col = min(self.start_col + 5 , self.num_cols - 1)
      return True
    return False

def vp_info_to_tbl(vp_info):
  res = []
  for (clstr, clstr_v) in vp_info[1].items():
    clstr_s = '  {0:<6}:'.format(clstr.replace('cluster_', 'clstr'))
    for (core, core_v) in clstr_v.items():
      core_s = ''
      for (vp, vp_v) in core_v.items():
        core_s += '{0:>2} '.format(vp_v['usage_percent'])
      clstr_s +=' [{0:<11}]'.format(core_s[:-1])
    res.append(clstr_s)
  res = [''] + res + ['']
  return res

def display_curses(mc, res, hdr, vp_info):
  w1 = mc.scr
  t1 = time.time()

  top_summary = vp_info_to_tbl(vp_info)
  status_str = 'q:quit\tg:group-toggle'

  while True:
    # top summary
    mc.update_top_summary(top_summary)
    # vp/wu header
    mc.update_hdr_line(hdr)
    # vp/wu list
    mc.update_wu_tbl(res)
    # status bar
    mc.update_status_bar(status_str)
    # and finally refresh
    mc.scr.refresh()

    while (True):
      t2 = time.time()
      t_rem = int((t1 + 1 - t2) * 10)
      if (t_rem <= 0):
        return True
      # nonblocking getch
      curses.halfdelay(t_rem)

      try:
        ch = mc.scr.getch()
      except:
        curses.endwin()
        return False
      if ch != curses.ERR:
        if ch < 256:
          if chr(ch) in ['q', 'Q']:
            # Finally go back to the terminal for real
            curses.endwin()
            return False
          if chr(ch) in ['g', 'G']:
            mc.group_toggle()
            return True

        if mc.handle_key_input(ch):
          break
          
  return True

def main(argv):
  mc = MyCurses()

  res1 = top_wu_info()
  time.sleep(1)
  while True:
    res2 = top_wu_info()
    vp_info = vp_usage_info()
    res = top_wu_info_delta(res1, res2, vp_info)
    (res, hdr) = top_wu_sort_vp_count_diff(res, mc.group_by_vp)
    ret = display_curses(mc, res, hdr, vp_info)
    if ret == False:
      break
    res1 = res2

if __name__ == '__main__':
  main(sys.argv)

