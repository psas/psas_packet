==============
Data Structure
==============


PSAS Packet
===========

A single packet is (usually) a UDP packet. The first 4 bytes are a sequence
number followed by a collection of *PSAS Messages*.

PSAS Message
============

A PSAS Message has a header with a four character code, e.g., 'ADIS' that
identifies it. This is followed by a 6 byte (space saving!) timestamp in
nanoseconds. This is always nanosecond since beginning of a program, which
is usually the same as boot time for a device. This is followed by two bytes
that give the size of the rest of the message. The remainder of the message
is made up of a collection of *Data*.

PSAS Data
=========

A single piece of data, e.g., a voltage reading, is single value. Sometimes
this is a string where the length is known because of the length of the
message explained in the header.

