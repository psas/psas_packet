#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_examples
----------------------------------

Test some of the code snipits in the examples directory
"""

import unittest


class TestExamples(unittest.TestCase):

    def test_send_packets(self):
        try:
            with open('./examples/send_packets.py', 'r') as ex:
                exec(ex.read())
        except ExceptionType:
            self.fail("examples/send_packets.py raised ExceptionType unexpectedly!")


if __name__ == '__main__':
    unittest.main()
