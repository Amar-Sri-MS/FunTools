#!/usr/bin/env python

import sys, os
from imgtec.console.support import command
from imgtec.lib.namedenum import namedenum
from imgtec.lib.namedbitfield import namedbitfield
from imgtec.console import *
from imgtec.console import CoreFamily
from array import array
import binascii
import time
import logging
import traceback

logger = logging.getLogger('jtagutils')
logger.setLevel(logging.INFO)

class constants(object):
    pass


class jtag:
    def __init__(self, dev_type, ip_addr):
        self.dev_type = dev_type
        self.ip_addr = ip_addr

    # Connects Codescape jtag debugger
    # Returns the device handle
    @command()
    def jtag_connect(self):
        '''Connect to jtag probe'''
        status = probe(self.dev_type, self.ip_addr)
        logger.info('jtag is connected!\n{0}'.format(status))
        status = tapi("10 0x01C1")
        logger.info('tap select status: {}'.format(status))
        return (True, "Jtag is connected")

    # Free the i2c bus and close the device handle
    def i2c_disconnect(self):
        pass

    # jtag csr read
    @command()
    def jtag_csr_peek(self, csr_addr, csr_width_words):
        '''csr peek'''
        logger.info(('JTAG peek csr_addr:{0}'
               ' csr_width_words:{1}').format(hex(csr_addr), csr_width_words))

        if csr_width_words == 0 or csr_width_words > 8:
            logger.error(('Invalid number csr width:'
                         ' {}\n').format(csr_width_words) +
                         'Csr width(64-bit words) should be in the range 1-8!')
            return None

        logger.info("\nWriting read cmd...........:")
        ring_sel = csr_addr >> 35
        cmd = ((csr_addr & 0xffffffffff) |
                    ((0x2 << 60) |
                    ((csr_width_words & 0x3F) << 54) |
                    (ring_sel << 49)))

        #cmd_str = hex(cmd)[2:].zfill()
        dr = '128 ' + '0x' + '%016x'%((0x3 << 60) | (1 << 54)) + '%016x'%(cmd)
        logger.info('dr: {}'.format(dr))
        status = tapd(dr)
        logger.info('peek tapd status: {}'.format(status))
        read_resp = status[0] >> 124
        read_status = (status[0] >> 96) & 0xFF
        jtag_ack = (status[0] >> 64) & 0x1
        jtag_running = (status[0] >> 65) & 0x1

        logger.info("read response: {}".format(read_resp))
        logger.info("read status: {}".format(read_status))
        logger.info("jtag ack: {}".format(jtag_ack))
        logger.info("jtag running: {}".format(jtag_running))
        #logger.info("status: {}".format(status))

        logger.info('peek shifting cmd first time')
        dr = "128 0x0"
        status = tapd(dr)
        logger.info('peek cmd shift tapd status: {}'.format(status))
        read_resp = status[0] >> 124
        read_status = (status[0] >> 96) & 0xFF
        jtag_ack = (status[0] >> 64) & 0x1
        jtag_running = (status[0] >> 65) & 0x1
        logger.info('peek tapd status: {}'.format(status))
        data = status[0] & 0xFFFFFFFFFFFFFFFF

        logger.info("read response: {}".format(read_resp))
        logger.info("read status: {}".format(read_status))
        logger.info("jtag ack: {}".format(jtag_ack))
        logger.info("jtag running: {}".format(jtag_running))
        logger.info("Data: {}".format(hex(data)))

        '''
        logger.info('peek shifting cmd second time')
        dr = "128 0x0"
        status = tapd(dr)
        logger.info('peek cmd shift tapd status: {}'.format(status))
        read_resp = status[0] >> 124
        read_status = (status[0] >> 96) & 0xFF
        jtag_ack = (status[0] >> 64) & 0x1
        jtag_running = (status[0] >> 65) & 0x1
        logger.info('peek tapd status: {}'.format(status))
        data = status[0] & 0xFFFFFFFFFFFFFFFF

        logger.info("read response: {}".format(read_resp))
        logger.info("read status: {}".format(read_status))
        logger.info("jtag ack: {}".format(jtag_ack))
        logger.info("jtag running: {}".format(jtag_running))
        logger.info("Data: {}".format(hex(data)))
        '''
        word_array = list()
        for i in range(csr_width_words):
            logger.info("\nReading Data[{}/{}]...........:".format(i+1,
                        csr_width_words))
            csr_data_addr = (i+1) * 8
            ring_sel = csr_data_addr >> 35
            cmd = ((csr_data_addr & 0xffffffffff) |
                ((0x2 << 60) | (0x1 << 54) |
                 (ring_sel << 49)))

            cmd_str = hex(cmd)[2:].zfill(16)
            dr = '128 ' + '0x' + cmd_str + '0'*16
            logger.info('dr: {}'.format(dr))
            status = tapd(dr)
            logger.info('peek tapd status: {}'.format(status))
            read_resp = status[0] >> 124
            read_status = (status[0] >> 96) & 0xFF
            jtag_ack = (status[0] >> 64) & 0x1
            jtag_running = (status[0] >> 65) & 0x1
            logger.info('peek tapd status: {}'.format(status))
            data = status[0] & 0xFFFFFFFFFFFFFFFF

            logger.info("read response: {}".format(read_resp))
            logger.info("read status: {}".format(read_status))
            logger.info("jtag ack: {}".format(jtag_ack))
            logger.info("jtag running: {}".format(jtag_running))
            logger.info("Data: {}".format(hex(data)))

            logger.info('peek shifting data-first time')
            dr = "128 0x0"
            status = tapd(dr)
            logger.info('peek zero shift tapd status: {}'.format(status))
            read_resp = status[0] >> 124
            read_status = (status[0] >> 96) & 0xFF
            jtag_ack = (status[0] >> 64) & 0x1
            jtag_running = (status[0] >> 65) & 0x1
            logger.info('peek tapd status: {}'.format(status))
            data = status[0] & 0xFFFFFFFFFFFFFFFF

            logger.info("read response: {}".format(read_resp))
            logger.info("read status: {}".format(read_status))
            logger.info("jtag ack: {}".format(jtag_ack))
            logger.info("jtag running: {}".format(jtag_running))
            logger.info("Data: {}".format(hex(data)))

            '''
            logger.info('peek shifting data-second time')
            dr = "128 0x0"
            status = tapd(dr)
            logger.info('peek zero shift tapd status: {}'.format(status))
            read_resp = status[0] >> 124
            read_status = (status[0] >> 96) & 0xFF
            jtag_ack = (status[0] >> 64) & 0x1
            jtag_running = (status[0] >> 65) & 0x1
            logger.info('peek tapd status: {}'.format(status))
            data = status[0] & 0xFFFFFFFFFFFFFFFF

            logger.info("read response: {}".format(read_resp))
            logger.info("read status: {}".format(read_status))
            logger.info("jtag ack: {}".format(jtag_ack))
            logger.info("jtag running: {}".format(jtag_running))
            logger.info("Data: {}".format(hex(data)))
            '''

            word_array.append(data)

        logger.info('Peeked word_array: {0}'.format([hex(x) for x in word_array]))
        return word_array


    # jtag csr write
    def jtag_csr_poke(self, csr_addr, csr_width_words, word_array):
        logger.info(('JTAG poke csr_addr:{0}'
                     ' csr_width_words:{1} words:{2}').format(hex(csr_addr),
                            csr_width_words,
                            [hex(x) for x in word_array]))

        if csr_width_words == 0 or csr_width_words > 8:
            logger.error(('Invalid number csr width:'
                         ' {}\n').format(csr_width_words) +
                         'Csr width(64-bit words) should be in the range 1-8!')
            return False

        if csr_width_words != len(word_array):
            logger.error(('Insufficient data! Expected: {0}'
                   ' data length: {0}').format(csr_width_words, len(word_array)))
            return False


        for i in range(csr_width_words):
            logger.info("\nWriting Data[{}/{} = {}]...........:".format(i+1,
                           csr_width_words, hex(word_array[i])))
            csr_data_addr = (i+1) * 8
            ring_sel = csr_data_addr >> 35
            cmd = ((csr_data_addr & 0xffffffffff) |
                ((0x3 << 60) | (0x1 << 54) |
                 (ring_sel << 49)))

            cmd_str = hex(cmd)[2:].zfill(16)
            #data_str = hex(word_array[i])[2:].zfill(16)
            dr = '128 ' + '0x' + cmd_str + "%016x"%word_array[i]
            logger.info('dr: {}'.format(dr))
            status = tapd(dr)
            logger.info('poke data tapd status: {}'.format(status))
            write_resp = status[0] >> 124
            write_status = (status[0] >> 96) & 0xFF
            jtag_ack = (status[0] >> 64) & 0x1
            jtag_running = (status[0] >> 65) & 0x1
            data = status[0] & 0xFFFFFFFFFFFFFFFF

            logger.info("write response: {}".format(write_resp))
            logger.info("write status: {}".format(write_status))
            logger.info("jtag ack: {}".format(jtag_ack))
            logger.info("jtag running: {}".format(jtag_running))
            logger.info("Data: {}".format(hex(data)))

            logger.info('poke shifting data-first time')
            #time.sleep(2)
            dr = "128 0x0"
            status = tapd(dr)
            logger.info('poke zero shift tapd status: {}'.format(status))
            write_resp = status[0] >> 124
            write_status = (status[0] >> 96) & 0xFF
            jtag_ack = (status[0] >> 64) & 0x1
            jtag_running = (status[0] >> 65) & 0x1
            data = status[0] & 0xFFFFFFFFFFFFFFFF

            logger.info("write response: {}".format(write_resp))
            logger.info("write status: {}".format(write_status))
            logger.info("jtag ack: {}".format(jtag_ack))
            logger.info("jtag running: {}".format(jtag_running))
            logger.info("Data: {}".format(hex(data)))

            '''
            logger.info('poke shifting data-second time')
            #time.sleep(2)
            dr = "128 0x0"
            status = tapd(dr)
            logger.info('poke zero shift tapd status: {}'.format(status))
            write_resp = status[0] >> 124
            write_status = (status[0] >> 96) & 0xFF
            jtag_ack = (status[0] >> 64) & 0x1
            jtag_running = (status[0] >> 65) & 0x1
            data = status[0] & 0xFFFFFFFFFFFFFFFF

            logger.info("write response: {}".format(write_resp))
            logger.info("write status: {}".format(write_status))
            logger.info("jtag ack: {}".format(jtag_ack))
            logger.info("jtag running: {}".format(jtag_running))
            logger.info("Data: {}".format(hex(data)))
            '''


        #time.sleep(2)
        logger.info("\nWriting write command....")
        ring_sel = csr_addr >> 35
        cmd = ((csr_addr & 0xffffffffff) |
                    ((0x3 << 60) |
                    ((csr_width_words & 0x3F) << 54) |
                    (ring_sel << 49)))

        #cmd_str = hex(cmd)[2:].zfill(16)
        #dr = '128 ' + '0x' + cmd_str + '0'*16
        dr = '128 ' + '0x' + '%016x'%((0x3 << 60) | (1 << 54)) + '%016x'%(cmd)
        logger.info('dr: {}'.format(dr))
        status = tapd(dr)
        logger.info('peek tapd status: {}'.format(status))
        write_resp = status[0] >> 124
        write_status = (status[0] >> 96) & 0xFF
        jtag_ack = (status[0] >> 64) & 0x1
        jtag_running = (status[0] >> 65) & 0x1

        logger.info("write response: {}".format(write_resp))
        logger.info("write status: {}".format(write_status))
        logger.info("jtag ack: {}".format(jtag_ack))
        logger.info("jtag running: {}".format(jtag_running))
        #logger.info("status: {}".format(status))

        logger.info('poke shifting cmd first time')
        #time.sleep(1)
        dr = "128 0x0"
        status = tapd(dr)
        logger.info('poke tapd status: {}'.format(status))
        write_resp = status[0] >> 124
        write_status = (status[0] >> 96) & 0xFF
        jtag_ack = (status[0] >> 64) & 0x1
        jtag_running = (status[0] >> 65) & 0x1
        data = status[0] & 0xFFFFFFFFFFFFFFFF

        logger.info("write response: {}".format(write_resp))
        logger.info("write status: {}".format(write_status))
        logger.info("jtag ack: {}".format(jtag_ack))
        logger.info("jtag running: {}".format(jtag_running))
        logger.info("Data: {}".format(hex(data)))

        '''
        logger.info('poke shifting cmd second time')
        #time.sleep(1)
        dr = "128 0x0"
        status = tapd(dr)
        logger.info('poke tapd status: {}'.format(status))
        write_resp = status[0] >> 124
        write_status = (status[0] >> 96) & 0xFF
        jtag_ack = (status[0] >> 64) & 0x1
        jtag_running = (status[0] >> 65) & 0x1
        data = status[0] & 0xFFFFFFFFFFFFFFFF

        logger.info("write response: {}".format(write_resp))
        logger.info("write status: {}".format(write_status))
        logger.info("jtag ack: {}".format(jtag_ack))
        logger.info("jtag running: {}".format(jtag_running))
        logger.info("Data: {}".format(hex(data)))
        '''


        return True

    # jtag csr read
    def jtag_csr_test(self, csr_addr):
        csr_data_addr = (8) * 8
        ring_sel = csr_data_addr >> 35
        cmd = ((csr_data_addr & 0xffffffffff) |
            ((0x3 << 60) | (0x1 << 54) |
             (ring_sel << 49)))

        cmd_str = hex(cmd)[2:].zfill(16)
        dr = '128 ' + '0x' + cmd_str + "%016x"%(0x1122334455661122)
        logger.info('dr: {}'.format(dr))
        status = tapd(dr)
        logger.info('poke data tapd status: {}'.format(status))
        write_resp = status[0] >> 124
        write_status = (status[0] >> 96) & 0xFF
        jtag_ack = (status[0] >> 64) & 0x1
        jtag_running = (status[0] >> 65) & 0x1
        data = status[0] & 0xFFFFFFFFFFFFFFFF

        logger.info("write response: {}".format(write_resp))
        logger.info("write status: {}".format(write_status))
        logger.info("jtag ack: {}".format(jtag_ack))
        logger.info("jtag running: {}".format(jtag_running))
        logger.info("Data: {}".format(hex(data)))

        logger.info('poke shifting data-first time')
        #time.sleep(2)
        dr = "128 0x0"
        status = tapd(dr)
        logger.info('poke zero shift tapd status: {}'.format(status))
        write_resp = status[0] >> 124
        write_status = (status[0] >> 96) & 0xFF
        jtag_ack = (status[0] >> 64) & 0x1
        jtag_running = (status[0] >> 65) & 0x1
        data = status[0] & 0xFFFFFFFFFFFFFFFF

        logger.info("write response: {}".format(write_resp))
        logger.info("write status: {}".format(write_status))
        logger.info("jtag ack: {}".format(jtag_ack))
        logger.info("jtag running: {}".format(jtag_running))
        logger.info("Data: {}".format(hex(data)))

        #wewe
        csr_data_addr = (7) * 8
        ring_sel = csr_data_addr >> 35
        cmd = ((csr_data_addr & 0xffffffffff) |
            ((0x3 << 60) | (0x1 << 54) |
             (ring_sel << 49)))

        cmd_str = hex(cmd)[2:].zfill(16)
        dr = '128 ' + '0x' + cmd_str + "%016x"%(0xdeadbeefdeadbeef)
        logger.info('dr: {}'.format(dr))
        status = tapd(dr)
        logger.info('poke data tapd status: {}'.format(status))
        write_resp = status[0] >> 124
        write_status = (status[0] >> 96) & 0xFF
        jtag_ack = (status[0] >> 64) & 0x1
        jtag_running = (status[0] >> 65) & 0x1
        data = status[0] & 0xFFFFFFFFFFFFFFFF

        logger.info("write response: {}".format(write_resp))
        logger.info("write status: {}".format(write_status))
        logger.info("jtag ack: {}".format(jtag_ack))
        logger.info("jtag running: {}".format(jtag_running))
        logger.info("Data: {}".format(hex(data)))

        logger.info('poke shifting data-first time')
        #time.sleep(2)
        dr = "128 0x0"
        status = tapd(dr)
        logger.info('poke zero shift tapd status: {}'.format(status))
        write_resp = status[0] >> 124
        write_status = (status[0] >> 96) & 0xFF
        jtag_ack = (status[0] >> 64) & 0x1
        jtag_running = (status[0] >> 65) & 0x1
        data = status[0] & 0xFFFFFFFFFFFFFFFF

        logger.info("write response: {}".format(write_resp))
        logger.info("write status: {}".format(write_status))
        logger.info("jtag ack: {}".format(jtag_ack))
        logger.info("jtag running: {}".format(jtag_running))
        logger.info("Data: {}".format(hex(data)))




        csr_data_addr = (8) * 8
        ring_sel = csr_data_addr >> 35
        cmd = ((csr_data_addr & 0xffffffffff) |
            ((0x2 << 60) | (0x1 << 54) |
             (ring_sel << 49)))

        cmd_str = hex(cmd)[2:].zfill(16)
        dr = '128 ' + '0x' + cmd_str + '0'*16
        logger.info('dr: {}'.format(dr))
        status = tapd(dr)
        logger.info('peek tapd status: {}'.format(status))
        read_resp = status[0] >> 124
        read_status = (status[0] >> 96) & 0xFF
        jtag_ack = (status[0] >> 64) & 0x1
        jtag_running = (status[0] >> 65) & 0x1
        logger.info('peek tapd status: {}'.format(status))
        data = status[0] & 0xFFFFFFFFFFFFFFFF

        logger.info("read response: {}".format(read_resp))
        logger.info("read status: {}".format(read_status))
        logger.info("jtag ack: {}".format(jtag_ack))
        logger.info("jtag running: {}".format(jtag_running))
        logger.info("Data: {}".format(hex(data)))

        logger.info('peek shifting data-first time')
        dr = "128 0x0"
        status = tapd(dr)
        logger.info('peek zero shift tapd status: {}'.format(status))
        read_resp = status[0] >> 124
        read_status = (status[0] >> 96) & 0xFF
        jtag_ack = (status[0] >> 64) & 0x1
        jtag_running = (status[0] >> 65) & 0x1
        logger.info('peek tapd status: {}'.format(status))
        data = status[0] & 0xFFFFFFFFFFFFFFFF

        logger.info("read response: {}".format(read_resp))
        logger.info("read status: {}".format(read_status))
        logger.info("jtag ack: {}".format(jtag_ack))
        logger.info("jtag running: {}".format(jtag_running))
        logger.info("Data: {}".format(hex(data)))

