""" PSAS Message definitions.
"""
import struct

# Constant, standard gravity
g_0 = 9.80665  # m/s/s

# conversion to c types
CTYPES = {
    'B': 'uint8_t',
    'b': 'int8_t',
    'H': 'uint16_t',
    'h': 'int16_t',
    'L': 'uint32_t',
    'l': 'int32_t',
    'Q': 'uint64_t',
    'q': 'int64_t',
    'f': 'float',
    'd': 'double',
}


def printable(s):
    """Takes fourcc code and makes a printable string

    :param bytes s: Four character code

    GPS fourccs have the last character as a raw byte. When we print them the
    byte should be converted to a string number. For example 'GPS\\x5e' should
    print as GPS94, not GPS^.
    """

    if b'GPS' in s:
        char = s[-1]
        if type(char) is int:
            s = 'GPS' + str(char)
        else:
            s = 'GPS' + str(ord(char))
        return s

    return s.decode('utf-8')


# for some reason floats in python 3 wont cast to int
class Packable(float):
    def __index__(self):
        return int(self)


class MessageSizeError(Exception):
    """Raised when the byte str to be unpacked does not match the expected
    size for this type. Check your message boundaries, or maybe you've
    reached EOF?

    :param int expected: correct size
    :param int got: attempted size
    :returns: MessageSizeError exception

    """

    def __init__(self, expected, got):
        msg = "Wrong data size, expected {0}, got {1}".format(expected, got)
        Exception.__init__(self, msg)


class Head(object):
    """Methods to encode and decodes message headers
    """

    struct = struct.Struct('!4sHLH')

    def __init__(self):
        self.size = self.struct.size

    @classmethod
    def size(cls):
        return cls.struct.size

    @classmethod
    def encode(cls, message_class, time):
        fourcc = message_class.fourcc
        length = message_class.struct.size

        # make timestamp
        timestamp_hi = (time >> 32) & 0xffff
        timestamp_lo = time & 0xffffffff

        # encode
        raw = cls.struct.pack(fourcc, timestamp_hi, timestamp_lo, length)
        return raw

    @classmethod
    def decode(cls, raw):

        if len(raw) != cls.struct.size:
            raise(MessageSizeError(cls.struct.size, len(raw)))
            return

        fourcc, timestamp_hi, timestamp_lo, message_length = cls.struct.unpack(raw)
        timestamp = timestamp_hi << 32 | timestamp_lo

        return {'fourcc': fourcc, 'timestamp': timestamp, 'length': message_length}


class Message(object):
    """Instantiates a message type definition

    :param dict definition: Dictionary defining data in a message
    :returns: Message instance

    Suitable metadata can be passed in and this class will perform
    necessary pre-compute steps and create a usable message instance for
    a specific data source.
    """

    def __init__(self, definition):
        self.name = definition['name']
        self.fourcc = definition['fourcc']

        # Pre-compute struct for fixed size packets
        self.member_dict = {}
        self.member_list = []
        if definition['size'] == "Fixed":
            struct_string = definition['endianness']
            for i, m in enumerate(definition['members']):
                self.member_dict[m['key']] = {'i': i, 'units': m.get('units', {})}
                self.member_list.append(m)
                struct_string += m['stype']
            self.struct = struct.Struct(struct_string)

        self.size = self.struct.size

    def __repr__(self):
        return "{0} message type".format(self.name)

    def encode(self, data):
        """Encode a set of data into binary

        :param dict data: A dictionary of values to encode
        :returns: Binary ecoded data

        Uses the struct package to encode into byte array. The dictionary should
        have values who's keys match the members list.
        """

        # Initialize as zeros
        values = [0] * len(self.member_list)

        # Lookup corresponding metadata
        for key, value in data.items():
            m = self.member_dict[key]
            units = m['units']

            # from native units to packed representation
            v = (value - units.get('bias', 0)) / units.get('scaleby', 1.0)

            # put value in the right place in the list
            values[m['i']] = Packable(v)

        return self.struct.pack(*values)

    def decode(self, raw):
        """Decode a single message body (the data lines). Header info and
        message boundaries are solved in network

        :param bytestr raw: Raw string of bytes the length of
        :returns: A dictionary of values in normal units
        """

        if len(raw) != self.struct.size:
            raise(MessageSizeError(self.struct.size, len(raw)))
            return

        unpack = self.struct.unpack(raw)

        values = {}
        for i, v in enumerate(unpack):
            m = self.member_list[i]
            units = m.get('units', {})
            v = (v * units.get('scaleby', 1)) + units.get('bias', 0)

            values[m['key']] = v

        # Return dictionary instead of list
        return values

    def typedef(self):
        """Autogen c style typedef structs

        :returns: String c code for the data and header for this packet
        """

        # Header comment
        typestruct = "/*! \\typedef\n"
        typestruct += " * {0} Data\n".format(self.name)
        typestruct += " */\n"
        typestruct += "typedef struct {\n"

        # data
        for line in self.member_list:
            stype = line['stype']

            var = "{0}_{1}".format(printable(self.fourcc).lower(), line['key'].lower())

            if 's' in stype:
                ctype = 'char'
                size = int(stype.replace('s', ''))
                var = var + '[{0}]'.format(size)
            else:
                ctype = CTYPES[stype]

            typestruct += "\t{0} {1};\n".format(ctype, var)

        typestruct += "}} __attribute__((packed)) {0}Data;\n".format(self.name)

        typestruct += """\ntypedef struct {{
\tchar     ID[4];
\tuint8_t  timestamp[6];
\tuint16_t data_length;
\t{1}Data data;
}} __attribute__((packed)) {0}Message;\n""".format(printable(self.fourcc), self.name)

        return typestruct


