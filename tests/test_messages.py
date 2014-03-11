#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_packets
----------------------------------

Tests for `packets` module.
"""

import unittest
from psas_packet import messages


class TestMessages(unittest.TestCase):

    def setUp(self):
        pass

    def test_repr(self):
        self.assertEqual(str(messages.ADIS), "ADIS16405 message [ADIS]")

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
        self.assertEqual(messages.ADIS.encode(data), expect)

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
        expect = b'ADIS' + b'\x00\x00\x00\x01\xe2@' + b'\x00\x18'
        expect += b'\x08\x13\x00\x00\x00\x00\x00\x14\xfe\xda\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xdd\x00\x00'
        self.assertEqual(messages.ADIS.encode(data, timestamp=t), expect)

    def test_typedef(self):

        self.maxDiff = None

        code = """/*! \\typedef
 * ADIS16405 data
 */
typedef struct {
	uint16_t adis_vcc;
	int16_t adis_gyro_x;
	int16_t adis_gyro_y;
	int16_t adis_gyro_z;
	int16_t adis_acc_x;
	int16_t adis_acc_y;
	int16_t adis_acc_z;
	int16_t adis_magn_x;
	int16_t adis_magn_y;
	int16_t adis_magn_z;
	int16_t adis_temp;
	int16_t adis_aux_adc;
} __attribute__((packed)) ADIS16405Data;

typedef struct {
	char     ID[4];
	uint8_t  timestamp[6];
	uint16_t data_length;
	ADIS16405Data data;
} __attribute__((packed)) ADIS16405Message;
"""

        self.assertEqual(messages.ADIS.typedef(), code)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
