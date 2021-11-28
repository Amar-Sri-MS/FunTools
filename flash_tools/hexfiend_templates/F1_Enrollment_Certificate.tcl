little_endian

set puf_key_length 96

if { [len] == 1548 } {
    set puf_key_length 64
}

requires 0 "1E 5C 00 B1"
hex 4 "Magic BlueSeas (A55E00B1)"
hex 4 "Flags"
section "Serial Info" {
    hex 8 "Raw Value"
}
section "Serial Number" {
    section "Part Number" {
	hex 1 "Family"
	hex 1 "Device"
	hex 1 "Revision"
    }
    hex 1 "Foundry + Fab"
    hex 1 "Year"
    uint8 "Week"
    hex 2 "Security Group"
    hex 4 "Reserved (Zero)"
    hex 4 "S/N"
}
hex $puf_key_length "ECC Public Key"
hex 48 "Nonce"
hex 888 "Activation Code"
section "Signature" {
    set sig_length [uint32 "Signature Length"]
    hex $sig_length "Signature"
}
