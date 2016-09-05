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

blockvoter = SpellbookWrapper.SpellbookWrapper(url).blockvoter()

address = '1G9JikTQ2TWUuNMP8bPPBYs7VtchzxLF2v'
proposal = "What should we invest our money in?"
options = ['No opinion', 'Buy Machine A', 'Buy Machine B', 'SatoshiDice']
vote_cost = 40000

block_height = 400000

weights = 'LRL'
registration_address = '1NC8LqAB99bYM9wVoD2grdYMMZAhjwy57A'
registration_block_height = 376000
registration_xpub = 'xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD'

pprint(blockvoter.proposal(address=address,
                           proposal=proposal,
                           options=options,
                           vote_cost=vote_cost,
                           weights=weights,
                           registration_address=registration_address,
                           registration_block_height=registration_block_height,
                           registration_xpub=registration_xpub))

pprint(blockvoter.results(address=address,
                          proposal=proposal,
                          options=options,
                          vote_cost=vote_cost,
                          block_height=block_height,
                          weights=weights,
                          registration_address=registration_address,
                          registration_block_height=registration_block_height,
                          registration_xpub=registration_xpub))