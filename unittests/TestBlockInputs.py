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
block_height = 425026

blockdata = SpellbookWrapper.SpellbookWrapper(url).blockdata()
pprint(blockdata.transactions(address))

blockinputs = SpellbookWrapper.SpellbookWrapper(url).blockinputs()

#Test most recent SIL
pprint(blockinputs.get_sil(address))

#Test SIL at specified block_height
pprint(blockinputs.get_sil(address, block_height))


#Test most recent profile
pprint(blockinputs.get_profile(address))

#Test profile at specified block_height
pprint(blockinputs.get_profile(address, block_height))