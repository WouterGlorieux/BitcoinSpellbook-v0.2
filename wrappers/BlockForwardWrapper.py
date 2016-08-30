#!/usr/bin/env python
# -*- coding: utf-8 -*-


import urllib2
import json
import urllib
import hashlib
import hmac
import base64


class BlockForwardWrapper():
    def __init__(self, url):
        self.url = url

    def get_forwarders(self):
        response = {'success': 0}
        parameters = {}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/forwarder/getForwarders?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve forwarders'

        return response

    def get_forwarder(self, name):
        response = {'success': 0}
        parameters = {'name': name}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/forwarder/getForwarder?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve forwarder'

        return response

    def check_address(self, name, address):
        response = {'success': 0}
        parameters = {'name': name,
                      'address': address}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/forwarder/checkAddress?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve forwarder'

        return response

    def save_forwarder(self, name, settings=None, api_key='', api_secret=''):
        if not settings:
            settings = {}
        response = {'success': 0}
        parameters = {'name': name}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/forwarder/saveForwarder?" + query_string

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
        except:
            response['error'] = 'Unable to save forwarder'

        return response

    def delete_forwarder(self, name, api_key='', api_secret=''):
        response = {'success': 0}
        parameters = {'name': name}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/forwarder/deleteForwarder?" + query_string

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
        except:
            response['error'] = 'Unable to delete forwarder'

        return response

    def do_forwarding(self, name=''):
        response = {'success': 0}
        parameters = {'name': name}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/forwarder/doForwarding?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to do forwarding'

        return response