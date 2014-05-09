#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_network
----------------------------------

Tests for `network` module.
"""

import unittest
import socket
from psas_packet import network, messages

class TestNetworkSend(unittest.TestCase):

    def setUp(self):
        self.reciever = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.reciever.bind(('0.0.0.0', 0))
        self.reciever.settimeout(0.01)
        self.receiver_port = self.reciever.getsockname()[1]

    def test_send_message(self):
        with network.SendUDP('127.0.0.1', self.receiver_port) as udp:
            data = {'PWM': 1.135e-3, 'Disable': 1}
            expect = messages.ROLL.encode(data)
            udp.send_message(messages.ROLL, data)

        recv_data = self.reciever.recv(1024)
        self.assertEqual(expect, recv_data)

    def tearDown(self):
        self.reciever.close()

class TestNetworkRecieve(unittest.TestCase):

    def setUp(self):
        self.sender = network.SendUDP('127.0.0.1', 1934)

    def test_recv_message(self):
        data = {'PWM': 1.135e-3, 'Disable': 1}

        with network.ListenUDP(1934) as listen:
            self.sender.send_message(messages.ROLL, data)
            recv_data = listen.listen()
            self.assertEqual(messages.ROLL.encode(data), recv_data)

    def tearDown(self):
        self.sender.close()
