import i2cutils
import i2cdev
import i2cclient
import i2cproxy
import dbgclient
from sys import platform as _platform
if _platform == "linux" or _platform == "linux2":
    import jtagclient
