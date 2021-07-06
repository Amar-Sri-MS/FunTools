little_endian

requires 0 "1E 5C 00 B1"
hex 4 "Magic BlueScie (A55E00B1)"
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
hex 64 "ECC P256 Public Key"
hex 48 "Nonce"
hex 888 "Activation Code"
section "Signature" {
    set sig_length [uint32 "Signature Length"]
    hex $sig_length "Signature"
}
