#!/usr/bin/env python2.7
#
# parse_dasm.py: Parse disassembler contents to help build call graph
#
# This code parses MIPS disassembly in a simplistic way, and uses heuristics
# to build up a call graph of the original program.
#
# The data from this will be used by profiling tools using the Samurai
# trace data - which provides instruction and data traces from the
# processor or emulation.  The client of this code would be running through
# the trace, and whenever the PC changes to a different function, would
# ask for the kind of control flow baseed on the old and new address.
# The GetBranchKind function performs these queries.
# 
# To detect the branches correctly, this code needs to handle a couple of
# complications.  First, classic MIPS branches have the idea of a "forbidden"
# slot - that the instruction after the branch will be executed before the
# branch takes effect.  That means that an instruction sequence like:
# 0x1000: beqz 0x20000
# 0x1004: li t9, 0
#
# the instruction sequence would be 1000, 1004, 2000.  This code needs to
# recognize that the beqz means that the transition between functions would
# happen between address 0x1004 and 0x2000.
#
# Note that instructions ending in "C" (compact) don't have the forbidden word
# concept, and usually will jump from the same address.  Usually.
#
# The second problem is that the Samurai data is occasionally incorrect;
# instructions are sometimes missing, or wait instructions may have surprising
# results.  This code must handle such cases... or at least recover
# gracefully.
#
# This code doesn't care about local jumps within functions, but does
# need to handle recursive functions.  It also needs to handle jumps and calls
# to registers (function pointers).
from __future__ import print_function

import fileinput
import re
import sys


# Number of bytes per bucket for the page map.
# Making this smaller shortens the number of lookups to find
# the function at an address.
PAGE_SIZE_BITS = 10

# Branch instructions indicating straight jumps between functions.
# Branches always take an instruction to execute, so we'll see the PC 1 word
# after.
branch_instructions = ['b', 'beq', 'beqz',  'bgez', 'bgtz', 'blez',  
                       'bltz', 'bne', 'bnez',  'bc1eqz', 
                       'bc1nez', 'bc2eqz', 'bc2nez']

# Branch instructions indicating straight jumps between functions.
# Compact branches don't have the forbidden word and so we see the jump
# happening on the branch's address.
branch_instructions_no_offset = ['bc', 'beqc', 'beqzalc', 'beqzc', 'bgec',
                                 'bgeuc', 'bgezalc', 'bgezc', 'bgtc', 'bgtzc',
                                 'blezalc', 'blezc', 'bltc', 'bltuc', 'bltzc',
                                 'bnec', 'bnezc', 'bnvc', 'bnvuc', 'bovc',
                                 'bc1eqc']

# LDPC? LWUPC?  LWPC?
# TODO(bowdidge): JAL
# Explicit jumps.  BC is often used for tail calls.
jump_instructions = ['j', 'lapc']

# Explicit call instructions where last instruction seen is PC of the
# instruction itself.
# Note lapc is replacement for bltzal branch and link condition.' 
call_instructions = ['jal', 'bal']
call_instructions_compact = ['balc']

# Instructions performing a call to a register value,
# indicating a call via a function pointer.
# PC will be address + 4.
call_to_register_instructions = ['jalr']

# Instructions performing a call to a register value,
# indicating a call via a function pointer.
# PC will be address.
call_to_register_instructions_compact = ['jalrc']

# Instructions that indicate a function return.
# jr always visits the instruction immediately after the JR,
# so PC for return is offset by 4.
# 
# Register ra is usually used for plain returns.
#
# Exception: for some tail calls (such as the jumps to comparators in
# qsort_compare), ra t9 is used, and should be treated as a JUMP.
return_instructions = ['jr']

# Instructions that indicate a function return.
# jrc immediately handles the jump 
return_instructions_compact = ['jrc']

# Wait instructions are odd -- they get called, the after a delay an
# odd address appears, and eventually the instruction after the wait appears.
# Ignoring the odd instruction for now.
# Wait gets used in platform_vp_idle.
wait_instructions = ['wait']

# Any way to infer starting an exception?  Function name?
exception_instructions = [''] 

exception_return_instructions = ['eret']

def IsLocalSymbol(sym):
    """Returns true if the symbol should be treated as local to function.

    """
    if sym[0] == '.' or sym[0] == '$':
        return True
    # cache_on is symbol immediately after jalr.
    # TODO(bowdidge): Can we handle these another way?
    if sym in ['cache_on', 'cache_on_skip']:
        return True
    return False

