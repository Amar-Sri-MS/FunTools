# This is related to Flash_Image.tcl

little_endian

bytes 1096 "customer certificate"
bytes 436 "padding"
bytes 516 "customer signature"
bytes 1096 "signing info"
bytes 436 "padding"
bytes 516 "signature"
set image_size [uint32 "size"]
uint32 "version"
ascii 4 "type"
section "attributes" {
    ascii 32 "reserved"
    ascii 32 "description"
}
entry "payload" bytes  $image_size
