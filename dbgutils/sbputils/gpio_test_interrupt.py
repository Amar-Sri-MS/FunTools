from aardvark_py import *
from time import sleep
import sys
import sys
from array import array
import logging
from .i2cdev import *
from .dututils import dut

logger = logging.getLogger('gpiotest')
logger.setLevel(logging.DEBUG)

def test(name):
    status, dev_id, ip, addr = dut().get_i2c_info(name)
    print(status, dev_id, ip, addr)
    dev_idx = aardvark_i2c_spi_dev_index_from_serial(dev_id)
    if dev_idx is None:
        dev_list = aardvark_i2c_spi_dev_list()
        status_msg = (('Failed to find i2c device: {0}! Found devices: {1}').format(dev_id, dev_list))
        logger.error(status_msg)
        return (False, status_msg)
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
        return (False, status_msg)

    dev_handle =  devs[dev_idx]
    logger.debug('Dev handle: {0}'.format(dev_handle))
    h = aa_open(dev_handle)
    if h == 0x8000:
        status_msg = 'Error opening i2c device. Invalid dev Handle! {0}'.format(h)
        logger.error(status_msg)
        return (False, status_msg)
    if h < 0:
        status_msg = 'Error opening i2c device! {0}({1})'.format(aa_status_string(h), h)
        logger.error(status_msg)
        return (False, status_msg)

    features = aa_features(h)
    if features != 27:
        status_msg = ('Error validating dev features!{0}({1})').format(aa_status_string(features), features)
        logger.error(status_msg)
        return (False, status_msg)

    status = aa_i2c_free_bus(h)
    status_msg = ('Free Bus! {0}({1})').format(aa_status_string(features), features)
    logger.debug(status_msg)

    status = aa_configure(h, 0)
    if status != 0:
        status_msg = ('Error configuring GPIO only mode:{0}({1})').format(aa_status_string(status), status)
        logger.error(status_msg)
        return (False, status_msg)

    print("listening to GPIO pin (esp. pin-5/gpio 0x04) as interrupt ....!")

    status = aa_gpio_direction(h, 0x00)
    print("Configuring GPIO direction as all INPUT. status: " + aa_status_string(status))
    
    status = aa_gpio_pullup(h, 0xFF)
    print("gpio pullup. status: " + aa_status_string(status))
    oldval = aa_gpio_get(h);
    print(hex(oldval))
    print("READ old GPIO value: ", hex(oldval)) #  + aa_status_string(oldval)

    print("Listen for a change in GPIO level ... ") # + aa_status_string(status)
    while True:
        newval = aa_gpio_change(h, 0xFFFF);
        if ((newval ^ oldval) == 0x04):
            print("SBP v_PAD_SP_TEST2 (newval=%s) asserted due to AUTH error ..." % hex(newval))
            break
    
    print("GPIO inputs changed ...", hex(oldval), hex(newval))
    #if (newval & 0x04):
    #    print "SBP v_PAD_SP_TEST2 asserted due to AUTH error ..."
    #else:
    #    print "GPIO timeout occurred no changed ...", oldval, newval
             
    aa_close(h)
    print("Done!")

if __name__== "__main__":
    name = sys.argv[1]
    test(name)


