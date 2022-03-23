#!/usr/bin/env python3
import unittest

import parse_dasm

simple_dasm_file = """
ffffffff00001000 <__start>:
ffffffff00001000:\t10000004\tb\tffffffff00001100 <end>
ffffffff00001004:\t00000000\tnop
ffffffff00001100 <end>:
ffffffff00001100:\t00000000\tnop\t
ffffffff00001104:\t00000000\tnop\t
ffffffff00001108:\t00000000\tnop\t
"""

class DasmInfoTest(unittest.TestCase):
 
  def testSimple(self):
      dasm_info = parse_dasm.DasmInfo()
      dasm_info.Read(simple_dasm_file.split('\n'))

      self.assertIsNotNone(dasm_info.GetFunctionInfo('__start'))
      self.assertIsNotNone(dasm_info.GetFunctionInfo('end'))

      self.assertEqual('__start',
                       dasm_info.FindFunction(0xffffffff00001000).name)
      self.assertEqual('__start',
                       dasm_info.FindFunction(0xffffffff00001004).name)
      self.assertEqual('end', dasm_info.FindFunction(0xffffffff00001100).name)
      self.assertEqual('end', dasm_info.FindFunction(0xffffffff00001104).name)

  def testOutOfRange(self):
    dasm_info = parse_dasm.DasmInfo()
    dasm_info.Read(simple_dasm_file)

    self.assertEqual(None, dasm_info.FindFunction(0))
    self.assertEqual(None, dasm_info.FindFunction(0xffffffff00000000))
    self.assertEqual(None, dasm_info.FindFunction(0xffffffff00000200))

class DasmTestParseLine(unittest.TestCase):
  def testLabel(self):
    dasm_info = parse_dasm.DasmInfo()
    
    self.assertTrue(dasm_info.ParseLabel('1000 <a>:'))
    self.assertEqual(0x1000, dasm_info.GetFunctionInfo('a').start_address)

    self.assertTrue(dasm_info.ParseLabel('2000 <_b>:'))
    self.assertEqual(0x2000, dasm_info.GetFunctionInfo('_b').start_address)

    self.assertTrue(dasm_info.ParseLabel(
        'fffffffff9888804 <c>:'))
    self.assertEqual('c', dasm_info.GetFunctionInfo('c').name)
    self.assertEqual(0xfffffffff9888804,
                     dasm_info.GetFunctionInfo('c').start_address)

    self.assertTrue(dasm_info.ParseLabel('3000 <long_name_with_num_1110>:'))
    self.assertEqual(0x3000, 
                     dasm_info.GetFunctionInfo('long_name_with_num_1110').
                     start_address)

    # Local labels are ignored because they're irrelevant.
    self.assertFalse(dasm_info.ParseLabel('3000 <.L21>:'))

    # $ labels are ignored.  I don't know what they're for, but they look
    # uninteresting.
    self.assertFalse(dasm_info.ParseLabel('3000 <$foobar>:'))

  def testReference(self):
    dasm_info = parse_dasm.DasmInfo()
    dasm_info.Read(simple_dasm_file)
    dasm_info.current_function = parse_dasm.FunctionInfo('foo', 0x1000)

    self.assertTrue(dasm_info.ParseReference(
        'ffffffff9fc00614:\t10800002\tbeqz\ta0,ffffffff9fc00620 <verify_isa>'))
    self.assertTrue(1,len(dasm_info.current_function.jumps))
    # +4 because branch happens after reading next instruction.
    self.assertEqual((0xffffffff9fc00618, 'beqz', 'verify_isa'),
                     dasm_info.current_function.jumps[0])

  def testParseInstruction(self):
    """Check we correctly handle instructions referencing jumps and calls."""
    dasm_info = parse_dasm.DasmInfo()
    dasm_info.current_function = parse_dasm.FunctionInfo('foo', 0)

    self.assertTrue(dasm_info.ParseInstruction('10000:\t00000000\tjr\tra'))
    self.assertEqual(1, len(dasm_info.current_function.returns))
    # One more than actual location because we'd see the jump after
    # 0x10004 executed.
    self.assertEqual((0x10004, 'jr', 'ra'),
                     dasm_info.current_function.returns[0])


