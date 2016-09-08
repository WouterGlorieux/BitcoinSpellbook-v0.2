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
xpub = 'xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD'

blockwriter = SpellbookWrapper.SpellbookWrapper(url).blockwriter()

pprint(blockwriter.get_writers())

pprint(blockwriter.delete_writer('testWriter1', key, secret))

settings = {'outputs': [('1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y', 50000), ('1SansacmMr38bdzGkzruDVajEsZuiZHx9', 50000)],
            'message': '0@1:ACK=1|1@0:ACK=1',
            'status': 'Active',
            'visibility': 'Public',
            'description': 'this is a test',
            'creator': 'Wouter Glorieux',
            'creator_email': 'info@valyrian.tech',
            'youtube': 'C0DPdy98e4c',
            'fee_address': '1Woutere8RCF82AgbPCc5F4KuYVvS4meW',
            'fee_percentage': 1.0,
            'maximum_transaction_fee': 15000,
            'address_type': 'BIP44'}


#pprint(blockwriter.save_writer('testWriter1', settings, key, secret))

pprint(blockwriter.save_writer(blockwriter.get_writer()['writer']['name'], settings, key, secret))