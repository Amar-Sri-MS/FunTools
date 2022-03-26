from .sbp_helpers import *

class WideCSRCTL(Packet):
    fields_desc = [
       CBitField('resv', 0x0, 13), 
       CBitField('ring', 0x0, 5), 
       CBitField('status', 0x0, 4), 
       CBitField('size', 0x0, 6), 
       CBitEnumField('op', 0x02, 4, { 2: 'peek', 3: 'poke'} ), 
       CIntField('addr', 0x0)
    ]
    def extract_padding(self, p):
        return "", p

#w = WideCSRCTL(size=2, op=2, addr=0x1546f618)
#hexdump(w)
#print map(ord, str(w))
