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
xpub = 'xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD'
block_height = 400000
rng_block_height = 420000

blockrandom = SpellbookWrapper.SpellbookWrapper(url).blockrandom()

#Test from_block most recent
pprint(blockrandom.from_block())

#Test from_block at rng_block_height
pprint(blockrandom.from_block(rng_block_height))

#Test from_sil
pprint(blockrandom.from_sil(address, block_height, rng_block_height))

#Test from_lbl
pprint(blockrandom.from_lbl(address, xpub, block_height, rng_block_height))

#Test from_lrl
pprint(blockrandom.from_lrl(address, xpub, block_height, rng_block_height))

#Test from_lsl
pprint(blockrandom.from_lsl(address, xpub, block_height, rng_block_height))