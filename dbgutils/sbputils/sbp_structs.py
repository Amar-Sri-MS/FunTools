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
        XByteField("cust_sec_ctrl", None),
        XByteField("cust_key_valid", None),
        XByteField("cust_key_revoked", None),
        XByteField("cust_key_type", None),
        XLEIntField("cust_dbg_prot_lock", None),
        XByteField("cust_key_zero", None),
        XByteField("cust_key_one", None),
        RsvBitField("c1reserved", 0x0, 16),
        RsvBitField("c2reserved", 0x0, 32),
		XStrLenField("cust_SRK", '\x00', 16),
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

bootStep_enum = {
    0x4     : "BOOT_STEP_FETCH_OTP",
    0x8     : "BOOT_STEP_QSPI_INIT",
    0xC     : "BOOT_STEP_TAMPER_TEST",
    0x10    : "BOOT_STEP_AES_INTEGRITY_TEST",
    0x14    : "BOOT_STEP_HASH_INTEGRITY_TEST",
    0x18    : "BOOT_STEP_PKE_SELF_TEST",
    0x1C    : "BOOT_STEP_SERIAL_NO_CHECK",
    0x20    : "BOOT_STEP_PUF_ROM_SELECT_IMAGE",
    0x24    : "BOOT_STEP_PUF_ROM_FETCH_FW",
    0x28    : "BOOT_STEP_PUF_ROM_HASH_FUN",
    0x2C    : "BOOT_STEP_PUF_ROM_VERIFY_FUN",
    0x30    : "BOOT_STEP_PUF_ROM_FETCH_CUST_SIG_INFO",
    0x34    : "BOOT_STEP_PUF_ROM_HASH_CUST",
    0x38    : "BOOT_STEP_PUF_ROM_VERIFY_CUST",
    0x3C    : "BOOT_STEP_JUMP_TO_RAM",
    0x40    : "BOOT_STEP_RNG_INIT",
    0x44    : "BOOT_STEP_QSPI_INIT2",
    0x48    : "BOOT_STEP_EEPROM_LOAD_EXEC",
    0x4C    : "BOOT_STEP_HSU_SBM_LOAD_EXEC",
    0x50    : "BOOT_STEP_PLL_LOCK",
    0x54    : "BOOT_STEP_MEM_REPAIR_DONE",
    0x58    : "BOOT_STEP_CPC_RESET",
    0x5C    : "BOOT_STEP_HSU_PHY_INIT",
    0x60    : "BOOT_STEP_PCIE_CONFIG_INIT",
    0x64    : "BOOT_STEP_ENROLLMENT_VERIFY",
    0x68    : "BOOT_STEP_PUF_INIT",
    0x6C    : "BOOT_STEP_FIRMWARE_SELECT_IMAGE",
    0x70    : "BOOT_STEP_FIRMWARE_CHECK_SIZE",
    0x74    : "BOOT_STEP_FIRMWARE_FETCH_FW",
    0x78    : "BOOT_STEP_FIRMWARE_FETCH_CUST_SIG_INFO",
    0x7C    : "BOOT_STEP_FIRMWARE_HASH",
    0x80    : "BOOT_STEP_FIRMWARE_VERIFY",
    0x90    : "BOOT_STEP_FIRMWARE_START",
    0x94    : "BOOT_STEP_HSU_FINISH",
    0x98    : "BOOT_STEP_HBM_SBUS",
    0x9C    : "BOOT_STEP_SKUID_VERIFY",
    0xA0    : "BOOT_STEP_HOST_SELECT_IMAGE",
    0xA4    : "BOOT_STEP_HOST_FETCH_FW",
    0xC0    : "BOOT_STEP_HOST_FETCH_CUST_SIG_INFO",
    0xC4    : "BOOT_STEP_HOST_HASH",
    0xC8    : "BOOT_STEP_HOST_CHECK_EXTDMA",
    0xCC    : "BOOT_STEP_HOST_VERIFY",
    0xD0    : "BOOT_STEP_HOST_LOADED",
    0xD4    : "BOOT_STEP_SHARE_BOOT_CONFIG",
    0xD8    : "BOOT_STEP_UNUSED",
    0xDC    : "BOOT_STEP_RESET_HOST",
    0xE0    : "BOOT_STEP_HOST_RUNNING",
    0xE4    : "BOOT_STEP_MAIN_LOOP",
    0xFC    : "BOOT_STEP_ESEC_SUCCESS",
    0xFF    : "BOOT_STEP_HOST_SUCCESS"
}

