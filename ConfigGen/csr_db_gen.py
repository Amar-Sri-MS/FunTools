#!/usr/bin/env python
import glob, os, sys, re, datetime
import getopt, platform, tempfile, re
from string import Template

input_base = ""
output_base = ""
csr_code_gen_out_base = ""
header_struct_declare_generated = 0

header = """
// AUTOGENERATED FILE - DO NOT EDIT
"""

# Dict for all CSR Registers per Ring
CSR_RING_REG_DB = {}
CSR_RING_REG_SCRATCHPAD_DB = {}
CSR_RING_REG_MODULE_ID_DB = {}
CSR_RING_REG_HOLES = { }
# Dict for the all CSR RING Base Addres
CSR_RING_DETAILS = {
	0x0 : ["F1_FIB_RING",  0x0000000000],
	0x1 : ["F1_PC_0_RING", 0x0800000000],
	0x2 : ["F1_PC_1_RING", 0x1000000000],
	0x3 : ["F1_PC_2_RING", 0x1800000000],
	0x4 : ["F1_PC_3_RING", 0x2000000000],
	0x5 : ["F1_PC_4_RING", 0x2800000000],
	0x6 : ["F1_PC_5_RING", 0x3000000000],
	0x7 : ["F1_PC_6_RING", 0x3800000000],
	0x8 : ["F1_PC_7_RING", 0x4000000000],
	0x9 : ["F1_CC_8_RING", 0x4800000000],
	0xA : ["F1_NU_0_RING", 0x5000000000],
	0xB : ["F1_NU_1_RING", 0x5800000000],
	0xC : ["F1_HU_0_RING", 0x6000000000],
	0xD : ["F1_HU_1_RING", 0x6800000000],
	0xE : ["F1_HU_2_RING", 0x7000000000],
	0xF : ["F1_HU_3_RING", 0x7800000000],
	0x10 : ["F1_HNU_0_RING", 0x8000000000],
	0x11 : ["F1_HNU_1_RING", 0x8800000000],
	0x12 : ["F1_MUH_0_RING", 0x9000000000],
	0x13 : ["F1_MUH_1_RING", 0x9800000000],
	0x14 : ["F1_MUD_0_RING", 0xa000000000],
	0x15 : ["F1_MUD_1_RING", 0xa800000000],
	0x16 : ["F1_MIO_0_RING", 0xb000000000],
	0x17 : ["F1_MIO_2_RING", 0xb800000000],
}

