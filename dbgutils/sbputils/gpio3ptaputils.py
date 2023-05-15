from aardvark_py import *
from time import sleep
import sys
import sys
from array import array
import logging
import signal

from dututils import dut
from i2cdev import *

logger = logging.getLogger('tap3p-gpio')
logger.setLevel(logging.DEBUG)

def signal_handler(sig, frame):
        print('You pressed Ctrl+C! ... exiting ...')
        sys.stdout.flush()
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

### tap-definitions
######################
# b'000 - Avago      (mosi/gpio4=0, ss/gpio5=0, miso/gpio2=0) 0x00
# b'001 - MDH        (mosi/gpio4=0, ss/gpio5=0, miso/gpio2=1) 0x04
# b'010 - MIPS       (mosi/gpio4=0, ss/gpio5=1, miso/gpio2=0) 0x20
# b'011 - Tessent    (mosi/gpio4=0, ss/gpio5=1, miso/gpio2=1) 0x24
# b'100 - CoreSight  (mosi/gpio4=1, ss/gpio5=0, miso/gpio2=0) 0x10
# b'101 - USB        (mosi/gpio4=1, ss/gpio5=0, miso/gpio2=1) 0x14
# b'111 - none       (mosi/gpio4=1, ss/gpio5=1, miso/gpio2=1) 0x34
######################

### TAP values
TAPs = {
    'avago'      : 0x00, #avago/csr
    'mdh'        : 0x04, #mdh
    'mips'       : 0x20, #mips
    'tessent'    : 0x24, #tessent
    'coresight'  : 0x10, #coresight
    'usb'        : 0x14, #usb
    'none'       : 0x34, #none
}

class JTAGTAP_Exception(BaseException):
    pass

class aardvark_gpio(object):
    def __init__(self, name):
        status, serial, ip, addr = dut().get_i2c_info(name)
        logger.info('Device({0}/{1}) with status: {2}!'.format(serial, ip, status))
        dev_idx = aardvark_i2c_spi_dev_index_from_serial(serial)
        if dev_idx is None:
            dev_list = aardvark_i2c_spi_dev_list()
            status_msg = (('Failed to find i2c device: {0}! Found devices: {1}').format(dev_id, dev_list))
            logger.error(status_msg)
            raise JTAGTAP_Exception(status_msg)

        dev_in_use = dev_idx & 0x8000
        dev_idx = dev_idx & 0x7FFF
        if dev_in_use != 0:
            logger.info('Device({0}/{1}) already in use! Disconnecting....'.format(dev_id, dev_idx))
            status = aa_close(dev_idx)
            logger.info('Device({0}/{1}) is closed with status: {2}!'.format(dev_id, dev_idx, status))

        n_devs, devs = aa_find_devices(dev_idx+1)
        logger.info('n_devs:{0} devs:{1}:'.format(n_devs, devs))
        if not devs or devs[dev_idx] is None:
            status_msg = 'Failed to detect i2c device! dev_list: {0}'.format(dev_list)
            logger.error(status_msg)
            raise JTAGTAP_Exception(status_msg)

        dev_handle =  devs[dev_idx]
        logger.debug('Dev handle: {0}'.format(dev_handle))
        self.handle = aa_open(dev_handle)
        if self.handle == 0x8000:
            status_msg = 'Error opening i2c device. Invalid dev Handle! {0}'.format(self.handle)
            logger.error(status_msg)
            self.handle = None
            raise JTAGTAP_Exception(status_msg)
        if self.handle < 0:
            status_msg = 'Error opening i2c device! {0}({1})'.format(aa_status_string(self.handle), self.handle)
            logger.error(status_msg)
            self.handle = None
            raise JTAGTAP_Exception(status_msg)

        features = aa_features(self.handle)
        if features != 27:
            status_msg = "Invalid device features!: {0}".format(features)
            logger.error(status_msg)
            self.handle = None
            raise JTAGTAP_Exception(status_msg)

        status = aa_configure(self.handle, 0) #AA_CONFIG_GPIO_ONLY
        logger.info("Configure AA_CONFIG_GPIO_ONLY mode! status:" + aa_status_string(status))

    def set_defaults(self, direction=0x34, dirmsg="all OUTPUT", pullups=0xFF, pullmsg="all HIGH"):
        """ default is all OUTPUT and pullups is all HIGH """
        sleep(1)
        status = aa_gpio_direction(self.handle, direction)
        logger.info("Configuring direction as {} - {}. status: ".format(hex(direction), dirmsg) + aa_status_string(status))
        sleep(1)
        #logger.info("skipping any gpio pullup for now .....")
        status = aa_gpio_pullup(self.handle, pullups) ## default TAP to MDH DBG
        logger.info("default gpio pullup as {} ... status:".format(hex(pullups)) + aa_status_string(status))
        sleep(1)

    def set_gpio(self, setval, setmsg=None):
        sleep(1)
        status = aa_gpio_set(self.handle, setval)
        logger.info( "gpio set {} - {}. status: ".format(hex(setval), setmsg) + aa_status_string(status)) 
        sleep(1)

    def get_gpio(self):
        return aa_gpio_get(self.handle)

    def close(self):
        aa_close(self.handle)
        logger.info( "Done!" )


