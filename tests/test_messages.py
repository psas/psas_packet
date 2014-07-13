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

ADIS = messages.MESSAGES['ADIS']
ROLL = messages.MESSAGES['ROLL']

class TestDecode(unittest.TestCase):

    def test_decode(self):
        expect = {
            'timestamp': 1,
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

        raw = b'ADIS\x00\x00\x00\x00\x00\x01\x00\x18\x08\x13\x00\x14\x00\x00\x00\x00\x0b\xbb\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

        bytes_read, output = messages.decode(raw)
        fourcc, data = output

        self.assertEqual(bytes_read, messages.HEADER.size+ADIS.size)
        self.assertEqual(fourcc, b'ADIS')
        self.assertEqual(len(expect), len(data))

        for item, value in data.items():
            sigfig = expect[item] / 100.0 # 1%
            self.assertAlmostEqual(expect[item], value, delta=sigfig)


class TestMessages(unittest.TestCase):

    def test_printable(self):
        self.assertEqual(messages.printable(b'GPS^'), "GPS94")

    def test_message_encode(self):
        # data with missing entires
        data = {
            'VCC': 5.0,
            'Gyro_X': 0.0,
            'Gyro_Z': 1,
            'Acc_X': -9.8,
            'Acc_Y': 0,
            'Acc_Z': 0,
            'Magn_X': 53e-6,
            'Magn_Z': 0,
            'Temp': 20,
            'Aux_ADC': 0,
        }
        expect = b'\x08\x13\x00\x00\x00\x00\x00\x14\xfe\xd4\x00\x00\x00\x00\x04$\x00\x00\x00\x00\xff\xdd\x00\x00'
        self.assertEqual(ADIS.encode(data), expect)

    def test_roll_message(self):
        data = {'Angle': 1.3, 'Disable': 1}

        encode = ROLL.encode(data)
        decode = ROLL.decode(encode)

        self.assertAlmostEqual(decode['Angle'], data['Angle'], delta=0.1e-1)
        self.assertEqual(decode['Disable'], data['Disable'])

    def test_decode_too_short(self):
        raw = b'\x08\x13\x00\x00\x00\x00\x00\x14\xfe\xda\x00\x00\x00'
        self.assertRaises(messages.MessageSizeError, ADIS.decode, raw)

    def test_decode_too_long(self):
        raw = b'\x08\x13\x00\x00\x00\x00\x00\x14\xfe\xda\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xdd\x00\x00\x00'
        self.assertRaises(messages.MessageSizeError, ADIS.decode, raw)

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

        output = ADIS.decode(raw)
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

        encode = ADIS.encode(data)
        decode = ADIS.decode(encode)

        for item, value in decode.items():
            sigfig = fabs(data[item]) / 100.0 # within 1%
            self.assertAlmostEqual(data[item], value, delta=sigfig)

    def test_typedef(self):

        code = """/*! \\typedef
 * ADIS16405 Data
 */
typedef struct {
	uint16_t vcc;
	int16_t gyro_x;
	int16_t gyro_y;
	int16_t gyro_z;
	int16_t acc_x;
	int16_t acc_y;
	int16_t acc_z;
	int16_t magn_x;
	int16_t magn_y;
	int16_t magn_z;
	int16_t temp;
	uint16_t aux_adc;
} __attribute__((packed)) ADIS16405Data;

typedef struct {
	char     ID[4];
	uint8_t  timestamp[6];
	uint16_t data_length;
	ADIS16405Data data;
} __attribute__((packed)) ADISMessage;
"""

        self.assertEqual(ADIS.typedef(), code)

    def test_typedef_corner(self):

        code = """/*! \\typedef
 * GPSWAASMessage Data
 */
typedef struct {
	uint16_t prn;
	uint16_t spare;
	uint32_t msg_sec_of_week;
	char waas_msg[32];
} __attribute__((packed)) GPSWAASMessageData;

typedef struct {
	char     ID[4];
	uint8_t  timestamp[6];
	uint16_t data_length;
	GPSWAASMessageData data;
} __attribute__((packed)) GPS80Message;
"""

        self.assertEqual(messages.MESSAGES['GPS80'].typedef(), code)

    def test_build_typedef(self):

        for fourcc, message in messages.MESSAGES.items():
            self.assertEqual(type(message.typedef()), str)

    def test_fourcc_unique(self):
        self.assertEqual(len(messages._list), len(messages.MESSAGES))

    def test_header_encode(self):
        raw = messages.HEADER.encode(ADIS, 0)
        self.assertEqual(raw, b'ADIS\x00\x00\x00\x00\x00\x00\x00\x18')

        raw = messages.HEADER.encode(ADIS, 1)
        self.assertEqual(raw, b'ADIS\x00\x00\x00\x00\x00\x01\x00\x18')

        raw = messages.HEADER.encode(ADIS, 226345)
        self.assertEqual(raw, b'ADIS\x00\x00\x00\x03t)\x00\x18')

    def test_header_decode(self):
        info = messages.HEADER.decode(b'ADIS\x00\x00\x00\x00\x00\x00\x00\x18')
        self.assertEqual(info, (b'ADIS', 0, 24))

        info = messages.HEADER.decode(b'ADIS\x00\x00\x00\x00\x00\x01\x00\x18')
        self.assertEqual(info, (b'ADIS', 1, 24))

        info = messages.HEADER.decode(b'ADIS\x00\x00\x00\x0b\x7fn\x00\x18')
        self.assertEqual(info, (b'ADIS', 753518, 24))

    def test_seqn_encode(self):
        SEQN = messages.MESSAGES['SEQN']
        s = SEQN.encode({'Sequence': 0})
        self.assertEqual(s, b'\x00\x00\x00\x00')

        s = SEQN.encode({'Sequence': 1})
        self.assertEqual(s, b'\x00\x00\x00\x01')

        s = SEQN.encode({'Sequence': 84729300})
        self.assertEqual(s, b'\x05\x0c\xdd\xd4')

    def test_seqn_decode(self):
        SEQN = messages.MESSAGES['SEQN']
        data = SEQN.decode(b'\x00\x00\x00\x00')
        self.assertEqual(data, {'Sequence': 0})

        data = SEQN.decode(b'\x00\x00\x00\x01')
        self.assertEqual(data, {'Sequence': 1})

        data = SEQN.decode(b'\x01\xf6\xc4\xb8')
        self.assertEqual(data, {'Sequence': 32949432})


if __name__ == '__main__':
    unittest.main()