# Here we define known PSAS message types:
SEQN = Message({
    'name': "SequenceNo",
    'fourcc': b'SEQN',
    'size': "Fixed",
    'endianness': '!',
    'members': [
        {'key': "Sequence", 'stype': "L"},
    ]
})

ADIS = Message({
    'name': "ADIS16405",
    'fourcc': b'ADIS',
    'size': "Fixed",
    'endianness': '!',
    'members': [
        {'key': "VCC",     'stype': "H", 'units': {'mks': "volt",      'scaleby': 0.002418}},
        {'key': "Gyro_X",  'stype': "h", 'units': {'mks': "hertz",     'scaleby': 0.05}},
        {'key': "Gyro_Y",  'stype': "h", 'units': {'mks': "hertz",     'scaleby': 0.05}},
        {'key': "Gyro_Z",  'stype': "h", 'units': {'mks': "hertz",     'scaleby': 0.05}},
        {'key': "Acc_X",   'stype': "h", 'units': {'mks': "meter/s/s", 'scaleby': 0.00333 * g_0}},
        {'key': "Acc_Y",   'stype': "h", 'units': {'mks': "meter/s/s", 'scaleby': 0.00333 * g_0}},
        {'key': "Acc_Z",   'stype': "h", 'units': {'mks': "meter/s/s", 'scaleby': 0.00333 * g_0}},
        {'key': "Magn_X",  'stype': "h", 'units': {'mks': "tesla",     'scaleby': 5e-8}},
        {'key': "Magn_Y",  'stype': "h", 'units': {'mks': "tesla",     'scaleby': 5e-8}},
        {'key': "Magn_Z",  'stype': "h", 'units': {'mks': "tesla",     'scaleby': 5e-8}},
        {'key': "Temp",    'stype': "h", 'units': {'mks': "degree c",  'scaleby': 0.14, 'bias': 25}},
        {'key': "Aux_ADC", 'stype': "H", 'units': {'mks': "volt",      'scaleby': 806}},
    ]
})

ROLL = Message({
    'name': "RollServo",
    'fourcc': b'ROLL',
    'size': "Fixed",
    'endianness': '!',
    'members': [
        {'key': "PWM",                  'stype': "H", 'units': {'mks': "second", 'scaleby': 1e-6, 'bias': -1.5e-3}},
        {'key': "Disable",              'stype': "B"},
    ]
})

RNHH = Message({
    'name': "RNHHealth",
    'fourcc': b'RNHH',
    'size': "Fixed",
    'endianness': '!',
    'members': [
        {'key': "Temperature",          'stype': "H", 'units': {'mks': "kelvin",    'scaleby': 0.1}},
        {'key': "TS1Temperature",       'stype': "h", 'units': {'mks': "degree c",  'scaleby': 0.1}},
        {'key': "TS2Temperature",       'stype': "h", 'units': {'mks': "degree c",  'scaleby': 0.1}},
        {'key': "TempRange",            'stype': "H"},
        {'key': "Voltage",              'stype': "H", 'units': {'mks': "volt",      'scaleby': 0.001}},
        {'key': "Current",              'stype': "h", 'units': {'mks': "amp",       'scaleby': 0.001}},
        {'key': "AverageCurrent",       'stype': "h", 'units': {'mks': "amp",       'scaleby': 0.001}},
        {'key': "CellVoltage1",         'stype': "H", 'units': {'mks': "volt",      'scaleby': 0.001}},
        {'key': "CellVoltage2",         'stype': "H", 'units': {'mks': "volt",      'scaleby': 0.001}},
        {'key': "CellVoltage3",         'stype': "H", 'units': {'mks': "volt",      'scaleby': 0.001}},
        {'key': "CellVoltage4",         'stype': "H", 'units': {'mks': "volt",      'scaleby': 0.001}},
        {'key': "PackVoltage",          'stype': "H", 'units': {'mks': "volt",      'scaleby': 0.001}},
        {'key': "AverageVoltage",       'stype': "H", 'units': {'mks': "volt",      'scaleby': 0.001}},
    ]
})

# ADC scale for power measuremnets
_rnhpscale = (3.3/2**12) * (63000.0/69800.0)

