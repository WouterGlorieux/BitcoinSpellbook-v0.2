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
import urllib2
import logging


from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(60)


import BlockData.BlockData as BlockData
import BlockInputs.BlockInputs as BlockInputs
import BlockLinker.BlockLinker as BlockLinker
import BlockRandom.BlockRandom as BlockRandom
import BlockVoter.BlockVoter as BlockVoter
import BlockForward.BlockForward as BlockForward
import BlockDistribute.BlockDistribute as BlockDistribute
import BlockTrigger.BlockTrigger as BlockTrigger
import BlockWriter.BlockWriter as BlockWriter
import datastore.datastore as datastore


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])


class AuthenticationStatus(object):
    OK = 'OK'
    INVALID_API_KEY = 'Invalid API key'
    NO_API_KEY = 'No API key supplied'
    INVALID_SIGNATURE = 'Invalid signature'
    NO_SIGNATURE = 'No signature supplied'


def is_authenticated(headers, body):
    if 'API_Key' in headers:
        api_key = headers['API_Key']

        authentication = None
        apikey = datastore.APIKeys.query(datastore.APIKeys.api_key == api_key).fetch(limit=1)
        if len(apikey) == 1:
            authentication = apikey[0]

        if authentication:
            if 'API_Sign' in headers:
                signature = str(headers['API_Sign'])
                message = hashlib.sha256(body).digest()
                if signature != base64.b64encode(hmac.new(base64.b64decode(authentication.api_secret),
                                                          message,
                                                          hashlib.sha512).digest()):
                    return AuthenticationStatus.INVALID_SIGNATURE
                else:
                    return AuthenticationStatus.OK
            else:
                return AuthenticationStatus.NO_SIGNATURE
        else:
            return AuthenticationStatus.INVALID_API_KEY
    else:
        return AuthenticationStatus.NO_API_KEY


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write("You shouldn't be here, go away!")


