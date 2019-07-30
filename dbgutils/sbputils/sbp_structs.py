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

class inputU32(Packet):
    fields_desc = [
        CIntField("input", 0xdeadface),
    ]
    def extract_padding(self, p):
        return "", p

msgStatusCodeEnum = {
    0 : 'Okay',
    1 : 'Invalid command',
    2 : 'Authorization error',
    3 : 'Invalid signature (if command is signature verification)',
    4 : 'Bus error (if DMA is used)',
    5 : 'Reserved',
    6 : 'Crypto error',
    7 : 'Invalid parameter',
}

class HEADER(Packet):
    fields_desc = [
        CShortField("MsgSize", 0x0),
        CBitEnumField("MsgStatus", 1, 4, msgStatusCodeEnum),
        RsvBitField("reserved", 0x0, 1),
        CBitEnumField("protected", 1, 1, {0: 'reserved', 1: 'ProtectionIgnored'} ),
        RsvBitField("reserved", 0x0, 10),
    ]
    def extract_padding(self, p):
        return "", p

commandEnum = {
    0x54000000 : 'Test commands',
    0xFC000000 : 'Flash/FlashEraseSection',
    0xFC010000 : 'Flash/FlashProgram',
    0xFC020000 : 'Flash/FlashRead',

    0xFD000000 : 'Maintenance/GetChallenge',
    0xFD010000 : 'Maintenance/DebugAccess/CM',
    0xFD010001 : 'Maintenance/DebugAccess/SM',

    0xFD020001 : 'Maintenance/DisableTamper/SM',

    0xFE000000 : 'Diagnostic/ReadSerialNumber',
    0xFE010000 : 'Diagnostic/GetStatus',
    0xFE020000 : 'Diagnostic/ReadPubKeyBoot/CM',
    0xFE020001 : 'Diagnostic/ReadPubKeyBoot/SM',
    0xFE030000 : 'Diagnostic/SetUpgradeFlag/CM',
    0xFE030001 : 'Diagnostic/SetUpgradeFlag/SM',

    0xFF000000 : 'Initialization/InitOTP/CM',
    0xFF000001 : 'Initialization/InitOTP/SM',
    0xFF010000 : 'Initialization/CreateEKPair/CM',
    0xFF020001 : 'Initialization/CreateSRK/SM',
    0xFF030000 : 'Initialization/EnrollPUF/CM',
    0xFF040000 : 'Initialization/ReadPubEK',
}

class COMMAND(Packet):
    fields_desc = [
        CIntEnumField('command', 0x0, commandEnum),
    ]
    def extract_padding(self, p):
        return "", p

