#!/usr/bin/env python
# -*- coding: utf-8 -*-


import urllib2
import json
import urllib


class BlockProfileWrapper():
    def __init__(self, url):
        self.url = url

    def get_profile(self, address, block_height=0):
        response = {'success': 0}
        parameters = {'address': address,
                      'block_height': str(block_height)}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/profile/profile?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve profile'

        return response