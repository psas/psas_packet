#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from psas_packet import messages

HEADERSIZE = messages.Head.size()
PSAS = {cls.fourcc: cls for cls in messages.PSAS_MESSAGES}


def _is_string_like(obj):
    """
    Check whether obj behaves like a string.
    """
    try:
        obj + ''
    except (TypeError, ValueError):
        return False
    return True


class BinFile(object):

    def __init__(self, fname):

        # Try and see if the passed in file is filename (string?) or an object that might act like a file
        if _is_string_like(fname):
            self.fh = open(fname, 'rb')
        else:
            self.fh = fname

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.fh.close()

    def read(self, chunk=1500):

        buff = self.fh.read(chunk)
        if len(buff) < HEADERSIZE:
            raise(Exception("End of file Reached with incomplete data"))
            return

        # Read header:
        info = messages.Head.decode(buff[:HEADERSIZE])

        message_cls = PSAS.get(info['fourcc'], None)
        if message_cls is not None:
            unpacked = message_cls.decode(buff[HEADERSIZE:HEADERSIZE+message_cls.size])
            yield {info['fourcc']: dict({'timestamp': info['timestamp']}, **unpacked)}

    def read_until_seq(self):
        while 'SEQN' in self.read():
            print('one')
            pass
