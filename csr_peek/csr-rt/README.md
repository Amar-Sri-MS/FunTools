# CSR Read Infrastructure
Infrastructure that supports raw read/write into CSR space.
It is expected that the caller of this infrastructure is aware of:
    (a) # of CSR Rings for any given module
    (b) Names of the CSR registers for any given module
    and (c) If debugging is desired, then the relationships between the address nodes.




$ make
builds everything, assumes currently present config files

$ make clean
cleans everything, except the previously generated files

$ make cfgupd
Gets the latest config files from Jenkins, and generates new C-files for consumption

$ make distclean
cleans absolutely everything, including previously gotten configfiles








