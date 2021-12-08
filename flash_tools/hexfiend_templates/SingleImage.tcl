# This is related to Flash_Image.tcl

little_endian

bytes 1096 "customer certificate"
bytes 428 "padding"
bytes 8   "customer magic"
bytes 516 "customer signature"
bytes 1096 "signing info"
bytes 428 "padding"
bytes 8    "fungible magic"
bytes 516 "signature"
set image_size [uint32 "size"]
uint32 "version"
ascii 4 "type"
section "attributes" {
    section "Part Number" {
	hex 1 "Family"
	hex 1 "Device"
	hex 1 "Revision"
	hex 1 "Alignment"
    }
    section AuthLocation {
	hex 4 "Location"
    }
    hex 24 "padding"
    ascii 32 "description"
}
entry "payload" bytes  $image_size
