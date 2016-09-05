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

blocklinker = SpellbookWrapper.SpellbookWrapper(url).blocklinker()

#Test LAL
pprint(blocklinker.get_lal(address, xpub, block_height))

#Test LBL
pprint(blocklinker.get_lbl(address, xpub, block_height))

#Test LRL
pprint(blocklinker.get_lrl(address, xpub, block_height))

#Test LSL
pprint(blocklinker.get_lsl(address, xpub, block_height))