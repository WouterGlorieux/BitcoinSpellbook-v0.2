#!/usr/bin/env python
# -*- coding: utf-8 -*-


import urllib2
import json
import urllib



class BlocklinkerWrapper():
    def __init__(self, url):
        self.url = url


    def LBL(self, address, xpub, blockHeight=0):
        response = {'success': 0}
        parameters = {}
        parameters['address'] = address
        parameters['xpub'] = xpub
        parameters['blockHeight'] = str(blockHeight)

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/linker/LBL?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve LBL'

        return response

    def LRL(self, address, xpub, blockHeight=0):
        response = {'success': 0}
        parameters = {}
        parameters['address'] = address
        parameters['xpub'] = xpub
        parameters['blockHeight'] = str(blockHeight)

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/linker/LRL?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve LRL'

        return response

    def LSL(self, address, xpub, blockHeight=0):
        response = {'success': 0}
        parameters = {}
        parameters['address'] = address
        parameters['xpub'] = xpub
        parameters['blockHeight'] = str(blockHeight)

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/linker/LSL?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve LSL'

        return response

    def LAL(self, address, xpub, blockHeight=0):
        response = {'success': 0}
        parameters = {}
        parameters['address'] = address
        parameters['xpub'] = xpub
        parameters['blockHeight'] = str(blockHeight)

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/linker/LAL?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve LAL'

        return response