RNHP = Message({
    'name': "RNHPower",
    'fourcc': b'RNHP',
    'size': "Fixed",
    'endianness': '<',
    'members': [
        {'key': "Port1", 'stype': "H", 'units': {'mks': 'amp', 'scaleby': _rnhpscale}},
        {'key': "Port2", 'stype': "H", 'units': {'mks': 'amp', 'scaleby': _rnhpscale}},
        {'key': "Port3", 'stype': "H", 'units': {'mks': 'amp', 'scaleby': _rnhpscale}},
        {'key': "Port4", 'stype': "H", 'units': {'mks': 'amp', 'scaleby': _rnhpscale}},
        {'key': "Port5", 'stype': "H", 'units': {'mks': 'amp', 'scaleby': _rnhpscale}},
        {'key': "Port6", 'stype': "H", 'units': {'mks': 'amp', 'scaleby': _rnhpscale}},
        {'key': "Port7", 'stype': "H", 'units': {'mks': 'amp', 'scaleby': _rnhpscale}},
        {'key': "Port8", 'stype': "H", 'units': {'mks': 'amp', 'scaleby': _rnhpscale}},
    ]
})


LTC = Message({
    'name': "LaunchTowerComputer",
    'fourcc': b'LTCH',
    'size': "Fixed",
    'endianness': '!',
    'members': [
        {'key': "Rocket_Ready",                  'stype': "f", 'units': {'mks': "volt"}},
        {'key': "Iginition_Relay",               'stype': "B"},
        {'key': "Ignition_Battery",              'stype': "f", 'units': {'mks': "volt"}},
        {'key': "Shore_Power_Relay",             'stype': "B"},
        {'key': "Shore_Power",                   'stype': "f", 'units': {'mks': "volt"}},
        {'key': "Solar_Voltage",                 'stype': "f", 'units': {'mks': "volt"}},
        {'key': "System_Battery",                'stype': "f", 'units': {'mks': "volt"}},
        {'key': "Internal_Temp",                 'stype': "f", 'units': {'mks': "celsius"}},
        {'key': "External_Temp",                 'stype': "f", 'units': {'mks': "celsius"}},
        {'key': "Humidity",                      'stype': "f"},
        {'key': "Wind_Speed",                    'stype': "f"},
        {'key': "Wind_Direction",                'stype': "f"},
        {'key': "Barometric_Pressure",           'stype': "f"}
    ]
})


GPS1 = Message({
    'name': "GPSFix",
    'fourcc': b'GPS'+chr(1).encode(),
    'size': "Fixed",
    'endianness': '<',
    'members': [
        {'key': "Age_Of_Diff",          'stype': 'B', 'units': {'mks': "second"}},
        {'key': "Num_Of_Sats",          'stype': 'B'},
        {'key': "GPS_Week",             'stype': 'H'},
        {'key': "GPS_Time_Of_Week",     'stype': 'd', 'units': {'mks': "second"}},
        {'key': "Latitude",             'stype': 'd', 'units': {'mks': "degree"}},
        {'key': "Longitude",            'stype': 'd', 'units': {'mks': "degree"}},
        {'key': "Height",               'stype': 'f', 'units': {'mks': "meter"}},
        {'key': "VNorth",               'stype': 'f', 'units': {'mks': "meter/s"}},
        {'key': "VEast",                'stype': 'f', 'units': {'mks': "meter/s"}},
        {'key': "VUp",                  'stype': 'f', 'units': {'mks': "meter/s"}},
        {'key': "Std_Dev_Resid",        'stype': 'f', 'units': {'mks': "meter"}},
        {'key': "Nav_Mode",             'stype': 'H'},
        {'key': "Extended_Age_Of_Diff", 'stype': 'H', 'units': {'mks': "second"}},
    ]
})

GPS2 = Message({
    'name': "GPSFixQuality",
    'fourcc': b'GPS'+chr(2).encode(),
    'size': "Fixed",
    'endianness': '<',
    'members': [
        {'key': "Mask_Sats_Tracked",    'stype': 'L'},
        {'key': "Mask_Sats_Used",       'stype': 'L'},
        {'key': "GPS_UTC_Diff",         'stype': 'H'},
        {'key': "HDOP",                 'stype': 'H', 'units': {'scaleby': 10}},
        {'key': "VDOP",                 'stype': 'H', 'units': {'scaleby': 10}},
        {'key': "Mask_WAAS_PRN",        'stype': 'H'},
    ]
})

GPS80 = Message({
    'name': "GPSWAASMessage",
    'fourcc': b'GPS'+chr(80).encode(),
    'size': "Fixed",
    'endianness': '<',
    'members': [
        {'key': "PRN",                  'stype': 'H'},
        {'key': "Spare",                'stype': 'H'},
        {'key': "Msg_Sec_of_Week",      'stype': 'L'},
        {'key': "Waas_Msg",             'stype': '32s'},
    ]
})

