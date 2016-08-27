#!/usr/bin/env python
# -*- coding: utf-8 -*-


import urllib2
import json
import urllib



class BlockRandomWrapper():
    def __init__(self, url):
        self.url = url

    def fromBlock(self, rngBlockHeight=0):
        response = {'success': 0}
        parameters = {}
        parameters['rngBlockHeight'] = str(rngBlockHeight)

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/random/block?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve random number from block'

        return response


    def fromSIL(self, address, blockHeight=0, rngBlockHeight=0):
        response = {'success': 0}
        parameters = {}
        parameters['source'] = 'SIL'
        parameters['address'] = address
        parameters['block_height'] = str(blockHeight)
        parameters['rngBlockHeight'] = str(rngBlockHeight)

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/random/proportional?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve random address from SIL'

        return response

    def fromLBL(self, address, xpub, blockHeight=0, rngBlockHeight=0):
        response = {'success': 0}
        parameters = {}
        parameters['source'] = 'LBL'
        parameters['address'] = address
        parameters['xpub'] = xpub
        parameters['block_height'] = str(blockHeight)
        parameters['rngBlockHeight'] = str(rngBlockHeight)

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/random/proportional?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve random address from LBL'

        return response

    def fromLRL(self, address, xpub, blockHeight=0, rngBlockHeight=0):
        response = {'success': 0}
        parameters = {}
        parameters['source'] = 'LRL'
        parameters['address'] = address
        parameters['xpub'] = xpub
        parameters['block_height'] = str(blockHeight)
        parameters['rngBlockHeight'] = str(rngBlockHeight)

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/random/proportional?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve random address from LRL'

        return response

    def fromLSL(self, address, xpub, blockHeight=0, rngBlockHeight=0):
        response = {'success': 0}
        parameters = {}
        parameters['source'] = 'LRL'
        parameters['address'] = address
        parameters['xpub'] = xpub
        parameters['block_height'] = str(blockHeight)
        parameters['rngBlockHeight'] = str(rngBlockHeight)

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/random/proportional?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve random address from LSL'

        return response