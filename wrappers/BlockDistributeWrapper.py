#!/usr/bin/env python
# -*- coding: utf-8 -*-


import urllib2
import json
import urllib
import hashlib
import hmac
import base64


class BlockDistributeWrapper():
    def __init__(self, url):
        self.url = url


    def getDistributers(self):
        response = {'success': 0}
        parameters = {}

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/distributer/getDistributers?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve distributers'

        return response

    def getDistributer(self, name):
        response = {'success': 0}
        parameters = {}
        parameters['name'] = name

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/distributer/getDistributer?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve distributer'

        return response


    def checkAddress(self, name, address):
        response = {'success': 0}
        parameters = {}
        parameters['name'] = name
        parameters['address'] = address

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/distributer/checkAddress?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve distributer'

        return response


    def saveDistributer(self, name, settings={}, APIkey='', APIsecret=''):
        response = {'success': 0}
        parameters ={}
        parameters['name'] = name

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/distributer/saveDistributer?" + queryString

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
            response['error'] = 'Unable to save distributer'

        return response


    def deleteDistributer(self, name, APIkey='', APIsecret=''):
        response = {'success': 0}
        parameters = {}
        parameters['name'] = name

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/distributer/deleteDistributer?" + queryString

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
            response['error'] = 'Unable to delete distributer'

        return response


    def updateDistribution(self, name, APIkey='', APIsecret=''):
        response = {'success': 0}
        parameters = {}
        parameters['name'] = name

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/distributer/updateDistribution?" + queryString

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
            response['error'] = 'Unable to update distribution'

        return response




    def doDistributing(self, name=''):
        response = {'success': 0}
        parameters = {}
        parameters['name'] = name

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/distributer/doDistributing?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to do distributing'

        return response