class tap(aardvark_gpio):
    def __init__(self, name, **kwargs):
        self.name = name
        thispullups = kwargs.get("pullups", 0xFF)
        super(tap, self).__init__(self.name)
        self.set_defaults(direction=0x34, dirmsg="(GPIO8_GRAY_MOSI|GPIO9_WHITE_SS|GPIO5_GREEN_MISO) as all OUTPUT", pullups=thispullups, pullmsg="pad sel b'111(none)")

    def set_val(self, modename, gpioval):
        self.set_gpio(gpioval, setmsg="setting mode=%s with pad sel=%s" % (modename, hex(gpioval)))

    def set_avago(self):
        self.set_gpio(0x00, setmsg="pad sel b'000(avago/csr)")

    def set_mdh(self):
        self.set_gpio(0x04, setmsg="pad sel b'001(dbg/mdh)")

    def set_mips(self):
        self.set_gpio(0x20, setmsg="pad sel b'010(mips)")

    def set_tessent(self):
        self.set_gpio(0x24, setmsg="pad sel b'011(i2c/tessent)")

    def set_coresight(self):
        self.set_gpio(0x10, setmsg="pad sel b'100(coresight)")

    def set_usb(self):
        self.set_gpio(0x14, setmsg="pad sel b'101(usb)")

    def set_none(self):
        self.set_gpio(0x34, setmsg="pad sel b'111(none)")

def setTapMode(name, tapname, keepforever=True):
    try:
        setval = TAPs[tapname]
    except:
        logger.error("gpio tapname %s undefined..." % tapname)
        sys.exit(1)

#    'avago'      : 0x00, #avago/csr
#    'mdh'        : 0x04, #mdh
#    'mips'       : 0x20, #mips
#    'tessent'    : 0x24, #tessent
#    'coresight'  : 0x10, #coresight
#    'usb'        : 0x14, #usb
#    'none'       : 0x34, #none

    t = tap(name)

    if 'tessent' in tapname:
        t.set_tessent()
    elif 'mdh' in tapname:
        t.set_mdh()
    elif 'avago' in tapname:
        t.set_avago()
    elif 'mips' in tapname:
        t.set_mips()
    elif 'coresight' in tapname:
        t.set_coresight()
    elif 'usb' in tapname:
        t.set_usb()
    elif 'none' in tapname:
        t.set_none()
    else:
        logger.info( "should never reach here")
        sys.exit(1)

    while(keepforever):
        logger.info(" holding the tap in mode=%s ... sleeping 10s ..." % tapname)
        sleep(10)

    t.close()

if __name__== "__main__":
    name = sys.argv[1]
    tapname = sys.argv[2]
    setTapMode(name, tapname)