GPS93 = Message({
    'name': "GPSWAASEphemeris",
    'fourcc': b'GPS'+chr(93).encode(),
    'size': "Fixed",
    'endianness': '<',
    'members': [
        {'key': "SV",                   'stype': 'H'},
        {'key': "spare",                'stype': 'H'},
        {'key': "TOW_Sec-of-Week",      'stype': 'L'},
        {'key': "IODE",                 'stype': 'H'},
        {'key': "URA",                  'stype': 'H'},
        {'key': "T_Zero",               'stype': 'l'},
        {'key': "XG",                   'stype': 'l', 'units': {'mks': "meter", 'scaleby': 0.08}},
        {'key': "YG",                   'stype': 'l', 'units': {'mks': "meter", 'scaleby': 0.08}},
        {'key': "ZG",                   'stype': 'l', 'units': {'mks': "meter", 'scaleby': 0.4}},
        {'key': "XG_Dot",               'stype': 'l', 'units': {'mks': "meter/s", 'scaleby': 0.000625}},
        {'key': "YG_Dot",               'stype': 'l', 'units': {'mks': "meter/s", 'scaleby': 0.000625}},
        {'key': "ZG_Dot",               'stype': 'l', 'units': {'mks': "meter/s", 'scaleby': 0.004}},
        {'key': "XG_DotDot",            'stype': 'l', 'units': {'mks': "meter/s/s", 'scaleby': 0.0000125}},
        {'key': "YG_DotDot",            'stype': 'l', 'units': {'mks': "meter/s/s", 'scaleby': 0.0000125}},
        {'key': "ZG_DotDot",            'stype': 'l', 'units': {'mks': "meter/s/s", 'scaleby': 0.0000625}},
        {'key': "Gf_Zero",              'stype': 'H'},
        {'key': "Gf_Zero_Dot",          'stype': 'H'},
    ]
})

GPS94 = Message({
    'name': "GPSIonosphereUTC",
    'fourcc': b'GPS'+chr(94).encode(),
    'size': "Fixed",
    'endianness': '<',
    'members': [
        {'key': "a0",                   'stype': 'd'},
        {'key': "a1",                   'stype': 'd'},
        {'key': "a2",                   'stype': 'd'},
        {'key': "a3",                   'stype': 'd'},
        {'key': "b0",                   'stype': 'd'},
        {'key': "b1",                   'stype': 'd'},
        {'key': "b2",                   'stype': 'd'},
        {'key': "b3",                   'stype': 'd'},
        {'key': "UTC_A0",               'stype': 'd'},
        {'key': "UTC_A1",               'stype': 'd'},
        {'key': "tot",                  'stype': 'L'},
        {'key': "wnt",                  'stype': 'H'},
        {'key': "wnlsf",                'stype': 'H'},
        {'key': "dn",                   'stype': 'H'},
        {'key': "dtls",                 'stype': 'H'},
        {'key': "dtlsf",                'stype': 'H'},
        {'key': "space",                'stype': 'H'},
    ]
})

GPS95 = Message({
    'name': "GPSEphemeris",
    'fourcc': b'GPS'+chr(95).encode(),
    'size': "Fixed",
    'endianness': '<',
    'members': [
        {'key': "SV",                   'stype': 'H'},
        {'key': "spare",                'stype': 'H'},
        {'key': "Sec_of_Week",          'stype': 'L'},
        {'key': "SF1_Words",            'stype': '40s'},
        {'key': "SF2_Words",            'stype': '40s'},
        {'key': "SF3_Words",            'stype': '40s'},
    ]
})

