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


from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(60)


import Blockchaindata.Blockchaindata as data
import SimplifiedInputsList.SimplifiedInputsList as SimplifiedInputsList
import Blocklinker.Blocklinker as Blocklinker
import BlockRandom.BlockRandom as BlockRandom
import BlockVoter.BlockVoter as BlockVoter
import HDForwarder.HDForwarder as HDForwarder
import DistributeBTC.DistributeBTC as DistributeBTC

import datastore.datastore as datastore


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])



def authenticate(headers, body):
    response = {'success': 0}

    if 'API_Key' in headers:
        API_key = headers['API_Key']

        authentication = None
        APIKey = datastore.APIKeys.query(datastore.APIKeys.api_key == API_key).fetch(limit=1)
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

        self.response.write(json.dumps(response, sort_keys=True))

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

        self.response.write(json.dumps(response, sort_keys=True))

class getProviders(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        try:
            response['providersList'] = data.getProvidersList()
            response['success'] = 1
        except:
            response['error'] = 'Unable to retrieve providers.'

        self.response.write(json.dumps(response, sort_keys=True))

class initialize(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}

        datastore.Parameters.get_or_insert('DefaultConfig')

        adminAPIKey = datastore.APIKeys.get_or_insert('Admin')
        adminAPIKey.api_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
        adminAPIKey.api_secret = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
        adminAPIKey.put()

        response['name'] = 'Admin'
        response['api_key'] = adminAPIKey.api_key
        response['api_secret'] = adminAPIKey.api_secret
        response['success'] = 1

        self.response.write(json.dumps(response, sort_keys=True))


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

        self.response.write(json.dumps(response, sort_keys=True))


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

        self.response.write(json.dumps(response, sort_keys=True))


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

        self.response.write(json.dumps(response, sort_keys=True))

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

        self.response.write(json.dumps(response, sort_keys=True))

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

        self.response.write(json.dumps(response, sort_keys=True))


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

        self.response.write(json.dumps(response, sort_keys=True))

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

        self.response.write(json.dumps(response, sort_keys=True))


class proposal(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}

        address = ''
        if self.request.get('address'):
            address = self.request.get('address')

        proposal = ''
        if self.request.get('proposal'):
            proposal = self.request.get('proposal')

        options = []
        if self.request.get('options'):
            options = self.request.get('options').split("|")

        voteCost = 0
        if self.request.get('voteCost'):
            try:
                voteCost = int(self.request.get('voteCost'))
            except ValueError:
                response['error'] = 'voteCost must be a positive integer.'

        weights = 'Equal'
        if self.request.get('weights'):
            weights = self.request.get('weights')

        registrationAddress = ''
        if self.request.get('regAddress'):
            registrationAddress = self.request.get('regAddress')

        registrationBlockHeight = 0
        if self.request.get('regBlockHeight'):
            try:
                registrationBlockHeight = int(self.request.get('regBlockHeight'))
            except ValueError:
                response['error'] = 'regBlockHeight must be a positive integer.'

        registrationXPUB = ''
        if self.request.get('regXPUB'):
            registrationXPUB = self.request.get('regXPUB')


        blockVoter = BlockVoter.BlockVoter(address, proposal, options, voteCost)
        blockVoter.setWeights(weights, registrationAddress, registrationBlockHeight, registrationXPUB)

        response = blockVoter.getProposal()


        self.response.write(json.dumps(response, sort_keys=True))

class results(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}

        address = ''
        if self.request.get('address'):
            address = self.request.get('address')

        proposal = ''
        if self.request.get('proposal'):
            proposal = self.request.get('proposal')

        options = []
        if self.request.get('options'):
            options = self.request.get('options').split("|")

        voteCost = 0
        if self.request.get('voteCost'):
            try:
                voteCost = int(self.request.get('voteCost'))
            except ValueError:
                response['error'] = 'voteCost must be a positive integer.'

        blockHeight = 0
        if self.request.get('blockHeight'):
            try:
                blockHeight = int(self.request.get('blockHeight'))
            except ValueError:
                response['error'] = 'blockHeight must be a positive integer.'

        weights = 'Equal'
        if self.request.get('weights'):
            weights = self.request.get('weights')

        registrationAddress = ''
        if self.request.get('regAddress'):
            registrationAddress = self.request.get('regAddress')

        registrationBlockHeight = 0
        if self.request.get('regBlockHeight'):
            try:
                registrationBlockHeight = int(self.request.get('regBlockHeight'))
            except ValueError:
                response['error'] = 'regBlockHeight must be a positive integer.'

        registrationXPUB = ''
        if self.request.get('regXPUB'):
            registrationXPUB = self.request.get('regXPUB')


        blockVoter = BlockVoter.BlockVoter(address, proposal, options, voteCost)
        blockVoter.setWeights(weights, registrationAddress, registrationBlockHeight, registrationXPUB)

        response = blockVoter.getResults(blockHeight)

        self.response.write(json.dumps(response, sort_keys=True))


class getForwarders(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        response = HDForwarder.getForwarders()

        self.response.write(json.dumps(response, sort_keys=True))


class getForwarder(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}

        name = ''
        if self.request.get('name'):
            name = self.request.get('name')

        response = HDForwarder.HDForwarder(name).get()

        self.response.write(json.dumps(response, sort_keys=True))


class checkForwarderAddress(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}

        name = ''
        if self.request.get('name'):
            name = self.request.get('name')

        address = ''
        if self.request.get('address'):
            address = self.request.get('address')

        response = HDForwarder.HDForwarder(name).checkAddress(address)

        self.response.write(json.dumps(response, sort_keys=True))


class saveForwarder(webapp2.RequestHandler):
    def post(self):
        response = {'success': 0}

        authenticationOK = False
        authentication = authenticate(self.request.headers, self.request.body)
        if 'success' in authentication and authentication['success'] == 1:
            authenticationOK = True

        if authenticationOK:
            if self.request.get('name'):
                name = self.request.get('name')

                settings = {}

                if self.request.get('xpub'):
                    settings['xpub'] = self.request.get('xpub')

                if self.request.get('description', None) is not None:
                    settings['description'] = self.request.get('description')

                if self.request.get('creator', None) is not None:
                    settings['creator'] = self.request.get('creator')

                if self.request.get('creatorEmail', None) is not None:
                    settings['creatorEmail'] = self.request.get('creatorEmail')

                if self.request.get('minimumAmount'):
                    try:
                        settings['minimumAmount'] = int(self.request.get('minimumAmount'))
                    except ValueError:
                        response['error'] = 'minimumAmount must be a positive integer or equal to 0 (in Satoshis)'

                if self.request.get('youtube', None) is not None:
                    settings['youtube'] = self.request.get('youtube')

                if self.request.get('visibility'):
                    settings['visibility'] = self.request.get('visibility')

                if self.request.get('status'):
                    settings['status'] = self.request.get('status')

                if self.request.get('feePercent'):
                    try:
                        settings['feePercent'] = float(self.request.get('feePercent'))
                    except ValueError:
                        response['error'] = 'Incorrect feePercent'

                if self.request.get('feeAddress', None) is not None:
                    settings['feeAddress'] = self.request.get('feeAddress')



                if self.request.get('confirmAmount'):
                    try:
                        settings['confirmAmount'] = int(self.request.get('confirmAmount'))
                    except ValueError:
                        response['error'] = 'confirmAmount must be a positive integer or equal to 0 (in Satoshis)'

                if self.request.get('addressType'):
                    settings['addressType'] = self.request.get('addressType')

                if self.request.get('walletIndex'):
                    try:
                        settings['walletIndex'] = int(self.request.get('walletIndex'))
                    except ValueError:
                        response['error'] = 'walletIndex must be a positive integer'

                if self.request.get('privateKey', None) is not None:
                    settings['privateKey'] = self.request.get('privateKey')

                response = HDForwarder.HDForwarder(name).saveForwarder(settings)

            else:
                response['error'] = 'Invalid parameters'
        else:
            response['error'] = authentication['error']

        self.response.write(json.dumps(response, sort_keys=True))


class deleteForwarder(webapp2.RequestHandler):
    def post(self):
        response = {'success': 0}

        authenticationOK = False
        authentication = authenticate(self.request.headers, self.request.body)
        if 'success' in authentication and authentication['success'] == 1:
            authenticationOK = True

        if authenticationOK:
            if self.request.get('name'):
                name = self.request.get('name')
                response = HDForwarder.HDForwarder(name).deleteForwarder()
        else:
            response['error'] = authentication['error']

        self.response.write(json.dumps(response, sort_keys=True))


class doForwarding(webapp2.RequestHandler):
    def get(self):
        name = ''
        if self.request.get('name'):
            name = self.request.get('name')

        HDForwarder.DoForwarding(name)

        response = {'success': 1}
        self.response.write(json.dumps(response, sort_keys=True))



class getDistributers(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        response = DistributeBTC.getDistributers()

        self.response.write(json.dumps(response, sort_keys=True))


class getDistributer(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}

        name = ''
        if self.request.get('name'):
            name = self.request.get('name')

        response = DistributeBTC.Distributer(name).get()

        self.response.write(json.dumps(response, sort_keys=True))


class checkDistributerAddress(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}

        name = ''
        if self.request.get('name'):
            name = self.request.get('name')

        address = ''
        if self.request.get('address'):
            address = self.request.get('address')

        response = DistributeBTC.Distributer(name).checkAddress(address)

        self.response.write(json.dumps(response, sort_keys=True))


class saveDistributer(webapp2.RequestHandler):
    def post(self):
        response = {'success': 0}

        authenticationOK = False
        authentication = authenticate(self.request.headers, self.request.body)
        if 'success' in authentication and authentication['success'] == 1:
            authenticationOK = True

        if authenticationOK:
            if self.request.get('name'):
                name = self.request.get('name')

                settings = {}

                if self.request.get('distributionSource') in ['LBL', 'LRL', 'LSL', 'SIL', 'Custom']:
                    settings['distributionSource'] = self.request.get('distributionSource')

                if self.request.get('registrationAddress', None) is not None:
                    settings['registrationAddress'] = self.request.get('registrationAddress')

                if self.request.get('registrationXPUB', None) is not None:
                    settings['registrationXPUB'] = self.request.get('registrationXPUB')

                if self.request.get('registrationBlockHeight'):
                    try:
                        settings['registrationBlockHeight'] = int(self.request.get('registrationBlockHeight'))
                    except ValueError:
                        response['error'] = 'registrationBlockHeight must be a positive integer or equal to 0'


                if self.request.get('distribution', None) is not None:
                    settings['distribution'] = self.request.get('distribution')


                if self.request.get('minimumAmount'):
                    try:
                        settings['minimumAmount'] = int(self.request.get('minimumAmount'))
                    except ValueError:
                        response['error'] = 'minimumAmount must be a positive integer or equal to 0 (in Satoshis)'

                if self.request.get('threshold'):
                    try:
                        settings['threshold'] = int(self.request.get('threshold'))
                    except ValueError:
                        response['error'] = 'threshold must be a positive integer or equal to 0 (in Satoshis)'


                if self.request.get('visibility'):
                    settings['visibility'] = self.request.get('visibility')

                if self.request.get('status'):
                    settings['status'] = self.request.get('status')


                if self.request.get('description', None) is not None:
                    settings['description'] = self.request.get('description')

                if self.request.get('creator', None) is not None:
                    settings['creator'] = self.request.get('creator')

                if self.request.get('creatorEmail', None) is not None:
                    settings['creatorEmail'] = self.request.get('creatorEmail')



                if self.request.get('youtube', None) is not None:
                    settings['youtube'] = self.request.get('youtube')


                if self.request.get('feePercent'):
                    try:
                        settings['feePercent'] = float(self.request.get('feePercent'))
                    except ValueError:
                        response['error'] = 'Incorrect feePercent'

                if self.request.get('feeAddress', None) is not None:
                    settings['feeAddress'] = self.request.get('feeAddress')


                if self.request.get('maxTransactionFee'):
                    try:
                        settings['maxTransactionFee'] = int(self.request.get('maxTransactionFee'))
                    except ValueError:
                        response['error'] = 'maxTransactionFee must be a positive integer or equal to 0 (in Satoshis)'


                if self.request.get('addressType'):
                    settings['addressType'] = self.request.get('addressType')

                if self.request.get('walletIndex'):
                    try:
                        settings['walletIndex'] = int(self.request.get('walletIndex'))
                    except ValueError:
                        response['error'] = 'walletIndex must be a positive integer'

                if self.request.get('privateKey', None) is not None:
                    settings['privateKey'] = self.request.get('privateKey')














                response = DistributeBTC.Distributer(name).saveDistributer(settings)

            else:
                response['error'] = 'Invalid parameters'
        else:
            response['error'] = authentication['error']

        self.response.write(json.dumps(response, sort_keys=True))


class deleteDistributer(webapp2.RequestHandler):
    def post(self):
        response = {'success': 0}

        authenticationOK = False
        authentication = authenticate(self.request.headers, self.request.body)
        if 'success' in authentication and authentication['success'] == 1:
            authenticationOK = True

        if authenticationOK:
            if self.request.get('name'):
                name = self.request.get('name')
                response = DistributeBTC.Distributer(name).deleteDistributer()
        else:
            response['error'] = authentication['error']

        self.response.write(json.dumps(response, sort_keys=True))


class updateDistribution(webapp2.RequestHandler):
    def post(self):
        response = {'success': 0}

        authenticationOK = False
        authentication = authenticate(self.request.headers, self.request.body)
        if 'success' in authentication and authentication['success'] == 1:
            authenticationOK = True

        if authenticationOK:
            if self.request.get('name'):
                name = self.request.get('name')
                response = DistributeBTC.Distributer(name).updateDistribution()
        else:
            response['error'] = authentication['error']

        self.response.write(json.dumps(response, sort_keys=True))




class doDistributing(webapp2.RequestHandler):
    def get(self):
        name = ''
        if self.request.get('name'):
            name = self.request.get('name')

        DistributeBTC.DoDistributing(name)

        response = {'success': 1}
        self.response.write(json.dumps(response, sort_keys=True))






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
    ('/voter/proposal', proposal),
    ('/voter/results', results),
    ('/forwarder/getForwarders', getForwarders),
    ('/forwarder/getForwarder', getForwarder),
    ('/forwarder/checkAddress', checkForwarderAddress),
    ('/forwarder/saveForwarder', saveForwarder),
    ('/forwarder/deleteForwarder', deleteForwarder),
    ('/forwarder/doForwarding', doForwarding),
    ('/distributer/getDistributers', getDistributers),
    ('/distributer/getDistributer', getDistributer),
    ('/distributer/checkAddress', checkDistributerAddress),
    ('/distributer/saveDistributer', saveDistributer),
    ('/distributer/deleteDistributer', deleteDistributer),
    ('/distributer/updateDistribution', updateDistribution),
    ('/distributer/doDistributing', doDistributing),



], debug=True)

