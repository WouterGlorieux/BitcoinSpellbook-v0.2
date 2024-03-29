#!/usr/bin/env python
# -*- coding: utf-8 -*-


import urllib2
import json
import urllib
import hashlib
import hmac
import base64
import logging


class BlockDistributeWrapper():
    def __init__(self, url):
        self.url = url

    def get_distributers(self):
        response = {'success': 0}
        parameters = {}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/distributer/get_distributers?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except Exception as ex:
            logging.warning(str(ex))
            response['error'] = 'Unable to retrieve distributers'

        return response

    def get_distributer(self, name):
        response = {'success': 0}
        parameters = {'name': name}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/distributer/get_distributer?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except Exception as ex:
            logging.warning(str(ex))
            response['error'] = 'Unable to retrieve distributer'

        return response

    def check_address(self, name, address):
        response = {'success': 0}
        parameters = {'name': name,
                      'address': address}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/distributer/check_address?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except Exception as ex:
            logging.warning(str(ex))
            response['error'] = 'Unable to retrieve distributer'

        return response

    def save_distributer(self, name, settings=None, api_key='', api_secret=''):
        if not settings:
            settings = {}
        response = {'success': 0}
        parameters = {'name': name}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/distributer/save_distributer?" + query_string

        postdata = urllib.urlencode(settings)
        message = hashlib.sha256(postdata).digest()
        signature = hmac.new(base64.b64decode(api_secret), message, hashlib.sha512)

        headers = {
            'API-Key': api_key,
            'API-Sign': base64.b64encode(signature.digest())
        }

        try:
            request = urllib2.Request(url=url, data=postdata, headers=headers)
            data = urllib2.urlopen(request).read()
            response = json.loads(data)
        except Exception as ex:
            logging.warning(str(ex))
            response['error'] = 'Unable to save distributer'

        return response

    def delete_distributer(self, name, api_key='', api_secret=''):
        response = {'success': 0}
        parameters = {'name': name}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/distributer/delete_distributer?" + query_string

        postdata = urllib.urlencode(parameters)
        message = hashlib.sha256(postdata).digest()
        signature = hmac.new(base64.b64decode(api_secret), message, hashlib.sha512)

        headers = {
            'API-Key': api_key,
            'API-Sign': base64.b64encode(signature.digest())
        }

        try:
            request = urllib2.Request(url=url, data=postdata, headers=headers)
            data = urllib2.urlopen(request).read()
            response = json.loads(data)
        except Exception as ex:
            logging.warning(str(ex))
            response['error'] = 'Unable to delete distributer'

        return response

    def update_distribution(self, name, api_key='', api_secret=''):
        response = {'success': 0}
        parameters = {'name': name}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/distributer/update_distribution?" + query_string

        postdata = urllib.urlencode(parameters)
        message = hashlib.sha256(postdata).digest()
        signature = hmac.new(base64.b64decode(api_secret), message, hashlib.sha512)

        headers = {
            'API-Key': api_key,
            'API-Sign': base64.b64encode(signature.digest())
        }

        try:
            request = urllib2.Request(url=url, data=postdata, headers=headers)
            data = urllib2.urlopen(request).read()
            response = json.loads(data)
        except Exception as ex:
            logging.warning(str(ex))
            response['error'] = 'Unable to update distribution'

        return response

    def do_distributing(self, name=''):
        response = {'success': 0}
        parameters = {'name': name}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/distributer/do_distributing?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except Exception as ex:
            logging.warning(str(ex))
            response['error'] = 'Unable to do distributing'

        return response