class S1CSRJTAG(Packet):
    fields_desc = [
        ConditionalField(RsvBitField("resv", 0x0, 16), lambda p: p.cmd == 3),
        ConditionalField(RsvBitField("resv", 0x0, 12), lambda p: p.cmd == 2),
        ConditionalField(CBitField("status", 0x0, 4), lambda p: p.cmd == 2),
        CBitEnumField("cmd", 2, 4, {2 : 'read', 3: 'write'}),
        CBitField("size", 1, 6),
        CBitField("priv", 0, 1),
        CBitField("tag", 0, 5),
        ConditionalField(CIntField("address", 0), lambda p: p.cmd == 3),
        ConditionalField(CBitField("running", 0, 1), lambda p: p.cmd == 2),
        ConditionalField(CBitField("valid", 0, 1), lambda p: p.cmd == 2),
        ConditionalField(CBitField("address", 0, 30), lambda p: p.cmd == 2),
        ConditionalField(CBitField("wdata", 0, 64), lambda p: p.cmd == 3),
        ConditionalField(CBitField("rdata", 0, 64), lambda p: p.cmd == 2),
    ]
    def extract_padding(self, p):
        return "", p

"""
typedef csr_status => enum {
    codepoint CSR_STATUS_OK      => 0;  # success
    codepoint CSR_STATUS_EADDR   => 1;  # (RSU) address claimed, but could not be decoded
    codepoint CSR_STATUS_EPRIV   => 2;  # (RSU) insufficient privilege, (CTL) WEN/REN enable not set
    codepoint CSR_STATUS_EACCESS => 3;  # (RSU) reading write-only or writing read-only register
    codepoint CSR_STATUS_ESIZE   => 4;  # (RSU) size mismatch
    codepoint CSR_STATUS_ENACK   => 5;  # (RSU) user logic nack
    codepoint CSR_STATUS_ERESET  => 6;  # (RSU) csrdec in reset
    codepoint CSR_STATUS_EUNCLM  => 7;  # (CTL) address was unclaimed
    codepoint CSR_STATUS_BUSY    => 8;  # (CTL) operation busy - info status in wide ctrl reg (not in response code)
    codepoint CSR_STATUS_EBADOP  => 9;  # (CTL) op is not read/write req
    codepoint CSR_STATUS_EBADADD => 10; # (CTL) address did not decode to a ring
    codepoint CSR_STATUS_ETIMOUT => 11; # (CTL) response did not come after timeout and cancel
} logic(4);

"""
enum_csrsubop = {
    0x0: 'read', 0x1: 'write', 0x2: 'dropCount', 0x8: 'disconnect', 0x9: 'ready'
}
class CSR(Packet):
    fields_desc = [
        CBitEnumField("cmd", 0, 2, { 0: 'csr', 1 : 'dbgRead', 2:'dbgWrite', 3: 'dbgWriteStart'} ),
        ConditionalField(CBitEnumField("subop", 0, 6, { 0x0: 'read', 0x1: 'write', 0x2: 'dropCount', 0x8: 'disconnect', 0x9: 'ready'} ), lambda p: p.cmd == 0),
        ConditionalField(CBitField("length", 0, 6), lambda p: p.cmd != 0),
    ]
    def extract_padding(self, p):
        return "", p


class HEADER(Packet):
    fields_desc = [
        RsvBitField("reserved", 0x0, 10),
        CBitEnumField("protected", 1, 1, {0: 'reserved', 1: 'ProtectionIgnored'} ),
        RsvBitField("reserved", 0x0, 1),
        CBitEnumField("MsgStatus", 1, 4, msgStatusCodeEnum),
        CShortField("MsgSize", 0x0),
    ]
    def extract_padding(self, p):
        return "", p

class RESP_raw(Packet):
    fields_desc = [
        PacketField('header', HEADER, HEADER)
    ]
    #def extract_padding(self, p):
    #    return "", p

