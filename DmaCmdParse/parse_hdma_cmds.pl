#!/usr/bin/perl
use strict;

my @cmdlist_qword;
my @dma_wu_qword;

# Arguments: DWord number, start bit, number of bits, list of hex qwords
sub bit_slice {
    my $num_arg = scalar(@_);
    if ($num_arg < 4) {
        die "Sanity check, bit_slice() called with wrong number of arguments";
    }
    my $dword_num = $_[0];
    my $start_bit = $_[1];
    if ($start_bit >= 32) {
        die "Sanity check, bit_slice() called with bad start_bit of ${start_bit}";
    }
    my $num_bits = $_[2];
    if (($num_bits + $start_bit) > 32) {
        die "Sanity check, bit_slice() called with bad start_bit ${start_bit} and num_bits ${num_bits}";
    }
    my $qword_num = $dword_num >> 1;
    if ($qword_num > ($num_arg - 4)) {
        die "Sanity check, bit_slice() called with out of range dword_num = ${dword_num}";
    }
    my $qword_start_bit = $start_bit + (($dword_num % 2) ? 0 : 32);
    my $qword = hex($_[$qword_num + 3]);
    my $val = ($qword >> $qword_start_bit);
    $val &= ((1 << $num_bits) - 1);
    return $val;
}

sub ins2str {
    my $num_arg = scalar(@_);
    if ($num_arg != 1) {
        die "Sanity check, ins2str() called with wrong number of arguments";
    }
    my $ins = $_[0];
    if ($ins == 0) { return "CM"; }
    elsif ($ins == 1) { return "BM"; }
    elsif ($ins == 2) { return "HBM"; }
    elsif ($ins == 3) { return "DDR"; }
    else {
        die "Sanity check, ins2str() called with bad argument: ${ins}";
    }
}

sub cond2str {
    my $num_arg = scalar(@_);
    if ($num_arg != 1) {
        die "Sanity check, cond2str() called with wrong number of arguments";
    }
    my $cond = $_[0];
    if ($cond == 0) { return "Success"; }
    elsif ($cond == 1) { return "Fail"; }
    elsif ($cond == 3) { return "Any"; }
    else {
        die "Sanity check, cond2str() called with bad argument: ${cond}";
    }
}

sub decode_pcie_ctrl {
    my $num_arg = scalar(@_);
    if ($num_arg < 1) {
        die "Sanity check, decode_pcie_ctrl() called with empty array";
    }
    my $func_id = bit_slice(0, 12, 9, @_);
    my $pf_id = bit_slice(0, 9, 3, @_);
    my $vf_id = bit_slice(0, 0, 9, @_);
    my $pasid = bit_slice(1, 0, 32, @_);
    printf("  FUNC_ID = 0x%0x, PF_ID = 0x%0x, VF_ID = 0x%0x, PASID = 0x%0x\n",
           $func_id, $pf_id, $vf_id, $pasid);
}

sub decode_pcie_info {
    my $num_arg = scalar(@_);
    if ($num_arg < 1) {
        die "Sanity check, decode_pcie_info() called with empty array";
    }
    my $mrs = bit_slice(0, 13, 3, @_);
    my $mps = bit_slice(0, 11, 2, @_);
    my $ns = bit_slice(0, 9, 1, @_);
    my $ro = bit_slice(0, 8, 1, @_);
    my $at = bit_slice(0, 7, 1, @_);
    my $ph = bit_slice(0, 5, 2, @_);
    my $th = bit_slice(0, 4, 1, @_);
    my $st_tag = (bit_slice(0, 0, 4, @_) << 12 | bit_slice(1, 20, 12, @_));
    my $st = bit_slice(1, 19, 1, @_);
    my $st_ctrl = bit_slice(1, 17, 2, @_);
    my $pasid_pre = bit_slice(1, 16, 1, @_);
    printf("  MRS = %0d, MPS = %0d, NS = %0d, RO = %0d, AT = %0d, PH = %0d, TH = %0d\n",
           $mrs, $mps, $ns, $ro, $at, $ph, $th);
    printf("  ST_TAG = 0x%0x, ST = %0d, ST_CTRL = %0d, PASID_PRE_EXIST = %0d\n",
           $st_tag, $st, $st_ctrl, $pasid_pre);
}