class DasmIdentifyControlFlowTest(unittest.TestCase):
  def testIdentifiesSimpleJump(self):
    contents = """
1000 <start>:
1000:\t:240dffff\tli\tt1,-1
1004:\t00000000\tj\t1100 <next>
1008:\t00000000\tnop
1100 <next>:
1100:\t000000\tnop
1104:\t000000\tnop
"""
    dasm_info = parse_dasm.DasmInfo()
    dasm_info.Read(contents.split('\n'))
    start_info = dasm_info.functions['start']
    next_info = dasm_info.functions['next']

    self.assertEqual(1, len(start_info.jumps))
    self.assertEqual((0x1008, 'j', 'next'), start_info.jumps[0])

    self.assertEqual('JUMP',
                     dasm_info.GetBranchKind('start', 0x1004, 'next', 0x1100))
    # What if we lost the first instruction after the jump?
    self.assertEqual('JUMP',
                     dasm_info.GetBranchKind('start', 0x1004, 'next', 0x1104))
    # What if we lost the first instruction before the jump?
    self.assertEqual('JUMP',
                     dasm_info.GetBranchKind('start', 0x1000, 'next', 0x1100))

    # next never seems to call start, and there's no call to register there
    # to make us think this is a function pointer or virtual function call.
    self.assertEqual(None,
                     dasm_info.GetBranchKind('next', 0x1100, 'start', 0x10000))


  def testIdentifiesSimpleFallThrough(self):
    contents = """
1000 <start>:
1000:\t:240dffff\tli\tt1,-1
1004:\t00000000\tbeqz\t1100 <next>
1008:\t00000000\tnop
100c:\t00000000\tnop
1010:\t00000000\li\tr4, 5
1014 <next>:
1018:\t000000\tnop
101c:\t000000\tnop
"""
    dasm_info = parse_dasm.DasmInfo()
    dasm_info.Read(contents.split('\n'))

    start_info = dasm_info.GetFunctionInfo('start')

    self.assertEqual('FALLTHROUGH',
                     dasm_info.GetBranchKind('start', 0x1010, 'next', 0x1014))
    self.assertEqual('JUMP',
                     dasm_info.GetBranchKind('start', 0x1008, 'next', 0x1014))

    # What if we lost the first instruction before the jump?
    self.assertEqual('JUMP',
                     dasm_info.GetBranchKind('start', 0x1004, 'next', 0x1014))

    # What if we lost the first instruction after the jump?
    self.assertEqual('JUMP',
                     dasm_info.GetBranchKind('start', 0x1004, 'next', 0x1018))


  def testIdentifiesSimpleCall(self):
    contents = """
1000 <start>:
1004:\t:240dffff\tli\tt1,-1
1008:\t00000000\tbalc\t1100 <next>
100c:\t00000000\tnop
1100 <next>:
1104:\t000000\tjr\ta2
1108:\t00000000\tnop
"""
    dasm_info = parse_dasm.DasmInfo()
    dasm_info.Read(contents.split('\n'))

    start_info = dasm_info.functions['start']
    next_info = dasm_info.functions['next']

    self.assertEqual(1, len(start_info.calls))
    self.assertEqual((0x1008, 'balc', 'next'), start_info.calls[0])

    self.assertEqual(1, len(next_info.returns))
    self.assertEqual((0x1108, 'jr', 'a2'), next_info.returns[0])

    self.assertEqual('RET',
                     dasm_info.GetBranchKind('next', 0x1108, 'start', 0x100c))
    # What if we lose the instruction before the return?
    self.assertEqual('RET',
                     dasm_info.GetBranchKind('next', 0x1104, 'start', 0x100c))

  def testIdentifiesVirtualCall(self):
    contents = """
1000 <start>:
1004:\t:240dffff\tli\tt1,-1
1008:\t00000000\tjalr\tra
100c:\t00000000\tnop
1100 <next>:
1100:\t000000000\tli\tt1, -1
1104:\t000000\tjr\ta2
1108:\t00000000\tnop
110c:\t00000000\tnop
"""
    dasm_info = parse_dasm.DasmInfo()
    dasm_info.Read(contents.split('\n'))

    start_info = dasm_info.functions['start']
    next_info = dasm_info.functions['next']

    self.assertEqual(1, len(start_info.calls))
    self.assertEqual((0x100c, 'jalr', None), start_info.calls[0])

    self.assertEqual(1, len(next_info.returns))
    self.assertEqual((0x1108, 'jr', 'a2'), next_info.returns[0])

    self.assertEqual('CALL',
                     dasm_info.GetBranchKind('start', 0x1008, 'next', 0x1100))

    self.assertEqual('RET',
                     dasm_info.GetBranchKind('next', 0x1108, 'start', 0x100c))
    # What if we lose the instruction before the return?
    self.assertEqual('RET',
                     dasm_info.GetBranchKind('next', 0x1104, 'start', 0x100c))

    # What if samurai gives us the instruction after the jalr?  It has in
    # the past.
    self.assertEqual('CALL',
                     dasm_info.GetBranchKind('start', 0x1008, 'next', 0x1104))

    # What if we lose the first instruction in the function?  The second?
    self.assertEqual('CALL',
                     dasm_info.GetBranchKind('start', 0x1008, 'next', 0x110c))


  def testHandlesRecursiveFunctions(self):
    contents = """
1000 <start>:
1000:\t00000000\tnop
1004:\t00000000\tbalc\t1100 <fn_recursive>
1008:\t00000000\tnop
100c:\t00000000\tnop
1100 <fn_recursive>:
1104:\t00000000\tnop
1108:\t00000000\tbalc\t1100 <fn_recursive>
110c:\t000000\tnop
1110:\t00000000\tjr\ta2
1114:\t00000000\tnop
"""
    dasm_info = parse_dasm.DasmInfo()
    dasm_info.Read(contents.split('\n'))
    
    start_info = dasm_info.functions['start']
    fn_recursive_info = dasm_info.functions['fn_recursive']

    self.assertEqual('CALL',
                     dasm_info.GetBranchKind('start', 0x1004,
                                             'fn_recursive', 0x1100))
    self.assertEqual('CALL',
                     dasm_info.GetBranchKind('fn_recursive', 0x1108,
                                             'fn_recursive', 0x1100))

    self.assertEqual('IGNORE',
                     dasm_info.GetBranchKind('fn_recursive', 0x110c,
                                             'fn_recursive', 0x1100))
    # Thinks this is a return.
    #self.assertEqual('CALL',
    #                 dasm_info.GetBranchKind('fn_recursive', 0x1110,
    #                                         'fn_recursive', 0x1100))
    
  def testMultipleStepJump(self):
    contents = """
1000 <a>:
1000:\t00000000\tnop
1004:\t000000000\tbeqzc\t1100 <b>
1008:\t00000000\tnop
1100 <b>:
1100:\t000000\tbeqzc\t1200 <c>
1104:\t0000000\tnop
1200 <c>:
1200:\t00000000\tli\tx,0
"""
    dasm_info = parse_dasm.DasmInfo()
    dasm_info.Read(contents.split('\n'))

 
    self.assertEqual('JUMP',
                     dasm_info.GetBranchKind('a', 0x1004, 'b', 0x1100))

    self.assertEqual('JUMP',
                     dasm_info.GetBranchKind('a', 0x1008, 'b', 0x1100))

    self.assertEqual('JUMP',
                     dasm_info.GetBranchKind('b', 0x1100, 'c', 0x1200))

    self.assertEqual('JUMP',
                     dasm_info.GetBranchKind('b', 0x1100, 'c', 0x1200))

    # What if we lost instruction just before jump?
    self.assertEqual('JUMP',
                     dasm_info.GetBranchKind('a', 0x1000, 'b', 0x1100))

    # What if we missed the intermediate jump?
    self.assertEqual('JUMP',
                     dasm_info.GetBranchKind('a', 0x1004, 'c', 0x1200))

    # If we lost both jumps, we're not going to believe the transition.
    self.assertEqual(None,
                     dasm_info.GetBranchKind('a', 0x1000, 'c', 0x1200))

  def tesTailCall(self):
    contents = """
1000 <a>:
1000:\t00000000\tnop
1004:\t00000000balc\t1100 <b>
1008:\td8400018\tbeqzc\tv0,1200 <c>
100c:\tdfa20018\tld\tv0, 24(sp)
1100 <b>:
1100:\tdfbf0038\tld\tra, 56(sp)
1104:\t03e00009\tjr\tra
1108:\t00000000\tnop
1200 <c>:
1200:\tdfbf0038\tld\tra, 56(sp)
"""
    dasm_info = parse_dasm.DasmInof()
    dasm_info.Read(contents.split('\n'))
    
    # Note that these two appear to come the same address - for the balc
    # (call), we'll
    # see address 0x1008 as the last instruction examined before the call
    # because the processor tries to execute the following instruction.
    # The bc (branch compact) doesn't look at the following instruction.
    # We need the target to figure out which instruction we're executing.
    self.assertEqual('CALL',
                     dasm_info.GetBranchKind('a', 0x1008, 'b', 0x1100))
    self.assertEqual('JUMP',
                     dasm_info.GetBranchKind('a', 0x1008, 'c', 0x1200))


  # Add tests:
  #  call with branch after (Branch doesn't get executed?)
  #  instr with return got lost.
  # bc to bc to actual function
  # ERRORS at 2534440 (call shows second instruction)
  # , 2526271 (call misses second of two bc)
  #
if __name__ == '__main__':
    unittest.main()
