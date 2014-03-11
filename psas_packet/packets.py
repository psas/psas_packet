""" Packet definitions
"""
import struct


class Packable(float):

    def __index__(self):
        return int(self)


class Packet(object):
    """Instantiates a packet definition

    :param dict definition: Dictionary defining data in a packet
    :returns: Packet instance

    Suitable metadata can be passed in and this class will perform
    necessary pre-compute steps and create a usable packet instance for
    a specific data source.
    """

    def __init__(self, definition):
        self.name = definition['name']
        self.fourcc = definition['fourcc']

        # pre compute struct for fixed size packets
        self.members = {}
        if definition['size'] == "Fixed":
            struct_string = definition['endianness']
            for i, member in enumerate(definition['members']):
                self.members[member['key']] = {'loc': i, 'units': member['units']}
                struct_string += member['type']
            self.struct = struct.Struct(struct_string)

    def __repr__(self):
        return "{0} packet [{1}]".format(self.name, self.fourcc)

    def encode(self, data):
        """Encode a set of data into binary

        :param dict data: A dictionary of values to encode
        :returns: binary ecoded data

        Uses the struct package to encode data. Objects should match keys in
        the members list.
        """

        # Initilize as zeros
        values = [0]*len(self.members)

        # lookup corisponding metadata
        for key, value in data.items():
            m = self.members[key]
            units = m['units']
            v = (value - units.get('bias', 0)) / units.get('scaleby', 1)
            values[m['loc']] = Packable(v)

        return self.struct.pack(*values)


ADIS = Packet({
    'name': "ADIS",
    'fourcc': "ADIS",
    'size': "Fixed",
    'endianness': '!',
    'members': [
        {'key': "VCC",     'type': "h", 'units': {'mks': "volt",      'scaleby': 0.002418}},
        {'key': "Gyro_X",  'type': "h", 'units': {'mks': "hertz",     'scaleby': 0.05}},
        {'key': "Gyro_Y",  'type': "h", 'units': {'mks': "hertz",     'scaleby': 0.05}},
        {'key': "Gyro_Z",  'type': "h", 'units': {'mks': "hertz",     'scaleby': 0.05}},
        {'key': "Acc_X",   'type': "h", 'units': {'mks': "meter/s/s", 'scaleby': 0.0333}},
        {'key': "Acc_Y",   'type': "h", 'units': {'mks': "meter/s/s", 'scaleby': 0.0333}},
        {'key': "Acc_Z",   'type': "h", 'units': {'mks': "meter/s/s", 'scaleby': 0.0333}},
        {'key': "Magn_X",  'type': "h", 'units': {'mks': "tesla",     'scaleby': 0.05}},
        {'key': "Magn_Y",  'type': "h", 'units': {'mks': "tesla",     'scaleby': 0.05}},
        {'key': "Magn_Z",  'type': "h", 'units': {'mks': "tesla",     'scaleby': 0.05}},
        {'key': "Temp",    'type': "h", 'units': {'mks': "degree c",  'scaleby': 0.14, 'bias': 25}},
        {'key': "Aux_ADC", 'type': "h", 'units': {'mks': "volt",      'scaleby': 806}},
    ]
})
