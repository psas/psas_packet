"""
Send A Telemetry Packet
-----------------------

Open a UDP socket, and send a message of type "ADIS" to port 25000 on localhost
"""

from psas_packet import network, messages

# set up a UDP packet sender
with network.SendUDP('127.0.0.1', 25000) as udp:

    # data that will go in our message
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
    })

    # send a whole message (with header)
    udp.send_message(messages.ADIS, data)

    # send just data (no header)
    udp.send_data(messages.ADIS, data)
