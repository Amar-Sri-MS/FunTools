#!/usr/bin/env python3

import tkinter as tk
import time
import json
import dpc_client

total_chunks = 0
active_cn = 100000000
transit_cn = 100000000
next_cn = 100000000
active_color = 'green'
transit_color = 'blue'
next_color = 'yellow'
no_color = 'white'

def run_test():
  client.execute_command('async', 'epnvme_test');

def update_chunks(stats):
  global total_chunks
  global active_cn
  global transit_cn
  global next_cn
  # Reset previous colors
  if active_cn < total_chunks:
	chunks[active_cn].configure(bg = no_color)
  if transit_cn < total_chunks:
	chunks[transit_cn].configure(bg = no_color)
  if next_cn < total_chunks:
	chunks[next_cn].configure(bg = no_color)
  # Set new colors
  active_cn = stats['active_cn']
  if active_cn < total_chunks:
  	chunks[active_cn].configure(bg = active_color)
  transit_cn = stats['transit_cn']
  if transit_cn < total_chunks:
  	chunks[transit_cn].configure(bg = transit_color)
  next_cn = stats['next_cn']
  if next_cn < total_chunks:
  	chunks[next_cn].configure(bg = next_color)

def update_stats():
  def get_stats():
	global total_chunks
	lsvstats = client.execute_command('peek', 'stats/lsv/0');
	if lsvstats is None:
		msg_label.configure(text = "No stats available", fg = 'red')
	else:
		msg_label.configure(text = "Got stats", fg = 'green')
		total_chunks = lsvstats['total_chunks']
	  	cc_value.configure(text = str(total_chunks)) 
	  	read_value.configure(text = str(lsvstats['reads'])) 
	  	write_value.configure(text = str(lsvstats['writes'])) 
		cpb_value.configure(text = lsvstats['chunks_per_bucket'])
		update_chunks(lsvstats)
	root.after(2000, get_stats);
  get_stats()

client = dpc_client.DpcClient()
client.set_verbose()

nextrow = 0
chunks = []

root = tk.Tk()
root.grid()
root.title("Log Structured Volume Demo")

button = tk.Button(root, text='Start', width=10, command=run_test)
button.grid(row = nextrow)
nextrow += 1

msg_label = tk.Label(root, text="Status: Connected", fg = 'green')
msg_label.grid(row = nextrow, column = 0)
nextrow += 1

cc_label = tk.Label(root, text="Chunk Count")
cc_label.grid(row = nextrow, column = 0)
cc_value = tk.Label(root, width = 10)
cc_value.grid(row = nextrow, column = 1)
nextrow += 1

read_label = tk.Label(root, text="Read Count")
read_label.grid(row = nextrow, column = 0)
read_value = tk.Label(root, width = 10)
read_value.grid(row = nextrow, column = 1)
nextrow += 1

write_label = tk.Label(root, text="Write Count")
write_label.grid(row = nextrow, column = 0)
write_value = tk.Label(root, width = 10)
write_value.grid(row = nextrow, column = 1)
nextrow += 1

cpb_label = tk.Label(root, text="Chunks Free Blocks Distribution")
cpb_label.grid(row = nextrow, columnspan = 2, column = 0)
cpb_value = tk.Label(root)
cpb_value.grid(row = nextrow, columnspan = 2, column = 2)
nextrow += 1

chunk_label = tk.Label(root, text="Chunk Usage:", width = 10)
chunk_label.grid(row = nextrow, column = 0)
active_label = tk.Label(root, text="Active", bg = active_color, width = 10)
active_label.grid(row = nextrow, column = 1)
transit_label = tk.Label(root, text="Transit", bg = transit_color, width = 10)
transit_label.grid(row = nextrow, column = 2)
next_label = tk.Label(root, text="Next", bg = next_color, width = 10)
next_label.grid(row = nextrow, column = 3)
nextrow += 1

for i in range(10):
	chunks.append(tk.Label(root, text="Chunk " + str(i), width = 10))
#	chunks[i].pack(side = tk.LEFT)
	chunks[i].grid(row = nextrow, column = 0)
	nextrow += 1

button = tk.Button(root, text='Quit', width=10, command=root.destroy)
button.grid(row = nextrow)

update_stats()
root.mainloop()
