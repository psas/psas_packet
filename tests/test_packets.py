#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_packets
----------------------------------

Tests for `packets` module.
"""

import unittest
from psas_packet import packets


class TestPackets(unittest.TestCase):

    def setUp(self):
        pass

    def test_repr(self):
        self.assertEqual(str(packets.ADIS), "ADIS packet [ADIS]")

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