my $numArgs = $#ARGV + 1;
my $mode = "logfile";
if ($numArgs > 2) {
    die "Too many arguments.";
} elsif ($numArgs == 0) {
    open(LOG, '-');
} else {
    my $arg1 = $ARGV[0];
    my $dasharg = 0;
    if ($arg1 eq "-cmdlist") {
        $mode = "cmdlist";
        $dasharg = 1;
    } elsif ($arg1 eq "-wu") {
        $mode = "wu";
        $dasharg = 1;
    } elsif ($numArgs == 2) {
        die "Invalid first argument: ${arg1}"
    }
    if ($dasharg) {
        if ($numArgs == 2) {
            open(LOG, "< ${ARGV[1]}") || die("Can't open logfile: $!");
        } else {
            open(LOG, '-');
        }
    } else {
        open(LOG, "< ${ARGV[0]}") || die("Can't open logfile: $!");
    }
}

my $err_cnt = 0;
my $warn_cnt = 0;

while (1) {
    my $letter;
    my $cmdlist_bytes;

    @cmdlist_qword = ();
    @dma_wu_qword = ();

    # ----------------------------------------
    # Logfile mode: Look for CMDLIST header
    # ----------------------------------------
    my $eof = 0;
    if ($mode eq "logfile") {
        $eof = 1;
        while (<LOG>) {
            if (/\[([SC])Q DMA CMDLIST\]: dump of (\d+) bytes starting from/) {
                $eof = 0;
                $letter = $1;
                $cmdlist_bytes = $2;
                print "\n";
                print "[HDMA_LOG_DUMP] Detected start of command list and HDMA WU\n";
                print "Log file dump:\n";
                print "$_";
                last;
            }
        }
        if ($cmdlist_bytes % 8 != 0) {
            die "Number of bytes dumped out in command list is not divisible by 8";
        }
    }
    last if $eof;

    # ----------------------------------------
    # Get command list bytes
    # ----------------------------------------
    if ($mode ne "wu") {
        my $bytecnt = 0;
        my $startflag = 0;
        while (<LOG>) {
            if ($mode eq "logfile") {
                print "$_";
            }
            if (/(\w+): (\w{16}) (\w{16})/) {
                if (hex($1) != $bytecnt) {
                    if ($mode eq "logfile") {
                        die "Bad byte number";                        
                    } elsif ($startflag) {
                        last;
                    }
                }
                $startflag = 1;
                $bytecnt += 16;
                push @cmdlist_qword, $2;
                push @cmdlist_qword, $3;
            } elsif (/(\w+): (\w{16})/) {
                if (hex($1) != $bytecnt) {
                    if ($mode eq "logfile") {
                        die "Bad byte number";                        
                    } elsif ($startflag) {
                        last;
                    }
                }
                $startflag = 1;
                $bytecnt += 8;
                push @cmdlist_qword, $2;
            } else {
                if ($mode eq "logfile" && !$startflag) {
                    die "Could not parse line";                    
                } elsif ($startflag) {
                    last;
                }
            }
        }
        if (!$startflag) {
            die "Premature end-of-file reached while looking for command list hexdump"
        }
    }

    #print "Saw command list:\n";
    #for (my $i = 0; $i < scalar @cmdlist_qword; $i++) {
    #    print "${i}: ${cmdlist_qword[$i]}\n";
    #}

    # ----------------------------------------
    # Logfile mode: Look for WU header
    # ----------------------------------------
    if ($mode eq "logfile") {
        if (/\[([SC])Q DMA WU\]: dump of 32 bytes starting from/) {
            if ($letter ne $1) {
                die "Expected ${letter}Q DMA WU but got ${1}Q DMA WU";
            }
        } else {
            die "Expected DMA WU immediately following command list";
        }
    }

    # ----------------------------------------
    # Then get DMA WU bytes
    # ----------------------------------------
    if ($mode ne "cmdlist") {
        my $bytecnt = 0;
        my $startflag = 0;
        while (<LOG>) {
            if ($mode eq "logfile") {
                print "$_";
            }
            if (/(\w+): (\w{16}) (\w{16})/) {
                if (hex($1) != $bytecnt) {
                    if ($mode eq "logfile") {
                        die "Bad byte number";
                    } elsif ($startflag) {
                        last;
                    }
                }
                $startflag = 1;
                $bytecnt += 16;
                push @dma_wu_qword, $2;
                push @dma_wu_qword, $3;
            } else {
                if ($mode eq "logfile" && !$startflag) {
                    die "Could not parse line";                    
                } elsif ($startflag) {
                    last;
                }
            }
            if ($bytecnt == 32) {
                last;
            } elsif ($bytecnt > 32) {
                die "Too many WU bytes"                
            }
        }
        if (!$startflag) {
            die "Premature end-of-file reached while looking for command list hexdump"
        } elsif ($bytecnt != 32) {
            die "Expected 32 bytes in WU hexdump but only saw ${bytecnt}"
        }
    }

    #print "Saw DMA WU:\n";
    #for (my $i = 0; $i < scalar @dma_wu_qword; $i++) {
    #    print "${i}: ${dma_wu_qword[$i]}\n";
    #}

    # ----------------------------------------
    # Parse DMA WU
    # ----------------------------------------
    my $wu_flags_cwu;
    my $opr_flags_type;
    my $opr_len;
    if ($mode ne "cmdlist") {
        # Check that the DMA WU opcode is correct.
        my $qword = hex($dma_wu_qword[0]);
        my $wu_opcode = $qword >> 59;
        if ($wu_opcode != 0x10) {
            printf("[ERROR]: Invalid WU opcode seen, expected 0x10 but saw 0x%0x\n", $wu_opcode);
            $err_cnt++;
        }

        # Get the WU fields
        my $wu_cmd = bit_slice(0, 27, 5, @dma_wu_qword);
        my $wu_so = bit_slice(0, 26, 1, @dma_wu_qword);
        my $wu_vc = bit_slice(0, 24, 2, @dma_wu_qword);
        my $wu_sgid = bit_slice(0, 19, 5, @dma_wu_qword);
        my $wu_slid = bit_slice(0, 14, 5, @dma_wu_qword);
        my $wu_dgid = bit_slice(0, 9, 5, @dma_wu_qword);
        my $wu_queueid = (bit_slice(0, 0, 7, @dma_wu_qword) << 4) + (bit_slice(1, 28, 4, @dma_wu_qword));
        my $wu_sw_opcodes = bit_slice(1, 0, 16, @dma_wu_qword);
        my $wu_flags_ow = bit_slice(2, 31, 1, @dma_wu_qword);
        my $wu_flags_or = bit_slice(2, 30, 1, @dma_wu_qword);
        my $wu_flags_ins = bit_slice(2, 28, 2, @dma_wu_qword);
        my $wu_flags_free = bit_slice(2, 27, 1, @dma_wu_qword);
        my $wu_flags_ro = bit_slice(2, 26, 1, @dma_wu_qword);
        my $wu_flags_so = bit_slice(2, 25, 1, @dma_wu_qword);
        $wu_flags_cwu = bit_slice(2, 24, 1, @dma_wu_qword);
        my $wu_cmdlist_size = bit_slice(2, 16, 8, @dma_wu_qword);
        my $wu_cmdlist_ptr = (bit_slice(2, 0, 16, @dma_wu_qword) << 32) + (bit_slice(3, 0, 32, @dma_wu_qword));
        my $opr_opc = bit_slice(4, 30, 2, @dma_wu_qword);
        my $opr_pipe = bit_slice(4, 24, 6, @dma_wu_qword);
        $opr_flags_type = bit_slice(4, 16, 3, @dma_wu_qword);
        my $opr_flags_chk = bit_slice(4, 19, 1, @dma_wu_qword);
        my $opr_flags_seed = bit_slice(4, 21, 1, @dma_wu_qword);
        my $opr_flags_pi = bit_slice(4, 22, 1, @dma_wu_qword);
        $opr_len = bit_slice(4, 0, 16, @dma_wu_qword);

        if ($mode eq "logfile") {
            print "\n";
            print "[HDMA_PARSE] Starting to parse HDMA WU fields and command list\n";
        }
        printf("WU fields:\n");
        printf("  CMDLIST_SIZE: %0d, CMDLIST_PTR: 0x%0x\n", $wu_cmdlist_size, $wu_cmdlist_ptr);
        printf("  CMD = 0x%0x, SO = %0d, VC = %0d, SGID = 0x%0x, SLID = 0x%0x, DGID = 0x%0x, QID = 0x%0x, SW_OPCODE = 0x%0x\n",
               $wu_cmd, $wu_so, $wu_vc, $wu_sgid, $wu_slid, $wu_dgid, $wu_queueid, $wu_sw_opcodes);
        printf("  FLAGS: OW = %0d, OR = %0d, INS = %0d, FREE = %0d, RO = %0d, SO = %0d, CWU = %0d\n",
               $wu_flags_ow, $wu_flags_or, $wu_flags_ins, $wu_flags_free, $wu_flags_ro, $wu_flags_so, $wu_flags_cwu);
        printf("  OPR: PIPE = %0d, LENGTH = %0d, TYPE = %0d, CHK = %0d, SEED = %0d, PI = %0d\n",
               $opr_pipe, $opr_len, $opr_flags_type, $opr_flags_chk, $opr_flags_seed, $opr_flags_pi);

        # Do some checks on the WU fields
        if ($wu_cmd != 0x10) {
            printf("[ERROR]: Invalid WU opcode 0x%0x\n", $wu_cmd);
            $err_cnt++;
        }
        my $exp_wu_cmdlist_size = scalar(@cmdlist_qword) + $wu_flags_cwu * 4;
        if ($mode eq "logfile" && $wu_cmdlist_size != $exp_wu_cmdlist_size) {
            printf("[ERROR]: Command list size mismatch, expected %0d\n", $exp_wu_cmdlist_size);
            $err_cnt++;
        }
        if ($opr_opc != 0x1) {
            printf("[ERROR]: Invalid OPR OPC field, expected 1 but saw %0d\n", $opr_opc);
            $err_cnt++;
       }
    }

    # ----------------------------------------
    # Parse the command list
    # ----------------------------------------
    if ($mode ne "wu") {
        # Figure out if the command list starts with a CWU or a Gather command
        my $cmd_opc = bit_slice(0, 30, 2, @cmdlist_qword);
        my $wu_opcode = bit_slice(0, 27, 5, @cmdlist_qword);
        if (($wu_opcode & 0x1e) == 0x10) {
            if ($mode eq "logfile" && !$wu_flags_cwu) {
                printf("[ERROR]: Command list seems to start with continuation WU, but CWU flag was not set in DMA WU\n");
                $err_cnt++;
            }
            $wu_flags_cwu = 1;
        } elsif ($cmd_opc == 0) {
            if ($mode eq "logfile" && $wu_flags_cwu) {
                printf("[ERROR]: Expected command list to start with continuation WU, but CWU opcode was incorrect: 0x%0x\n", $wu_opcode);
                $err_cnt++;
            }
            $wu_flags_cwu = 0;
        } else {
            printf("[ERROR]: Command list did not start with either continuation WU or gather command\n");
            $wu_flags_cwu = 0;
            $err_cnt++;
        }

        # First, strip off the continuation WU, if it exists.
        # TODO: Parse the CWU fields
        if ($wu_flags_cwu) {
            if (scalar(@cmdlist_qword) < 4) {
                die "Unexpected end of command list seen while parsing continuation WU";
            }
            printf("Continuation WU:\n");
            printf("  0: %0s\n", shift(@cmdlist_qword));
            printf("  1: %0s\n", shift(@cmdlist_qword));
            printf("  2: %0s\n", shift(@cmdlist_qword));
            printf("  3: %0s\n", shift(@cmdlist_qword));
        }

        # Now go down the command list, qword by qword
        my $cmd_num = 0;
        my $gtr_sum = 0;
        my $str_sum = 0;
        my $warn_str_0b = 0;
        my $warn_str_f1 = 0;
        my $warn_str_pcie = 0;
        my $qword;
        my $gtr_eop = 0;
        my $str_eop = 0;
        while (scalar(@cmdlist_qword) > 0) {
            my $cmd_opc = bit_slice(0, 30, 2, @cmdlist_qword);
            my $cmd_tgt = bit_slice(0, 28, 2, @cmdlist_qword);
            my $cmd_ins = bit_slice(0, 26, 2, @cmdlist_qword);
            my $cmd_type = bit_slice(0, 24, 2, @cmdlist_qword);
            my $eop;
            my $eop_str;
            
            # ----------------------------------------
            # Gather commands
            # ----------------------------------------
            if ($cmd_opc == 0) {
                if ($cmd_tgt == 0) {
                    my $bm_flags = bit_slice(1, 16, 8, @cmdlist_qword);
                    my $len = bit_slice(1, 0, 16, @cmdlist_qword);
                    my $addr = (bit_slice(2, 0, 16, @cmdlist_qword) << 32) + (bit_slice(3, 0, 32, @cmdlist_qword));
                    my $ins_str = ins2str($cmd_ins);

                    if ($cmd_type == 2) {
                        $eop = 1;
                        $eop_str = ", EOP"
                    } else {
                        $eop = 0;
                        $eop_str = "";
                    }
                    printf("CMD %0d: GTR F1 read\n", $cmd_num);
                    printf("  ADDR = 0x%0x, LEN = %0d, BM_FLAGS = 0x%0x, INS = %0s%0s\n",
                        $addr, $len, $bm_flags, $ins_str, $eop_str);
                    if ($cmd_type == 1 || $cmd_type == 3) {
                        printf("[ERROR] GTR F1 read command had invalid TYPE of %0d\n", $cmd_type);
                        $err_cnt++;
                    }
                    $qword = shift(@cmdlist_qword);
                    $qword = shift(@cmdlist_qword);
                    $gtr_sum += $len;
                } elsif ($cmd_tgt == 1) {
                    my $len = bit_slice(1, 0, 16, @cmdlist_qword);
                    my $addr;
                    my $rmmu_idx;

                    if ($cmd_type == 2) {
                        $eop = 1;
                        $eop_str = ", EOP"
                    } else {
                        $eop = 0;
                        $eop_str = "";
                    }
                    if ($cmd_ins == 0) {
                        $addr = (bit_slice(2, 0, 32, @cmdlist_qword) << 32) + (bit_slice(3, 0, 32, @cmdlist_qword));
                        printf("CMD %0d: GTR PCIe read\n", $cmd_num);
                        printf("  ADDR = 0x%0x, LEN = %0d%0s\n", $addr, $len, $eop_str);
                    } elsif ($cmd_ins == 1) {
                        $rmmu_idx = bit_slice(3, 2, 10, @cmdlist_qword);
                        printf("CMD %0d: GTR read from RMMU\n, $cmd_num");
                        printf("  IDX = %0d%0s\n", $rmmu_idx, $eop_str);
                    }
                    decode_pcie_info(@cmdlist_qword);
                    if ($cmd_type == 1 || $cmd_type == 3) {
                        printf("[ERROR] GTR PCIe read command had invalid TYPE of %0d\n", $cmd_type);
                        $err_cnt++;
                    }
                    $qword = shift(@cmdlist_qword);
                    $qword = shift(@cmdlist_qword);
                    $gtr_sum += $len;
                } elsif ($cmd_tgt == 2 && ($cmd_type == 0 || $cmd_type == 2)) {
                    my $imm_len = bit_slice(0, 16, 8, @cmdlist_qword);
                    my $imm_off = bit_slice(0, 8, 4, @cmdlist_qword);
                    my $imm_cmd_bytes = 3 + $imm_len + $imm_off;
                    my $imm_cmd_qwords = $imm_cmd_bytes / 8;

                    if ($imm_cmd_bytes % 8) {
                        $imm_cmd_qwords++;
                    }
                    if ($cmd_type == 2) {
                        $eop = 1;
                        $eop_str = ", EOP"
                    } else {
                        $eop = 0;
                        $eop_str = "";
                    }

                    printf("CMD %0d: GTR Inline Immediate\n", $cmd_num);
                    printf("  LEN = %0d, OFFSET = %0d%0s\n", $imm_len, $imm_off, $eop_str);
                    my $in_ptr = 3;
                    my $out_cnt = 0;
                    my $dword = 0;
                    for (my $i = 0; $i < $imm_len + $imm_off; $i++) {
                        if ($i < $imm_off) { next; }
                        $dword <<= 8;
                        $dword |= (hex($cmdlist_qword[$in_ptr / 8]) >> ((7 - $in_ptr % 8) * 8)) & 0xff;
                        $out_cnt++;
                        if ($out_cnt == 4) {
                            printf("  Data: 0x%08x\n", $dword);
                            $out_cnt = 0;
                            $dword = 0;
                        }
                    }
                    for (my $i = 0; $i < $imm_cmd_qwords; $i++) {
                        $qword = shift(@cmdlist_qword);
                    }
                    $gtr_sum += $imm_len;
                } elsif ($cmd_tgt == 2) {
                    if ($cmd_type == 1) {
                        printf("CMD %0d: GTR Inline PCIe control\n", $cmd_num);
                        decode_pcie_ctrl(@cmdlist_qword);
                        $qword = shift(@cmdlist_qword);
                    } else {
                        printf("[ERROR] GTR Inline PCIe control command had invalid TYPE of %0d\n", $cmd_type);                                    
                        $err_cnt++;
                    }
                } elsif ($cmd_tgt == 3) {
                    my $len = bit_slice(1, 0, 16, @cmdlist_qword);
                    my $pat0 = bit_slice(2, 0, 32, @cmdlist_qword);
                    my $pat1 = bit_slice(3, 0, 32, @cmdlist_qword);

                    if ($cmd_type == 2) {
                        $eop = 1;
                        $eop_str = ", EOP"
                    } else {
                        $eop = 0;
                        $eop_str = "";
                    }
                    printf("CMD %0d: GTR Inline Generated\n", $cmd_num);
                    printf("  LEN = %0d%0s\n", $len, $eop_str);
                    printf("  PATTERN[63:32] = 0x%08x\n", $pat0);
                    printf("  PATTERN[31:0]  = 0x%08x\n", $pat1);
                    if ($cmd_type == 1 || $cmd_type == 3) {
                        printf("[ERROR] GTR Inline Generated command had invalid TYPE of %0d\n", $cmd_type);
                        $err_cnt++;
                    }
                    $qword = shift(@cmdlist_qword);
                    $qword = shift(@cmdlist_qword);
                    $gtr_sum += $len;
                } else {
                    printf("[ERROR] while parsing GTR command\n");
                    $err_cnt++;
                    last;
                }

                if ($gtr_eop) {
                    if ($eop) {
                        printf("[ERROR] Two or more GTR commands has EOP set. (Only the last GTR command should have EOP set.)\n");
                        $err_cnt++;
                    } else {
                        printf("[ERROR] Another GTR command seen after EOP. (EOP shall only be set on the last GTR command.)\n");
                        $err_cnt++;
                    }
                }
                if ($eop) {
                    $gtr_eop = 1;
                }
            }

            # ----------------------------------------
            # Should not see operator commands in command list
            # ----------------------------------------
            elsif ($cmd_opc == 1) {
                printf("[ERROR] Should not see OPR command in command list\n");
                $err_cnt++;
                # This is not likely to be a valid OPR command.
                # But just pull the typical size of an OPR command just for the heck of it.
                $qword = shift(@cmdlist_qword);
                $qword = shift(@cmdlist_qword);                
            }

            # ----------------------------------------
            # Scatter commands
            # ----------------------------------------
            elsif ($cmd_opc == 2) {
                if ($cmd_tgt == 0) {
                    my $flags = bit_slice(0, 16, 8, @cmdlist_qword);
                    my $len = bit_slice(1, 0, 8, @cmdlist_qword);
                    my $addr = (bit_slice(2, 0, 16, @cmdlist_qword) << 32) + (bit_slice(3, 0, 32, @cmdlist_qword));
                    my $ins_str = ins2str($cmd_ins);

                    if ($cmd_type == 2) {
                        $eop = 1;
                        $eop_str = ", EOP"
                    } else {
                        $eop = 0;
                        $eop_str = "";
                    }

                    printf("CMD %0d: STR F1 write\n", $cmd_num);
                    printf("  ADDR = 0x%0x, LEN = %0d, FLAGS = 0x%0x, INS = %0s%0s\n",
                        $addr, $len, $flags, $ins_str, $eop_str);
                    if ($cmd_type == 1 || $cmd_type == 3) {
                        printf("[ERROR] STR F1 write command had invalid TYPE of %0d\n", $cmd_type);
                        $err_cnt++;
                    }
                    $qword = shift(@cmdlist_qword);
                    $qword = shift(@cmdlist_qword);
                    $str_sum += $len;
                    $warn_str_f1 = 1;
                    if ($len == 0) { $warn_str_0b = 1; }
                } elsif ($cmd_tgt == 1) {
                    my $len = bit_slice(1, 0, 16, @cmdlist_qword);

                    if ($cmd_type == 2) {
                        $eop = 1;
                        $eop_str = ", EOP"
                    } else {
                        $eop = 0;
                        $eop_str = "";
                    }

                    if ($cmd_ins == 0) {
                        my $addr = (bit_slice(2, 0, 32, @cmdlist_qword) << 32) + (bit_slice(3, 0, 32, @cmdlist_qword));
                        my $prepend = bit_slice(0, 20, 1, @cmdlist_qword);
                        my $append = bit_slice(0, 20, 1, @cmdlist_qword);
                        printf("CMD %0d: STR PCIe write\n", $cmd_num);
                        printf("  ADDR = 0x%0x, LEN = %0d, PREPEND = %0d, APPEND = %0d%0s\n",
                               $addr, $len, $prepend, $append, $eop_str);
                    } elsif ($cmd_ins == 1) {
                        my $rmmu_idx = bit_slice(3, 2, 10, @cmdlist_qword);
                        printf("CMD %0d: STR write to RMMU\n", $cmd_num);
                        printf("  IDX = %0d%0s\n", $rmmu_idx, $eop_str);
                    } elsif ($cmd_ins == 3) {
                        my $func_id = bit_slice(2, 16, 9, @cmdlist_qword);
                        my $int_vec = bit_slice(2, 0, 11, @cmdlist_qword);
                        printf("CMD %0d: STR PCIe interrupt\n", $cmd_num);
                        printf("  FUNC_ID = 0x%0x, INT_VEC = 0x%0x%0s\n", $func_id, $int_vec, $eop_str);
                    }
                    decode_pcie_info(@cmdlist_qword);
                    if ($cmd_type == 1 || $cmd_type == 3) {
                        printf("[ERROR] STR PCIe write command had invalid TYPE of %0d\n", $cmd_type);
                        $err_cnt++;
                    }
                    $qword = shift(@cmdlist_qword);
                    $qword = shift(@cmdlist_qword);
                    $str_sum += $len;
                    $warn_str_pcie = 1;
                } elsif ($cmd_tgt == 2) {
                    printf("CMD %0d: STR Inline PCIe control\n", $cmd_num);
                    decode_pcie_ctrl(@cmdlist_qword);
                    if ($cmd_type != 1) {
                        printf("[ERROR] STR Inline PCIe control command had invalid TYPE of %0d\n", $cmd_type);
                        $err_cnt++;
                    }
                    $qword = shift(@cmdlist_qword);
                } else {
                    my $len = bit_slice(1, 0, 16, @cmdlist_qword);

                    if ($cmd_type == 2) {
                        $eop = 1;
                        $eop_str = ", EOP"
                    } else {
                        $eop = 0;
                        $eop_str = "";
                    }

                    printf("CMD %0d: STR NULL (Delete)\n", $cmd_num);
                    printf("  LEN = %0d%0s\n", $len, $eop_str);
                    if ($cmd_type == 1 || $cmd_type == 3) {
                        printf("[ERROR] STR NULL (Delete) command had invalid TYPE of %0d\n", $cmd_type);
                        $err_cnt++;
                    }
                    $qword = shift(@cmdlist_qword);
                    $str_sum += $len;
                }

                if ($str_eop) {
                    if ($eop) {
                        printf("[ERROR] Two or more STR commands has EOP set. (Only the last STR command should have EOP set.)\n");
                    } else {
                        printf("[ERROR] Another STR command seen after EOP. (EOP shall only be set on the last STR command.)\n");
                    }
                    $err_cnt++;
                }
                if ($eop) {
                    $str_eop = 1;
                }
            }

            # ----------------------------------------
            # Completion commands
            # ----------------------------------------
            elsif ($cmd_opc == 3) {
                if ($cmd_tgt == 0) {
                    my $flags = bit_slice(0, 16, 8, @cmdlist_qword);
                    my $addr = (bit_slice(2, 0, 16, @cmdlist_qword) << 32) + (bit_slice(3, 0, 32, @cmdlist_qword));
                    my $ins_str = ins2str($cmd_ins);
                    my $cond_str = cond2str($cmd_type);
                    my $len = bit_slice(1, 0, 16, @cmdlist_qword);
                    my $cmd_bytes = 16 + $len;
                    my $cmd_qwords = $cmd_bytes / 8;
                    my $dword = 0;
                    if ($cmd_bytes % 8) { $cmd_qwords++; }
                    printf("CMD %0d: CMP F1 memory write", $cmd_num);
                    printf("  ADDR = 0x%0x, LEN = %0d, FLAGS = 0x%0x, INS = %0s, COND = %0s\n",
                        $addr, $len, $flags, $ins_str, $cond_str);
                    if ($len > 256) {
                        printf("[ERROR] Length of CMP command with immediate data cannot exceed 256B\n");
                        $err_cnt++;
                        $len = 256;
                    }
                    for (my $i = 0; $i < $len; $i += 4) {
                        $dword = (hex($cmdlist_qword[$i / 8 + 2]) >> (32 - ($i % 8 * 8))) & 0xffffffff;
                        printf("  Data: 0x%08x\n", $dword);
                    }
                    for (my $i = 0; $i < $cmd_qwords; $i++) {
                        $qword = shift(@cmdlist_qword);
                    }
                } elsif ($cmd_tgt == 1) {
                    my $cond_str = cond2str($cmd_type);
                    my $len = bit_slice(1, 0, 16, @cmdlist_qword);
                    my $cmd_bytes = 16 + $len;
                    my $cmd_qwords = $cmd_bytes / 8;
                    if ($cmd_bytes % 8) { $cmd_qwords++; }
                    if ($cmd_ins == 0) {
                        my $addr = (bit_slice(2, 0, 32, @cmdlist_qword) << 32) + (bit_slice(3, 0, 32, @cmdlist_qword));
                        my $prepend = bit_slice(0, 20, 1, @cmdlist_qword);
                        my $append = bit_slice(0, 20, 1, @cmdlist_qword);
                        printf("CMD %0d: CMP PCIe write\n", $cmd_num);
                        printf("  ADDR = 0x%0x, LEN = %0d, COND = %0s, PREPEND = %0d, APPEND = %0d\n",
                               $addr, $len, $cond_str, $prepend, $append);
                    } elsif ($cmd_ins == 1) {
                        my $rmmu_idx = bit_slice(3, 2, 10, @cmdlist_qword);
                        printf("CMD %0d: CMP write to RMMU\n", $cmd_num);
                        printf("  IDX = %0d, COND = %0s\n", $rmmu_idx, $cond_str);
                    } elsif ($cmd_ins == 3) {
                        my $func_id = bit_slice(2, 16, 9, @cmdlist_qword);
                        my $int_vec = bit_slice(2, 0, 11, @cmdlist_qword);
                        printf("CMD %0d: CMP PCIe interrupt\n", $cmd_num);
                        printf("  FUNC_ID = 0x%0x, INT_VEC = 0x%0x, COND = %0s\n", $func_id, $int_vec, $cond_str);
                    }
                    decode_pcie_info(@cmdlist_qword);
                    for (my $i = 0; $i < $len; $i += 4) {
                        my $dword = (hex($cmdlist_qword[$i / 8 + 2]) >> (32 - ($i % 8 * 8))) & 0xffffffff;
                        printf("  Data: 0x%08x\n", $dword);
                    }
                    for (my $i = 0; $i < $cmd_qwords; $i++) {
                        $qword = shift(@cmdlist_qword);
                    }
                } elsif ($cmd_tgt == 2) {
                    my $cond_str = cond2str($cmd_type);
                    my $len = bit_slice(1, 0, 8, @cmdlist_qword);
                    my $cmd_bytes = 8 + $len;
                    my $cmd_qwords = $cmd_bytes / 8;
                    if ($cmd_bytes % 8) { $cmd_qwords++; }
                    printf("CMD %0d: CMP SN message", $cmd_num);
                    printf("  LEN = %0d, COND = %0s\n", $len, $cond_str);
                    for (my $i = 0; $i < $len; $i += 4) {
                        my $dword = (hex($cmdlist_qword[$i / 8 + 1]) >> (32 - ($i % 8 * 8))) & 0xffffffff;
                        printf("  Data: 0x%08x\n", $dword);
                    }
                    for (my $i = 0; $i < $cmd_qwords; $i++) {
                        $qword = shift(@cmdlist_qword);
                    }
                } else {
                    printf("CMD %0d: CMP Inline PCIe control\n", $cmd_num);
                    decode_pcie_ctrl(@cmdlist_qword);
                    $qword = shift(@cmdlist_qword);
                }
            }
            $cmd_num++;
        } # while (scalar(@cmdlist_qword) > 0)

        # ----------------------------------------
        # Print the total number of GTR and STR data bytes
        # ----------------------------------------
        printf("Sum of GTR bytes: %0d\n", $gtr_sum);
        printf("Sum of STR bytes: %0d\n", $str_sum);

        # Check if GTR and STR byte sums match. (Only for COPY OPR, and only in logfile or cmdlist mode)
        # TODO: Add checks for other operator types.
        if ($mode ne "wu") {
            if ($opr_flags_type == 0 && $gtr_sum != $str_sum) {
                printf("[ERROR]: GTR and STR data byte sums mismatch! Will see STR non-fatal interrupts!\n");
                $err_cnt++;
            }
            if ($mode ne "cmdlist" && ($gtr_sum != $opr_len || $str_sum != $opr_len)) {
                printf("[ERROR]: Mismatch between OPR LENGTH (%0d) and GTR/STR byte sum\n", $opr_len);
                $err_cnt++;
            }
        }
        if ($warn_str_0b) {
            printf("[WARNING]: STR zero-byte F1 command seen! Will see STR non-fatal interrupts!\n");
            $warn_cnt++;
        }
        if ($warn_str_f1 && $warn_str_pcie) {
            printf("[WARNING]: Mix of F1 and PCIe STR commands seen! May see STR non-fatal interrupts!\n");
            $warn_cnt++;
        }
    }

    if ($mode ne "logfile") {
        last;
    }
}

printf("\n");
printf("Number of ERROR messages: %0d\n", $err_cnt);
printf("Number of WARNING messages: %0d\n", $warn_cnt);

close LOG;
