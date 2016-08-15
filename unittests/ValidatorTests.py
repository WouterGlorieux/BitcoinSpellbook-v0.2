#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import logging
import TestVectors
import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from validators import validators

logging.basicConfig(filename='validatortests.log',level=logging.DEBUG)

class ValidatorTests(unittest.TestCase):
    def test_unittest(self):
        print 'testing unittest...',
        self.assertEqual(1, 1)
        print 'OK'

    def test_ValidAddress(self):
        print 'testing ValidAddress...',
        for vector in TestVectors.address_test_vectors:
            self.assertEqual(validators.validAddress(vector[0]), vector[1], "%s should return %s: %s" % (vector[0], vector[1], vector[2]))
        print 'OK'

    def test_ValidAddresses(self):
        print 'testing ValidAddresses...',
        for vector in TestVectors.addresses_test_vectors:
            self.assertEqual(validators.validAddresses(vector[0]), vector[1], "%s should return %s: %s" % (vector[0], vector[1], vector[2]))
        print 'OK'

    def test_ValidBlockProfileMessage(self):
        print 'testing ValidBlockProfileMessage...',
        for vector in TestVectors.profile_message_test_vectors:
            self.assertEqual(validators.validBlockProfileMessage(vector[0]), vector[1], "%s should return %s: %s" % (vector[0], vector[1], vector[2]))
        print 'OK'