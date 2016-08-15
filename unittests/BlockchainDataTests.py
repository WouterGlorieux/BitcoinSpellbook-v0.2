import unittest
import logging

PROVIDERS = ['Blocktrail.com', 'Blockchain.info', 'Blockexplorer.com']
from wrappers import SpellbookWrapper


logging.basicConfig(filename='unittests.log',level=logging.DEBUG)

class BlockchainDataTests(unittest.TestCase):

    def test_BlockchainData_GenesisBlock(self):
        api = SpellbookWrapper.SpellbookWrapper().BlockchainData()
        for provider in PROVIDERS:
            data = api.block(0, provider)

            self.assertIn('success', data, provider)
            if 'success' in data and data['success'] == 1:
                genesisBlock = data['block']
                self.assertEqual(genesisBlock['hash'], "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f")
                self.assertEqual(genesisBlock['merkleroot'], "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b")
                self.assertEqual(genesisBlock['size'], 285)
                self.assertEqual(genesisBlock['height'], 0)
                self.assertEqual(genesisBlock['time'], 1231006505)

            else:
                logging.error(data['error'])
                self.fail('Unable to retrieve genesisBlock from ' + provider)







