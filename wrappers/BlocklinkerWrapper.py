#!/usr/bin/env python
# -*- coding: utf-8 -*-


import urllib2
import json
import urllib


class BlockLinkerWrapper():
    def __init__(self, url):
        self.url = url

    def LBL(self, address, xpub, block_height=0):
        response = {'success': 0}
        parameters = {'address': address,
                      'xpub': xpub,
                      'block_height': str(block_height)}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/linker/LBL?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve LBL'

        return response

    def LRL(self, address, xpub, block_height=0):
        response = {'success': 0}
        parameters = {'address': address,
                      'xpub': xpub,
                      'block_height': str(block_height)}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/linker/LRL?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve LRL'

        return response

    def LSL(self, address, xpub, block_height=0):
        response = {'success': 0}
        parameters = {'address': address,
                      'xpub': xpub,
                      'block_height': str(block_height)}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/linker/LSL?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve LSL'

        return response

    def LAL(self, address, xpub, block_height=0):
        response = {'success': 0}
        parameters = {'address': address,
                      'xpub': xpub,
                      'block_height': str(block_height)}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/linker/LAL?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve LAL'

        return response