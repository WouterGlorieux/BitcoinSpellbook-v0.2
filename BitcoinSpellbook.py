#!/usr/bin/env python
# -*- coding: utf-8 -*-




import os
import jinja2
import webapp2
import json

import string
import random
import hashlib
import hmac
import base64

from google.appengine.ext import ndb
from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(60)


import Blockchaindata.Blockchaindata as data
import SimplifiedInputsList.SimplifiedInputsList as SimplifiedInputsList
import Blocklinker.Blocklinker as Blocklinker
import BlockRandom.BlockRandom as BlockRandom

class Parameters(ndb.Model):
    #Model for 3rd party data providers parameters
    blocktrail_key = ndb.StringProperty(indexed=True, default="a8a84ed2929da8313d75d16e04be2a26c4cc4ea4")
    insight_url = ndb.StringProperty(indexed=True, default="https://blockexplorer.com/api/")

class APIKeys(ndb.Model):
    api_key = ndb.StringProperty(indexed=True, default='')
    api_secret = ndb.StringProperty(indexed=True, default='')


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])



def authenticate(headers, body):
    response = {'success': 0}

    if 'API_Key' in headers:
        API_key = headers['API_Key']

        authentication = None
        APIKey = APIKeys.query(APIKeys.api_key == API_key).fetch(limit=1)
        if len(APIKey) == 1:
            authentication = APIKey[0]

        if authentication:
            if 'API_Sign' in headers:
                signature = str(headers['API_Sign'])
                message = hashlib.sha256(body).digest()
                if signature != base64.b64encode(hmac.new(base64.b64decode(authentication.api_secret), message, hashlib.sha512).digest()):
                    response['error'] = 'Invalid signature'
                else:
                    response['success'] = 1
            else:
                response['error'] = 'No signature supplied'
        else:
            response['error'] = 'Invalid API_key'

    else:
        response['error'] = 'No API_key supplied'



    return response


class mainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write("You shouldn't be here, go away!")


