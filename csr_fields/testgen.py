#!/usr/bin/python

import random
import sys

# bits per word
BPW = 64

# maximum number of registers to generate
NREGS = 5

###
##  wrap random functionality
#

def rand(min, max):
    return random.randint(min, max)

def randbit():
    return rand(0, 1)

def randbitstring(n):
    return [randbit() for x in range(0, n)]

###
##  convert a bitstring into a register
#

def bits2words(bits, zerofill=False):

    # make a fresh copy of the list
    bits = list(bits)

    if (len(bits) > NREGS * BPW):
        raise "list already too long!"

    # pad the list randomly to word size, unless it's already full add
    # a whole extra register if we're too short, unless we're the full
    # length. padding is good for detecting bugs, and simplifies the
    # integer conversion.
    if (len(bits) != NREGS * BPW):
        n = len(bits) % BPW
        n = 64 - n

        if (zerofill):
            bits += [0] * n
        else:
            bits += randbitstring(n)
        
    # convert to a series of numbers
    words = []
    while(len(bits)):
        word = 0
        for idx in range(0, BPW):
            word |= bits[0] << idx
            del(bits[0])
        words.append(word)
    
    return words


def aprint(xs):
    return "".join(["0x%x, " % x for x in xs])


###
##  stamp a field over a register
#

def bitstring_update(in_regbit, in_fld, fld_pos):

    out = list(in_regbit)
    
    for i in in_fld:
        out[fld_pos] = i
        fld_pos += 1
        
    return out

###
##  read test generation
#


def gen_read_test(max_bits):

    # struct read_test {
    #	unsigned reg_size;
    #	unsigned fld_size;
    #	unsigned fld_pos;
    #	uint64_t in_reg[NREGS];
    #	uint64_t out_fld[NREGS];
    # };

    reg_size = rand(1, max_bits - 1)
    fld_pos = rand(0, reg_size - 1)
    fld_size = rand(1, reg_size - fld_pos)
    
    # generate a random bit string of that length
    regbits = randbitstring(reg_size)

    # extract the bits that would be output
    outbits = regbits[fld_pos:fld_pos+fld_size]

    # convert to words
    inwords = bits2words(regbits)
    outwords = bits2words(outbits, True)
    
    print "{ %s, %s, %s, { %s}, { %s} }," % (reg_size, fld_size, fld_pos, aprint(inwords), aprint(outwords))

    
###
##  write test generation
#


def gen_write_test(max_bits):

    # struct write_test {
    #	unsigned reg_size;
    #	unsigned fld_size;
    #	unsigned fld_pos;
    #	uint64_t in_reg[NREGS];
    #	uint64_t in_fld[NREGS];
    #	uint64_t out_reg[NREGS];
    # };

    reg_size = rand(1, max_bits - 1)
    fld_pos = 0 # rand(0, reg_size - 1)
    fld_size = rand(1, reg_size - fld_pos)
    
    # generate a random bit string of that length that we're updating
    in_regbits = randbitstring(reg_size)

    # generate a random bit string of the field we're updating
    in_fld = randbitstring(fld_size)

    # combine them to make the the expected output value
    out_reg = bitstring_update(in_regbits, in_fld, fld_pos)
    
    # convert to words
    inregwords = bits2words(in_regbits, True)
    infldwords = bits2words(in_fld)
    outwords = bits2words(out_reg, True)
    
    print "{ %s, %s, %s, { %s}, { %s}, { %s} }," % (reg_size, fld_size, fld_pos, aprint(inregwords), aprint(infldwords), aprint(outwords))
    
###
##  Entrypoint
#

if (__name__ == "__main__"):

    random.seed()
    count = 0

    if (len(sys.argv) == 1):
        count = 1000
    elif (len(sys.argv) == 2):
        count = int(sys.argv[1])

    if (count == 0):
        print "usage: testgen.py [test-count]"
        sys.exit(1)

    print "/* auto generated csr field tests: %s */" % sys.argv
    print "#ifdef AUTO_READ"
    for i in range(0, count):
        gen_read_test(NREGS * BPW)
    print "#endif /* AUTO_READ */"

    print "#ifdef AUTO_WRITE"
    for i in range(0, count):
        gen_write_test(NREGS * BPW)
    print "#endif /* AUTO_WRITE */"
