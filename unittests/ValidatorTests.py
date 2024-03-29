#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import TestVectors
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from validators import validators


class ValidatorTests(unittest.TestCase):
    def test_unittest(self):
        print 'testing unittest...',
        self.assertEqual(1, 1)
        print 'OK'

    def test_valid_address(self):
        print 'testing valid_address...',
        for vector in TestVectors.address_test_vectors:
            self.assertEqual(validators.valid_address(vector[0]), vector[1],
                             "%s should return %s: %s" % (vector[0], vector[1], vector[2]))
        print 'OK'

    def test_valid_addresses(self):
        print 'testing valid_addresses...',
        for vector in TestVectors.addresses_test_vectors:
            self.assertEqual(validators.valid_addresses(vector[0]), vector[1],
                             "%s should return %s: %s" % (vector[0], vector[1], vector[2]))
        print 'OK'

    def test_valid_txid(self):
        print 'testing valid_txid...',
        for vector in TestVectors.txid_test_vectors:
            self.assertEqual(validators.valid_txid(vector[0]), vector[1],
                             "%s should return %s: %s" % (vector[0], vector[1], vector[2]))
        print 'OK'

    def test_valid_xpub(self):
        print 'testing valid_xpub...',
        for vector in TestVectors.xpub_test_vectors:
            self.assertEqual(validators.valid_xpub(vector[0]), vector[1],
                             "%s should return %s: %s" % (vector[0], vector[1], vector[2]))
        print 'OK'

    def test_valid_description(self):
        print 'testing valid_description...',
        for vector in TestVectors.description_test_vectors:
            self.assertEqual(validators.valid_description(vector[0]), vector[1],
                             "%s should return %s: %s" % (vector[0], vector[1], vector[2]))
        print 'OK'

    def test_valid_op_return(self):
        print 'testing valid_op_return...',
        for vector in TestVectors.op_return_test_vectors:
            self.assertEqual(validators.valid_op_return(vector[0]), vector[1],
                             "%s should return %s: %s" % (vector[0], vector[1], vector[2]))
        print 'OK'

    def test_valid_blockprofile_message(self):
        print 'testing valid_blockprofile_message...',
        for vector in TestVectors.profile_message_test_vectors:
            self.assertEqual(validators.valid_blockprofile_message(vector[0]), vector[1],
                             "%s should return %s: %s" % (vector[0], vector[1], vector[2]))
        print 'OK'

    def test_valid_text(self):
        print 'testing valid_text...',
        for vector in TestVectors.text_test_vectors:
            self.assertEqual(validators.valid_text(vector[0]), vector[1],
                             "%s should return %s: %s" % (vector[0], vector[1], vector[2]))
        print 'OK'

    def test_valid_url(self):
        print 'testing valid_url...',
        for vector in TestVectors.url_test_vectors:
            self.assertEqual(validators.valid_url(vector[0]), vector[1],
                             "%s should return %s: %s" % (vector[0], vector[1], vector[2]))
        print 'OK'

    def test_valid_creator(self):
        print 'testing valid_creator...',
        for vector in TestVectors.creator_test_vectors:
            self.assertEqual(validators.valid_creator(vector[0]), vector[1],
                             "%s should return %s: %s" % (vector[0], vector[1], vector[2]))
        print 'OK'

    def test_valid_email(self):
        print 'testing valid_email...',
        for vector in TestVectors.email_test_vectors:
            self.assertEqual(validators.valid_email(vector[0]), vector[1],
                             "%s should return %s: %s" % (vector[0], vector[1], vector[2]))
        print 'OK'

    def test_valid_amount(self):
        print 'testing valid_amount...',
        for vector in TestVectors.amount_test_vectors:
            self.assertEqual(validators.valid_amount(vector[0]), vector[1],
                             "%s should return %s: %s" % (vector[0], vector[1], vector[2]))
        print 'OK'

    def test_valid_block_height(self):
        print 'testing valid_block_height...',
        for vector in TestVectors.block_height_test_vectors:
            self.assertEqual(validators.valid_block_height(vector[0]), vector[1],
                             "%s should return %s: %s" % (vector[0], vector[1], vector[2]))
        print 'OK'

    def test_valid_percentage(self):
        print 'testing valid_percentage...',
        for vector in TestVectors.percentage_test_vectors:
            self.assertEqual(validators.valid_percentage(vector[0]), vector[1],
                             "%s should return %s: %s" % (vector[0], vector[1], vector[2]))
        print 'OK'

    def test_valid_youtube(self):
        print 'testing valid_youtube...',
        for vector in TestVectors.youtube_test_vectors:
            self.assertEqual(validators.valid_youtube(vector[0]), vector[1],
                             "%s should return %s: %s" % (vector[0], vector[1], vector[2]))
        print 'OK'

    def test_valid_youtube_id(self):
        print 'testing valid_youtube_id...',
        for vector in TestVectors.youtube_id_test_vectors:
            self.assertEqual(validators.valid_youtube_id(vector[0]), vector[1],
                             "%s should return %s: %s" % (vector[0], vector[1], vector[2]))
        print 'OK'

    def test_valid_private_key(self):
        print 'testing valid_private_key...',
        for vector in TestVectors.private_key_test_vectors:
            self.assertEqual(validators.valid_private_key(vector[0]), vector[1],
                             "%s should return %s: %s" % (vector[0], vector[1], vector[2]))
        print 'OK'

    def test_valid_distribution(self):
        print 'testing valid_distribution...',
        for vector in TestVectors.distribution_test_vectors:
            self.assertEqual(validators.valid_distribution(vector[0]), vector[1],
                             "%s should return %s: %s" % (vector[0], vector[1], vector[2]))
        print 'OK'

    def test_valid_outputs(self):
        print 'testing valid_outputs...',
        for vector in TestVectors.outputs_test_vectors:
            self.assertEqual(validators.valid_outputs(vector[0]), vector[1],
                             "%s should return %s: %s" % (vector[0], vector[1], vector[2]))
        print 'OK'
