=======
Network
=======

SendUDP Class
=============

This class can be used to send packets on a network.

.. autoclass:: psas_packet.network.SendUDP
   :members: send_message, close


ListenUDP Class
===============

This class provides low level UDP listening. ListenUDP will connect to a socket
and has an infinite loop listener with optional timeout.

.. autoclass:: psas_packet.network.ListenUDP
   :members: listen, close

