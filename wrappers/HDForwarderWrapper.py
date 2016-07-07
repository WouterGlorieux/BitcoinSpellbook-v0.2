#!/usr/bin/env python
# -*- coding: utf-8 -*-


import urllib2
import json
import urllib
import hashlib
import hmac
import base64


class HDForwarderWrapper():
    def __init__(self, url):
        self.url = url


    def getForwarders(self):
        response = {'success': 0}
        parameters = {}

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/forwarder/getForwarders?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve forwarders'

        return response

    def getForwarder(self, name):
        response = {'success': 0}
        parameters = {}
        parameters['name'] = name

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/forwarder/getForwarder?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve forwarder'

        return response


    def checkAddress(self, name, address):
        response = {'success': 0}
        parameters = {}
        parameters['name'] = name
        parameters['address'] = address

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/forwarder/checkAddress?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve forwarder'

        return response


    def saveForwarder(self, name, settings={}, APIkey='', APIsecret=''):
        response = {'success': 0}
        parameters ={}
        parameters['name'] = name

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/forwarder/saveForwarder?" + queryString

        postdata = urllib.urlencode(settings)
        message = hashlib.sha256(postdata).digest()
        signature = hmac.new(base64.b64decode(APIsecret), message, hashlib.sha512)

        headers = {
            'API-Key': APIkey,
            'API-Sign': base64.b64encode(signature.digest())
        }

        try:
            request = urllib2.Request(url=url, data=postdata, headers=headers)
            data = urllib2.urlopen(request).read()
            response = json.loads(data)
        except:
            response['error'] = 'Unable to save forwarder'

        return response


    def deleteForwarder(self, name, APIkey='', APIsecret=''):
        response = {'success': 0}
        parameters = {}
        parameters['name'] = name

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/forwarder/deleteForwarder?" + queryString

        postdata = urllib.urlencode(parameters)
        message = hashlib.sha256(postdata).digest()
        signature = hmac.new(base64.b64decode(APIsecret), message, hashlib.sha512)

        headers = {
            'API-Key': APIkey,
            'API-Sign': base64.b64encode(signature.digest())
        }

        try:
            request = urllib2.Request(url=url, data=postdata, headers=headers)
            data = urllib2.urlopen(request).read()
            response = json.loads(data)
        except:
            response['error'] = 'Unable to delete forwarder'

        return response

    def doForwarding(self, name=''):
        response = {'success': 0}
        parameters = {}
        parameters['name'] = name

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/forwarder/doForwarding?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to do forwarding'

        return response