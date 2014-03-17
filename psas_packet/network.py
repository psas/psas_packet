# -*- coding: utf-8 -*-
"""Network stack for exchanging packets with messages.
"""
import socket

class SendUDP(object):
    """UDP socket sender context

    :param string addr: IP Address to send to
    :param int send_port: Port number to send to
    :param int from_port: Port number to send from (default=0)
    :returns: SendUDP instance

    Example use with a context manager::

        with SendUDP('127.0.0.1', 4321) as udp:
            udp.send_message(msgtype, data)

    """

    def __init__(self, addr, send_port, from_port=0):
        self.ip_address = addr
        self.send_port = send_port
        self.from_port = from_port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', self.from_port))
        self.socket.connect((self.ip_address, self.send_port))

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.socket.close()

    def close(self):
        """Release the socket
        """
        self.socket.close()        

    def send_message(self, msgtype, data):
        """Send message over socket. Does the packing for you.

        :param Message msgtype: Message class to use for packing, see: psas_packet.messages
        :param dict data: Data to get packed and sent

        """
        self.socket.send(msgtype.encode(data))
