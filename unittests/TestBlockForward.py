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


blockforward = SpellbookWrapper.SpellbookWrapper(url).blockforward()

pprint(blockforward.get_forwarders())

pprint(blockforward.delete_forwarder('testForwarder1', key, secret))

settings = {'xpub': xpub,
            'description': 'this is a test',
            'creator': 'Wouter Glorieux',
            'creator_email': 'info@valyrian.tech',
            'minimum_amount': 500000,
            'youtube': 'C0DPdy98e4c',
            'visibility': 'Public',
            'status': 'Active',
            'fee_percentage': 1.0,
            'fee_address': '1Woutere8RCF82AgbPCc5F4KuYVvS4meW',
            'confirm_amount': 10000,
            'address_type': 'BIP44'}

pprint(blockforward.save_forwarder('testForwarder1', settings, key, secret))

pprint(blockforward.save_forwarder('', settings, key, secret))

pprint(blockforward.save_forwarder('1', settings, key, secret))

pprint(blockforward.check_address('testForwarder1', '1Woutere8RCF82AgbPCc5F4KuYVvS4meW'))

#pprint(blockforward.do_forwarding('testForwarder1'))