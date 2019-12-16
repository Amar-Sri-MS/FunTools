little_endian

requires 0 "A5 5E 00 B1"
hex 4 "Magic BlueSeas (A55E00B1)"
hex 4 "Debug Locks"
hex 1 "Authorizations"
hex 1 "Key Index (unused)"
hex 2 "Reserved (Zero)"
uint32 "Tamper Authorizations (unused)"
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
    hex 6 "Reserved (Zero)"
    hex 4 "S/N"
}
section "Serial Info Mask" {
    hex 8 "Raw Value"
}
section "Serial Number Mask" {
        section "Part Number" {
	hex 1 "Family"
	hex 1 "Device"
	hex 1 "Revision"
    }
    hex 1 "Foundry + Fab"
    hex 1 "Year"
    hex 1 "Week"
    hex 6 "Reserved (Zero)"
    hex 4 "S/N"
}
section "Key" {
    set save_pos [pos]
    set key_length [uint32 "Key Length"]
    hex $key_length "Key"
    goto [expr {$save_pos + 4 + 512}]
}
