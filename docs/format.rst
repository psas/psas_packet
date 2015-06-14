===================
Message Definitions
===================

These are all the message types pre-defined in :code:`psas_packet.messages.MESSAGES`

ADIS
====

Raw data from the `Analog Devices ADIS16405 9DOF IMU <http://www.analog.com/en/products/sensors/isensor-mems-inertial-measurement-units/adis16405.html>`_. Includes acceleration, gyroscope, magnetometer, and temperature data.

**Format Description:**

+--------+--------------------------------------+------------------+--------------+
|  Field |                          Description |             Type | Size [Bytes] |
+========+======================================+==================+==============+
|    VCC |                          Bus voltage | :code:`uint16_t` |            2 |
+--------+--------------------------------------+------------------+--------------+
| Gyro_X | **X axis** value from rate-gyroscope | :code:`uint16_t` |            2 |
+--------+--------------------------------------+------------------+--------------+
| Gyro_Y | **Y axis** value from rate-gyroscope | :code:`uint16_t` |            2 |
+--------+--------------------------------------+------------------+--------------+


--------------------------------------------------------------------------------