def generate_csr_reg_db():
    global CSR_RING_REG_HOLES
    global CSR_RING_REG_DB
    global CSR_RING_REG_MODULE_ID_DB
    global CSR_RING_REG_SCRATCHPAD_DB

    print("==== csr base addr header files ===")
    for slave_reg_file in glob.glob(input_base + "/*_an.h"):
        #print slave_reg_file
        # Open the file and parse line "AN_BASE_ADDR".
        # This is the base address for csr block
	fp = open(slave_reg_file, "r")
	for line in fp:
	    if len(line) == 0 or len(line) == 1:
    		continue
    	    #print line
    	    if line.rfind("AN_BASE_ADDR") >= 0:
    		# line found is #define FEP_LSNMUX_AN_BASE_ADDR          0x0882080000
    		# Parse the line
	    	an_base_addr = line.strip("\n").split()[2]
	    	#print an_base_addr
    		# Find the RING which this csr addr/reg belongs to
    		# For that walk through all the items of dict.
	    	for ring_id in CSR_RING_DETAILS:
	    	    ring_name, base_addr = CSR_RING_DETAILS[ring_id]
                    # Check the range. Cannot use range() as the
                    # memory requirement is huge.
                    if int(an_base_addr, 16) >= base_addr and int(an_base_addr, 16) < (base_addr + 0x800000000):
                        try:
                            a = CSR_RING_REG_DB[ring_name]
                            print('RING:%s FOUND SECOND TIME IN FILE:%s'%(ring_name, slave_reg_file))
                        except KeyError:
                            print('RING:%s FOUND FIRST TIME in FILE:%s'%(ring_name, slave_reg_file))
			    CSR_RING_REG_DB[ring_name] = []
			#Found the ring, break here. so that we can use the same var "ring_name"
			break
		# go and parse again
		continue
    	    if line.rfind("REG_BASE_ADDR") >= 0:
    		# line found is #define FEP_LSNMUX_AN_BASE_ADDR          0x0882080000
    		# Parse the line
	    	addr = line.strip("\n").split()[2]
	    	#print addr
                if addr.rfind("0x") < 0:
                    #print "Bad Line: ", addr
                    continue
                try:
                    #print 'Adding Ring:%s an_base_addr:%s addr:%s'%(ring_name, an_base_addr, addr)
                    if int(an_base_addr, 16) + int(addr, 16) in CSR_RING_REG_DB[ring_name]:
                        print('Ring:%s an_base_addr:%s addr:%s DUPLICATE FOUND File:%s'%\
                        (ring_name, an_base_addr, addr, slave_reg_file))
                        continue
	            CSR_RING_REG_DB[ring_name].append(int(an_base_addr, 16) + int(addr, 16))
	            # Check if the register is SCRATCHPAD, then add to scratchpad DB
                    if line.rfind("SCRATCHPAD_") >= 0:
                        CSR_RING_REG_SCRATCHPAD_DB[ring_name] = [int(an_base_addr, 16) + int(addr, 16)]
                    if line.rfind("MODULE_ID_") >= 0:
                        reg_addr = int(an_base_addr, 16) + int(addr, 16)
                        #Next line will be DFLT Value for ModID
                        #print 'MODULE ID REG BASE FOUND......'
                        next_line = next(fp)
                        #print 'NEXT LINE IS AFTER MODULE ID IS: ', next_line
                        if next_line.rfind("_DFLT") >= 0:
                            dflt_modid_val = re.sub('[{|}]', '', next_line.strip("\n").split()[3])
                            #print 'DFLT MOD ID: ', dflt_modid_val
                        try:
                            CSR_RING_REG_MODULE_ID_DB[ring_name].append((reg_addr, dflt_modid_val))
                        except KeyError:
                            CSR_RING_REG_MODULE_ID_DB[ring_name] = [(reg_addr, dflt_modid_val)]
                    """
                    print 'MODULE_ID_DB'
                    print CSR_RING_REG_MODULE_ID_DB[ring_name]
                    print 'MODULE_SCRATCH PAD_DB'
                    print CSR_RING_REG_SCRATCHPAD_DB[ring_name]
                    """
	        except KeyError:
                    print("ring_id:%d not found in CSR_RING_REG_DB"%(ring_id))
	        continue
	#close
	fp.close

    """
    # After parsing all the files, dump the DB
    for ring_name in CSR_RING_REG_DB:
        reg_list = CSR_RING_REG_DB[ring_name]
        print 'RING: %s'%(ring_name)
        for val in reg_list:
            print hex(val)
    sys.exit(2)
    """

    """
    for ring_name in CSR_RING_REG_DB:
        try:
            for (x,y) in sorted(CSR_RING_REG_MODULE_ID_DB[ring_name]):
                print "MODULE ID DB RING: %s: %s:%s"%(ring_name, hex(x), y)
        except KeyError:
            print "Ring ", ring_name, " ModuleID Reg Not Found"
    print 'MODULE_SCRATCH PAD_DB', CSR_RING_REG_SCRATCHPAD_DB
    print 'MODULE_ID_DB', CSR_RING_REG_MODULE_ID_DB
    for ring_name in CSR_RING_REG_DB:
        try:
            for x in sorted(CSR_RING_REG_SCRATCHPAD_DB[ring_name]):
                print "SCRATCHPAD DB RING: %s @%s"%(ring_name, hex(x))
        except KeyError:
            print "Ring ", ring_name, " ModuleID Reg Not Found"
    """
    #Pack the list into a struct of register ranges
    for ring_name in CSR_RING_REG_DB:
        reg_list = sorted(CSR_RING_REG_DB[ring_name])
        """
        print 'Total Registers Available in CSR RING:%s is %d'%(ring_name, len(reg_list))
        print [hex(x) for x in reg_list]
        """
        #calculate the differences between regiser addresses
        # Go through every index and create a tupe, which will have
        # (start_addr, end_addr) type tuple
        hole_found = False
        CSR_RING_REG_HOLES[ring_name] = []
        start_base = reg_list[0]
        temp_base = reg_list[0]
        for addr in reg_list[1:]:
            if temp_base + 0x8 == addr:
                temp_base = addr
                continue
            else:
                CSR_RING_REG_HOLES[ring_name].append((start_base, (temp_base + 0x8)))
                start_base = addr
                temp_base = addr
                #We found atleast one hole
                hole_found = True
        #This special case is for scenario when a CSR RING Has no Holes
        #So there will be only 1 Range Entry, which will be start to End
        if hole_found is False:
            #print 'Hurray one CSR Ring:%s has NO HOLES..'%(ring_name)
            CSR_RING_REG_HOLES[ring_name].append((reg_list[0], (reg_list[-1]+0x8)))
            #print reg_list, CSR_RING_REG_HOLES[ring_name]
        """
        print 'ALGO CSR HOLES'
        #Print all the entries
        for (start, end) in CSR_RING_REG_HOLES[ring_name]:
            print hex(start),hex(end)
        """
        #For each such range, we create a struct in the headerfile
	#Generate CSR Reg header file
	generate_csr_reg_header_code(CSR_RING_REG_HOLES[ring_name], ring_name)

