===============
psas_packet API
===============

Message Class
=============

The message class can be initialized with information about the data that can
be packed in it. This will make an object with encode and decode methods
available for packing and unpacking.

.. autoclass:: psas_packet.messages.Message
   :members: encode, decode, typedef


Header
======

Encodes and decodes message headers

.. autoclass:: psas_packet.messages.Head
   :members: encode, decode


--------------------------------------------------------------------------------

Exceptions
==========

.. autoclass::  psas_packet.messages.MessageSizeError