commandEnum = {
    0x54000000 : 'Test commands',

    0xFC000000 : 'Flash Erase',
    0xFC011000 : 'Flash Program/GetBufferSizes',
    0xFC012000 : 'Flash Program/DataAdd',
    0xFC013000 : 'Flash Program/DataClear',
    0xFC014000 : 'Flash Program/DataFlush',
    0xFC020000 : 'Flash Read',
    0xFC021000 : 'Flash Read/GetBufferSizes',
    0xFC022000 : 'Flash Read/Data',

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
    0xFE0A0000 : 'CM Diagnostic/injectCertificate',
    0xFE0A0001 : 'SM Diagnostic/injectCertificate',
    0xFE0B0000 : 'Diagnostic/fetchOTP',

    0xFF000000 : 'Initialization/InitOTP/CM',
    0xFF000001 : 'Initialization/InitOTP/SM',
    0xFF010000 : 'Initialization/CreateEKPair/CM',
    0xFF020001 : 'Initialization/CreateSRK/SM',
    0xFF030000 : 'Initialization/EnrollPUF/CM',
    0xFF040000 : 'Initialization/ReadPubEK',


}

class COMMAND(Packet):
    fields_desc = [
        CIntField('size', 0x0),
        CIntEnumField('command', 0x0, commandEnum),
    ]
    def extract_padding(self, p):
        return "", p

class RESP_getStatus(Packet):
    fields_desc = [
        PacketField('header', HEADER, HEADER),
        CLEIntField('statusLastTamper', 0x0),
        CLEIntField('timestampLastTamper', 0x0),
        CLEIntField('statusCurrentTamper', 0x0),
        CLEIntField('currentTime', 0x0),
        CBitEnumField('bootStep', 0, 8, bootStep_enum),
        CBitEnumField('hostImage', 1, 4, { 0: 'imageA', 1: 'imageB'}),
        CBitEnumField('esecureImage', 1, 4, { 0: 'imageA', 1: 'imageB'}),
        CBitEnumField('hostUpgradeFlag', 1, 4, { 0: 'False', 1: 'True'}),
        CBitEnumField('esecureUpgradeFlag', 1, 4, { 0: 'False', 1: 'True'}),
        CBitField('rsvd', 0, 8),
        CLEIntField('esecureFirmwareVersion', 0x0),
        CLEIntField('hostFirmwareVersion', 0x0),
        CLEIntEnumField('debugGrants', 0x0, { 0xFFFFFFFF : 'full-access' }),
        ConditionalField(CLEIntField('MagicVersion', 0x0), lambda p: p.bootStep > 0x80),
        ConditionalField(CLEIntField('qspiFlashSize', 0x0), lambda p: p.bootStep > 0x80),
        ConditionalField(CLEIntField('qspiStatusFlags', 0x0), lambda p: p.bootStep > 0x80),
        ConditionalField(CByteField('qspiQioModeBits', 0x0), lambda p: p.bootStep > 0x80),
        ConditionalField(CByteField('qspiQioDummyCycles', 0x0), lambda p: p.bootStep > 0x80),
        ConditionalField(CByteField('qspiQioRdCmd', 0x0), lambda p: p.bootStep > 0x80),
        ConditionalField(CByteField('qspiInitDone', 0x0), lambda p: p.bootStep > 0x80),
        XStrLenField('firmwareString', '\x00', 20),
    ]
    def extract_padding(self, p):
        return "", p

class RESP_getChallenge(Packet):
    fields_desc = [
        PacketField('header', HEADER, HEADER),
        XStrLenField('challenge', '\x00', 16),
    ]
    def extract_padding(self, p):
        return "", p

class RESP_fetchOTP(Packet):
    fields_desc = [
        PacketField('header', HEADER, HEADER),
        PacketField('otp', otp, otp),
    ]
    def extract_padding(self, p):
        return "", p

class RESP_getSerial(Packet):
    fields_desc = [
        PacketField('header', HEADER, HEADER),
        PacketField('serialInfo', serialInfo, serialInfo),
        PacketField('serialNo', serialNo, serialNo),
    ]
    def extract_padding(self, p):
        return "", p

