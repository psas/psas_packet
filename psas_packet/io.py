#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from psas_packet import messages

HEADER = messages.Head()
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


class BlockSize(Exception):

    def __init__(self):
        msg = "Block to decode is too small"
        Exception.__init__(self, msg)


def decode_block(block):
    """Decode a single message from a block of bytes.

    :param bytes block: bytes to try and decode
    :returns: number of bytes read, dictionary with unpacked values

    Raises exeptions if block is not readable
    """

    # HEADER:

    # make sure we have enough bytes to deocde a header, then do it
    if len(block) < HEADER.size:
        raise(BlockSize)
        return
    info = HEADER.decode(block[:HEADER.size])

    # DATA:

    # figure out what type it is based on FOURCC, and get that message class
    message_cls = PSAS.get(info['fourcc'], None)

    # Yay! We know about this type, lets unpack it
    if message_cls is not None:
        if len(block) < HEADER.size+message_cls.size:
            raise(BlockSize)
            return
        unpacked = message_cls.decode(block[HEADER.size:HEADER.size+message_cls.size])
        return HEADER.size+message_cls.size, {info['fourcc']: dict({'timestamp': info['timestamp']}, **unpacked)}


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

    def read(self):
        buff = self.fh.read(1<<20) # 1 MB

        while buff != b'':
            try:
                bytes_read, data = decode_block(buff)
                buff = buff[bytes_read:]
                yield data
            except (BlockSize):
                buff += self.fh.read(1<<20)