class FunctionInfo(object):
    """Information on the function parsed from the disassembly."""
    
    def __init__(self, name, start_address):
        # Name of the function.
        self.name = name

        # Start and end address for the function.
        self.start_address = start_address
        self.end_address = 0

        # List of duplicate ranges for the symbol, if exists.
        self.other_ranges = []

        # List of calls made from the function.
        # This is a list of (address, instruction, called_symbol)
        self.calls = []


        # List of jumps made from the function to other functions.
        # This is a list of (address, instruction, called_symbol)
        self.jumps = []

        # List of returns from the function.
        # List of (address, instruction, arguments).
        self.returns = []

        # List of wait instructions in the function.
        self.waits = []

    def __str__(self):
        return ('<FunctionInfo: name:%s start:0x%x end:0x%x, %d other calls, '
                '%d calls, %d jumps, %d returns, %d waits>' % (
                self.name, self.start_address, self.end_address,
                len(self.other_ranges),
                len(self.calls), len(self.jumps), len(self.returns), 
                len(self.waits)))

    def AddCall(self, address, instruction, called_symbol):
        """ Remember a call from this function.
        
        address is integer value of address
        instruction is string name of MIPS instruction.
        called_symbol is where we're jumping to.
        """
        self.calls.append((address, instruction, called_symbol))

    def AddJump(self, address, instruction, called_symbol):
        """ Remember a call from this function.

        address is integer value of address
        instruction is string name of MIPS instruction.
        called_symbol is where we're jumping to.
        """
        self.jumps.append((address, instruction, called_symbol))

    def AddReturn(self, address, instruction, args):
        """Remember a place where there is a return from the function."""
        self.returns.append((address, instruction, args))

    def AddWait(self, address):
        """Remember a place where there is a wait instruction in function."""
        self.waits.append(address)

    def Dump(self):
        """Print out the FunctionInfo object in gory detail."""
        start_addr = self.start_address
        end_addr = self.end_address
        calls_str = ''
        duplicates_str = ''
        range_strings = ''
        if self.other_ranges:
            range_strings = ['0x%x-0x%x' % (start, end)for (start, end) in
                             self.other_ranges]
        duplicates_str = ('duplicates: %s' % range_strings)
            
        if self.calls:
                
            calls_str = ', '.join([symbol for (addr, instr, symbol) in
                                  self.calls if symbol])
        print('Function %s:\n' % self.name)
        print('  Range: 0x%x-0x%0x' % (start_addr, end_addr))
        if self.other_ranges:
            print('  Also seen at %s' % duplicates_str)
        # returns win over calls.
        if self.returns:
            for (addr, instr, args) in self.returns:
                print('  RET %x: %s %s' % (addr, instr, args))
        if self.calls:
            for (addr, instr, symbol) in self.calls:
                print('  CALL %x: %s %s' % (addr, instr, symbol))
        if self.jumps:
            for (addr, instr, symbol) in self.jumps:
                print('  JUMP %x: %s %s' % (addr, instr, symbol))
            print('  Calls: %s' % calls_str)
    
