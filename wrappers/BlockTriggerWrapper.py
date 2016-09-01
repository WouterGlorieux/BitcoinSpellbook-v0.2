#!/usr/bin/env python
# -*- coding: utf-8 -*-


import urllib2
import json
import urllib
import hashlib
import hmac
import base64
import logging


class BlockTriggerWrapper():
    def __init__(self, url):
        self.url = url

    def get_triggers(self):
        response = {'success': 0}
        parameters = {}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/trigger/get_triggers?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except Exception as ex:
            logging.warning(str(ex))
            response['error'] = 'Unable to retrieve triggers'

        return response

    def get_trigger(self, name):
        response = {'success': 0}
        parameters = {'name': name}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/trigger/get_trigger?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except Exception as ex:
            logging.warning(str(ex))
            response['error'] = 'Unable to retrieve trigger'

        return response

    def save_trigger(self, name, settings=None, api_key='', api_secret=''):
        if not settings:
            settings = {}
        response = {'success': 0}
        parameters = {'name': name}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/trigger/save_trigger?" + query_string

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
            response['error'] = 'Unable to save trigger'

        return response

    def delete_trigger(self, name, api_key='', api_secret=''):
        response = {'success': 0}
        parameters = {'name': name}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/trigger/delete_trigger?" + query_string

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
            response['error'] = 'Unable to delete trigger'

        return response

    def save_action(self, trigger_name, action_name, settings=None, api_key='', api_secret=''):
        if not settings:
            settings = {}
        response = {'success': 0}
        parameters = {'trigger_name': trigger_name,
                      'action_name': action_name}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/trigger/save_action?" + query_string

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
            response['error'] = 'Unable to save action'

        return response

    def delete_action(self, trigger_name, action_name, api_key='', api_secret=''):
        response = {'success': 0}
        parameters = {'trigger_name': trigger_name,
                      'action_name': action_name}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/trigger/delete_action?" + query_string

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
            response['error'] = 'Unable to delete action'

        return response

    def check_triggers(self, name=''):
        response = {'success': 0}
        parameters = {'name': name}

        query_string = urllib.urlencode(parameters)
        url = self.url + "/trigger/check_triggers?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except Exception as ex:
            logging.warning(str(ex))
            response['error'] = 'Unable to check triggers'

        return response