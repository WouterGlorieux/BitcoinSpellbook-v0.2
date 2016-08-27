#!/usr/bin/env python
# -*- coding: utf-8 -*-


import urllib2
import json
import urllib



class BlockInputsWrapper():
    def __init__(self, url):
        self.url = url


    def SIL(self, address, blockHeight=0):
        response = {'success': 0}
        parameters = {}
        parameters['address'] = address
        parameters['block_height'] = str(blockHeight)

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/SIL/SIL?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve SIL'

        return response