DBG_CMDRESP = {
    0x54000000 : RESP_raw,  #'Test commands',

    0xFC000000 : RESP_raw, #'Flash Erase',
    0xFC011000 : RESP_raw, # 'Flash Program/GetBufferSizes',
    0xFC012000 : RESP_raw, # 'Flash Program/DataAdd',
    0xFC013000 : RESP_raw, # 'Flash Program/DataClear',
    0xFC014000 : RESP_raw, # 'Flash Program/DataFlush',
    0xFC020000 : RESP_raw, # 'Flash Read',
    0xFC021000 : RESP_raw, # 'Flash Read/GetBufferSizes',
    0xFC022000 : RESP_raw, # 'Flash Read/Data',

    0xFD000000 : RESP_getChallenge,  #'Maintenance/GetChallenge',
    0xFD010000 : RESP_raw,  #'Maintenance/DebugAccess/CM',
    0xFD010001 : RESP_raw,  #'Maintenance/DebugAccess/SM',

    0xFD020001 : RESP_raw,  #'Maintenance/DisableTamper/SM',

    0xFE000000 : RESP_getSerial,  #'Diagnostic/ReadSerialNumber',
    0xFE010000 : RESP_getStatus,  #'Diagnostic/GetStatus',
    0xFE020000 : RESP_raw,  #'Diagnostic/ReadPubKeyBoot/CM',
    0xFE020001 : RESP_raw,  #'Diagnostic/ReadPubKeyBoot/SM',
    0xFE030000 : RESP_raw,  #'Diagnostic/SetUpgradeFlag/CM',
    0xFE030001 : RESP_raw,  #'Diagnostic/SetUpgradeFlag/SM',
    0xFE0A0000 : RESP_raw,  #'Diagnostic/InjectCertificate/CM',
    0xFE0B0000 : RESP_fetchOTP,  #'Diagnostic/fetchOTP/CM',

    0xFF000000 : RESP_raw,  #'Initialization/InitOTP/CM',
    0xFF000001 : RESP_raw,  #'Initialization/InitOTP/SM',
    0xFF010000 : RESP_raw,  #'Initialization/CreateEKPair/CM',
    0xFF020001 : RESP_raw,  #'Initialization/CreateSRK/SM',
    0xFF030000 : RESP_raw,  #'Initialization/EnrollPUF/CM',
    0xFF040000 : RESP_raw,  #'Initialization/ReadPubEK',
}

O = """
00 00 00 38 00 00 00 00  00 00 00 00 00 00 01 00
0C 03 00 00 FF 00 00 00  01 00 00 00 00 00 00 00
00 0C 00 00 62 6C 64 5F  33 36 35 30 35 2D 65 36
36 35 64 62 39 32 00 A5
"""
O = """
00 00 00 38 00 00 00 00  00 00 00 00 00 00 01 00
C6 00 00 00 A0 01 00 00  00 00 00 00 00 00 00 00
00 0C 00 00 62 6C 64 5F  33 36 35 30 35 2D 65 36
36 35 64 62 39 32 00 A5
"""
O = """
00 00 00 38 01 01 00 00  0E 00 00 00 00 00 00 00
00 00 00 00 20 00 00 00  00 00 00 00 00 00 00 00
00 0C 00 00 62 6C 64 5F  31 39 30 32 39 2D 63 36
38 64 37 35 65 65 34 00
"""
O = """
00 00 00 4C 01 00 00 00  00 00 00 00 00 00 00 00
00 00 00 00 E4 11 00 00  00 00 00 00 00 00 00 00
FF FF FF FF 01 D0 DE AD  FF FF FF 7F 8E 01 00 00
01 09 EB 01 62 6C 64 5F  31 32 31 30 37 39 2D 32
34 62 63 34 63 32 64 33  00 A5 A5 A5
"""

SN = """
00 00 00 1C 00 00 00 00  00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00  00 00 12 34
"""

GOOD = [0, 0, 0, 4]
AE = [0, 2, 0, 4]
GC = [0, 0, 0, 20, 240, 66, 80, 78, 189, 77, 223, 230, 139, 100, 140, 194, 246, 137, 141, 104]
OTP = [0, 0, 0, 52, 7, 2, 31, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 18, 52, 17, 68, 68, 65, 68, 17, 68, 20, 0, 0, 0, 0, 1, 0, 0, 64]

#cmd = 0xFE010000
#C = bytepack(O)
#hexdump(C)
#print DBG_CMDRESP[cmd](C).show2()
#C = arraypack(OTP)
#hexdump(C)
#print RESP_raw(C).show2()
