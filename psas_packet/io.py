#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import socket
import errno
import sys
import time
from psas_packet import messages

SEQN = messages.MESSAGES['SEQN']
HEADER = messages.HEADER

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

    def __init__(self, connection, logfile=None):
        self.conn = connection

        self.fh = None
        if logfile is not None:
            # does this look like an object we can write to?
            # otherwise assume it's the filename to open
            if hasattr(logfile, 'write'):
                self.fh = logfile
            else:
                self.fh = open(logfile, 'wb')

    def listen(self):
        """Read from socket, and decode the messages inside.
        """

        # grab bits off the wire
        buff, addr = self.conn.recvfrom(2048)
        timestamp = time.time()

        if buff is not None:
            seqn = SEQN.decode(buff[:SEQN.size])
            if seqn is None:
                return
            yield timestamp, ('SEQN', seqn)
            buff = buff[SEQN.size:]

            if self.fh is not None:
                self.fh.write(HEADER.encode(SEQN, int(timestamp)))
                self.fh.write(SEQN.encode(seqn))
                self.fh.write(buff)
                self.fh.flush()

            # decode until we run out of bytes
            while buff != '':
                try:
                    bytes_read, data = messages.decode(buff)
                    buff = buff[bytes_read:]
                    yield timestamp, data
                except messages.MessageSizeError:
                    print("out of sync")
                    return
                except:
                    print("Reader Broke!")
                    return

    def send_data(self, msgtype, seqn, data):
        """Send message with a sequence number header over a socket. Does the packing for you.

        :param Message msgtype: Message class to use for packing, see: psas_packet.messages
        :param int seqn: Sequence number
        :param dict data: Data to get packed and sent

        """

        packed = msgtype.encode(data)
        s = messages.MESSAGES['SEQN'].encode({'Sequence': seqn})

        try:
            self.conn.send(s + packed)
        except socket.error as e:
            if e.errno == errno.ECONNREFUSED:
                print('connection refused, continuing')
            else:
                raise


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

    def scan(self):
        """Only unpack sequence numbers and return raw data inbetween
        """

        # Read a chunk of file
        buff = self.fh.read(1 << 20)  # 1 MB

        # As long as we have something to look at
        while buff != b'':
            try:
                fourcc, timestamp, length = HEADER.decode(buff[:HEADER.size])
                bytes_read = HEADER.size + length

                if len(buff) < bytes_read:
                    b = self.fh.read(1 << 20)  # 1 MB
                    # Check that we didn't actually hit the end of the file
                    if b == b'':
                        break
                    buff += b

                raw = buff[:bytes_read]
                yield fourcc, raw

                buff = buff[bytes_read:]
                # check boundary
                if len(buff) < 4:
                    b = self.fh.read(1 << 20)  # 1 MB
                    # Check that we didn't actually hit the end of the file
                    if b == b'':
                        break
                    buff += b
            except (messages.MessageSizeError):
                b = self.fh.read(1 << 20)  # 1 MB
                # Check that we didn't actually hit the end of the file
                if b == b'':
                    break
                buff += b


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

                # check boundary
                if len(buff) < 4:
                    b = self.fh.read(1 << 20)  # 1 MB
                    # Check that we didn't actually hit the end of the file
                    if b == b'':
                        print('boundary?')
                        break
                    buff += b
            except (messages.MessageSizeError):
                b = self.fh.read(1 << 20)  # 1 MB
                # Check that we didn't actually hit the end of the file
                if b == b'':
                    print('end?')
                    break
                buff += b


def log2csv(f_in):
    """Read in a binary logfile and output a set of .csv files with the data
    """

    files = {}
    seq = 0
    with BinFile(f_in) as log:

        # Read file
        for fourcc, data in log.read():
            if fourcc in messages.MESSAGES:

                # first time seeing data from this type
                if fourcc not in files:
                    files[fourcc] = open(str(fourcc)+'.csv', 'w')
                    files[fourcc].write("# [0]SEQN, [1]Timestamp")
                    for i, member in enumerate(messages.MESSAGES[fourcc].member_list):
                        files[fourcc].write(", [{0}]{1}".format(i+2, member['key']))
                    files[fourcc].write('\n')

                if fourcc == b'SEQN':
                    seq = data['Sequence']
                    sys.stdout.write(" SEQN: %10d \r" % seq)
                    sys.stdout.flush()

                f_out = files[fourcc]
                f_out.write(str(seq)+","+str(data['timestamp']))
                for member in messages.MESSAGES[fourcc].member_list:
                    f_out.write(","+str(data[member['key']]))
                f_out.write('\n')

    for fourcc, fh in files.items():
        fh.close()
