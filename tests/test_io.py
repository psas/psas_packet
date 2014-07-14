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

    def test_log2csv(self):
        # smoke test
        try:
            io.log2csv("tests/data/simple_log.json")
        except:
            self.fail("log2csv exception")

    def test_read_logfile(self):
        with io.BinFile("tests/data/simple_logfile") as log:
            """Uncomment to generate test data from new logfile:
            with open("tests/data/simple_log.json", 'w') as j:
                data = []
                for fourcc, d in log.read():
                    data.append({fourcc: d})
                j.write(json.dumps(data))
            """

            for i, d in enumerate(log.read()):
                fourcc, data = d
                self.assertEqual(self.simple_log_data[i], {fourcc.decode('utf-8'): data})


if __name__ == '__main__':
    unittest.main()
