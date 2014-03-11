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
        self.assertEqual(str(packets.ADIS), "ADIS16405 packet [ADIS]")

    def test_encode(self):
        data = {
            'VCC': 5.0,
            'Gyro_X': 0.0,
            'Gyro_Y': 0,
            'Gyro_Z': 1,
            'Acc_X': -9.8,
            'Acc_Y': 0,
            'Acc_Z': 0,
            'Magn_X': 5.3e-5,
            'Magn_Y': 0,
            'Magn_Z': 0,
            'Temp': 20,
            'Aux_ADC': 0,
        }
        expect = b'\x08\x13\x00\x00\x00\x00\x00\x14\xfe\xda\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xdd\x00\x00'
        self.assertEqual(packets.ADIS.encode(data), expect)

    def test_encode_header(self):
        data = {
            'VCC': 5.0,
            'Gyro_X': 0.0,
            'Gyro_Y': 0,
            'Gyro_Z': 1,
            'Acc_X': -9.8,
            'Acc_Y': 0,
            'Acc_Z': 0,
            'Magn_X': 5.3e-5,
            'Magn_Y': 0,
            'Magn_Z': 0,
            'Temp': 20,
            'Aux_ADC': 0,
        }
        t = 123456
        expect  = b'ADIS' + b'\x00\x00\x00\x01\xe2@' + b'\x00\x18'
        expect += b'\x08\x13\x00\x00\x00\x00\x00\x14\xfe\xda\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xdd\x00\x00'
        self.assertEqual(packets.ADIS.encode(data, timestamp=t), expect)


    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
