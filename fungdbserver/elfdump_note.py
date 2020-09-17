#!/usr/bin/env python3

#
# Extracts note information from an ELF core dump
#

import argparse
import struct


from elftools.elf.elffile import ELFFile


class ELFDumpNote:
    """
    Pulls Fungible-specific notes out of the ELF dump.
    """

    def __init__(self, fh):
        """
        fh is a stream from the file or shard containing the elf header.
        Must be opened in binary mode.

        Will throw an ELFError if the file isn't ELF. There are no guarantees
        about correctness if the header is incomplete, so it's wise to at least
        have ~10kB of the stream before invoking this.
        """
        self.elf = ELFFile(fh)

    def get_note(self):
        """
        Returns the note information as a dict.

        Expect { version: 0, num_shards: N, dump_size: Z }
        """
        for seg in self.elf.iter_segments():
            if seg['p_type'] != 'PT_NOTE':
                continue

            note = self._find_note_in_segment(seg)
            if note is not None:
                return note

    def _find_note_in_segment(self, seg):
        """ Returns the fungible note from this segment, or None """

        for note in seg.iter_notes():
            if note['n_name'] == 'Fungible' and note['n_type'] == 0:
                # reverse the less-than-helpful string conversion done
                # by the pyelftools module
                desc = note['n_desc'].encode('latin-1')
                t = struct.unpack('>LLQ', desc)

                ret = {}
                ret['version'] = t[0]
                ret['num_shards'] = t[1]
                ret['dump_size'] = t[2]
                return ret
        return None


def main():
    """ Really a usage example """
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='File or shard with ELF header')

    args = parser.parse_args()

    fh = open(args.file, 'rb')
    note = ELFDumpNote(fh)
    print(note.get_note())


if __name__ == '__main__':
    main()
