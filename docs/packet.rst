==============
Data Structure
==============

PSAS Packet
===========

Is a *Data Structure*. Can be implemented for example as a UDP packet, or as
a logfile.


PSAS Message
============

A PSAS Message has a header with a four character code, e.g., 'ADIS' that
identifies it. This is followed by a 6 byte (space saving!) timestamp in
nanoseconds. This is always nanosecond since beginning of a program, which
is usually the same as boot time for a device. This is followed by two bytes
that give the size of the rest of the message. The remainder of the message
is *Data Structure*.


PSAS Data Structure
===================

A collection of *Data*. Is associated with a sequence number
