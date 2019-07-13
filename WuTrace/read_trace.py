import os
import re
import struct
import subprocess


# The header is two 32-bit words, big endian
HDR_LEN = 8
HDR_DEF = '>LL'


class Event(object):
    def __init__(self, hdr):
        hdr_words = struct.unpack(HDR_DEF, hdr)
        rsvd = hdr_words[1] & 0xfff
        if rsvd != 0:
            raise ValueError('Unexpected reserved value')

        self.timestamp = hdr_words[0]
        # Unpack the bits
        self.evt_id = (hdr_words[1] >> 26) & 0x3f
        self.src_id = (hdr_words[1] & 0x3ff0000) >> 16
        self.add_word_count = (hdr_words[1] & 0xf000) >> 12

    def get_values(self, wu_list):
        d = dict()
        d['timestamp'] = self.timestamp
        d['faddr'] = self.global_vp_to_faddr_str(self.src_id)
        return d

    @staticmethod
    def global_vp_to_faddr_str(src):
        cluster = src / 24
        lid = 8 + (src % 24)
        return '%d:%d:0' % (cluster, lid)


class WuStartEvent(Event):

    def __init__(self, hdr, addl_words):
        super(WuStartEvent, self).__init__(hdr)

        if self.add_word_count != 3:
            raise ValueError('Additional word count value')
        result = struct.unpack('>QQLL', addl_words)
        self.arg0 = result[0]
        self.arg1 = result[1]
        self.wuid = result[2]
        self.origin = result[3]

    def get_values(self, wu_list):
        d = super(WuStartEvent, self).get_values(wu_list)
        d['verb'] = 'WU'
        d['noun'] = 'START'
        d['arg0'] = self.arg0
        d['arg1'] = self.arg1
        d['wuid'] = self.wuid
        d['name'] = wu_list[self.wuid]
        return d


class WuSendEvent(Event):

    def __init__(self, hdr, addl_words):
        super(WuSendEvent, self).__init__(hdr)

        if self.add_word_count != 4:
            raise ValueError('Additional word count value')
        result = struct.unpack('>QQLLHHHH', addl_words)
        self.arg0 = result[0]
        self.arg1 = result[1]
        self.wuid = result[2] & 0xffff
        self.dest = result[3]
        self.flags = result[4] & 0xffff

    def get_values(self, wu_list):
        d = super(WuSendEvent, self).get_values(wu_list)
        d['verb'] = 'WU'
        d['noun'] = 'SEND'
        d['arg0'] = self.arg0
        d['arg1'] = self.arg1
        d['wuid'] = self.wuid
        d['dest'] = self.faddr_to_str(self.dest)
        d['name'] = wu_list[self.wuid]
        d['flags'] = self.flags
        return d

    @staticmethod
    def faddr_to_str(faddr):
        cluster = (faddr >> 15) & 0x1f
        lid = (faddr >> 10) & 0x1f
        return '%s:%s:0' % (cluster, lid)


class WuEndEvent(Event):

    def __init__(self, hdr, addl_words):
        super(WuEndEvent, self).__init__(hdr)

        if self.add_word_count != 0:
            raise ValueError('Additional word count value')

    def get_values(self, wu_list):
        d = super(WuEndEvent, self).get_values(wu_list)
        d['verb'] = 'WU'
        d['noun'] = 'END'
        return d


class TimeSyncEvent(Event):

    def __init__(self, hdr, addl_words):
        super(TimeSyncEvent, self).__init__(hdr)

        if self.add_word_count != 1:
            raise ValueError('Additional word count value')
        result = struct.unpack('>Q', addl_words)
        self.full_time = result[0]

    def get_values(self, wu_list):
        d = super(TimeSyncEvent, self).get_values(wu_list)
        d['verb'] = 'TIME'
        d['noun'] = 'SYNC'
        return d


class BinaryFileParser(object):
    """ Handles trace cluster input """

    def __init__(self, fh, wu_list_extractor):
        self.fh = fh
        self.wu_list_extractor = wu_list_extractor

    def parse(self):

        events = []
        # Get rid of cluster byte
        self.fh.read(1)

        wu_list = self.wu_list_extractor.generate_wu_list()

        while True:
            hdr = self.fh.read(HDR_LEN)
            if not hdr:
                break

            hdr_words = struct.unpack(HDR_DEF, hdr)
            evt_id = (hdr_words[1] >> 26) & 0x3f
            addl_word_count = (hdr_words[1] & 0xf000) >> 12

            # Read the additional words
            content = None
            if addl_word_count > 0:
                content = self.fh.read(addl_word_count * 8)
                if not content:
                    # We have a problem: the file contents are too short
                    raise ValueError('Truncated file')

            if evt_id == 1:
                event = WuStartEvent(hdr, content)
            elif evt_id == 2:
                event = WuSendEvent(hdr, content)
            elif evt_id == 3:
                event = WuEndEvent(hdr, content)
            elif evt_id == 7:
                event = TimeSyncEvent(hdr, content)
            else:
                raise ValueError('Unhandled event id')
                pass

            events.append(event.get_values(wu_list))

        # sort the events by timestamp
        events.sort(key=lambda e: e['timestamp'])
        return events


class WuListExtractor(object):
    def __init__(self, image_path):
        self.funos_image_path = image_path

    def generate_wu_list(self):
        """
        Generates WU list from FunOS image file.
        """

        print 'Generating WU List'
        print

        linux_gdb_path = '/project/tools/mips/mips-img-elf/2015.06-05/bin/mips-img-elf-gdb'
        mac_gdb_path = '/Users/Shared/cross/mips64/bin/mips64-unknown-elf-gdb'
        gdb_path = mac_gdb_path if os.uname()[0] == 'Darwin' else linux_gdb_path

        gdb_command = [gdb_path,
                       '--nx',  # Do not read any .gdbinit files in any directory.
                       '-batch',  # Exit after processing options.
                       '--eval-command', 'set print elements 100000',
                       '--eval-command', 'set print repeats 0',
                       '--eval-command', 'set print array on',
                       '--eval-command', 'p wu_handlers_default',
                       self.funos_image_path]

        gdb_command_string = ' '.join(gdb_command).replace(' -', ' \\\n-')
        print 'Executing GDB as:'
        print '  ', gdb_command_string.replace('\n', '\n    ')
        print

        try:
            gdb_output = subprocess.check_output(gdb_command, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as error:
            print 'GDB failed with return code %d\n' % error.returncode
            print 'GDB output:\n%s\n' % error.output
            raise error

        # GDB output is like so:
        #
        # $1 =   {0xa800000000118c38 <wuh_idle>,
        #   0xa800000000104e38 <ws_free_frame>,
        #   0xa800000000107348 <ws_free_frame_with_callback>,
        #   ...
        #   0xa800000000103e80 <invalid_runtime_wuh>,
        #   0xa800000000103e80 <invalid_runtime_wuh>}
        #

        wu_pattern = r'<(?P<wu>.+?)>'
        wu_regex = re.compile(wu_pattern)

        wu_list = []
        for line in gdb_output.split('\n'):
            match = wu_regex.search(line)
            if match:
                wu = match.group('wu')
                assert ' ' not in wu
                wu_list.append(wu)

        return wu_list


def main():
    extractor = WuListExtractor('/Users/jimmyyeap/Fun/FunOS/build/funos-f1')

    with open('trace_cluster_00', 'r') as fh:
        p = BinaryFileParser(fh, extractor)
        p.parse()


if __name__ == '__main__':
    main()
