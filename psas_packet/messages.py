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
            units = m['units']
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
        {'key': "PWM",                  'stype': "H", 'units': {'mks': "second", 'scale': 1e-6, 'shift': -1.5e-3}},
        {'key': "Disable",              'stype': "B"},
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


# A list of all message types we know about
PSAS_MESSAGES = [
    ADIS,
    ROLL,
    GPS1,
    GPS2,
    GPS80,
    GPS93,
]