class block(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        provider = ''
        if self.request.get('provider'):
            provider = self.request.get('provider')

        if self.request.get('height'):
            try:
                blockHeight = int(self.request.get('height'))
                response = data.block(blockHeight, provider)
                self.response.write(json.dumps(response, sort_keys=True))

            except ValueError:
                response['error'] = 'Invalid value for height: must be a positive integer.'
                self.response.write(json.dumps(response, sort_keys=True))
        else:
            response['error'] = 'You must specify a height.'
            self.response.write(json.dumps(response, sort_keys=True))


class latestBlock(webapp2.RequestHandler):
    def get(self):
        provider = ''
        if self.request.get('provider'):
            provider = self.request.get('provider')

        response = data.latestBlock(provider)
        self.response.write(json.dumps(response, sort_keys=True))

class primeInputAddress(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        provider = ''
        if self.request.get('provider'):
            provider = self.request.get('provider')

        if self.request.get('txid'):
            txid = self.request.get('txid')
            response = data.primeInputAddress(txid, provider)
            self.response.write(json.dumps(response, sort_keys=True))
        else:
            response['error'] = 'You must specify a txid.'
            self.response.write(json.dumps(response, sort_keys=True))

class transactions(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        provider = ''
        if self.request.get('provider'):
            provider = self.request.get('provider')

        if self.request.get('address'):
            address = self.request.get('address')
            response = data.transactions(address, provider)
            self.response.write(json.dumps(response, sort_keys=True))
        else:
            response['error'] = 'You must specify an address.'
            self.response.write(json.dumps(response, sort_keys=True))


class balances(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        provider = ''
        if self.request.get('provider'):
            provider = self.request.get('provider')

        if self.request.get('addresses'):
            addresses = self.request.get('addresses')
            response = data.balances(addresses, provider)
            self.response.write(json.dumps(response, sort_keys=True))
        else:
            response['error'] = 'You must specify one or more addresses.'
            self.response.write(json.dumps(response, sort_keys=True))


class utxos(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        provider = ''
        if self.request.get('provider'):
            provider = self.request.get('provider')

        if self.request.get('addresses'):
            addresses = self.request.get('addresses')
            response = data.utxos(addresses, provider)
            self.response.write(json.dumps(response, sort_keys=True))
        else:
            response['error'] = 'You must specify one or more addresses.'
            self.response.write(json.dumps(response, sort_keys=True))




class saveProvider(webapp2.RequestHandler):
    def post(self):
        response = {'success': 0}

        authenticationOK = False
        authentication = authenticate(self.request.headers, self.request.body)
        if 'success' in authentication and authentication['success'] == 1:
            authenticationOK = True

        if authenticationOK:
            if self.request.get('name') and self.request.get('priority') and self.request.get('providerType') in ['Blocktrail.com', 'Blockchain.info', 'Insight']:
                name = self.request.get('name')
                try:
                    priority = int(self.request.get('priority'))
                except ValueError:
                    response['error'] = 'priority must be an integer.'
                    self.response.write(json.dumps(response))
                    return

                providerType = self.request.get('providerType')
                param = self.request.get('param')

                if data.saveProvider(name, priority, providerType, param) == True:
                    response['success'] = 1

            else:
                response['error'] = 'Invalid parameters'
        else:
            response['error'] = authentication['error']

        self.response.write(json.dumps(response))

class deleteProvider(webapp2.RequestHandler):
    def post(self):
        response = {'success': 0}

        authenticationOK = False
        authentication = authenticate(self.request.headers, self.request.body)
        if 'success' in authentication and authentication['success'] == 1:
            authenticationOK = True

        if authenticationOK:
            if self.request.get('name'):
                name = self.request.get('name')
                if data.deleteProvider(name) == True:
                    response['success'] = 1

            else:
                response['error'] = 'Invalid parameters'
        else:
            response['error'] = authentication['error']

        self.response.write(json.dumps(response))

class getProviders(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        try:
            response['providersList'] = data.getProvidersList()
            response['success'] = 1
        except:
            response['error'] = 'Unable to retrieve providers.'

        self.response.write(json.dumps(response))

class initialize(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        adminAPIKey = APIKeys.get_or_insert('Admin')
        adminAPIKey.api_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
        adminAPIKey.api_secret = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
        adminAPIKey.put()

        response['name'] = 'Admin'
        response['api_key'] = adminAPIKey.api_key
        response['api_secret'] = adminAPIKey.api_secret
        response['success'] = 1

        self.response.write(json.dumps(response))


class SIL(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        if self.request.get('address'):
            address = self.request.get('address')

            if self.request.get('blockHeight'):
                try:
                    blockHeight = int(self.request.get('blockHeight'))
                    response = SimplifiedInputsList.SIL(address, blockHeight)
                except ValueError:
                    response['error'] = 'blockHeight must be a positive integer.'

            else:
                response = SimplifiedInputsList.SIL(address)

        else:
            response['error'] = 'You must provide an address.'

        self.response.write(json.dumps(response))


class LBL(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        if self.request.get('address') and self.request.get('xpub'):
            address = self.request.get('address')
            xpub = self.request.get('xpub')

            if self.request.get('blockHeight'):
                try:
                    blockHeight = int(self.request.get('blockHeight'))
                    response = Blocklinker.Blocklinker(address, xpub, blockHeight).LBL()
                except ValueError:
                    response['error'] = 'blockHeight must be a positive integer.'

            else:
                response = Blocklinker.Blocklinker(address, xpub).LBL()

        else:
            response['error'] = 'You must provide an address and an xpub key.'

        self.response.write(json.dumps(response))


class LRL(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        if self.request.get('address') and self.request.get('xpub'):
            address = self.request.get('address')
            xpub = self.request.get('xpub')

            if self.request.get('blockHeight'):
                try:
                    blockHeight = int(self.request.get('blockHeight'))
                    response = Blocklinker.Blocklinker(address, xpub, blockHeight).LRL()
                except ValueError:
                    response['error'] = 'blockHeight must be a positive integer.'

            else:
                response = Blocklinker.Blocklinker(address, xpub).LRL()

        else:
            response['error'] = 'You must provide an address and an xpub key.'

        self.response.write(json.dumps(response))

class LSL(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        if self.request.get('address') and self.request.get('xpub'):
            address = self.request.get('address')
            xpub = self.request.get('xpub')

            if self.request.get('blockHeight'):
                try:
                    blockHeight = int(self.request.get('blockHeight'))
                    response = Blocklinker.Blocklinker(address, xpub, blockHeight).LSL()
                except ValueError:
                    response['error'] = 'blockHeight must be a positive integer.'

            else:
                response = Blocklinker.Blocklinker(address, xpub).LSL()

        else:
            response['error'] = 'You must provide an address and an xpub key.'

        self.response.write(json.dumps(response))

class LAL(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        if self.request.get('address') and self.request.get('xpub'):
            address = self.request.get('address')
            xpub = self.request.get('xpub')

            if self.request.get('blockHeight'):
                try:
                    blockHeight = int(self.request.get('blockHeight'))
                    response = Blocklinker.Blocklinker(address, xpub, blockHeight).LAL()
                except ValueError:
                    response['error'] = 'blockHeight must be a positive integer.'

            else:
                response = Blocklinker.Blocklinker(address, xpub).LAL()

        else:
            response['error'] = 'You must provide an address and an xpub key.'

        self.response.write(json.dumps(response))


class proportionalRandom(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        if self.request.get('address'):
            address = self.request.get('address')
            blockHeight = 0
            rngBlockHeight = 0
            xpub = ''
            source = 'SIL'

            if self.request.get('blockHeight'):
                try:
                    blockHeight = int(self.request.get('blockHeight'))
                except ValueError:
                    response['error'] = 'blockHeight must be a positive integer.'

            if self.request.get('rngBlockHeight'):
                try:
                    rngBlockHeight = int(self.request.get('rngBlockHeight'))
                except ValueError:
                    response['error'] = 'rngBlockHeight must be a positive integer.'

            if self.request.get('xpub'):
                xpub = self.request.get('xpub')

            if self.request.get('source') and self.request.get('source') in ['SIL', 'LBL', 'LRL', 'LSL']:
                source = self.request.get('source')

            response = BlockRandom.Random(address, blockHeight, xpub).proportionalRandom(source, rngBlockHeight)

        else:
            response['error'] = 'You must provide an address.'

        self.response.write(json.dumps(response))

class randomFromBlock(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        rngBlockHeight = 0

        if self.request.get('rngBlockHeight'):
            try:
                rngBlockHeight = int(self.request.get('rngBlockHeight'))
            except ValueError:
                response['error'] = 'rngBlockHeight must be a positive integer.'

        response = BlockRandom.Random().fromBlock(rngBlockHeight)

        self.response.write(json.dumps(response))



app = webapp2.WSGIApplication([
    ('/', mainPage),
    ('/admin/initialize', initialize),
    ('/data/saveProvider', saveProvider),
    ('/data/deleteProvider', deleteProvider),
    ('/data/getProviders', getProviders),
    ('/data/block', block),
    ('/data/latestBlock', latestBlock),
    ('/data/primeInputAddress', primeInputAddress),
    ('/data/transactions', transactions),
    ('/data/balances', balances),
    ('/data/utxos', utxos),
    ('/SIL/SIL', SIL),
    ('/linker/LBL', LBL),
    ('/linker/LRL', LRL),
    ('/linker/LSL', LSL),
    ('/linker/LAL', LAL),
    ('/random/proportional', proportionalRandom),
    ('/random/block', randomFromBlock),


], debug=True)

