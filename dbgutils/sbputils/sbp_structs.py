import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *
from sbp_helpers import *

class Remains(Packet):
    fields_desc = [HexDumpStrField("payload", None)]
conf.raw_layer = Remains

class CONSTANT:
    TOTAL_OTP_LENGTH = 512

class serialInfo(Packet):
    fields_desc = [
        RsvBitField("reserved", 0x0, 24),
        CByteField("lcId", 0x0),
        X3BytesField("OID", 0x0),
        RsvBitField("reserved", 0x0, 8),
	]
    def extract_padding(self, p):
        return "", p

class serialNo(Packet):
    fields_desc = [
        CBitField("fabId", 0x0, 4),
        CBitField("foundaryId", 0x0, 4),
        CByteField("revId", 0x0),
        CByteField("chipId", 0x0),
        CByteField("familyId", 0x0),
        RsvBitField("reserved", 0x0, 16),
        CByteField("wk", 0x0),
        CByteField("yy", 0x0),
        RsvBitField("reserved", 0x0, 32),
        CIntField("serial_no", 0x0),
	]
    def extract_padding(self, p):
        return "", p


class otp(Packet):
    fields_desc = [
        CLEFlagsField("security_ctrl", 0x0, 16, { 0: 'hw', 1: 'te', 2: 'wd', 8: 'cu', 9: 'i2c', 10: 'dbu-cu', 11: 'dbu-pc'} ) ,
        XByteField("tamper_filter_period", 0x0),
        XByteField("tamper_filter_threshold", 0x0),
        XLEIntField("dbg_prot_lock", 0x0),
        PacketField("serialInfo", "", serialInfo, serialInfo),
        PacketField("serialNo", "", serialNo, serialNo),
		XStrLenField("tamper_lvl", "", 16),
        XByteField("cust_sec_ctrl", 0x0),
        XByteField("cust_key_valid", 0x0),
        XByteField("cust_key_revoked", 0x0),
        XByteField("cust_key_type", 0x0),
        XLEIntField("cust_dbg_prot_lock", 0x0),
        XByteField("cust_key_zero", 0x0),
        XByteField("cust_key_one", 0x0),
        RsvBitField("c1reserved", 0x0, 16),
        RsvBitField("c2reserved", 0x0, 32),
		XStrLenField("cust_SRK", "", 16),
		XStrLenField("cust_keyhash_zero", '\x00', 32),
		XStrLenField("cust_keyhash_one", '\x00', 32),
		XStrLenField("payload", '\x00', 0x150),
		XStrLenField("binningInfo", '\x00', 16),
		XStrLenField("chipInfo", '\x00', 16),
    ]
