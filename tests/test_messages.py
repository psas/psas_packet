#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_messages
----------------------------------

Tests for `messages` module.
"""

import unittest
from math import fabs
from psas_packet import messages

class TestMessages(unittest.TestCase):

    def setUp(self):
        pass

    def test_encode(self):
        data = {
            'VCC': 5.0,
            'Gyro_X': 0.0,
            'Gyro_Y': 0,
            'Gyro_Z': 1,
            'Acc_X': -9.8,
            'Acc_Y': 0,
            'Acc_Z': 0,
            'Magn_X': 53e-6,
            'Magn_Y': 0,
            'Magn_Z': 0,
            'Temp': 20,
            'Aux_ADC': 0,
        }
        expect = b'\x08\x13\x00\x00\x00\x00\x00\x14\xfe\xd4\x00\x00\x00\x00\x04$\x00\x00\x00\x00\xff\xdd\x00\x00'
        self.assertEqual(messages.ADIS.encode(data), expect)

    def test_roll_message(self):
        data = {'PWM': -1.35e-3, 'Disable': 1}

        encode = messages.ROLL.encode(data)
        decode = messages.ROLL.decode(encode)

        self.assertAlmostEqual(decode['PWM'], data['PWM'], delta=0.1e-3)
        self.assertEqual(decode['Disable'], data['Disable'])


    def test_decode_too_short(self):
        raw = b'\x08\x13\x00\x00\x00\x00\x00\x14\xfe\xda\x00\x00\x00'
        self.assertRaises(messages.MessageSizeError, messages.ADIS.decode, raw)

    def test_decode_too_long(self):
        raw = b'\x08\x13\x00\x00\x00\x00\x00\x14\xfe\xda\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xdd\x00\x00\x00'
        self.assertRaises(messages.MessageSizeError, messages.ADIS.decode, raw)

    def test_decode(self):
        expect = {
            'VCC': 5.0,
            'Gyro_X': 1.0,
            'Gyro_Y': 0,
            'Gyro_Z': 0,
            'Acc_X': 98.0,
            'Acc_Y': 0,
            'Acc_Z': 0,
            'Magn_X': 0,
            'Magn_Y': 0,
            'Magn_Z': 0,
            'Temp': 25,
            'Aux_ADC': 0,
        }

        raw = b'\x08\x13\x00\x14\x00\x00\x00\x00\x0b\xbb\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

        output = messages.ADIS.decode(raw)
        self.assertEqual(len(expect), len(output))

        for item, value in output.items():
            sigfig = expect[item] / 100.0 # 1%
            self.assertAlmostEqual(expect[item], value, delta=sigfig)

    def test_back_and_forth(self):
        data = {
            'VCC': 14.5,
            'Gyro_X': 125.4,
            'Gyro_Y': 574.1,
            'Gyro_Z': 0.0,
            'Acc_X': -9.8,
            'Acc_Y': 0,
            'Acc_Z': 120.2,
            'Magn_X': 38.5e-6,
            'Magn_Y':  2.1e-6,
            'Magn_Z': 20.9e-6,
            'Temp': 60,
            'Aux_ADC': 0,
        }

        encode = messages.ADIS.encode(data)
        decode = messages.ADIS.decode(encode)

        for item, value in decode.items():
            sigfig = fabs(data[item]) / 100.0 # 1%
            self.assertAlmostEqual(data[item], value, delta=sigfig)

    def test_typedef(self):

        code = """/*! \\typedef
 * ADIS16405 Data
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
	uint16_t adis_aux_adc;
} __attribute__((packed)) ADIS16405Data;

typedef struct {
	char     ID[4];
	uint8_t  timestamp[6];
	uint16_t data_length;
	ADIS16405Data data;
} __attribute__((packed)) ADISMessage;
"""

        self.assertEqual(messages.ADIS.typedef(), code)

    def test_typedef_corner(self):

        code = """/*! \\typedef
 * GPSWAASMessage Data
 */
typedef struct {
	uint16_t gps80_prn;
	uint16_t gps80_spare;
	uint32_t gps80_msg_sec_of_week;
	char gps80_waas_msg[32];
} __attribute__((packed)) GPSWAASMessageData;

typedef struct {
	char     ID[4];
	uint8_t  timestamp[6];
	uint16_t data_length;
	GPSWAASMessageData data;
} __attribute__((packed)) GPS80Message;
"""

        self.assertEqual(messages.GPS80.typedef(), code)

    def test_build_typedef(self):

        for message in messages.PSAS_MESSAGES:
            self.assertEqual(type(message.typedef()), str)

    def test_fourcc_unique(self):
        fourcc = [msg.fourcc for msg in messages.PSAS_MESSAGES]
        dupes = set([x for x in fourcc if fourcc.count(x) > 1])
        self.assertEqual(len(dupes), 0)

    def test_header_encode(self):
        h = messages.Head()
        raw = h.encode(messages.ADIS, 0)
        self.assertEqual(raw, b'ADIS\x00\x00\x00\x00\x00\x00\x00\x18')

        raw = h.encode(messages.ADIS, 1)
        self.assertEqual(raw, b'ADIS\x00\x00\x00\x00\x00\x01\x00\x18')

        raw = h.encode(messages.ADIS, 226345)
        self.assertEqual(raw, b'ADIS\x00\x00\x00\x03t)\x00\x18')

    def test_header_decode(self):
        h = messages.Head()
        info = h.decode(b'ADIS\x00\x00\x00\x00\x00\x00\x00\x18')
        self.assertEqual(info, {'fourcc': b'ADIS', 'timestamp': 0, 'length': 24})

        info = h.decode(b'ADIS\x00\x00\x00\x00\x00\x01\x00\x18')
        self.assertEqual(info, {'fourcc': b'ADIS', 'timestamp': 1, 'length': 24})

        info = h.decode(b'ADIS\x00\x00\x00\x0b\x7fn\x00\x18')
        self.assertEqual(info, {'fourcc': b'ADIS', 'timestamp': 753518, 'length': 24})

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