GPS96 = Message({
    'name': "GPSPsudorange",
    'fourcc': b'GPS'+chr(96).encode(),
    'size': "Fixed",
    'endianness': '<',
    'members': [
        {'key': "spare",                'stype': 'H'},
        {'key': "Week",                 'stype': 'H'},
        {'key': "TOW",                  'stype': 'd'},
        {'key': "UICS_TT_SNR_PRN_0",    'stype': 'L'},
        {'key': "UICS_TT_SNR_PRN_1",    'stype': 'L'},
        {'key': "UICS_TT_SNR_PRN_2",    'stype': 'L'},
        {'key': "UICS_TT_SNR_PRN_3",    'stype': 'L'},
        {'key': "UICS_TT_SNR_PRN_4",    'stype': 'L'},
        {'key': "UICS_TT_SNR_PRN_5",    'stype': 'L'},
        {'key': "UICS_TT_SNR_PRN_6",    'stype': 'L'},
        {'key': "UICS_TT_SNR_PRN_7",    'stype': 'L'},
        {'key': "UICS_TT_SNR_PRN_8",    'stype': 'L'},
        {'key': "UICS_TT_SNR_PRN_9",    'stype': 'L'},
        {'key': "UICS_TT_SNR_PRN_10",   'stype': 'L'},
        {'key': "UICS_TT_SNR_PRN_11",   'stype': 'L'},
        {'key': "UIDoppler_FL_0",       'stype': 'L'},
        {'key': "UIDoppler_FL_1",       'stype': 'L'},
        {'key': "UIDoppler_FL_2",       'stype': 'L'},
        {'key': "UIDoppler_FL_3",       'stype': 'L'},
        {'key': "UIDoppler_FL_4",       'stype': 'L'},
        {'key': "UIDoppler_FL_5",       'stype': 'L'},
        {'key': "UIDoppler_FL_6",       'stype': 'L'},
        {'key': "UIDoppler_FL_7",       'stype': 'L'},
        {'key': "UIDoppler_FL_8",       'stype': 'L'},
        {'key': "UIDoppler_FL_9",       'stype': 'L'},
        {'key': "UIDoppler_FL_10",      'stype': 'L'},
        {'key': "UIDoppler_FL_11",      'stype': 'L'},
        {'key': "PseudoRange_0",        'stype': 'd'},
        {'key': "PseudoRange_1",        'stype': 'd'},
        {'key': "PseudoRange_2",        'stype': 'd'},
        {'key': "PseudoRange_3",        'stype': 'd'},
        {'key': "PseudoRange_4",        'stype': 'd'},
        {'key': "PseudoRange_5",        'stype': 'd'},
        {'key': "PseudoRange_6",        'stype': 'd'},
        {'key': "PseudoRange_7",        'stype': 'd'},
        {'key': "PseudoRange_8",        'stype': 'd'},
        {'key': "PseudoRange_9",        'stype': 'd'},
        {'key': "PseudoRange_10",       'stype': 'd'},
        {'key': "PseudoRange_11",       'stype': 'd'},
        {'key': "Phase_0",              'stype': 'd', 'units': {'mks': "meter"}},
        {'key': "Phase_1",              'stype': 'd', 'units': {'mks': "meter"}},
        {'key': "Phase_2",              'stype': 'd', 'units': {'mks': "meter"}},
        {'key': "Phase_3",              'stype': 'd', 'units': {'mks': "meter"}},
        {'key': "Phase_4",              'stype': 'd', 'units': {'mks': "meter"}},
        {'key': "Phase_5",              'stype': 'd', 'units': {'mks': "meter"}},
        {'key': "Phase_6",              'stype': 'd', 'units': {'mks': "meter"}},
        {'key': "Phase_7",              'stype': 'd', 'units': {'mks': "meter"}},
        {'key': "Phase_8",              'stype': 'd', 'units': {'mks': "meter"}},
        {'key': "Phase_9",              'stype': 'd', 'units': {'mks': "meter"}},
        {'key': "Phase_10",             'stype': 'd', 'units': {'mks': "meter"}},
        {'key': "Phase_11",             'stype': 'd', 'units': {'mks': "meter"}},
    ]
})

GPS98 = Message({
    'name': "GPSAlmanac",
    'fourcc': b'GPS'+chr(98).encode(),
    'size': "Fixed",
    'endianness': '<',
    'members': [
        {'key': "Alman_Data",           'stype': '64s'},
        {'key': "Last_Alman",           'stype': 'B'},
        {'key': "IonoUTCV_Flag",        'stype': 'B'},
        {'key': "spare",                'stype': 'H'},
    ]
})