if __name__== "__main__":
    jp = jtag('sp55e', '10.1.23.132')
    jp.jtag_connect()

    logger.info('\n\n\n************POKE***************')
    jp.jtag_csr_poke(0x4883160000, 6, [0x1111, 0x2222, 0x3333, 0x4444, 0x5555, 0x6666])
    jp.jtag_csr_poke(0xb000000078, 1, [0xabcdabcdabcdabcd])
    jp.jtag_csr_poke(0xb800000078, 1, [0xdeadbeefdeadbeef])

    logger.info('\n\n\n************PEEK***************')
    jp.jtag_csr_peek(0xb000000078, 1)
    jp.jtag_csr_peek(0xb800000078, 1)
    jp.jtag_csr_peek(0x4883160000, 6)







    #jp.jtag_csr_test(0x4883760000)
    #jp.jtag_csr_poke(0x4883760000, 8, [0x11, 0x22, 0x33, 0x44, 0x55,
    #                                   0x6666666666666666, 0x7777777777777777,
    #                                  0x8888888888888888])
    #jp.jtag_csr_poke(0x4883760038, 1, [0x9999999999999999])
    #jp.jtag_csr_poke(0x5008964000, 2, [0x1122334455667788, 0x8877665544332211])


    #logger.info('\n\n\n************PEEK***************')
    #jp.jtag_csr_peek(0x5008964000, 2)


@command()
def nag_test():
    ''' NAG test function'''
    pass
