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


blocktrigger = SpellbookWrapper.SpellbookWrapper(url).blocktrigger()

pprint(blocktrigger.get_triggers())

pprint(blocktrigger.delete_trigger('testTrigger1', key, secret))

settings = {'trigger_type': 'block_height',
            'block_height': block_height,
            'address': '1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8',
            'amount': 200000,
            'confirmations': 3,
            'triggered': False,
            'status': 'Active',
            'visibility': 'Public',
            'description': 'this is a test',
            'creator': 'Wouter Glorieux',
            'creator_email': 'info@valyrian.tech',
            'youtube': 'C0DPdy98e4c'}

pprint(blocktrigger.save_trigger('testTrigger1', settings, key, secret))

settings = {'action_type': 'webhook',
            'description': 'test action description',
            'reveal_text': 'secret text',
            'reveal_link_text': 'secret link text',
            'reveal_link_url': 'http://www.valyrian.tech',
            'mail_to': 'skidzobolder@gmail.com',
            'mail_subject': 'test subject',
            'mail_body': 'this is a test',
            'webhook': 'http://localhost:34080/data/latest_block',
            'mail_sent': False,
            'webhook_activated': False}

pprint(blocktrigger.save_action('testTrigger1', 'testAction1', settings, key, secret))

pprint(blocktrigger.delete_action('testTrigger1', 'testAction1', key, secret))

pprint(blocktrigger.save_action('testTrigger1', 'testAction1', settings, key, secret))

