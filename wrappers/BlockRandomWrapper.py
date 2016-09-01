#!/usr/bin/env python
# -*- coding: utf-8 -*-


import urllib2
import json
import urllib
import logging


class BlockRandomWrapper():
    def __init__(self, url):
        self.url = url

    def from_block(self, rng_block_height=0):
        response = {'success': 0}
        parameters = {'rng_block_height': str(rng_block_height)}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/random/block?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except Exception as ex:
            logging.warning(str(ex))
            response['error'] = 'Unable to retrieve random number from block'

        return response

    def from_sil(self, address, block_height=0, rng_block_height=0):
        response = {'success': 0}
        parameters = {'source': 'SIL',
                      'address': address,
                      'block_height': str(block_height),
                      'rng_block_height': str(rng_block_height)}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/random/proportional?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except Exception as ex:
            logging.warning(str(ex))
            response['error'] = 'Unable to retrieve random address from sil'

        return response

    def from_lbl(self, address, xpub, block_height=0, rng_block_height=0):
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
        except Exception as ex:
            logging.warning(str(ex))
            response['error'] = 'Unable to retrieve random address from LBL'

        return response

    def from_lrl(self, address, xpub, block_height=0, rng_block_height=0):
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
        except Exception as ex:
            logging.warning(str(ex))
            response['error'] = 'Unable to retrieve random address from LRL'

        return response

    def from_lsl(self, address, xpub, block_height=0, rng_block_height=0):
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
        except Exception as ex:
            logging.warning(str(ex))
            response['error'] = 'Unable to retrieve random address from LSL'

        return response