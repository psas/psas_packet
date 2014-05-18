#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_io
----------------------------------

Tests for `io` module.
"""

from __future__ import print_function

import unittest
import json
from psas_packet import io


class TestIO(unittest.TestCase):

    def setUp(self):
        with open("tests/data/simple_log.json") as j:
            self.simple_log_data = json.loads(j.read())

    def test_read_logfile(self):
        with io.BinFile("tests/data/simple_logfile") as log:
            for i, d in enumerate(log.read()):
                for key in d:
                    self.assertEqual(self.simple_log_data[i][key.decode('utf-8')], d[key])

