#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import logging

PROVIDERS = ['Blocktrail.com', 'Blockchain.info', 'Blockexplorer.com']
from wrappers import SpellbookWrapper


logging.basicConfig(filename='unittests.log', level=logging.DEBUG)


class BlockDataTests(unittest.TestCase):

    def test_blockdata_genesisblock(self):
        api = SpellbookWrapper.SpellbookWrapper().blockdata()
        for provider in PROVIDERS:
            data = api.block(0, provider)

            self.assertIn('success', data, provider)
            if 'success' in data and data['success'] == 1:
                genesis_block = data['block']
                self.assertEqual(genesis_block['hash'],
                                 "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f")
                self.assertEqual(genesis_block['merkleroot'],
                                 "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b")
                self.assertEqual(genesis_block['size'], 285)
                self.assertEqual(genesis_block['height'], 0)
                self.assertEqual(genesis_block['time'], 1231006505)

            else:
                logging.error(data['error'])
                self.fail('Unable to retrieve genesisBlock from ' + provider)