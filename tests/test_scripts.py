#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_scripts
----------------------------------

Smoke tests for the scripts that come with this package
"""

import unittest
import subprocess

class TestExamples(unittest.TestCase):

    def test_gen_types(self):
        try:
            output = subprocess.check_output(["gen-psas-types"])
            self.assertGreater(len(output), 1)
        except:
            self.fail("gen-psas-types blew up!")

    def test_slice_log(self):
        try:
            output = subprocess.check_output(["slicelog", "./tests/data/simple_logfile", ":"])
            self.assertGreater(len(output), 1)
        except:
            self.fail("slicelog blew up!")

if __name__ == '__main__':
    unittest.main()
