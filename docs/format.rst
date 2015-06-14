===================
Message Definitions
===================

These are all the message types pre-defined in :code:`psas_packet.messages.MESSAGES`

ADIS
====

Raw data from the `Analog Devices ADIS16405 9DOF IMU <http://www.analog.com/en/products/sensors/isensor-mems-inertial-measurement-units/adis16405.html>`_. Includes acceleration, gyroscope, magnetometer, and temperature data.

**Format Description:**

+---------+--------------------------------------+------------------+--------------+
|   Field |                          Description |             Type | Size [Bytes] |
+=========+======================================+==================+==============+
|     VCC |                          Bus voltage | :code:`uint16_t` |            2 |
+---------+--------------------------------------+------------------+--------------+
|  Gyro_X | **X axis** value from rate-gyroscope | :code:`uint16_t` |            2 |
+---------+--------------------------------------+------------------+--------------+
|  Gyro_Y | **Y axis** value from rate-gyroscope | :code:`uint16_t` |            2 |
+---------+--------------------------------------+------------------+--------------+
|  Gyro_Z | **Z axis** value from rate-gyroscope | :code:`uint16_t` |            2 |
+---------+--------------------------------------+------------------+--------------+
|   Acc_X |  **X axis** value from accelerometer | :code:`uint16_t` |            2 |
+---------+--------------------------------------+------------------+--------------+
|   Acc_Y |  **Y axis** value from accelerometer | :code:`uint16_t` |            2 |
+---------+--------------------------------------+------------------+--------------+
|   Acc_Z |  **Z axis** value from accelerometer | :code:`uint16_t` |            2 |
+---------+--------------------------------------+------------------+--------------+
|  Magn_X |   **X axis** value from magnetometer | :code:`uint16_t` |            2 |
+---------+--------------------------------------+------------------+--------------+
|  Magn_Y |   **Y axis** value from magnetometer | :code:`uint16_t` |            2 |
+---------+--------------------------------------+------------------+--------------+
|  Magn_Z |   **Z axis** value from magnetometer | :code:`uint16_t` |            2 |
+---------+--------------------------------------+------------------+--------------+
|    Temp |                     Unit temperature | :code:`uint16_t` |            2 |
+---------+--------------------------------------+------------------+--------------+
| Aux_ADC |                        Auxiliary ADC | :code:`uint16_t` |            2 |
+---------+--------------------------------------+------------------+--------------+


--------------------------------------------------------------------------------


ROLL
====

Roll servo positon

**Format Description:**

+---------+---------------------+-----------------+--------------+
|   Field |         Description |            Type | Size [Bytes] |
+=========+=====================+=================+==============+
|   Angle |           Fin angle |  :code:`double` |            8 |
+---------+---------------------+-----------------+--------------+
| Disable | Enable/disable flag | :code:`uint8_t` |            1 |
+---------+---------------------+-----------------+--------------+


--------------------------------------------------------------------------------


SEQN
====

Sequence Number

**Format Description:**

+----------+-------------+------------------+--------------+
|    Field | Description |             Type | Size [Bytes] |
+==========+=============+==================+==============+
| Sequence |    Sequence | :code:`uint32_t` |            8 |
+----------+-------------+------------------+--------------+


--------------------------------------------------------------------------------


