#!/usr/bin/env python
# -*- coding: utf-8 -*-


import urllib2
import json
import urllib


class BlockRandomWrapper():
    def __init__(self, url):
        self.url = url

    def fromBlock(self, rng_block_height=0):
        response = {'success': 0}
        parameters = {'rng_block_height': str(rng_block_height)}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/random/block?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve random number from block'

        return response

    def fromSIL(self, address, block_height=0, rng_block_height=0):
        response = {'success': 0}
        parameters = {'source': 'sil',
                      'address': address,
                      'block_height': str(block_height),
                      'rng_block_height': str(rng_block_height)}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/random/proportional?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve random address from sil'

        return response

    def fromLBL(self, address, xpub, block_height=0, rng_block_height=0):
        response = {'success': 0}
        parameters = {'source': 'LBL',
                      'address': address,
                      'xpub': xpub,
                      'block_height': str(block_height),
                      'rng_block_height': str(rng_block_height)}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/random/proportional?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve random address from LBL'

        return response

    def fromLRL(self, address, xpub, block_height=0, rng_block_height=0):
        response = {'success': 0}
        parameters = {'source': 'LRL',
                      'address': address,
                      'xpub': xpub,
                      'block_height': str(block_height),
                      'rng_block_height': str(rng_block_height)}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/random/proportional?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve random address from LRL'

        return response

    def fromLSL(self, address, xpub, block_height=0, rng_block_height=0):
        response = {'success': 0}
        parameters = {'source': 'LRL',
                      'address': address,
                      'xpub': xpub,
                      'block_height': str(block_height),
                      'rng_block_height': str(rng_block_height)}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/random/proportional?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve random address from LSL'

        return response