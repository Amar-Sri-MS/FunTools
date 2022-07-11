#
#  lex.py
#
#  Created by Hariharan Thantry on 2017-07-11
#
#  Copyright  2017 Fungible Inc. All rights reserved.
# 
#  Simple lexer for breaking down any expression consisting
#  and returning individual symbols with types

import logging
import ply.lex as lex

class Lexer(object):
    tokens = (
            'NUMBER',
            'ID',
            'OPER',
    )
    t_OPER    = r'[\+\-\|\&\^\&&\||\*\/\(\)]'
    t_ignore  = ' \t'

    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def __init__(self, const_map, logger=None):
        self.const_map = const_map
        self.logger = logger or logging.getLogger(__name__)

    def t_NUMBER(self, t):
        r'\b(\d+|0[Xx][0-9a-fA-F]+|0[Bb][0-1]+)\b'
        return t
    def t_ID(self, t):
        r'[a-zA-Z_][\.a-zA-Z_0-9]*'
        c_obj = self.const_map.get(t.value, None)
        assert c_obj != None, "Do not have ID:{} in the map".format(t)
        t.value = c_obj.val
        return t

    def t_error(self, t):
        self.logger.warning(("Illegal character: {}".format(t.value[0])))
        t.lexer.skip(1)

    def eval(self, data):
        m_str = ""
        self.lexer.input(str(data))
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            m_str = "{}{}".format(m_str, tok.value)
        return eval(m_str)

class LexTok(object):
    def __init__(self, val):
        self.val = val


if __name__ == '__main__':
    m_map = {
                'A.p': LexTok(0xf),
                'B': LexTok('4'),
                'C': LexTok('3 | 2')
            }
    m = Lexer(m_map)
    m.build()
    value = m.eval("B")
    value = m.eval("0")
    print("Value = {}".format(value))
    value = m.eval("(0b10100 + 0x3)- ((A.p | B) + (C))")
    print("Value = {}".format(value))
    assert value == eval("0b1010 + 0x3 - (0xf | 4) + (3 | 2)"), "Custom lexer not working!"

