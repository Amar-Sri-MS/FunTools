#!/usr/bin/python

# shard and unshard HBM memory images

import sys
import struct

###
##  helpers
#

def red_xor(x):
    x = (x>>16) ^ x
    x = (x>>8)  ^ x
    x = (x>>4)  ^ x
    x = (x>>2)  ^ x
    x = (x>>1)  ^ x
    x &= 1
    return x


# constants
H0=0x001
H1=0x002
H2=0x180
H3=0x240
H4=0x028
H5=0x410
H6=0x000
H7=0x004

CH_SWIZZLE= 1
HBM_MODE = 4

CHNUMS = [2, 3, 6, 7, 0, 1, 4, 5, 10, 11, 14, 15, 8, 9, 12, 13]

def addr2shard(addr, shard_list):
    shard = addr & 3
    saddr = addr >> 2

    qsn_0 = red_xor(H0 & saddr)
    qsn_1 = red_xor(H1 & saddr)

    qn_1 = red_xor(H2 & saddr)
    qn_2 = red_xor(H3 & saddr)
    qn_3 = red_xor(H4 & saddr)
    qn_4 = red_xor(H5 & saddr)
    qn_5 = red_xor(H6 & saddr)
    qn_6 = red_xor(H7 & saddr)
        
    qsys_num = (qsn_1 << 1) | qsn_0
    qsys_num = qsys_num + shard * 4

    if (CH_SWIZZLE):
        assert(qsys_num >= 0)
        assert(qsys_num <= 15)
        ch_num = CHNUMS[qsys_num]
    else:
        ch_num = qsys_num

    row = (saddr >> 11) & 0x3fff
    col = (saddr & 0xf0) >> 1
    bank = (qn_4 << 3) | (qn_3 << 2) | (qn_2 << 1) | qn_1

    sid = 0
    pseudo_chan = qn_6
    ch_num2 = (pseudo_chan * 16) + ch_num

    assert((pseudo_chan == 0) or (pseudo_chan == 1))
    assert(ch_num >= 0)
    assert(ch_num <= 15)
        
    ch_addr = (bank << 21) | (row << 7) | col

    # print ch_num2

    return (ch_addr, shard_list[ch_num2])

def open_shard_files(prefix, mode):

    files = []
    for j in range(2):
        for i in range(16):
            fname = "%s.ch%s_pc%s" % (prefix, i, j)
            fl = open(fname, mode)
            # print fname
            files.append(fl)

    return files

###
##  unshard
#

# input line format is xx001122334455667788
IN_BYTES_PER_LINE = 8

# read n lines at a time
IN_LINE_BATCH = 8

# so we can seek around the file
IN_LINE_LEN = 2*9 + 1

# wrap the <address, file handle> in a class so we can make sure we're
# writing consistently
class InFile:
    def __init__(self, fh, base_addr=0):
        self.fh = fh
        self.base_addr = base_addr

    def read_address_words(self, address):

        address -= self.base_addr

        # compute a line number
        lno = address / IN_BYTES_PER_LINE
        faddr = lno * IN_LINE_LEN
        self.fh.seek(faddr)

        l = []
        for i in range(IN_LINE_BATCH):
            line = self.fh.readline()
            if (line == ""):
                return None
            
            # take the junk off the front and newline off the end
            line = line[2:-1]

            # convert it straight to an int
            val = int(line, 16)

            # print shex
            l.append(val)

        return l
            
        
def unshard(prefix):

    # open the input files
    flist = open_shard_files(prefix, 'r')
    
    # turn them into a list of InFiles
    infiles = []
    for fl in flist:
        print "parsing a file"
        infiles.append(InFile(fl))

    # open the output file
    fname = "%s-hbmdump.bin" % prefix
    hfl = open(fname, "w")

    address = 0
    bs = ""
    while (True):

        (baseAddr, fh) = addr2shard(address, infiles)

        # read a line
        words = fh.read_address_words(baseAddr)

        # exit on EOF
        if (words is None):
            print "EOF reached accessing addres 0x%x" % address
            break

        # split the line into nyble pairs (skipping the first dead one)
        for word in words:
        
            # turn that into a string of raw bytes
            sbytes  = struct.pack('Q', word)
            assert(len(sbytes) == IN_BYTES_PER_LINE)
        
            bs += sbytes
        
            # next address
            address += IN_BYTES_PER_LINE

        # progress marker
        if ((address % (1<<20)) == 0):
            hfl.write(bs)
            bs = ""

        if ((address % (1<<30)) == 0):
            sys.stdout.write("%s" % address >> 30)
            sys.stdout.flush()
        elif ((address % (1<<20)) == 0):
            sys.stdout.write(".")
            sys.stdout.flush()

        if (address > (1<<24)):
            sys.exit(1)
            
###
##  shard
#

def shard(hexname):

    # open the input to make sure it's there first
    fl = open(hexname)
    
    # make all the output files
    outfiles = open_shard_files(hexname, 'w')
    
    for line in fl.readlines():
        assert(line[0] == "@")
        line = line[1:]
        (addr, val) = line.split()
        addr = int(addr, 16)

        (baseAddr, fh) = addr2shard(addr, outfiles)
        
        # split the input value into 8B strings
        wA = [ val[i*16:(i+1)*16] for i in range(8) ]

        fh.write("@%07x %s\n" % (baseAddr+0, wA[3]))
        fh.write("@%07x %s\n" % (baseAddr+1, wA[2]))
        fh.write("@%07x %s\n" % (baseAddr+2, wA[1]))
        fh.write("@%07x %s\n" % (baseAddr+3, wA[0]))

        fh.write("@%07x %s\n" % (baseAddr+4, wA[7]))
        fh.write("@%07x %s\n" % (baseAddr+5, wA[6]))
        fh.write("@%07x %s\n" % (baseAddr+6, wA[5]))
        fh.write("@%07x %s\n" % (baseAddr+7, wA[4]))
        
        
###
##  command-line parsing
#

def main():

    if (len(sys.argv) != 3):
        print "usage: %s -s hexfile" % sys.argv[0]
        print "       %s -u prefix" % sys.argv[0]
        sys.exit(1)

    op = sys.argv[1]
    fname = sys.argv[2]

    if (op == "-s"):
        shard(fname)
    elif (op == "-u"):
        unshard(fname)
    else:
        print "%s: unknown operation '%s'" % (sys.argv[0], op)
        sys.exit(1)
        
    return 0

###
##  entrypoint
#

if (__name__ == "__main__"):
    sys.exit(main())
