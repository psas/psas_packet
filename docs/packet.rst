==============
Data Structure
==============


Message
=======

A PSAS Message has a header with an ASCII four character code (e.g., 'ADIS')
that identifies it. This is followed by a 6 byte timestamp in nanoseconds.
This is always nanosecond since beginning of a program, which
is usually the same as boot time for a device. This is followed by two bytes
that give the size of the rest of the message. The remainder of the message
is a collection of *Data*.

Data
====

Data can be almost anything, even other messages. Usually it's a pre-defined
set of fixed sized numbers


.. figure:: diagrams/definition.svg
    :scale: 100 %
    :alt: Data structure overview

    A Message with a header and pre-defined container
