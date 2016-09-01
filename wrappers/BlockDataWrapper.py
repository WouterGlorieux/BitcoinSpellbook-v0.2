#!/usr/bin/env python
# -*- coding: utf-8 -*-


import urllib2
import json
import urllib
import hashlib
import hmac
import base64
import logging


class BlockDataWrapper():
    def __init__(self, url):
        self.url = url

    def utxos(self, addresses=None, provider=''):
        if not addresses:
            addresses = []
        response = {'success': 0}
        parameters = {'provider': provider}

        if addresses:
            str_addresses = ""
            for address in addresses:
                str_addresses += address + "|"

            str_addresses = str_addresses[:-1]
            parameters['addresses'] = str_addresses

        query_string = urllib.urlencode(parameters)
        url = self.url + "/data/utxos?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except Exception as ex:
            logging.warning(str(ex))
            response['error'] = 'Unable to retrieve utxos'

        return response

    def balances(self, addresses=None, provider=''):
        if not addresses:
            addresses = []
        response = {'success': 0}
        parameters = {'provider': provider}

        if addresses:
            str_addresses = ""
            for address in addresses:
                str_addresses += address + "|"

            str_addresses = str_addresses[:-1]
            parameters['addresses'] = str_addresses

        query_string = urllib.urlencode(parameters)
        url = self.url + "/data/balances?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except Exception as ex:
            logging.warning(str(ex))
            response['error'] = 'Unable to retrieve balances'

        return response

    def transactions(self, address, provider=''):
        response = {'success': 0}
        parameters = {'address': address,
                      'provider': provider}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/data/transactions?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except Exception as ex:
            logging.warning(str(ex))
            response['error'] = 'Unable to retrieve transactions'

        return response

    def block(self, height, provider=''):
        response = {'success': 0}
        parameters = {'height': str(height),
                      'provider': provider}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/data/block?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except Exception as ex:
            logging.warning(str(ex))
            response['error'] = 'Unable to retrieve block'

        return response

    def latest_block(self, provider=''):
        response = {'success': 0}
        parameters = {'provider': provider}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/data/latestBlock?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except Exception as ex:
            logging.warning(str(ex))
            response['error'] = 'Unable to retrieve latest block'

        return response

    def prime_input_address(self, txid, provider=''):
        response = {'success': 0}
        parameters = {'txid': txid,
                      'provider': provider}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/data/prime_input_address?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except Exception as ex:
            logging.warning(str(ex))
            response['error'] = 'Unable to retrieve prime input address'

        return response

    def save_provider(self, name, priority, provider_type, param="", api_key='', api_secret=''):
        response = {'success': 0}
        parameters = {'name': name,
                      'priority': priority,
                      'provider_type': provider_type}

        if provider_type == 'Blocktrail.com' or 'Insight':
            parameters['param'] = param

        query_string = urllib.urlencode(parameters)
        url = self.url + "/data/save_provider?" + query_string

        postdata = urllib.urlencode(parameters)
        message = hashlib.sha256(postdata).digest()
        signature = hmac.new(base64.b64decode(api_secret), message, hashlib.sha512)

        headers = {
            'API_Key': api_key,
            'API_Sign': base64.b64encode(signature.digest())
        }

        try:
            request = urllib2.Request(url=url, data=postdata, headers=headers)
            data = urllib2.urlopen(request).read()
            response = json.loads(data)
        except Exception as ex:
            logging.warning(str(ex))
            response['error'] = 'Unable to save provider'

        return response

    def delete_provider(self, name, api_key='', api_secret=''):
        response = {'success': 0}
        parameters = {'name': name}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/data/delete_provider?" + query_string

        postdata = urllib.urlencode(parameters)
        message = hashlib.sha256(postdata).digest()
        signature = hmac.new(base64.b64decode(api_secret), message, hashlib.sha512)

        headers = {
            'API_Key': api_key,
            'API_Sign': base64.b64encode(signature.digest())
        }

        try:
            request = urllib2.Request(url=url, data=postdata, headers=headers)
            data = urllib2.urlopen(request).read()
            response = json.loads(data)
        except Exception as ex:
            logging.warning(str(ex))
            response['error'] = 'Unable to delete provider'

        return response

    def get_providers(self):
        response = {'success': 0}
        parameters = {}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/data/get_providers?" + query_string

        try:
            request = urllib2.Request(url=url)
            data = urllib2.urlopen(request).read()
            response = json.loads(data)
        except Exception as ex:
            logging.warning(str(ex))
            response['error'] = 'Unable to get providers'

        return response