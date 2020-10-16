#  Perl script that will parse HDMA command list dump in FunOS log
If FunOS enables dump of the DMA WU and the command list then this script 
will parse it to display in a human readable format as well as provide
errors and warnings if it sees any issues.

An Example of FunOS dumping the DMA command list can be seen in flow/eqsq.c
        syslog_hex_dump(CRIT, (uint8_t *)cmdlist,
                        dump_len, "SQ DMA CMDLIST");
        syslog_hex_dump(CRIT, (uint8_t *)&dma_wu,
                        sizeof(dma_wu), "SQ DMA WU");


WARNING is printed if any of the following conditions are encountered.
1) Total number of Gather bytes does not match total number of Scatter bytes.
2) Scatter F1 zero-byte commands exist.
3) A mix of Scatter F1 and PCIe commands exist.

Here are the searchable tags in the output of this script:

HDMA_LOG_DUMP: This is the start of a HDMA WU stack (WU and command list). The dump of the original log file follows this tag.
HDMA_PARSE: This is where the parsing of the WU fields and command list starts.
ERROR: Any problems detected in the WU or commands will be flagged with this tag.
WARNING: Any issues that could lead to side effects, such as the STR non-fatal interrupts that led to the JIRA issue in the first place, will be flagged with this tag.



to run the script:
./parse_hdma_cmds.pl uartout0.0.txt

Sample script output:
[HDMA_LOG_DUMP] Detected start of command list and HDMA WU
Log file dump:
[315.537516 6.0.3] [SQ DMA CMDLIST]: dump of 120 bytes starting from 0x880000332c6f8000^M
[315.540732 6.0.3] 00000000: 2110a40000000000 1200d90000000040 ^M
[315.542541 6.0.3] 00000010: 0000000467f14780 8600000000000040 ^M
[315.542595 6.0.3] 00000020: 000000332c6f8000 e400000000000020 ^M
[315.542620 6.0.3] 00000030: 82920cb010630aa0 0000000000000001 ^M
[315.542644 6.0.3] 00000040: a8000000b318a000 880000332c6f8000 ^M
[315.542669 6.0.3] 00000050: e500000000000020 82920cb010630a90 ^M
[315.542693 6.0.3] 00000060: 0000000000000001 a8000000b318a000 ^M
[315.542714 6.0.3] 00000070: 880000332c6f8000 ^M
[315.542730 6.0.3] [SQ DMA WU]: dump of 32 bytes starting from 0xc000000010bd2e70^M
[315.542759 6.0.3] 00000000: 8200260920630a90 100f00332c6f8000 ^M
[315.542783 6.0.3] 00000010: 4c00004000000000 0000000000000000 ^M

[HDMA_PARSE] Starting to parse HDMA WU fields and command list
WU fields:
  CMDLIST_SIZE: 15, CMDLIST_PTR: 0x332c6f8000
  CMD = 0x10, SO = 0, VC = 2, SGID = 0x0, SLID = 0x0, DGID = 0x13, QID = 0x92, SW_OPCODE = 0xa90
  FLAGS: OW = 0, OR = 0, INS = 1, FREE = 0, RO = 0, SO = 0, CWU = 0
  OPR: PIPE = 12, LENGTH = 64, TYPE = 0, CHK = 0, SEED = 0, PI = 0
CMD 0: GTR Inline PCIe control
  FUNC_ID = 0x10a, PF_ID = 0x2, VF_ID = 0x0, PASID = 0x0
CMD 1: GTR PCIe read
  ADDR = 0x467f14780, LEN = 64
  MRS = 6, MPS = 3, NS = 0, RO = 1, AT = 0, PH = 0, TH = 0
  ST_TAG = 0x0, ST = 0, ST_CTRL = 0, PASID_PRE_EXIST = 0
CMD 2: STR F1 write
  ADDR = 0x332c6f8000, LEN = 64, FLAGS = 0x0, INS = BM
CMD 3: CMP SN message  LEN = 32, COND = Success
  Data: 0x82920cb0
  Data: 0x10630aa0
  Data: 0x00000000
  Data: 0x00000001
  Data: 0xa8000000
  Data: 0xb318a000
  Data: 0x88000033
  Data: 0x2c6f8000
CMD 4: CMP SN message  LEN = 32, COND = Fail
  Data: 0x82920cb0
  Data: 0x10630a90
  Data: 0x00000000
  Data: 0x00000001
  Data: 0xa8000000
  Data: 0xb318a000
  Data: 0x88000033
  Data: 0x2c6f8000
Sum of GTR bytes: 64
Sum of STR bytes: 64


