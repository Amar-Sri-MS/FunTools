little_endian


section "Dir of Dir 1" {
    hex 4 "CRC Dir of Dir"
    set directory_1_1 [uint32  "Directory 1"]
    set directory_1_2 [uint32  "Directory 2"]
    goto 0x0200
}


section "Dir of Dir 2" {
    hex 4 "CRC Dir of Dir"
    set directory_2_1 [uint32  "Directory 1"]
    set directory_2_2 [uint32 "Directory 2"]
}

goto [expr $directory_1_1]

set images [list]

section "Directory 1" {
    hex 4 "CRC Fixed Directory"
    set puf_rom1 [uint32 "PUF ROM 1"]
    set puf_rom2 [uint32 "PUF ROM 2"]
    set image_info [list]
    lappend image_info "pufr"
    lappend image_info $puf_rom1
    lappend image_info $puf_rom2
    lappend images $image_info
    hex 4 "CRC Variable Directory"


    while 1 {
	set addr1 [uint32 "Addr1"]
	set addr2 [uint32 "Addr2"]
	if {$addr1 == 0xFFFFFFFF} break
	set image_type [ascii 4 "type"]

	set image_info [list]
	lappend image_info $image_type
	lappend image_info $addr1
	lappend image_info $addr2
	lappend images $image_info
    }
}

goto [expr $directory_1_2]

section "Directory 2" {
    hex 4 "CRC Fixed Directory"
    set puf_rom1 [uint32 "PUF ROM 1"]
    set puf_rom2 [uint32 "PUF ROM 2"]
    hex 4 "CRC Variable Directory"

    while 1 {
	set addr1 [uint32 "Addr1"]
	set addr2 [uint32 "Addr2"]
	if {$addr1 == 0xFFFFFFFF} break
	set image_type [ascii 4 "type"]
    }
}


section "Images" {
    foreach image_info $images {
	goto [lindex $image_info 1]
	section [lindex $image_info 0] {
	    bytes 1096 "customer certificate"
	    bytes 428 "padding"
	    bytes 8   "customer magic"
	    bytes 516 "customer signature"
	    bytes 1096 "signing info"
	    bytes 428 "padding"
	    bytes 8   "fungible magic"
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
	}
	goto [lindex $image_info 2]
	section [lindex $image_info 0] {
	    bytes 1096 "customer certificate"
	    bytes 428 "padding"
	    bytes 8   "customer magic"
	    bytes 516 "customer signature"
	    bytes 1096 "signing info"
	    bytes 428 "padding"
	    bytes 8   "fungible magic"
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
	}
    }
}
