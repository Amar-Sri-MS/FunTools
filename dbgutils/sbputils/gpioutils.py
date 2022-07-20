from aardvark_py import *
from time import sleep
import sys
import sys
from array import array
import logging

from dututils import dut
from i2cdev import *

logger = logging.getLogger('tap-gpio')
logger.setLevel(logging.DEBUG)

TAPs = {
    'i2c'   : 0x24,
    'jdbg'  : 0x04,
    'jcsr'  : 0x00,
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

    def set_defaults(self, direction=0xFF, dirmsg="all OUTPUT", pullups=0xFF, pullmsg="all HIGH"):
        """ default is all OUTPUT and pullups is all HIGH """
        sleep(1)
        status = aa_gpio_direction(self.handle, direction)
        logger.info("Configuring direction as {} - {}. status: ".format(hex(direction), dirmsg) + aa_status_string(status))
        sleep(1)
        status = aa_gpio_pullup(self.handle, pullups) ## default TAP to MDH DBG
        logger.info("default gpio pullup as {} - {}. status: ".format(hex(pullups), pullmsg) + aa_status_string(status))

    def set_gpio(self, setval, setmsg=None):
        sleep(1)
        status = aa_gpio_set(self.handle, setval)
        logger.info( "gpio set {} - {}. status: ".format(hex(setval), setmsg) + aa_status_string(status)) 

    def get_gpio(self):
        return aa_gpio_get(self.handle)

    def any_change_in_gpio(self, expected, chgmsg=None):
        oldval = aa_gpio_get(self.handle);
        logger.info("Listening gpio change from {} expect_only={} - {}".format(hex(oldval), hex(expected), chgmsg))
        while True:
            newval = aa_gpio_change(self.handle, 0xFFFF);
            if ((newval ^ oldval) == expected):
                logger.info("gpio changed observed (old={}, new={}) asserted - {}".format(hex(oldval), hex(newval), hex(expected), chgmsg))
                break
        logger.info( "captured gpio change.")
        return True

    def close(self):
        aa_close(self.handle)
        logger.info( "Done!" )


class tap(aardvark_gpio):
    def __init__(self, name, **kwargs):
        self.name = name
        super(tap, self).__init__(self.name)
        self.set_defaults(direction=0x24, dirmsg="pin5 and pin9 as all OUTPUT", pullups=0x04, pullmsg="pad sel b'01(dbg)")

    def seti2c(self):
        self.set_gpio(0x24, setmsg="pad sel b'11(i2c)")

    def setjdbg(self):
        self.set_gpio(0x04, setmsg="pad sel b'01(dbg)")

    def setjcsr(self):
        self.set_gpio(0x00, setmsg="pad sel b'00(csr)")

class gpio_set(aardvark_gpio):
    def __init__(self, name, **kwargs):
        self.name = name
        super(gpio_set, self).__init__(self.name)
        self.set_defaults(direction=0x18, dirmsg="pin7 and pin8 as all OUTPUT", pullups=0x18, pullmsg="ping7/pin8 as HIGH")
    def gpio_00(self):
        self.set_gpio(0x00, setmsg="both down. Observe(0xA020)")
    def gpio_01(self):
        self.set_gpio(0x08, setmsg="gpio0 up. Observe(0xA021)")
    def gpio_10(self):
        self.set_gpio(0x10, setmsg="gpio1 up. Observe(0xA022)")
    def gpio_11(self):
        self.set_gpio(0x18, setmsg="both up. Observe(0xA023)")

class gpio_get(aardvark_gpio):
    def __init__(self, name, **kwargs): #direction=0xE7, dirmsg="pin7 and pin8 as all INPUT", pullups=0xFF, pullmsg="all HIGH (observe pins LOW in SBP)" ):
        self.name = name
        super(gpio_get, self).__init__(self.name)
        self.set_defaults(**kwargs) #direction=0xE7, dirmsg="pin7 and pin8 as all INPUT", pullups=0xFF, pullmsg="all HIGH (observe pins LOW in SBP)" )
    def monitor_gpio0(self):
        return self.any_change_in_gpio(0x08, "Observe gpio0 UP")
    def monitor_gpio1(self):
        return self.any_change_in_gpio(0x10, "Observe gpio1 UP")
    def monitor_gpio_both(self):
        return self.any_change_in_gpio(0x18, "Observe both gpio flip UP")
    def monitor_gpio_autfail(self):
        return self.any_change_in_gpio(0x04, "Observe gpio/pin5 flip UP on AUTHFAIL")

def test1(name, tapname):
    try:
        setval = TAPs[tapname]
    except:
        logger.error("gpio tapname %s undefined..." % tapname)
        sys.exit(1)

    t = tap(name)
    if 'i2c' in tapname:
        t.seti2c()
    elif 'jdbg' in tapname:
        t.setjdbg()
    elif 'jcsr' in tapname:
        t.setjcsr()
    else:
        logger.info( "should never reach here")
    t.close()

def test2(name):
    t = gpio_set(name)
    t.gpio_00()
    t.gpio_01()
    t.gpio_10()
    t.gpio_11()
    t.close()

def test3(name):
    t = gpio_get(name, direction=0xE7, dirmsg="pin7 and pin8 as all INPUT", pullups=0xFF, pullmsg="all HIGH (observe pins LOW in SBP)" )
    t.monitor_gpio0()
    t.monitor_gpio1()
    t.monitor_gpio_both()
    t.close()

def test4(name):
    t = gpio_get(name, direction=0xFB, dirmsg="pin5 as INPUT", pullups=0xFF, pullmsg="all HIGH (observe pin5 pull LOW in SBP)")
    t.monitor_gpio_autfail()
    t.close()

if __name__== "__main__":
    name = sys.argv[1]
    tapname = sys.argv[2]
    pass
    #test1(name, tapname)
    #test2(name)
    #test3(name)
    #test4(name)
