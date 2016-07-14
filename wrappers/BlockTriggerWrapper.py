#!/usr/bin/env python
# -*- coding: utf-8 -*-


import urllib2
import json
import urllib
import hashlib
import hmac
import base64


class BlockTriggerWrapper():
    def __init__(self, url):
        self.url = url


    def getTriggers(self):
        response = {'success': 0}
        parameters = {}

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/trigger/getTriggers?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve triggers'

        return response

    def getTrigger(self, name):
        response = {'success': 0}
        parameters = {}
        parameters['name'] = name

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/trigger/getTrigger?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve trigger'

        return response


    def saveTrigger(self, name, settings={}, APIkey='', APIsecret=''):
        response = {'success': 0}
        parameters ={}
        parameters['name'] = name

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/trigger/saveTrigger?" + queryString

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
            response['error'] = 'Unable to save trigger'

        return response


    def deleteTrigger(self, name, APIkey='', APIsecret=''):
        response = {'success': 0}
        parameters = {}
        parameters['name'] = name

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/trigger/deleteTrigger?" + queryString

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
            response['error'] = 'Unable to delete trigger'

        return response


    def saveAction(self, triggerName, actionName, settings={}, APIkey='', APIsecret=''):
        response = {'success': 0}
        parameters ={}
        parameters['triggerName'] = triggerName
        parameters['actionName'] = actionName

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/trigger/saveAction?" + queryString

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
            response['error'] = 'Unable to save action'

        return response


    def deleteAction(self, triggerName, actionName, APIkey='', APIsecret=''):
        response = {'success': 0}
        parameters = {}
        parameters['triggerName'] = triggerName
        parameters['actionName'] = actionName

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/trigger/deleteAction?" + queryString

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
            response['error'] = 'Unable to delete action'

        return response










    def checkTriggers(self, name=''):
        response = {'success': 0}
        parameters = {}
        parameters['name'] = name

        queryString  = urllib.urlencode(parameters)
        url = self.url + "/trigger/checkTriggers?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to check triggers'

        return response