class DasmInfo(object):
    """Parses disassembly, and serves data about the disassembled program."""

    def __init__(self):
        # Map from symbol name to information to FunctionInfo.
        self.functions = {}

        # FunctionInfo for current symbol being read.
        self.current_function = None

        # Address of last line parsed.
        self.current_address = 0

        # Map storing all the functions in a page of memory.
        # The dictionary is actually a map from page address to list of
        # functions on that page, provided as triples of
        # (start_address, end_address,  function_info).
        self.page_map = {}

        # Counts for all the exceptional situations.
        self.missed_return = 0
        self.missed_jump = 0
        self.missed_call = 0
        self.missed1 = 0
        self.missed2 = 0

    def PrintMisses(self):
        # For one of Bertrand's traces (24M cycles), we saw
        # 6 missed returns, 5 missed jumps, 29 missed calls,
        # 7 missed1's, 0 missed2's.
        print('Missed returns: %d' % self.missed_return)
        print('Missed jumps: %d' % self.missed_jump)
        print('Missed calls: %d' % self.missed_call)
        print('Missed1: %d' % self.missed1)
        print('Missed2: %d' % self.missed2)

    def Read(self, contents):
        """Reads disassembly from a stream of data."""
        # Note we look for representative strings in the file to decide
        # whether it's a label, a branch or jump, or an arbitrary instruction.
        # We do this so we only do one expensive regex to parse each line.
        for line in contents:
            if '>:' in line:
                # Label at the start of a function.
                # address <symbol>:
                if self.ParseLabel(line):
                    # Match.
                    continue

            if '>' in line:
                # May contain a label.
                # address: instr args <label>
                if self.ParseReference(line):
                    # match.
                    continue
                
            if ':' in line:
                # Any other instruction.  Form is
                # address: instr args
                self.ParseInstruction(line)

        if self.current_function:
            self.current_function.end_address = self.current_address

        # Build up the page map after all functions have been parsed.
        for name in self.functions:
            function_info = self.functions[name]

            start_addr = function_info.start_address
            if not function_info.end_address:
                function_info.end_address = function_info.start_address
            end_addr = function_info.end_address

            self.PlaceFunction(function_info, start_addr, end_addr)

            if function_info.other_ranges:
                for (start, end) in function_info.other_ranges:
                    self.PlaceFunction(function_info, start, end)

    def GetBranchKindForAddr(self, last_func, last_addr, next_func, next_addr):
        """Determine what sort of branch caused the function to change.

        last_func: FunctionInfo for function before branch.
        last_addr: last address executed before switch to other function.
        next_func: FunctionInfo for function after branch.
        next_addr: first instruction executed in next instruction.

        Returns:
          IGNORE if not a branch.
          JUMP if code was a straight jump or tail call from a function.
          CALL if code was a subroutine call with an assumed return.
          RET if the code was a return from a subroutine.
          FALLTHROUGH if the code simply incremented into the next function.
          ROOT if the call should be the start of a new call tree.

        This function is supposed to be non-fuzzy, based on how we believe
        Samurai data should be set up.
        """
        if last_addr in last_func.waits:
            # Instructions after wait seem to have hiccups.
            return 'IGNORE'

        # Check returns first so we don't think we're looking at the
        # call.
        if last_func.returns:
            for (addr, instr, args) in last_func.returns:
                if last_addr == addr:
                    if 't9' in args:
                        # Tail call, such as those in qsort_compare.
                        # Might be distinguished from different register
                        return 'JUMP'
                    # Usually ra for straight return.
                    return 'RET'

        if last_func.calls:
            for (addr, instr, symbol) in last_func.calls:
                if last_addr == addr and symbol == next_func.name:
                    return 'CALL'
                elif last_addr == addr and symbol == None:
                    # Call to function pointer..
                    return 'CALL'

        if last_func.jumps:
            for (addr, instr, symbol) in last_func.jumps:
                if last_addr == addr and symbol == next_func.name:
                    return 'JUMP'

        if last_addr == next_addr - 4 and last_func != next_func:
            return 'FALLTHROUGH'

        return None

    def GetBranchKind(self, last_func_name, last_addr, next_func_name,
                      next_addr):
        """Determine what sort of branch caused the function to change.

        last_func_name: name of function executing before branch.
        last_addr: last instruction executed before switch to other function.
        next_func_name: name of function executing after branch.
        next_addr: first instruction executed after switch to next function.
 
        Returns:
          IGNORE if not a branch, and don't consider we're in a different
          function.
          JUMP if code was a straight jump or tail call from a function.
          CALL if code was a subroutine call with an assumed return.
          RET if the code was a return from a subroutine.
          FALLTHROUGH if the code simply incremented into the next function.
          ROOT if the call should be the start of a new call tree.

        This version of the function attempts to always give an answer, and
        works in the presence of missing or odd function sequences.
        """
        # TODO(bowdidge): Generalize idea of switching to new stack.
        if last_func_name == 'exit':
            if last_addr & 0xffffffff00000000 == 0xffffffff00000000:
                # kernel exit. reset start.
                return 'ROOT'

        if last_func_name == 'wu_dispatch_loop_asm_ns':
            return 'ROOT'

        # Those wacky build-the-stack-and-use-bc in parse_json_recursive.
        # These are tail calls.
        #if last_addr in [0x980000000012ae38,
        #                 0x980000000012adf4,
        #                 0x980000000012ad84,
        #                 0x980000000012abd8,
        #                 0x980000000012ab18]:
        #    return 'JUMP'
        
        last_func = self.GetFunctionInfo(last_func_name)
        next_func = self.GetFunctionInfo(next_func_name)

        if not last_func or not next_func:
            return None

        if last_func_name == next_func_name:
            # For recursive calls, watch for returns to the address after
            # the jump.  Otherwise it's not a recursive call, it's stepping
            # in the same function.
            for (addr, instr, symbol) in next_func.calls:
                if symbol == next_func_name:
                    if addr == last_addr:
                        return 'CALL'
                    elif addr + 4 == next_addr:
                        return 'RET'
            return 'IGNORE'

        ret = self.GetBranchKindForAddr(last_func, last_addr,
                                        next_func, next_addr)
        if ret:
            return ret

        # Bunch of heuristics for catching odd cases and missing
        # instructions.
        # TODO(bowdidge): Fuzzy?  Try ranking possibilities?

        # TODO(bowdidge): Count number of failures, kinds.

        # Did we lose an instruction near the return?
        if last_func.returns:
            for (addr, instr, args) in last_func.returns:
                if last_addr == addr - 4:
                    return 'RET'

        # Is next_addr - 4 a call?  Then we've got a return.
        # TODO(bowdidge): this is really strange - 
        for (addr, instr, symbol) in next_func.calls:
            if ((next_addr - 4 == addr or next_addr - 8 == addr) and
                (not symbol or symbol == last_func.name)):
                # Missed the return instruction, but we've got it.
                self.missed_return += 1
                print('LOST: Missed return instruction.')
                return 'RET'

        # If there's a jump at a different address to this function,
        # or a jump at this address to a different function, allow it.
        if last_func.jumps:
            for (addr, instr, symbol) in last_func.jumps:
                if (last_addr == addr and symbol != next_func.name or
                    last_addr != addr and symbol == next_func.name):
                    self.missed_jump += 1
                    print('LOST: Missed jump instruction.')
                    return 'JUMP'
        # Same for calls.
        if last_func.calls:
            for (addr, instr, symbol) in last_func.calls:
                if ((last_addr == addr and symbol != next_func.name) or
                    # This is a weird one - we see the instruction after
                    # the balc and then the first instr of the call.
                    (last_addr == addr + 4 and 
                     (symbol == next_func.name or not symbol)) or
                    (last_addr != addr and symbol == next_func.name)):
                    print('LOST: Missed call instruction.')
                    self.missed_call += 1
                    return 'CALL'


        # If we called a function we're likely to really call but it's 
        # the wrong location, treat as call anyway?

        # Maybe previous instruction for return got lost?
        ret = self.GetBranchKindForAddr(last_func, last_addr + 4,
                                        next_func, next_addr)
        if ret:
            print('LOST: Return went one instruction beyond.')
            self.missed1 += 1
            return ret

        # Maybe 
        ret = self.GetBranchKindForAddr(last_func, last_addr,
                                        next_func, next_addr - 4)
        if ret:
            print('LOST: Lost first instruction in called function.')
            self.missed2 += 1
            return ret

        return None
        
    def PlaceFunction(self, function_info, start_addr, end_addr):
        start_page = start_addr >> PAGE_SIZE_BITS
        end_page = end_addr >> PAGE_SIZE_BITS
        page = start_page
        while page <= end_page:
            if page not in self.page_map:
                self.page_map[page] = []
            self.page_map[page].append((start_addr, end_addr, function_info))
            page += 1

    def ParseInstruction(self, line):
        """Parse the next machine instruction.

        Returns true if affected call graph.
        """
        match = re.match('([0-9a-f]+):\s+([0-9a-f]+)\s+([a-z0-9]+)\s(.*)',
                         line)

        if not match:
            return False
        self.current_address = int(match.group(1), 16)
        instruction = match.group(3)
        args = match.group(4)

        #Shouldn't see any of these - should have caught with label.
        if instruction in return_instructions:
            self.current_function.AddReturn(self.current_address + 4,
                                            instruction,
                                            args)
            return True
        elif (instruction in return_instructions_compact or
              instruction in exception_return_instructions):
            self.current_function.AddReturn(self.current_address,
                                            instruction,
                                            args)
            return True
        elif instruction in call_to_register_instructions_compact:
            self.current_function.AddCall(self.current_address,
                                          instruction, None)
            return True

        elif instruction in call_to_register_instructions:
            self.current_function.AddCall(self.current_address + 4,
                                          instruction, None)
            return True

        elif instruction in wait_instructions:
            self.current_function.AddWait(self.current_address)
            return True
        else:
            if instruction.startswith('j') or instruction.startswith('b'):
                pattern = '.<(.*)>.*'
                match = re.match('.*<(.*)>.*', line)
                if match:
                    symbol = match.group(1)
                    if not IsLocalSymbol(symbol):
                        print('Missed %s' % instruction)
                        print(line)
        return False

    def ParseLabel(self, line):
        """Parse a line from input assuming it's a label.

        Returns False if not a label.
        """
        match = re.match('([0-9a-f]+) <(.*)>:', line)
        if not match:
            return False

        self.current_address = int(match.group(1), 16)

        if self.current_function:
            self.current_function.end_address = (
                self.current_address - 4)

        new_label = match.group(2)

        if IsLocalSymbol(new_label):
            return False

        if  new_label in self.functions:
            self.current_function = self.functions[new_label]
            self.current_function.other_ranges.append(
                (self.current_function.start_address,
                 self.current_function.end_address))
            self.current_function.start_address = self.current_address
            self.current_function.end_address = 0
        else:
            function_info = FunctionInfo(new_label, self.current_address)
            self.functions[new_label] = function_info
            self.current_function = function_info
        return True

    def ParseReference(self, line):
        """Parse a line from input assuming it's an instruction referencing a symbol.

        Returns False if not an interesting line..
        """
        match = re.match('([0-9a-f]+):\s+([0-9a-f]+)\s+([a-z0-9]+)\s+.*<(.*)>',
                         line)

        if not match:
            return False
        self.current_address = int(match.group(1), 16)
        instruction = match.group(3)
        symbol = match.group(4)

        if IsLocalSymbol(symbol):
            return False

        if not self.current_function:
            print('No idea where call came from\n')
            return False

        if (instruction in branch_instructions or 
            instruction in jump_instructions):
            self.current_function.AddJump(self.current_address + 4,
                                          instruction, symbol)
            return True
        if instruction in branch_instructions_no_offset:
            self.current_function.AddJump(self.current_address,
                                          instruction, symbol)
            return True

        elif instruction in call_instructions:
            self.current_function.AddCall(self.current_address + 4,
                                          instruction, symbol)
            return True

        elif instruction in call_instructions_compact:
            self.current_function.AddCall(self.current_address, instruction,
                                          symbol)
            return True
        else:
            print('How to handle %s?' % instruction)

        return False

    def FindCallers(self, function_name):
        """Returns the list of functions called by the named function.

        Returns None if function is unknown.
        """
        if function_name not in self.functions:
            return None
        
        if not self.functions[function_name].calls:
            return None

        return [name for (_, name, _) in self.functions[function_name].calls]

    def FindFunction(self, address):
        """Returns the function likely to be at that address.

        Returns None if no function is known."""
        if address & 0x20000000:
            # Bootloader is accessed from cached and uncached memory.
            # TODO(bowdidge): Generalize how we rewrite addresses.
            address = address & 0xffffffffdfffffff

        page = address >> PAGE_SIZE_BITS
        if page not in self.page_map:
            return None

        for (start_addr, end_addr, function_info) in self.page_map[page]:
            if address >= start_addr and address <= end_addr:
                return function_info
        
        return None

    def GetFunctionInfo(self, name):
        if not name in self.functions:
            return None

        return self.functions[name]

    def FindCallInfo(self, caller, callee):
        """Returns whether caller ever calls callee."""
        if caller not in self.functions:
            return False
        if callee not in self.functions:
            return False
        caller_dict = self.functions[caller]
        if not 'calls' in caller_dict:
            return False
        for (symbol, type, addr) in caller_dict['calls']:
            if callee == symbol:
                return True
        return False

        
    def DumpFunctionInfo(self):
        """Print out summary of function information in human-readable form."""
        for symbol in sorted(self.functions):
            function_info = self.functions[symbol]
            function_info.Dump()
            print
                                                
if __name__ == '__main__':
    f = open(sys.argv[1], 'r')
    text_info = DasmInfo()
    text_info.Read(f.readlines())
    f.close()
    
    text_info.DumpFunctionInfo()
