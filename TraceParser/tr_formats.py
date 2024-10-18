#
# Trace format classes.
#
# Copyright (c) 2019 Fungible Inc.  All rights reserved.
#

import re


class BaseTF(object):

    __slots__ = ['tf_type']
    def __init__(self, tf_type):
        self.tf_type = tf_type

    def init_from_msg(self, msg):
        raise NotImplementedError('subclasses must implement this')


class TF2(BaseTF):
    def __init__(self):
        BaseTF.__init__(self, 2)


class TF3(BaseTF):
    #
    # Pattern for TF3 messages. These are samples of the TF3 messages
    # that we need to match.
    #
    # 1.046: 82 00003333 33333333 3334FE00  TF3 ic[0]=ni  tt=tu1 te=1 tm=1      va[64]=0x3333333333333333
    # 2.039: 26                   00000000  TF3 ic[0]=ni  tt=nt  te=0 tm=0      va[08]=              0x00
    # 2.133: 34          00000003 33333F80  TF3 ic[3]=ni  tt=tu2 te=1 tm=1      va[16]=            0x3333
    # 2.339: 26                   00000000  TF3 ic[0]=?   tt=nt  te=0 tm=0      va[08]=              0x00
    #
    # Note that the last example trace has a inscomp of ? - this only
    # occurs during overflow or TMOAS when the frame gets messed up.
    #
    pattern = re.compile(r'^\s*\d+\.\d+: '
                         r'([\s0-9A-F]+)'
                         r'TF3\s+'
                         r'ic\[(\d+)\]=([\w?]+)\s+'
                         r'tt=(\w+)\s+'
                         r'te=(\d)\s+'
                         r'tm=(\d)\s+'
                         r'va\[(\d+)\]=\s*0x([0-9A-F]+)')

    __slots__ = ['inscomp', 'ttype', 'addr']
    def __init__(self):
        BaseTF.__init__(self, 3)
        self.inscomp = None
        self.ttype = None
        self.addr = None

    def init_from_msg(self, msg):
        """
        Returns a TF3 object with information from the parsed message.
        """
        match = TF3.pattern.match(msg)
        if match:
            self.inscomp = match.group(3)
            self.ttype = match.group(4)
            self.addr = int(match.group(8), 16)
        else:
            raise ValueError('wrong format for TF3 %s' % msg)


class TF4(BaseTF):
    def __init__(self):
        BaseTF.__init__(self, 4)


class TF5(BaseTF):
    def __init__(self):
        BaseTF.__init__(self, 5)


class TF6(BaseTF):
    def __init__(self):
        BaseTF.__init__(self, 6)


class TF7(BaseTF):
    def __init__(self):
        BaseTF.__init__(self, 7)


class TF8(BaseTF):
    def __init__(self):
        BaseTF.__init__(self, 8)


def is_tu2(tf):
    """
    Whether this is a TU2 trace.

    A TU2 trace is triggered by a write to the UserTraceData2 register
    in the MIPS coprocessor space (CP0).
    """
    return tf.tf_type == 3 and tf.ttype == 'tu2'


def is_tu1(tf):
    """
    Whether this is a TU1 trace.

    A TU1 trace is triggered by a write to the UserTraceData1 register
    in the MIPS coprocessor space (CP0).
    """
    return tf.tf_type == 3 and tf.ttype == 'tu1'


def is_tmoas(tf):
    """
    Whether this is a TMOAS trace.

    TMOAS traces show up for a variety of reasons: the most common one
    being the processor changing its operating mode (i.e. from user to
    kernel mode, or taking an exception). It appears to be impossible
    to switch these off.
    """
    return tf.tf_type == 3 and tf.ttype == 'tmo'


def is_tpc(tf):
    """
    Whether this is a program counter trace, TPC.
    """
    return tf.tf_type == 3 and tf.ttype == 'tpc'


def is_tla(tf):
    """
    Whether this is a load address trace, TLA.
    """
    return tf.tf_type == 3 and tf.ttype == 'tla'


def is_tsa(tf):
    """
    Whether this is a store address trace, TSA.
    """
    return tf.tf_type == 3 and tf.ttype == 'tsa'
