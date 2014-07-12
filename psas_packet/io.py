#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from psas_packet import messages
import time


def _is_string_like(obj):
    """
    Check whether obj behaves like a string.
    """
    try:
        obj + ''
    except (TypeError, ValueError):
        return False
    return True


class Network(object):
    """Read from a network protcol and decode

    :param connection: socket to read from
    :returns: Network object

    """

    def __init__(self, connection):
        self.conn = connection

    def listen(self):
        """Read from socket, and decode the messages inside.
        """

        # grab bits off the wire
        buff, addr = self.conn.recvfrom(2048)
        timestamp = time.time()

        if buff is not None:
            seqn = messages.SequenceNo.decode(buff, timestamp)
            if seqn is None:
                return
            yield seqn
            buff = buff[messages.SequenceNo.size:]

            # decode until we run out of bytes
            while buff != '':
                try:
                    bytes_read, data = messages.decode(buff)
                    for d in data:
                        data[d]['recv'] = timestamp
                    buff = buff[bytes_read:]
                    yield data
                except:
                    print("Reader Broke!")
                    return


class BinFile(object):
    """Read from a binary log file

    :param fname: A filename or file-like object
    :returns: BinFile object

    """

    def __init__(self, fname):

        # Try and see if the passed in file is filename (string) or an object that might act like a file
        if _is_string_like(fname):
            self.fh = open(fname, 'rb')
        else:
            self.fh = fname

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.fh.close()

    def read(self):
        """Read the file and return data inside it
        """

        # Read a chunk of file
        buff = self.fh.read(1 << 20)  # 1 MB

        # As long as we have something to look at
        while buff != b'':
            try:
                bytes_read, data = messages.decode(buff)
                buff = buff[bytes_read:]
                yield data
            except (messages.BlockSize):
                b = self.fh.read(1 << 20)  # 1 MB
                # Check that we didn't actually hit the end of the file
                if b == b'':
                    break
                buff += b
            except:
                #print(buff[:100])
                pass
