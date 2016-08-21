#!/usr/bin/env python
# -*- coding: utf-8 -*-


import urllib2
import json
import urllib
import hashlib
import hmac
import base64


class BlockDataWrapper():
    def __init__(self, url):
        self.url = url


    def utxos(self, addresses=[], provider=''):
        response = {'success': 0}
        parameters = {}
        parameters['provider'] = provider

        if addresses != []:
            strAddresses = ""
            for address in addresses:
                strAddresses += address + "|"

            strAddresses = strAddresses[:-1]
            parameters['addresses'] = strAddresses

        queryString  = urllib.urlencode(parameters)
        url = self.url +"/data/utxos?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve utxos'

        return response



    def balances(self, addresses=[], provider=''):
        response = {'success': 0}
        parameters = {}
        parameters['provider'] = provider

        if addresses != []:
            strAddresses = ""
            for address in addresses:
                strAddresses += address + "|"

            strAddresses = strAddresses[:-1]
            parameters['addresses'] = strAddresses

        queryString  = urllib.urlencode(parameters)
        url = self.url +"/data/balances?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve balances'

        return response

    def transactions(self, address, provider=''):
        response = {'success': 0}
        parameters = {}
        parameters['address'] = address
        parameters['provider'] = provider

        queryString  = urllib.urlencode(parameters)
        url = self.url +"/data/transactions?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve transactions'

        return response

    def block(self, height, provider=''):
        response = {'success': 0}
        parameters = {}
        parameters['height'] = str(height)
        parameters['provider'] = provider

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/data/block?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve block'

        return response

    def latestBlock(self, provider=''):
        response = {'success': 0}
        parameters = {}
        parameters['provider'] = provider

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/data/latestBlock?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve latest block'

        return response


    def primeInputAddress(self, txid, provider=''):
        response = {'success': 0}
        parameters = {}
        parameters['txid'] = txid
        parameters['provider'] = provider

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/data/primeInputAddress?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
           response['error'] = 'Unable to retrieve prime input address'

        return response


    def saveProvider(self, name, priority, providerType, param="", API_key='', API_secret=''):
        response = {'success': 0}
        parameters = {}
        parameters['name'] = name
        parameters['priority'] = priority
        parameters['providerType'] = providerType

        if providerType == 'Blocktrail.com' or 'Insight':
            parameters['param'] = param

        queryString  = urllib.urlencode(parameters)
        url = self.url +"/data/saveProvider?" + queryString

        postdata = urllib.urlencode(parameters)
        message = hashlib.sha256(postdata).digest()
        signature = hmac.new(base64.b64decode(API_secret), message, hashlib.sha512)

        headers = {
            'API_Key': API_key,
            'API_Sign': base64.b64encode(signature.digest())
        }

        try:
            request = urllib2.Request(url=url, data=postdata, headers=headers)
            data = urllib2.urlopen(request).read()
            response = json.loads(data)
        except:
            response['error'] = 'Unable to save provider'

        return response


    def deleteProvider(self, name, API_key='', API_secret=''):
        response = {'success': 0}
        parameters = {}
        parameters['name'] = name

        queryString  = urllib.urlencode(parameters)
        url = self.url +"/data/deleteProvider?" + queryString

        postdata = urllib.urlencode(parameters)
        message = hashlib.sha256(postdata).digest()
        signature = hmac.new(base64.b64decode(API_secret), message, hashlib.sha512)

        headers = {
            'API_Key': API_key,
            'API_Sign': base64.b64encode(signature.digest())
        }

        try:
            request = urllib2.Request(url=url, data=postdata, headers=headers)
            data = urllib2.urlopen(request).read()
            response = json.loads(data)
        except:
            response['error'] = 'Unable to delete provider'

        return response

    def getProviders(self):
        response = {'success': 0}
        parameters = {}

        queryString  = urllib.urlencode(parameters)
        url = self.url +"/data/getProviders?" + queryString

        try:
            request = urllib2.Request(url=url)
            data = urllib2.urlopen(request).read()
            response = json.loads(data)
        except:
            response['error'] = 'Unable to get providers'

        return response