GPS99 = Message({
    'name': "GPSSatellite",
    'fourcc': b'GPS'+chr(99).encode(),
    'size': "Fixed",
    'endianness': '<',
    'members': [
        {'key': "Nav_Mode_2",           'stype': 'B'},
        {'key': "UTC_Time_Diff",        'stype': 'B', 'units': {'mks': "second"}},
        {'key': "GPS_Week",             'stype': 'H'},
        {'key': "GPS_Time_of_Week",     'stype': 'd', 'units': {'mks': "second"}},

        {'key': "Channel_0",            'stype': 'B'},
        {'key': "Tracked_0",            'stype': 'B'},
        {'key': "Status_0",             'stype': 'B'},
        {'key': "Last_Subframe_0",      'stype': 'B'},
        {'key': "Ephm_V_Flag_0",        'stype': 'B'},
        {'key': "Ephm_Health_0",        'stype': 'B'},
        {'key': "Alm_V_Flag_0",         'stype': 'B'},
        {'key': "Alm_Health_0",         'stype': 'B'},
        {'key': "Elev_Angle_0",         'stype': 'b', 'units': {'mks': "degree"}},
        {'key': "Azimuth_Angle_0",      'stype': 'B', 'units': {'mks': "degree", 'scaleby': 2.0}},
        {'key': "URA_0",                'stype': 'B'},
        {'key': "spare_0",              'stype': 'B'},
        {'key': "CLI_for_SNR_0",        'stype': 'H'},
        {'key': "DiffCorr_0",           'stype': 'h'},
        {'key': "Pos_Resid_0",          'stype': 'h'},
        {'key': "Vel_Resid_0",          'stype': 'h'},
        {'key': "Dopplr_0",             'stype': 'h'},
        {'key': "N_Carr_Offset_0",      'stype': 'h'},

        {'key': "Channel_1",            'stype': 'B'},
        {'key': "Tracked_1",            'stype': 'B'},
        {'key': "Status_1",             'stype': 'B'},
        {'key': "Last_Subframe_1",      'stype': 'B'},
        {'key': "Ephm_V_Flag_1",        'stype': 'B'},
        {'key': "Ephm_Health_1",        'stype': 'B'},
        {'key': "Alm_V_Flag_1",         'stype': 'B'},
        {'key': "Alm_Health_1",         'stype': 'B'},
        {'key': "Elev_Angle_1",         'stype': 'b', 'units': {'mks': "degree"}},
        {'key': "Azimuth_Angle_1",      'stype': 'B', 'units': {'mks': "degree", 'scaleby': 2.0}},
        {'key': "URA_1",                'stype': 'B'},
        {'key': "spare_1",              'stype': 'B'},
        {'key': "CLI_for_SNR_1",        'stype': 'H'},
        {'key': "DiffCorr_1",           'stype': 'h'},
        {'key': "Pos_Resid_1",          'stype': 'h'},
        {'key': "Vel_Resid_1",          'stype': 'h'},
        {'key': "Dopplr_1",             'stype': 'h'},
        {'key': "N_Carr_Offset_1",      'stype': 'h'},

        {'key': "Channel_2",            'stype': 'B'},
        {'key': "Tracked_2",            'stype': 'B'},
        {'key': "Status_2",             'stype': 'B'},
        {'key': "Last_Subframe_2",      'stype': 'B'},
        {'key': "Ephm_V_Flag_2",        'stype': 'B'},
        {'key': "Ephm_Health_2",        'stype': 'B'},
        {'key': "Alm_V_Flag_2",         'stype': 'B'},
        {'key': "Alm_Health_2",         'stype': 'B'},
        {'key': "Elev_Angle_2",         'stype': 'b', 'units': {'mks': "degree"}},
        {'key': "Azimuth_Angle_2",      'stype': 'B', 'units': {'mks': "degree", 'scaleby': 2.0}},
        {'key': "URA_2",                'stype': 'B'},
        {'key': "spare_2",              'stype': 'B'},
        {'key': "CLI_for_SNR_2",        'stype': 'H'},
        {'key': "DiffCorr_2",           'stype': 'h'},
        {'key': "Pos_Resid_2",          'stype': 'h'},
        {'key': "Vel_Resid_2",          'stype': 'h'},
        {'key': "Dopplr_2",             'stype': 'h'},
        {'key': "N_Carr_Offset_2",      'stype': 'h'},

        {'key': "Channel_3",            'stype': 'B'},
        {'key': "Tracked_3",            'stype': 'B'},
        {'key': "Status_3",             'stype': 'B'},
        {'key': "Last_Subframe_3",      'stype': 'B'},
        {'key': "Ephm_V_Flag_3",        'stype': 'B'},
        {'key': "Ephm_Health_3",        'stype': 'B'},
        {'key': "Alm_V_Flag_3",         'stype': 'B'},
        {'key': "Alm_Health_3",         'stype': 'B'},
        {'key': "Elev_Angle_3",         'stype': 'b', 'units': {'mks': "degree"}},
        {'key': "Azimuth_Angle_3",      'stype': 'B', 'units': {'mks': "degree", 'scaleby': 2.0}},
        {'key': "URA_3",                'stype': 'B'},
        {'key': "spare_3",              'stype': 'B'},
        {'key': "CLI_for_SNR_3",        'stype': 'H'},
        {'key': "DiffCorr_3",           'stype': 'h'},
        {'key': "Pos_Resid_3",          'stype': 'h'},
        {'key': "Vel_Resid_3",          'stype': 'h'},
        {'key': "Dopplr_3",             'stype': 'h'},
        {'key': "N_Carr_Offset_3",      'stype': 'h'},


        {'key': "Channel_4",            'stype': 'B'},
        {'key': "Tracked_4",            'stype': 'B'},
        {'key': "Status_4",             'stype': 'B'},
        {'key': "Last_Subframe_4",      'stype': 'B'},
        {'key': "Ephm_V_Flag_4",        'stype': 'B'},
        {'key': "Ephm_Health_4",        'stype': 'B'},
        {'key': "Alm_V_Flag_4",         'stype': 'B'},
        {'key': "Alm_Health_4",         'stype': 'B'},
        {'key': "Elev_Angle_4",         'stype': 'b', 'units': {'mks': "degree"}},
        {'key': "Azimuth_Angle_4",      'stype': 'B', 'units': {'mks': "degree", 'scaleby': 2.0}},
        {'key': "URA_4",                'stype': 'B'},
        {'key': "spare_4",              'stype': 'B'},
        {'key': "CLI_for_SNR_4",        'stype': 'H'},
        {'key': "DiffCorr_4",           'stype': 'h'},
        {'key': "Pos_Resid_4",          'stype': 'h'},
        {'key': "Vel_Resid_4",          'stype': 'h'},
        {'key': "Dopplr_4",             'stype': 'h'},
        {'key': "N_Carr_Offset_4",      'stype': 'h'},

        {'key': "Channel_5",            'stype': 'B'},
        {'key': "Tracked_5",            'stype': 'B'},
        {'key': "Status_5",             'stype': 'B'},
        {'key': "Last_Subframe_5",      'stype': 'B'},
        {'key': "Ephm_V_Flag_5",        'stype': 'B'},
        {'key': "Ephm_Health_5",        'stype': 'B'},
        {'key': "Alm_V_Flag_5",         'stype': 'B'},
        {'key': "Alm_Health_5",         'stype': 'B'},
        {'key': "Elev_Angle_5",         'stype': 'b', 'units': {'mks': "degree"}},
        {'key': "Azimuth_Angle_5",      'stype': 'B', 'units': {'mks': "degree", 'scaleby': 2.0}},
        {'key': "URA_5",                'stype': 'B'},
        {'key': "spare_5",              'stype': 'B'},
        {'key': "CLI_for_SNR_5",        'stype': 'H'},
        {'key': "DiffCorr_5",           'stype': 'h'},
        {'key': "Pos_Resid_5",          'stype': 'h'},
        {'key': "Vel_Resid_5",          'stype': 'h'},
        {'key': "Dopplr_5",             'stype': 'h'},
        {'key': "N_Carr_Offset_5",      'stype': 'h'},


        {'key': "Channel_6",            'stype': 'B'},
        {'key': "Tracked_6",            'stype': 'B'},
        {'key': "Status_6",             'stype': 'B'},
        {'key': "Last_Subframe_6",      'stype': 'B'},
        {'key': "Ephm_V_Flag_6",        'stype': 'B'},
        {'key': "Ephm_Health_6",        'stype': 'B'},
        {'key': "Alm_V_Flag_6",         'stype': 'B'},
        {'key': "Alm_Health_6",         'stype': 'B'},
        {'key': "Elev_Angle_6",         'stype': 'b', 'units': {'mks': "degree"}},
        {'key': "Azimuth_Angle_6",      'stype': 'B', 'units': {'mks': "degree", 'scaleby': 2.0}},
        {'key': "URA_6",                'stype': 'B'},
        {'key': "spare_6",              'stype': 'B'},
        {'key': "CLI_for_SNR_6",        'stype': 'H'},
        {'key': "DiffCorr_6",           'stype': 'h'},
        {'key': "Pos_Resid_6",          'stype': 'h'},
        {'key': "Vel_Resid_6",          'stype': 'h'},
        {'key': "Dopplr_6",             'stype': 'h'},
        {'key': "N_Carr_Offset_6",      'stype': 'h'},

        {'key': "Channel_7",            'stype': 'B'},
        {'key': "Tracked_7",            'stype': 'B'},
        {'key': "Status_7",             'stype': 'B'},
        {'key': "Last_Subframe_7",      'stype': 'B'},
        {'key': "Ephm_V_Flag_7",        'stype': 'B'},
        {'key': "Ephm_Health_7",        'stype': 'B'},
        {'key': "Alm_V_Flag_7",         'stype': 'B'},
        {'key': "Alm_Health_7",         'stype': 'B'},
        {'key': "Elev_Angle_7",         'stype': 'b', 'units': {'mks': "degree"}},
        {'key': "Azimuth_Angle_7",      'stype': 'B', 'units': {'mks': "degree", 'scaleby': 2.0}},
        {'key': "URA_7",                'stype': 'B'},
        {'key': "spare_7",              'stype': 'B'},
        {'key': "CLI_for_SNR_7",        'stype': 'H'},
        {'key': "DiffCorr_7",           'stype': 'h'},
        {'key': "Pos_Resid_7",          'stype': 'h'},
        {'key': "Vel_Resid_7",          'stype': 'h'},
        {'key': "Dopplr_7",             'stype': 'h'},
        {'key': "N_Carr_Offset_7",      'stype': 'h'},

        {'key': "Channel_8",            'stype': 'B'},
        {'key': "Tracked_8",            'stype': 'B'},
        {'key': "Status_8",             'stype': 'B'},
        {'key': "Last_Subframe_8",      'stype': 'B'},
        {'key': "Ephm_V_Flag_8",        'stype': 'B'},
        {'key': "Ephm_Health_8",        'stype': 'B'},
        {'key': "Alm_V_Flag_8",         'stype': 'B'},
        {'key': "Alm_Health_8",         'stype': 'B'},
        {'key': "Elev_Angle_8",         'stype': 'b', 'units': {'mks': "degree"}},
        {'key': "Azimuth_Angle_8",      'stype': 'B', 'units': {'mks': "degree", 'scaleby': 2.0}},
        {'key': "URA_8",                'stype': 'B'},
        {'key': "spare_8",              'stype': 'B'},
        {'key': "CLI_for_SNR_8",        'stype': 'H'},
        {'key': "DiffCorr_8",           'stype': 'h'},
        {'key': "Pos_Resid_8",          'stype': 'h'},
        {'key': "Vel_Resid_8",          'stype': 'h'},
        {'key': "Dopplr_8",             'stype': 'h'},
        {'key': "N_Carr_Offset_8",      'stype': 'h'},

        {'key': "Channel_9",            'stype': 'B'},
        {'key': "Tracked_9",            'stype': 'B'},
        {'key': "Status_9",             'stype': 'B'},
        {'key': "Last_Subframe_9",      'stype': 'B'},
        {'key': "Ephm_V_Flag_9",        'stype': 'B'},
        {'key': "Ephm_Health_9",        'stype': 'B'},
        {'key': "Alm_V_Flag_9",         'stype': 'B'},
        {'key': "Alm_Health_9",         'stype': 'B'},
        {'key': "Elev_Angle_9",         'stype': 'b', 'units': {'mks': "degree"}},
        {'key': "Azimuth_Angle_9",      'stype': 'B', 'units': {'mks': "degree", 'scaleby': 2.0}},
        {'key': "URA_9",                'stype': 'B'},
        {'key': "spare_9",              'stype': 'B'},
        {'key': "CLI_for_SNR_9",        'stype': 'H'},
        {'key': "DiffCorr_9",           'stype': 'h'},
        {'key': "Pos_Resid_9",          'stype': 'h'},
        {'key': "Vel_Resid_9",          'stype': 'h'},
        {'key': "Dopplr_9",             'stype': 'h'},
        {'key': "N_Carr_Offset_9",      'stype': 'h'},

        {'key': "Channel_10",           'stype': 'B'},
        {'key': "Tracked_10",           'stype': 'B'},
        {'key': "Status_10",            'stype': 'B'},
        {'key': "Last_Subframe_10",     'stype': 'B'},
        {'key': "Ephm_V_Flag_10",       'stype': 'B'},
        {'key': "Ephm_Health_10",       'stype': 'B'},
        {'key': "Alm_V_Flag_10",        'stype': 'B'},
        {'key': "Alm_Health_10",        'stype': 'B'},
        {'key': "Elev_Angle_10",        'stype': 'b', 'units': {'mks': "degree"}},
        {'key': "Azimuth_Angle_10",     'stype': 'B', 'units': {'mks': "degree", 'scaleby': 2.0}},
        {'key': "URA_10",               'stype': 'B'},
        {'key': "spare_10",             'stype': 'B'},
        {'key': "CLI_for_SNR_10",       'stype': 'H'},
        {'key': "DiffCorr_10",          'stype': 'h'},
        {'key': "Pos_Resid_10",         'stype': 'h'},
        {'key': "Vel_Resid_10",         'stype': 'h'},
        {'key': "Dopplr_10",            'stype': 'h'},
        {'key': "N_Carr_Offset_10",     'stype': 'h'},

        {'key': "Channel_11",           'stype': 'B'},
        {'key': "Tracked_11",           'stype': 'B'},
        {'key': "Status_11",            'stype': 'B'},
        {'key': "Last_Subframe_11",     'stype': 'B'},
        {'key': "Ephm_V_Flag_11",       'stype': 'B'},
        {'key': "Ephm_Health_11",       'stype': 'B'},
        {'key': "Alm_V_Flag_11",        'stype': 'B'},
        {'key': "Alm_Health_11",        'stype': 'B'},
        {'key': "Elev_Angle_11",        'stype': 'b', 'units': {'mks': "degree"}},
        {'key': "Azimuth_Angle_11",     'stype': 'B', 'units': {'mks': "degree", 'scaleby': 2.0}},
        {'key': "URA_11",               'stype': 'B'},
        {'key': "spare_11",             'stype': 'B'},
        {'key': "CLI_for_SNR_11",       'stype': 'H'},
        {'key': "DiffCorr_11",          'stype': 'h'},
        {'key': "Pos_Resid_11",         'stype': 'h'},
        {'key': "Vel_Resid_11",         'stype': 'h'},
        {'key': "Dopplr_11",            'stype': 'h'},
        {'key': "N_Carr_Offset_11",     'stype': 'h'},

        {'key': "Clock_Err_L1",         'stype': 'h'},
        {'key': "spare",                'stype': 'H'},
    ]
})


# A list of all message types we know about
PSAS_MESSAGES = [
    SEQN,
    ADIS,
    ROLL,
    RNHH,
    RNHP,
    LTC,
    GPS1,
    GPS2,
    GPS80,
    GPS93,
    GPS95,
    GPS96,
    GPS98,
    GPS99,
]
