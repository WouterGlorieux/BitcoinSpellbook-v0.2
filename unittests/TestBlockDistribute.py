#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from pprint import pprint
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from wrappers import SpellbookWrapper as SpellbookWrapper
import testconfig


url = testconfig.url
key = testconfig.key
secret = testconfig.secret

#test parameters
address = '1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y'
block_height = 400000


registration_address = '1NC8LqAB99bYM9wVoD2grdYMMZAhjwy57A'
registration_block_height = 376000
registration_xpub = 'xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD'

distribution = [[u'1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y', 100000, 0.1, 375786],
                [u'1SansacmMr38bdzGkzruDVajEsZuiZHx9', 400000, 0.4, 375790],
                [u'1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y', 500000, 0.5, 375786]]


blockdistribute = SpellbookWrapper.SpellbookWrapper(url).blockdistribute()

pprint(blockdistribute.get_distributers())

pprint(blockdistribute.delete_distributer('testDistributer1', key, secret))

settings = {'distribution_source': 'LBL',
            'registration_address': registration_address,
            'registration_block_height': registration_block_height,
            'registration_xpub': registration_xpub,
            'distribution': distribution,
            'minimum_amount': 12300,
            'threshold': 150000,
            'status': 'Active',
            'visibility': 'Public',
            'description': 'this is a test',
            'creator': 'Wouter Glorieux',
            'creator_email': 'info@valyrian.tech',
            'youtube': 'C0DPdy98e4c',
            'fee_address': '1Woutere8RCF82AgbPCc5F4KuYVvS4meW',
            'fee_percentage': 1.0,
            'maximum_transaction_fee': 7500,
            'address_type': 'BIP44'}


pprint(blockdistribute.save_distributer('testDistributer1', settings, key, secret))

pprint(blockdistribute.save_distributer('', settings, key, secret))

pprint(blockdistribute.save_distributer('1', settings, key, secret))

pprint(blockdistribute.update_distribution('testDistributer1', key, secret))

pprint(blockdistribute.get_distributer('testDistributer1'))

pprint(blockdistribute.check_address('testDistributer1', '1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y'))

#pprint(blockdistribute.do_distributing('testDistributer1'))