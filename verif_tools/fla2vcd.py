#!/usr/bin/env python3
import os,sys,code
import rlcompleter, readline
import argparse
import re
from vcd import VCDWriter

SIG_P1 = re.compile(r"^(\S+)\[(\d+):(\d+)]")
SIG_P2 = re.compile(r"^(\S+)\b")
SIG_P3 = re.compile("\.")

def proc_file():
    sig_name=[]
    sig_list=[]
    sig_lsb=[]
    sig_mask=[]
    cur_lsb=64
    mf=open(args.mf,'r')
    for l in mf:
        if '[' in l:
            m=SIG_P1.match(l)
            w=int(m.group(2)) -  int(m.group(3)) + 1
            s=m.group(1)
            s2=SIG_P3.split(s)
            path=".".join(s2[:-1])
            sig=s2[-1]
            if args.debug:
                print("path=%s sig=%s width=%0d"%(path,sig,w))

        else:
            s=l.rstrip()
            s2=SIG_P3.split(s)
            path=".".join(s2[:-1])
            sig=s2[-1]
            w=1
            if args.debug:
                print("path=%s sig=%s width=1"%(path,sig))
        var=writer.register_var(path,sig,'reg',size=w)
        sig_name.append(path+"."+sig)
        sig_list.append(var)
        cur_lsb=cur_lsb-w
        sig_lsb.append(cur_lsb)
        sig_mask.append((1<<w)-1)

    df=open(args.df,'r')
    time=0
    for l in df:
        val=int(l.rstrip(),16)
        for i in range(len(sig_list)):
            v2=(val>>sig_lsb[i])&sig_mask[i]
            if args.debug:
                print("time=%0d %s=0x%0x"%(time,sig_name[i],v2))
            writer.change(sig_list[i],time,v2)
        time+=1
        
################################################################################
def proc_arg():
    global args
    global writer
    parser = argparse.ArgumentParser()
    parser.add_argument('-mf', nargs='?', type=str, default='map.txt', help='Mapping file. Default %(default)s')
    parser.add_argument('-df', nargs='?', type=str, default='data.txt', help='Data file. Default %(default)s')
    parser.add_argument('-of', nargs='?', type=str, default='out.vcd', help='Output file. Default %(default)s')
    parser.add_argument('-debug', action='store_true', help='Debug. Default %(default)s')
    args = parser.parse_args()
    writer=VCDWriter(open(args.of,'w'), timescale='1 ns', date='today')

def main():
    proc_arg()
    proc_file()

if (__name__ == "__main__"):
    main()