class Block(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        provider = ''
        if self.request.get('provider'):
            provider = self.request.get('provider')

        if self.request.get('height'):
            try:
                block_height = int(self.request.get('height'))
                response = BlockData.block(block_height, provider)
                self.response.write(json.dumps(response, sort_keys=True))

            except ValueError:
                response['error'] = 'Invalid value for height: must be a positive integer.'
                self.response.write(json.dumps(response, sort_keys=True))
        else:
            response['error'] = 'You must specify a height.'
            self.response.write(json.dumps(response, sort_keys=True))


class LatestBlock(webapp2.RequestHandler):
    def get(self):
        provider = ''
        if self.request.get('provider'):
            provider = self.request.get('provider')

        response = BlockData.latest_block(provider)
        self.response.write(json.dumps(response, sort_keys=True))


class PrimeInputAddress(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        provider = ''
        if self.request.get('provider'):
            provider = self.request.get('provider')

        if self.request.get('txid'):
            txid = self.request.get('txid')
            response = BlockData.prime_input_address(txid, provider)
            self.response.write(json.dumps(response, sort_keys=True))
        else:
            response['error'] = 'You must specify a txid.'
            self.response.write(json.dumps(response, sort_keys=True))


class Transactions(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        provider = ''
        if self.request.get('provider'):
            provider = self.request.get('provider')

        if self.request.get('address'):
            address = self.request.get('address')
            response = BlockData.transactions(address, provider)
            self.response.write(json.dumps(response, sort_keys=True))
        else:
            response['error'] = 'You must specify an address.'
            self.response.write(json.dumps(response, sort_keys=True))


class Balances(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        provider = ''
        if self.request.get('provider'):
            provider = self.request.get('provider')

        if self.request.get('addresses'):
            addresses = self.request.get('addresses')
            response = BlockData.balances(addresses, provider)
            self.response.write(json.dumps(response, sort_keys=True))
        else:
            response['error'] = 'You must specify one or more addresses.'
            self.response.write(json.dumps(response, sort_keys=True))


class Utxos(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        provider = ''
        if self.request.get('provider'):
            provider = self.request.get('provider')

        if self.request.get('addresses'):
            addresses = self.request.get('addresses')
            response = BlockData.utxos(addresses, provider)
            self.response.write(json.dumps(response, sort_keys=True))
        else:
            response['error'] = 'You must specify one or more addresses.'
            self.response.write(json.dumps(response, sort_keys=True))


class SaveProvider(webapp2.RequestHandler):
    def post(self):
        response = {'success': 0}
        authentication_status = is_authenticated(self.request.headers, self.request.body)
        if authentication_status == AuthenticationStatus.OK:
            if self.request.get('name') and self.request.get('priority') \
                    and self.request.get('provider_type') in ['Blocktrail.com', 'Blockchain.info', 'Insight']:
                name = self.request.get('name')
                try:
                    priority = int(self.request.get('priority'))
                except ValueError:
                    response['error'] = 'priority must be an integer.'
                    self.response.write(json.dumps(response))
                    return

                provider_type = self.request.get('provider_type')
                param = self.request.get('param')

                if BlockData.save_provider(name, priority, provider_type, param):
                    response['success'] = 1

            else:
                response['error'] = 'Invalid parameters'
        else:
            response['error'] = 'Authentication error: %s' % authentication_status

        self.response.write(json.dumps(response, sort_keys=True))


class DeleteProvider(webapp2.RequestHandler):
    def post(self):
        response = {'success': 0}

        authentication_status = is_authenticated(self.request.headers, self.request.body)
        if authentication_status == AuthenticationStatus.OK:
            if self.request.get('name'):
                name = self.request.get('name')
                if BlockData.delete_provider(name):
                    response['success'] = 1

            else:
                response['error'] = 'Invalid parameters'
        else:
            response['error'] = 'Authentication error: %s' % authentication_status

        self.response.write(json.dumps(response, sort_keys=True))


class GetProviders(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        try:
            response['providersList'] = BlockData.get_providers()
            response['success'] = 1
        except Exception as ex:
            logging.warning(str(ex))
            response['error'] = 'Unable to retrieve providers.'

        self.response.write(json.dumps(response, sort_keys=True))


class Initialize(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}

        datastore.Parameters.get_or_insert('DefaultConfig')

        admin_api_key = datastore.APIKeys.get_or_insert('Admin')
        admin_api_key.api_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
        admin_api_key.api_secret = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
        admin_api_key.put()

        response['name'] = 'Admin'
        response['api_key'] = admin_api_key.api_key
        response['api_secret'] = admin_api_key.api_secret
        response['success'] = 1

        self.response.write(json.dumps(response, sort_keys=True))


class UpdateRecommendedFee(webapp2.RequestHandler):
    @staticmethod
    def get():
        parameters = datastore.Parameters.get_or_insert('DefaultConfig')
        blocktrail_key = datastore.Providers.get_by_id('Blocktrail.com').blocktrail_key
        fee_data = {}

        url = 'https://api.blocktrail.com/v1/BTC/fee-per-kb?api_key=' + blocktrail_key
        try:
            fee_data = json.loads(urllib2.urlopen(urllib2.Request(url)).read())
        except Exception as ex:
            logging.warning(str(ex))

        if 'optimal' in fee_data:
            parameters.optimal_fee_per_kb = fee_data['optimal']
            parameters.put()


class SIL(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        if self.request.get('address'):
            address = self.request.get('address')

            if self.request.get('block_height'):
                try:
                    block_height = int(self.request.get('block_height'))
                    response = BlockInputs.get_sil(address, block_height)
                except ValueError:
                    response['error'] = 'block_height must be a positive integer.'

            else:
                response = BlockInputs.get_sil(address)

        else:
            response['error'] = 'You must provide an address.'

        self.response.write(json.dumps(response, sort_keys=True))


class Profile(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        if self.request.get('address'):
            address = self.request.get('address')

            if self.request.get('block_height'):
                try:
                    block_height = int(self.request.get('block_height'))
                    response = BlockInputs.get_profile(address, block_height)
                except ValueError:
                    response['error'] = 'block_height must be a positive integer.'

            else:
                response = BlockInputs.get_profile(address)

        else:
            response['error'] = 'You must provide an address.'

        self.response.write(json.dumps(response, sort_keys=True))


class LBL(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        if self.request.get('address') and self.request.get('xpub'):
            address = self.request.get('address')
            xpub = self.request.get('xpub')

            if self.request.get('block_height'):
                try:
                    block_height = int(self.request.get('block_height'))
                    response = BlockLinker.BlockLinker(address, xpub, block_height).get_lbl()
                except ValueError:
                    response['error'] = 'block_height must be a positive integer.'

            else:
                response = BlockLinker.BlockLinker(address, xpub).get_lbl()

        else:
            response['error'] = 'You must provide an address and an xpub key.'

        self.response.write(json.dumps(response, sort_keys=True))


class LRL(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        if self.request.get('address') and self.request.get('xpub'):
            address = self.request.get('address')
            xpub = self.request.get('xpub')

            if self.request.get('block_height'):
                try:
                    block_height = int(self.request.get('block_height'))
                    response = BlockLinker.BlockLinker(address, xpub, block_height).get_lrl()
                except ValueError:
                    response['error'] = 'block_height must be a positive integer.'

            else:
                response = BlockLinker.BlockLinker(address, xpub).get_lrl()

        else:
            response['error'] = 'You must provide an address and an xpub key.'

        self.response.write(json.dumps(response, sort_keys=True))


class LSL(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        if self.request.get('address') and self.request.get('xpub'):
            address = self.request.get('address')
            xpub = self.request.get('xpub')

            if self.request.get('block_height'):
                try:
                    block_height = int(self.request.get('block_height'))
                    response = BlockLinker.BlockLinker(address, xpub, block_height).get_lsl()
                except ValueError:
                    response['error'] = 'block_height must be a positive integer.'

            else:
                response = BlockLinker.BlockLinker(address, xpub).get_lsl()

        else:
            response['error'] = 'You must provide an address and an xpub key.'

        self.response.write(json.dumps(response, sort_keys=True))


class LAL(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        if self.request.get('address') and self.request.get('xpub'):
            address = self.request.get('address')
            xpub = self.request.get('xpub')

            if self.request.get('block_height'):
                try:
                    block_height = int(self.request.get('block_height'))
                    response = BlockLinker.BlockLinker(address, xpub, block_height).get_lal()
                except ValueError:
                    response['error'] = 'block_height must be a positive integer.'

            else:
                response = BlockLinker.BlockLinker(address, xpub).get_lal()

        else:
            response['error'] = 'You must provide an address and an xpub key.'

        self.response.write(json.dumps(response, sort_keys=True))


class ProportionalRandom(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        if self.request.get('address'):
            address = self.request.get('address')
            block_height = 0
            rng_block_height = 0
            xpub = ''
            source = 'SIL'

            if self.request.get('block_height'):
                try:
                    block_height = int(self.request.get('block_height'))
                except ValueError:
                    response['error'] = 'block_height must be a positive integer.'

            if self.request.get('rng_block_height'):
                try:
                    rng_block_height = int(self.request.get('rng_block_height'))
                except ValueError:
                    response['error'] = 'rng_block_height must be a positive integer.'

            if self.request.get('xpub'):
                xpub = self.request.get('xpub')

            if self.request.get('source') and self.request.get('source') in ['SIL', 'LBL', 'LRL', 'LSL']:
                source = self.request.get('source')

            response = BlockRandom.Random(address, block_height, xpub).proportional_random(source, rng_block_height)

        else:
            response['error'] = 'You must provide an address.'

        self.response.write(json.dumps(response, sort_keys=True))


class RandomFromBlock(webapp2.RequestHandler):
    def get(self):
        response = {'success': 0}
        rng_block_height = 0

        if self.request.get('rng_block_height'):
            try:
                rng_block_height = int(self.request.get('rng_block_height'))
            except ValueError:
                response['error'] = 'rng_block_height must be a positive integer.'

        response = BlockRandom.Random().from_block(rng_block_height)

        self.response.write(json.dumps(response, sort_keys=True))


class Proposal(webapp2.RequestHandler):
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

        vote_cost = 0
        if self.request.get('vote_cost'):
            try:
                vote_cost = int(self.request.get('vote_cost'))
            except ValueError:
                response['error'] = 'vote_cost must be a positive integer.'

        weights = 'Equal'
        if self.request.get('weights'):
            weights = self.request.get('weights')

        registration_address = ''
        if self.request.get('registration_address'):
            registration_address = self.request.get('registration_address')

        registration_block_height = 0
        if self.request.get('registration_block_height'):
            try:
                registration_block_height = int(self.request.get('registration_block_height'))
            except ValueError:
                response['error'] = 'registration_block_height must be a positive integer.'

        registration_xpub = ''
        if self.request.get('registration_xpub'):
            registration_xpub = self.request.get('registration_xpub')

        blockvoter = BlockVoter.BlockVoter(address, proposal, options, vote_cost)
        blockvoter.set_weights(weights, registration_address, registration_block_height, registration_xpub)

        response = blockvoter.get_proposal()

        self.response.write(json.dumps(response, sort_keys=True))


class Results(webapp2.RequestHandler):
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

        vote_cost = 0
        if self.request.get('vote_cost'):
            try:
                vote_cost = int(self.request.get('vote_cost'))
            except ValueError:
                response['error'] = 'vote_cost must be a positive integer.'

        block_height = 0
        if self.request.get('block_height'):
            try:
                block_height = int(self.request.get('block_height'))
            except ValueError:
                response['error'] = 'block_height must be a positive integer.'

        weights = 'Equal'
        if self.request.get('weights'):
            weights = self.request.get('weights')

        registration_address = ''
        if self.request.get('registration_address'):
            registration_address = self.request.get('registration_address')

        registration_block_height = 0
        if self.request.get('registration_block_height'):
            try:
                registration_block_height = int(self.request.get('registration_block_height'))
            except ValueError:
                response['error'] = 'registration_block_height must be a positive integer.'

        registration_xpub = ''
        if self.request.get('registration_xpub'):
            registration_xpub = self.request.get('registration_xpub')

        blockvoter = BlockVoter.BlockVoter(address, proposal, options, vote_cost)
        blockvoter.set_weights(weights, registration_address, registration_block_height, registration_xpub)

        response = blockvoter.get_results(block_height)

        self.response.write(json.dumps(response, sort_keys=True))


class GetForwarders(webapp2.RequestHandler):
    def get(self):
        response = BlockForward.get_forwarders()
        self.response.write(json.dumps(response, sort_keys=True))


class GetForwarder(webapp2.RequestHandler):
    def get(self):
        name = ''
        if self.request.get('name'):
            name = self.request.get('name')

        response = BlockForward.BlockForward(name).get()
        self.response.write(json.dumps(response, sort_keys=True))


class CheckForwarderAddress(webapp2.RequestHandler):
    def get(self):
        name = ''
        if self.request.get('name'):
            name = self.request.get('name')

        address = ''
        if self.request.get('address'):
            address = self.request.get('address')

        response = BlockForward.BlockForward(name).check_address(address)
        self.response.write(json.dumps(response, sort_keys=True))


class SaveForwarder(webapp2.RequestHandler):
    def post(self):
        response = {'success': 0}
        authentication_status = is_authenticated(self.request.headers, self.request.body)
        if authentication_status == AuthenticationStatus.OK:
            name = ''
            if self.request.get('name'):
                name = self.request.get('name')

            settings = {}

            if self.request.get('xpub'):
                settings['xpub'] = self.request.get('xpub')

            if self.request.get('description', None) is not None:
                settings['description'] = self.request.get('description')

            if self.request.get('creator', None) is not None:
                settings['creator'] = self.request.get('creator')

            if self.request.get('creator_email', None) is not None:
                settings['creator_email'] = self.request.get('creator_email')

            if self.request.get('minimum_amount'):
                try:
                    settings['minimum_amount'] = int(self.request.get('minimum_amount'))
                except ValueError:
                    response['error'] = 'minimum_amount must be a positive integer or equal to 0 (in Satoshis)'

            if self.request.get('youtube', None) is not None:
                settings['youtube'] = self.request.get('youtube')

            if self.request.get('visibility'):
                settings['visibility'] = self.request.get('visibility')

            if self.request.get('status'):
                settings['status'] = self.request.get('status')

            if self.request.get('fee_percentage'):
                try:
                    settings['fee_percentage'] = float(self.request.get('fee_percentage'))
                except ValueError:
                    response['error'] = 'Incorrect fee_percentage'

            if self.request.get('fee_address', None) is not None:
                settings['fee_address'] = self.request.get('fee_address')

            if self.request.get('confirm_amount'):
                try:
                    settings['confirm_amount'] = int(self.request.get('confirm_amount'))
                except ValueError:
                    response['error'] = 'confirm_amount must be a positive integer or equal to 0 (in Satoshis)'

            if self.request.get('address_type'):
                settings['address_type'] = self.request.get('address_type')

            if self.request.get('wallet_index'):
                try:
                    settings['wallet_index'] = int(self.request.get('wallet_index'))
                except ValueError:
                    response['error'] = 'wallet_index must be a positive integer'

            if self.request.get('private_key', None) is not None:
                settings['private_key'] = self.request.get('private_key')

            response = BlockForward.BlockForward(name).save_forwarder(settings)

        else:
            response['error'] = 'Authentication error: %s' % authentication_status

        self.response.write(json.dumps(response, sort_keys=True))


class DeleteForwarder(webapp2.RequestHandler):
    def post(self):
        response = {'success': 0}
        authentication_status = is_authenticated(self.request.headers, self.request.body)
        if authentication_status == AuthenticationStatus.OK:
            if self.request.get('name'):
                name = self.request.get('name')
                response = BlockForward.BlockForward(name).delete_forwarder()
        else:
            response['error'] = 'Authentication error: %s' % authentication_status

        self.response.write(json.dumps(response, sort_keys=True))


class DoForwarding(webapp2.RequestHandler):
    def get(self):
        name = ''
        if self.request.get('name'):
            name = self.request.get('name')

        BlockForward.DoForwarding(name)

        response = {'success': 1}
        self.response.write(json.dumps(response, sort_keys=True))


class GetDistributers(webapp2.RequestHandler):
    def get(self):
        response = BlockDistribute.get_distributers()
        self.response.write(json.dumps(response, sort_keys=True))


class GetDistributer(webapp2.RequestHandler):
    def get(self):
        name = ''
        if self.request.get('name'):
            name = self.request.get('name')

        response = BlockDistribute.Distributer(name).get()
        self.response.write(json.dumps(response, sort_keys=True))


class CheckDistributerAddress(webapp2.RequestHandler):
    def get(self):
        name = ''
        if self.request.get('name'):
            name = self.request.get('name')

        address = ''
        if self.request.get('address'):
            address = self.request.get('address')

        response = BlockDistribute.Distributer(name).check_address(address)

        self.response.write(json.dumps(response, sort_keys=True))


class SaveDistributer(webapp2.RequestHandler):
    def post(self):
        response = {'success': 0}
        authentication_status = is_authenticated(self.request.headers, self.request.body)
        if authentication_status == AuthenticationStatus.OK:
            name = ''
            if self.request.get('name'):
                name = self.request.get('name')

            settings = {}

            if self.request.get('distribution_source') in ['LBL', 'LRL', 'LSL', 'SIL', 'Custom']:
                settings['distribution_source'] = self.request.get('distribution_source')

            if self.request.get('registration_address', None) is not None:
                settings['registration_address'] = self.request.get('registration_address')

            if self.request.get('registration_xpub', None) is not None:
                settings['registration_xpub'] = self.request.get('registration_xpub')

            if self.request.get('registration_block_height'):
                try:
                    settings['registration_block_height'] = int(self.request.get('registration_block_height'))
                except ValueError:
                    response['error'] = 'registration_block_height must be a positive integer or equal to 0'

            if self.request.get('distribution', None) is not None:
                settings['distribution'] = self.request.get('distribution')

            if self.request.get('minimum_amount'):
                try:
                    settings['minimum_amount'] = int(self.request.get('minimum_amount'))
                except ValueError:
                    response['error'] = 'minimum_amount must be a positive integer or equal to 0 (in Satoshis)'

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

            if self.request.get('creator_email', None) is not None:
                settings['creator_email'] = self.request.get('creator_email')

            if self.request.get('youtube', None) is not None:
                settings['youtube'] = self.request.get('youtube')

            if self.request.get('fee_percentage'):
                try:
                    settings['fee_percentage'] = float(self.request.get('fee_percentage'))
                except ValueError:
                    response['error'] = 'Incorrect fee_percentage'

            if self.request.get('fee_address', None) is not None:
                settings['fee_address'] = self.request.get('fee_address')

            if self.request.get('maximum_transaction_fee'):
                try:
                    settings['maximum_transaction_fee'] = int(self.request.get('maximum_transaction_fee'))
                except ValueError:
                    response['error'] = 'maximum_transaction_fee must be a greater than or equal to 0 (in Satoshis)'

            if self.request.get('address_type'):
                settings['address_type'] = self.request.get('address_type')

            if self.request.get('wallet_index'):
                try:
                    settings['wallet_index'] = int(self.request.get('wallet_index'))
                except ValueError:
                    response['error'] = 'wallet_index must be a positive integer'

            if self.request.get('private_key', None) is not None:
                settings['private_key'] = self.request.get('private_key')

            response = BlockDistribute.Distributer(name).save_distributer(settings)

        else:
            response['error'] = 'Authentication error: %s' % authentication_status

        self.response.write(json.dumps(response, sort_keys=True))


class DeleteDistributer(webapp2.RequestHandler):
    def post(self):
        response = {'success': 0}
        authentication_status = is_authenticated(self.request.headers, self.request.body)
        if authentication_status == AuthenticationStatus.OK:
            if self.request.get('name'):
                name = self.request.get('name')
                response = BlockDistribute.Distributer(name).delete_distributer()
        else:
            response['error'] = 'Authentication error: %s' % authentication_status

        self.response.write(json.dumps(response, sort_keys=True))


class UpdateDistribution(webapp2.RequestHandler):
    def post(self):
        response = {'success': 0}
        authentication_status = is_authenticated(self.request.headers, self.request.body)
        if authentication_status == AuthenticationStatus.OK:
            if self.request.get('name'):
                name = self.request.get('name')
                response = BlockDistribute.Distributer(name).update_distribution()
        else:
            response['error'] = 'Authentication error: %s' % authentication_status

        self.response.write(json.dumps(response, sort_keys=True))


class DoDistributing(webapp2.RequestHandler):
    def get(self):
        name = ''
        if self.request.get('name'):
            name = self.request.get('name')

        BlockDistribute.DoDistributing(name)

        response = {'success': 1}
        self.response.write(json.dumps(response, sort_keys=True))


class GetTriggers(webapp2.RequestHandler):
    def get(self):
        response = BlockTrigger.get_triggers()
        self.response.write(json.dumps(response, sort_keys=True))


class GetTrigger(webapp2.RequestHandler):
    def get(self):
        name = ''
        if self.request.get('name'):
            name = self.request.get('name')

        response = BlockTrigger.BlockTrigger(name).get()
        self.response.write(json.dumps(response, sort_keys=True))


class SaveTrigger(webapp2.RequestHandler):
    def post(self):
        response = {'success': 0}
        authentication_status = is_authenticated(self.request.headers, self.request.body)
        if authentication_status == AuthenticationStatus.OK:
            name = ''
            if self.request.get('name'):
                name = self.request.get('name')

            settings = {}

            if self.request.get('trigger_type'):
                settings['trigger_type'] = self.request.get('trigger_type')

            if self.request.get('block_height'):
                try:
                    settings['block_height'] = int(self.request.get('block_height'))
                except ValueError:
                    response['error'] = 'block_height must be a positive integer'

            if self.request.get('address', None) is not None:
                settings['address'] = self.request.get('address')

            if self.request.get('amount'):
                try:
                    settings['amount'] = int(self.request.get('amount'))
                except ValueError:
                    response['error'] = 'amount must be a positive integer or equal to 0 (in Satoshis)'

            if self.request.get('confirmations'):
                try:
                    settings['confirmations'] = int(self.request.get('confirmations'))
                except ValueError:
                    response['error'] = 'confirmations must be a positive integer or equal to 0'

            if self.request.get('triggered') == 'True':
                settings['triggered'] = True
            elif self.request.get('triggered') == 'False':
                settings['triggered'] = False

            if self.request.get('description', None) is not None:
                settings['description'] = self.request.get('description')

            if self.request.get('creator', None) is not None:
                settings['creator'] = self.request.get('creator')

            if self.request.get('creator_email', None) is not None:
                settings['creator_email'] = self.request.get('creator_email')

            if self.request.get('youtube', None) is not None:
                settings['youtube'] = self.request.get('youtube')

            if self.request.get('visibility'):
                settings['visibility'] = self.request.get('visibility')

            if self.request.get('status'):
                settings['status'] = self.request.get('status')

            response = BlockTrigger.BlockTrigger(name).save_trigger(settings)

        else:
            response['error'] = 'Authentication error: %s' % authentication_status

        self.response.write(json.dumps(response, sort_keys=True))


class DeleteTrigger(webapp2.RequestHandler):
    def post(self):
        response = {'success': 0}
        authentication_status = is_authenticated(self.request.headers, self.request.body)
        if authentication_status == AuthenticationStatus.OK:
            if self.request.get('name'):
                name = self.request.get('name')
                response = BlockTrigger.BlockTrigger(name).delete_trigger()
        else:
            response['error'] = 'Authentication error: %s' % authentication_status

        self.response.write(json.dumps(response, sort_keys=True))


class SaveAction(webapp2.RequestHandler):
    def post(self):
        response = {'success': 0}
        authentication_status = is_authenticated(self.request.headers, self.request.body)
        if authentication_status == AuthenticationStatus.OK:
            if self.request.get('trigger_name'):
                trigger_name = self.request.get('trigger_name')

                action_name = ''
                if self.request.get('action_name'):
                    action_name = self.request.get('action_name')

                settings = {}
                if self.request.get('action_type'):
                    settings['action_type'] = self.request.get('action_type')

                if self.request.get('description', None) is not None:
                    settings['description'] = self.request.get('description')

                if self.request.get('reveal_text', None) is not None:
                    settings['reveal_text'] = self.request.get('reveal_text')

                if self.request.get('reveal_link_text', None) is not None:
                    settings['reveal_link_text'] = self.request.get('reveal_link_text')

                if self.request.get('reveal_link_url', None) is not None:
                    settings['reveal_link_url'] = self.request.get('reveal_link_url')

                if self.request.get('mail_to', None) is not None:
                    settings['mail_to'] = self.request.get('mail_to')

                if self.request.get('mail_subject', None) is not None:
                    settings['mail_subject'] = self.request.get('mail_subject')

                if self.request.get('mail_body', None) is not None:
                    settings['mail_body'] = self.request.get('mail_body')

                if self.request.get('mail_sent') == 'True':
                    settings['mail_sent'] = True
                elif self.request.get('mail_sent') == 'False':
                    settings['mail_sent'] = False

                if self.request.get('webhook', None) is not None:
                    settings['webhook'] = self.request.get('webhook')

                response = BlockTrigger.BlockTrigger(trigger_name).save_action(action_name, settings)

            else:
                response['error'] = 'Invalid parameters'
        else:
            response['error'] = 'Authentication error: %s' % authentication_status

        self.response.write(json.dumps(response, sort_keys=True))


class DeleteAction(webapp2.RequestHandler):
    def post(self):
        response = {'success': 0}
        authentication_status = is_authenticated(self.request.headers, self.request.body)
        if authentication_status == AuthenticationStatus.OK:
            if self.request.get('trigger_name') and self.request.get('action_name'):
                trigger_name = self.request.get('trigger_name')
                action_name = self.request.get('action_name')

                response = BlockTrigger.BlockTrigger(trigger_name).delete_action(action_name)
        else:
            response['error'] = 'Authentication error: %s' % authentication_status

        self.response.write(json.dumps(response, sort_keys=True))


class CheckTriggers(webapp2.RequestHandler):
    def get(self):
        name = ''
        if self.request.get('name'):
            name = self.request.get('name')

        BlockTrigger.CheckTriggers(name)

        response = {'success': 1}
        self.response.write(json.dumps(response, sort_keys=True))


class GetWriters(webapp2.RequestHandler):
    def get(self):
        response = BlockWriter.get_writers()
        self.response.write(json.dumps(response, sort_keys=True))


class GetWriter(webapp2.RequestHandler):
    def get(self):
        name = ''
        if self.request.get('name'):
            name = self.request.get('name')

        response = BlockWriter.Writer(name).get()
        self.response.write(json.dumps(response, sort_keys=True))


class SaveWriter(webapp2.RequestHandler):
    def post(self):
        response = {'success': 0}
        authentication_status = is_authenticated(self.request.headers, self.request.body)
        if authentication_status == AuthenticationStatus.OK:
            settings = {}
            name = ''
            if self.request.get('name'):
                name = self.request.get('name')

            if self.request.get('outputs', None) is not None:
                settings['outputs'] = self.request.get('outputs')

            if self.request.get('message', None) is not None:
                settings['message'] = self.request.get('message')

            if self.request.get('visibility'):
                settings['visibility'] = self.request.get('visibility')

            if self.request.get('status'):
                settings['status'] = self.request.get('status')

            if self.request.get('description', None) is not None:
                settings['description'] = self.request.get('description')

            if self.request.get('creator', None) is not None:
                settings['creator'] = self.request.get('creator')

            if self.request.get('creator_email', None) is not None:
                settings['creator_email'] = self.request.get('creator_email')

            if self.request.get('youtube', None) is not None:
                settings['youtube'] = self.request.get('youtube')

            if self.request.get('fee_percentage'):
                try:
                    settings['fee_percentage'] = float(self.request.get('fee_percentage'))
                except ValueError:
                    response['error'] = 'Incorrect fee_percentage'

            if self.request.get('fee_address', None) is not None:
                settings['fee_address'] = self.request.get('fee_address')

            if self.request.get('maximum_transaction_fee'):
                try:
                    settings['maximum_transaction_fee'] = int(self.request.get('maximum_transaction_fee'))
                except ValueError:
                    response['error'] = 'maximum_transaction_fee must be greater than or equal to 0 (in Satoshis)'

            if self.request.get('address_type'):
                settings['address_type'] = self.request.get('address_type')

            if self.request.get('wallet_index'):
                try:
                    settings['wallet_index'] = int(self.request.get('wallet_index'))
                except ValueError:
                    response['error'] = 'wallet_index must be a positive integer'

            if self.request.get('private_key', None) is not None:
                settings['private_key'] = self.request.get('private_key')

            response = BlockWriter.Writer(name).save_writer(settings)
        else:
            response['error'] = 'Authentication error: %s' % authentication_status

        self.response.write(json.dumps(response, sort_keys=True))


class DeleteWriter(webapp2.RequestHandler):
    def post(self):
        response = {'success': 0}
        authentication_status = is_authenticated(self.request.headers, self.request.body)
        if authentication_status == AuthenticationStatus.OK:
            if self.request.get('name'):
                name = self.request.get('name')
                response = BlockWriter.Writer(name).delete_writer()
        else:
            response['error'] = 'Authentication error: %s' % authentication_status

        self.response.write(json.dumps(response, sort_keys=True))


class DoWriting(webapp2.RequestHandler):
    def get(self):
        name = ''
        if self.request.get('name'):
            name = self.request.get('name')

        BlockWriter.DoWriting(name)

        response = {'success': 1}
        self.response.write(json.dumps(response, sort_keys=True))


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/admin/initialize', Initialize),
    ('/admin/updateRecommendedFee', UpdateRecommendedFee),

    ('/data/save_provider', SaveProvider),
    ('/data/delete_provider', DeleteProvider),
    ('/data/get_providers', GetProviders),
    ('/data/block', Block),
    ('/data/latest_block', LatestBlock),
    ('/data/prime_input_address', PrimeInputAddress),
    ('/data/transactions', Transactions),
    ('/data/balances', Balances),
    ('/data/utxos', Utxos),

    ('/inputs/SIL', SIL),
    ('/inputs/profile', Profile),

    ('/linker/LBL', LBL),
    ('/linker/LRL', LRL),
    ('/linker/LSL', LSL),
    ('/linker/LAL', LAL),

    ('/random/proportional', ProportionalRandom),
    ('/random/block', RandomFromBlock),

    ('/voter/proposal', Proposal),
    ('/voter/results', Results),

    ('/forwarder/get_forwarders', GetForwarders),
    ('/forwarder/get_forwarder', GetForwarder),
    ('/forwarder/check_address', CheckForwarderAddress),
    ('/forwarder/save_forwarder', SaveForwarder),
    ('/forwarder/delete_forwarder', DeleteForwarder),
    ('/forwarder/do_forwarding', DoForwarding),

    ('/distributer/get_distributers', GetDistributers),
    ('/distributer/get_distributer', GetDistributer),
    ('/distributer/check_address', CheckDistributerAddress),
    ('/distributer/save_distributer', SaveDistributer),
    ('/distributer/delete_distributer', DeleteDistributer),
    ('/distributer/update_distribution', UpdateDistribution),
    ('/distributer/do_distributing', DoDistributing),

    ('/trigger/get_triggers', GetTriggers),
    ('/trigger/get_trigger', GetTrigger),
    ('/trigger/save_trigger', SaveTrigger),
    ('/trigger/delete_trigger', DeleteTrigger),
    ('/trigger/save_action', SaveAction),
    ('/trigger/delete_action', DeleteAction),
    ('/trigger/check_triggers', CheckTriggers),

    ('/writer/get_writers', GetWriters),
    ('/writer/get_writer', GetWriter),
    ('/writer/save_writer', SaveWriter),
    ('/writer/delete_writer', DeleteWriter),
    ('/writer/do_writing', DoWriting),
], debug=True)