def generate_csr_ring_reg_header_file(out_base, header_file, input_base, reg_range_list, ring_name):
    print("Generating csr reg db header file %s@%s\n"%(header_file, out_base))
    """
    print 'Printing the RING RANGES FOR RING: ', ring_name
    for (start, end) in reg_range_list:
        print hex(start),hex(end)
    """
    global header_struct_declare_generated
    if header_struct_declare_generated == 0:
        print("Generating disclaimer header file")
        fp = open(out_base + header_file, "w+")
        file_templ = Template('// Source file generated by ' + __file__ + ' at $date \n'\
                            '// Do not change this file\n')
        fp.write(file_templ.substitute(input_base=input_base,
                    date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
        # generate the structure as below
        # struct csr_ring_reg_range {
        #   uint64_t start_addr;
        #   uint64_t end_addr;
        # }
        #
        # struct csr_mod_id {
        #   uint64_t modid_addr;
        #   uint64_t modid_val;
        # }
        #
        # struct csr_ring_<ring_name>_reg_db {
        #   uint8_t ring_name[64];
        #   uint32_t entries;
        #   uint32_t modid_entries;
        #   uint64_t scratchpad_addr;
        #   struct csr_mod_id mod_id[M];
        #   struct csr_ring_reg_range range[N];
        # }
        print("Generating struct definition")
        fp.write("struct csr_ring_reg_range {")
        fp.write("\n")
        fp.write("\t uint64_t start_addr;")
        fp.write("\n")
        fp.write("\t uint64_t end_addr;")
        fp.write("\n")
        fp.write("};")
        fp.write("\n")
        fp.write("struct csr_mod_id {")
        fp.write("\n")
        fp.write("\t uint64_t modid_addr;")
        fp.write("\n")
        fp.write("\t uint64_t modid_val;")
        fp.write("\n")
        fp.write("};")
        fp.write("\n")
 
        # mark generated
        header_struct_declare_generated = 1
    else:
        #print 'Opening File in Append Mode'
        fp = open(out_base + header_file, "a")
    
    # Go to end of file
    fp.seek(fp.tell())
    # Count the number of range tuple entries. We need that many struct array
    array_size = len(reg_range_list)
    try:
        modid_size = len(CSR_RING_REG_MODULE_ID_DB[ring_name])
    except KeyError:
        print('Ring: ', ring_name, ' Has no ModuleID registers')
        modid_size = 0
    fp.write("struct csr_ring_"+ring_name.lower()+"_reg_db {")
    fp.write("\n")
    fp.write("\t uint8_t ring_name[64];")
    fp.write("\n")
    fp.write("\t uint32_t entries;")
    fp.write("\n")
    fp.write("\t uint32_t modid_entries;")
    fp.write("\n")
    fp.write("\t uint64_t scratchpad_addr;")
    fp.write("\n")
    fp.write("\t struct csr_ring_reg_range range["+str(array_size)+"];")
    fp.write("\n")
    fp.write("\t struct csr_mod_id mod_id["+str(modid_size)+"];")
    fp.write("\n")
    fp.write("};")
    fp.write("\n")
    print("Generating struct Initialization")
    # Static structure Init Code also needs to be generated
    # It will be like below
    #   struct csr_ring_<ring_name>_reg_db csr_ring_<ring_name> =
    #   {
    #       .name = <ring_name>
    #       .entries = <n>
    #       .range[0] = {x, y},
    #       ....
    #       .range[10] = {a,b},
    #   };
    fp.write("struct csr_ring_"+ring_name.lower()+"_reg_db " + "csr_ring_"+ring_name.lower() + " =")
    fp.write("\n")
    fp.write("{")
    fp.write("\n")
    fp.write("\t.ring_name = " + "\"" + ring_name.lower() + "\"" + ",")
    fp.write("\n")
    fp.write("\t.entries = " + str(len(reg_range_list)) + ",")
    fp.write("\n")
    try:
        fp.write("\t.scratchpad_addr = " + hex(CSR_RING_REG_SCRATCHPAD_DB[ring_name][0]) + ",")
    except KeyError:
        fp.write("\t.scratchpad_addr = 0x0,")
    fp.write("\n")
    """
    if modid_size == 0:
        fp.write("\t.modid_info_prsnt = 0,")
        fp.write("\n")
    else:
        fp.write("\t.modid_info_prsnt = 1,")
        fp.write("\n")
    """
    fp.write("\t.modid_entries = " + hex(modid_size) + ",")
    fp.write("\n")
    # Initialize the range array
    for i in range(0, len(reg_range_list)):
        (start, end) = reg_range_list[i]
        fp.write("\t.range["+str(i)+"] = {" + hex(start) + ", " + hex(end) + "},")
        fp.write("\n")
    # Initialize the modid array
    if modid_size > 0:
        for i in range(0, modid_size):
            (addr, val) = CSR_RING_REG_MODULE_ID_DB[ring_name][i]
            fp.write("\t.mod_id["+str(i)+"] = {" + hex(addr) + ", " + val + "},")
            fp.write("\n")
    else:
        print('Skipping ModId Array Initialization for Ring: ', ring_name)

    fp.write("};")
    fp.write("\n")
    fp.close()

def generate_csr_reg_header_code(csr_ring_reg_list, ring_name):
    header_file = "csr_cfg_ring_reg_db.h"
    generate_csr_ring_reg_header_file(csr_code_gen_out_base, header_file, input_base, csr_ring_reg_list, ring_name)

def Usage():
	sys.stderr.write('csr_db_gen.py: usage: [-i [csr *_an.h input dir] [-o csr regdb hdr output dir]\n')

def main():
        global output_base
        global input_base
        global csr_code_gen_out_base

	print("CSR Reg DB Generation")
	try:
            opts, args = getopt.getopt(sys.argv[1:], 'hi:o:s:')

	except getopt.GetoptError as err:
		print(str(err))
    		Usage()
    		sys.exit(2)

  	for o, a in opts:
    		if o in ('-h', '--help'):
      			Usage()
      			sys.exit(1)
    		elif o in ('-i', '--input'):
      			input_base = a
                        print("input dir: " + a)
    		elif o in ('-o', '--output'):
      			output_base = a
                        print("output dir: " + a)
                elif o in ('-s', '--src'):
                        csr_code_gen_out_base = a
                        #print 'CSR CODE GEN OUT:', csr_code_gen_out_base
    		else:
      			assert False, 'Unhandled option %s' % o

	#CSR Reg offset db build
	generate_csr_reg_db()

if __name__ == "__main__":
	main()
