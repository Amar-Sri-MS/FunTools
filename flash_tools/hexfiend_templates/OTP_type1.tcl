include SBP_common.tcl

set security1 [hex 1 "Security"]
section "Security Flags" {
    entry "HW Lock" [expr $security1 & 1]
    entry "Secure boot" [expr ($security1 >> 1) & 1]
    entry "Watchdog" [expr ($security1 >> 2) & 1]
}
set security2 [hex 1 "Security-Extra"]
section "Security-Extra Flags" {
    entry "Customer" [expr $security2 & 1]
    entry "I2C challenge" [expr ($security2 >> 1) & 1]
    entry "CC DBU master" [expr ($security2 >> 2) & 1]
    entry "PC DBU master" [expr ($security2 >> 3) & 1]
}

hex 1 "Tamper filtering period"
hex 1 "Tamper filtering threshold"
set debug_prots [hex 4 "Debug Protection Locks"]
section "Flags" {
    entry "repeat" [expr $debug_prots]
}

section "Serial Info" {
    hex 8 "Raw Value"
}

section "Serial Number" {
    serial_number
}

section "Tamper levels" {
    hex 1 "Tamper 1"
    hex 1 "Tamper 2"
    hex 1 "Tamper 3"
    hex 1 "Tamper 4"
    hex 1 "Tamper 5"
    hex 1 "Tamper 6"
    hex 1 "Tamper 7"
    hex 1 "Tamper 8"
    hex 1 "Tamper 9"
    hex 1 "Tamper 10"
    hex 1 "Tamper 11"
    hex 1 "Tamper 12"
    hex 1 "Tamper 13"
    hex 1 "Tamper 14"
    hex 1 "Tamper 15"
    hex 1 "Tamper 16"
}

section "Customer" {
    hex 1 "Security"
    hex 1 "Valid Keys"
    hex 1 "Revoked Keys"
    hex 1 "Key Type"
    hex 4 "Debug Protection Locks"
    hex 1 "Number zeroes in key 1 hash"
    hex 1 "Number zeroes in key 2 hash"
    hex 6 "Reserved"
    hex 16 "Customer firmware root key"
    hex 32 "Key 1 Hash"
    hex 32 "Key 2 Hash"
}
