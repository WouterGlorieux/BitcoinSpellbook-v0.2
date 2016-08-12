#!/usr/bin/env python
# -*- coding: utf-8 -*-


import urllib2
import json
import urllib
import hashlib
import hmac
import base64


class BlockWriterWrapper():
    def __init__(self, url):
        self.url = url


    def getWriters(self):
        response = {'success': 0}
        parameters = {}

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/writer/getWriters?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve writers'

        return response

    def getWriter(self, name=''):
        response = {'success': 0}
        parameters = {}
        parameters['name'] = name

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/writer/getWriter?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve writer'

        return response


    def saveWriter(self, name, settings={}, APIkey='', APIsecret=''):
        response = {'success': 0}
        parameters ={}
        parameters['name'] = name

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/writer/saveWriter?" + queryString

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
            response['error'] = 'Unable to save writer'

        return response


    def deleteWriter(self, name, APIkey='', APIsecret=''):
        response = {'success': 0}
        parameters = {}
        parameters['name'] = name

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/writer/deleteWriter?" + queryString

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
            response['error'] = 'Unable to delete writer'

        return response




    def doWriting(self, name=''):
        response = {'success': 0}
        parameters = {}
        parameters['name'] = name

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/writer/doWriting?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to do writing'

        return response