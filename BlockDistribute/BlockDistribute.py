#!/usr/bin/env python
# -*- coding: utf-8 -*-

from validators import validators as validator
from BIP44 import BIP44 as BIP44
import BlockData.BlockData as BlockData
from BlockLinker import BlockLinker as BlockLinker
from BlockInputs import BlockInputs as BlockInputs


import datastore.datastore as datastore
import TxFactory.TxFactory as TxFactory

import time
import bitcoin
import logging

from google.appengine.ext import ndb
from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(60)


REQUIRED_CONFIRMATIONS = 3  # must be at least 3
TRANSACTION_FEE = 10000  # in Satoshis


def getNextIndex():
    distributers_query = datastore.Distributer.query(ancestor=datastore.distributers_key()).order(-datastore.Distributer.wallet_index)
    distributers = distributers_query.fetch()

    if len(distributers) > 0:
        i = distributers[0].wallet_index + 1
    else:
        i = 1

    return i


def distributerToDict(distributer):
    distributer_dict = {'name': distributer.key.id(),
                        'address': distributer.address,
                        'distributionSource': distributer.distributionSource,
                        'registration_address': distributer.registrationAddress,
                        'registration_block_height': distributer.registrationBlockHeight,
                        'registration_xpub': distributer.registrationXPUB,
                        'distribution': distributer.distribution,
                        'minimum_amount': distributer.minimum_amount,
                        'threshold': distributer.threshold,
                        'status': distributer.status,
                        'visibility': distributer.visibility,
                        'description': distributer.description,
                        'creator': distributer.creator,
                        'creator_email': distributer.creator_email,
                        'youtube': distributer.youtube,
                        'fee_address': distributer.fee_address,
                        'fee_percentage': distributer.fee_percentage,
                        'maximum_transaction_fee': distributer.maximum_transaction_fee,
                        'date': int(time.mktime(distributer.date.timetuple()))}

    return distributer_dict


def getDistributers():
    response = {'success': 0}
    distributers = []

    distributers_query = datastore.Distributer.query(datastore.Distributer.visibility == 'Public',
                                                     datastore.Distributer.status == 'Active',
                                                     ancestor=datastore.distributers_key()).order(-datastore.Distributer.date)
    data = distributers_query.fetch()
    for distributer in data:
        distributers.append(distributerToDict(distributer))

    response['distributers'] = distributers
    response['success'] = 1

    return response


class Distributer():
    @ndb.transactional(xg=True)
    def __init__(self, name):
        self.error = ''
        if isinstance(name, (str, unicode)) and len(name) > 0:
            self.name = name
        else:
            self.error = 'Name cannot be empty'

    def get(self):
        response = {'success': 0}
        if self.error == '':
            distributer = datastore.Distributer.get_by_id(self.name, parent=datastore.distributers_key())

            if distributer:
                response['distributer'] = distributerToDict(distributer)
                response['success'] = 1
            else:
                response['error'] = 'No distributer with that name found.'

        return response

    def checkAddress(self, address):
        response = {'success': 0}
        if self.error == '':
            distributer = datastore.Distributer.get_by_id(self.name, parent=datastore.distributers_key())

            if distributer:
                distributing_relation = {'relation': 'unrelated address'}
                if distributer.address == address:
                    distributing_relation['relation'] = 'distributing address'
                else:
                    share = 0
                    for recipient in distributer.distribution:
                        if recipient[0] == address:
                            distributing_relation['relation'] = 'receiving address'
                            if len(recipient) >= 3:
                                share += recipient[2]

                    if distributing_relation['relation'] == 'receiving address':
                        distributing_relation['share'] = share

                    if distributer.registrationAddress == address and distributer.distributionSource in ['SIL', 'LBL', 'LRL', 'LSL']:
                        distributing_relation['relation'] = 'registration address'

                response[address] = distributing_relation
                response['success'] = 1

            else:
                response['error'] = 'No distributer with that name found.'

        return response

    def saveDistributer(self, settings=None):
        if not settings:
            settings = {}
        response = {'success': 0}

        if self.error == '':
            distributer = datastore.Distributer.get_or_insert(self.name, parent=datastore.distributers_key())

            if 'distributionSource' in settings and settings['distributionSource'] in ['LBL', 'LRL', 'LSL', 'SIL', 'Custom']:
                distributer.distributionSource = settings['distributionSource']
            elif 'distributionSource' in settings:
                self.error = 'Invalid distributionSource'

            if 'registration_address' in settings and (validator.validAddress(settings['registration_address']) or settings['registration_address'] == ''):
                distributer.registrationAddress = settings['registration_address']
            elif 'registration_address' in settings:
                self.error = 'Invalid registration_address'

            if 'registration_xpub' in settings and (validator.validXPUB(settings['registration_xpub']) or settings['registration_xpub'] == ''):
                distributer.registrationXPUB = settings['registration_xpub']
            elif 'registration_xpub' in settings:
                self.error = 'Invalid registration_xpub'

            if 'registration_block_height' in settings and (validator.validBlockHeight(settings['registration_block_height'])):
                distributer.registrationBlockHeight = settings['registration_block_height']
            elif 'registration_block_height' in settings:
                self.error = 'Invalid registration_block_height: ' + str(settings['registration_block_height'])

            if 'distribution' in settings and validator.validDistribution(eval(settings['distribution'])):
                distributer.distribution = eval(settings['distribution'])
            elif 'distribution' in settings and settings['distribution'] == u'[]':
                distributer.distribution = []
            elif 'distribution' in settings:
                self.error = 'Invalid distribution: ' + settings['distribution']

            if 'minimum_amount' in settings and validator.validAmount(settings['minimum_amount']):
                distributer.minimum_amount = settings['minimum_amount']
            elif 'minimum_amount' in settings:
                self.error = 'minimum_amount must be a positive integer or equal to 0 (in Satoshis)'

            if 'threshold' in settings and validator.validAmount(settings['threshold']):
                distributer.minimum_amount = settings['threshold']
            elif 'threshold' in settings:
                self.error = 'threshold must be a positive integer or equal to 0 (in Satoshis)'

            if 'status' in settings and settings['status'] in ['Pending', 'Active', 'Disabled']:
                distributer.status = settings['status']
            elif 'status' in settings:
                self.error = 'status must be Pending, Active or Disabled'

            if 'visibility' in settings and settings['visibility'] in ['Public', 'Private']:
                distributer.visibility = settings['visibility']
            elif 'visibility' in settings:
                self.error = 'visibility must be Public or Private'

            if 'description' in settings and validator.validDescription(settings['description']):
                distributer.description = settings['description']
            elif 'description' in settings:
                self.error = 'Invalid description'

            if 'creator' in settings and validator.validCreator(settings['creator']):
                distributer.creator = settings['creator']
            elif 'creator' in settings:
                self.error = 'Invalid creator'

            if 'creator_email' in settings and validator.validEmail(settings['creator_email']):
                distributer.creator_email = settings['creator_email']
            elif 'creator_email' in settings:
                self.error = 'Invalid email address'

            if 'youtube' in settings and validator.validYoutubeID(settings['youtube']):
                distributer.youtube = settings['youtube']
            elif 'youtube' in settings:
                self.error = 'Invalid youtube video ID'

            if 'fee_percentage' in settings and validator.validPercentage(settings['fee_percentage']):
                distributer.fee_percentage = settings['fee_percentage']
            elif 'fee_percentage' in settings:
                self.error = 'fee_percentage must be greater than or equal to 0'

            if 'fee_address' in settings and (validator.validAddress(settings['fee_address']) or settings['fee_address'] == ''):
                distributer.fee_address = settings['fee_address']
            elif 'fee_address' in settings:
                self.error = 'Invalid fee_address'

            if 'maximum_transaction_fee' in settings and validator.validAmount(settings['maximum_transaction_fee']):
                distributer.maximum_transaction_fee = settings['maximum_transaction_fee']
            elif 'maximum_transaction_fee' in settings:
                self.error = 'maximum_transaction_fee must be a positive integer or equal to 0 (in Satoshis)'

            if 'address_type' in settings and settings['address_type'] in ['PrivKey', 'BIP44']:
                distributer.address_type = settings['address_type']
            elif 'address_type' in settings:
                self.error = 'address_type must be BIP44 or PrivKey'

            if 'wallet_index' in settings and validator.validAmount(settings['wallet_index']):
                distributer.wallet_index = settings['wallet_index']
            elif 'wallet_index' in settings:
                self.error = 'wallet_index must be greater than or equal to 0'

            if 'private_key' in settings and validator.validprivate_key(settings['private_key']):
                distributer.private_key = settings['private_key']
            elif 'private_key' in settings:
                self.error = 'Invalid private_key'

            if distributer.address_type == 'PrivKey' and distributer.private_key != '':
                distributer.address = bitcoin.privtoaddr(distributer.private_key)
            elif distributer.address_type == 'BIP44':
                if distributer.wallet_index == 0:
                    distributer.wallet_index = getNextIndex()
                distributer.address = datastore.get_service_address(datastore.Services.BlockDistribute, distributer.wallet_index)

            if not validator.validAddress(distributer.address):
                self.error = 'Unable to get address for distributer'

            if self.error == '':
                distributer.put()
                response['distributer'] = distributerToDict(distributer)
                response['success'] = 1
            else:
                response['error'] = self.error

        return response

    def deleteDistributer(self):
        response = {'success': 0}

        if self.error == '':
            distributer = datastore.Distributer.get_by_id(self.name, parent=datastore.distributers_key())

            if distributer:
                distributer.key.delete()
                response['success'] = 1
            else:
                response['error'] = 'No distributer with that name found.'

        return response

    def updateDistribution(self):
        response = {'success': 0}

        if self.error == '':
            distributer = datastore.Distributer.get_by_id(self.name, parent=datastore.distributers_key())

            if distributer:
                distribution = distributer.distribution
                if distributer.distributionSource == 'SIL':
                    SIL_data = BlockInputs.SIL(distributer.registrationAddress, distributer.registrationBlockHeight)
                    if 'success' in SIL_data and SIL_data['success'] == 1:
                        distribution = SIL_data['SIL']
                    else:
                        self.error = 'Unable to retrieve SIL'

                elif distributer.distributionSource in ['LBL', 'LRL', 'LSL']:
                    linker = BlockLinker.BlockLinker(distributer.registrationAddress,
                                                     distributer.registrationXPUB,
                                                     distributer.registrationBlockHeight)
                    linker_data = {}
                    if distributer.distributionSource == 'LBL':
                        linker_data = linker.LBL()
                    elif distributer.distributionSource == 'LRL':
                        linker_data = linker.LRL()
                    elif distributer.distributionSource == 'LSL':
                        linker_data = linker.LSL()

                    if 'success' in linker_data and linker_data['success'] == 1:
                        distribution = linker_data[distributer.distributionSource]
                    else:
                        self.error = 'Unable to retrieve ' + distributer.distributionSource

                if validator.validDistribution(distribution):
                    distributer.distribution = distribution
                    distributer.put()
                else:
                    self.error = 'Invalid distribution'

            else:
                response['error'] = 'No distributer with that name found.'

        if self.error == '':
            response['success'] = 1
            response['distribution'] = distributer.distribution
        else:
            response['error'] = self.error

        return response


class DoDistributing():
    def __init__(self, name=''):
        self.error = ''

        if name != '':
            distributer = datastore.Distributer.get_by_id(name, parent=datastore.distributers_key())
            if distributer:
                self.run(distributer)

        else:
            distributers_query = datastore.Distributer.query(datastore.Distributer.status == 'Active')
            distributers = distributers_query.fetch()

            for distributer in distributers:
                self.run(distributer)

    def run(self, distributer):
        success = False
        utxos_data = BlockData.utxos(distributer.address)
        if 'success' in utxos_data and utxos_data['success'] == 1:
            utxos = utxos_data['UTXOs']
        else:
            self.error = 'Unable to retrieve UTXOs'

        total_input_value = 0
        for utxo in utxos:
            total_input_value += utxo['value']

        if total_input_value >= distributer.threshold:
            logging.info(
                'Starting distribution of {0} Satoshis, minimum output value: {1}'.format(str(total_input_value),
                                                                                          str(distributer.minimum_amount)))

            if distributer.distributionSource in ['SIL', 'LBL', 'LRL', 'LSL']:
                distribution_data = Distributer(distributer.key.id()).updateDistribution()
                if 'success' in distribution_data and distribution_data['success'] == 1:
                    distribution = distribution_data['distribution']
                else:
                    self.error = 'Unable to update distribution'
            elif distributer.distributionSource == 'Custom':
                distribution = distributer.distribution

            if validator.validDistribution(distribution):
                logging.info("distribution: " + str(distribution))
                optimal_outputs = self.optimalOutputs(total_input_value, distribution, distributer)
                logging.info("optimal outputs: " + str(optimal_outputs))

                private_keys = {}
                if distributer.address_type == 'PrivKey':
                    private_keys = {distributer.address: distributer.private_key}

                elif distributer.address_type == 'BIP44':
                    private_keys = datastore.get_service_private_key(datastore.Services.BlockDistribute, distributer.wallet_index)

                if distributer.distributionSource == 'SIL' and distributer.address == distributer.registrationAddress:
                    self.error = 'Dark magic detected! Ponzi schemes are illegal!!'

                if len(optimal_outputs) > 0 and self.error == '':
                    total_output_value = 0
                    for tx_output in optimal_outputs:
                        total_output_value += tx_output['value']

                    total_fee = total_input_value - total_output_value
                    logging.info(
                        "Sending {0} Satoshis to {1} recipients with a total fee of {2}".format(str(total_input_value),
                                                                                                str(len(optimal_outputs)),
                                                                                                str(total_fee)))
                    tx = TxFactory.makeCustomTransaction(private_keys, utxos, optimal_outputs, total_fee)
                    if tx is not None:
                        TxFactory.sendTransaction(tx)
                else:
                    logging.error(self.error)

                if success:
                    logging.info("Success")
                else:
                    logging.error("Failed to send transaction")

            else:
                self.error = 'Invalid distribution: ' + str(distribution)

        return success

    def optimalOutputs(self, amount, distribution, distributer):
        optimal = []
        value_to_distribute = amount-distributer.maximum_transaction_fee

        if distributer.fee_percentage != 0 and distributer.fee_address != '':
            distributing_fee = int(value_to_distribute * (distributer.fee_percentage / 100.0))
            if distributing_fee < 10000:
                distributing_fee = 10000

            value_to_distribute -= distributing_fee
            optimal.append({'address': distributer.fee_address, 'value': distributing_fee})

        if value_to_distribute < distributer.minimum_amount:
            self.error = 'minimum_amount is lower than the amount available to distribute.'

        sorted_distribution = sorted(distribution, key=lambda x: x[1], reverse=True)

        for i in range(len(sorted_distribution)-1, -1, -1):
            tmp_total = 0
            for j in range(0, len(sorted_distribution)):
                tmp_total += sorted_distribution[j][1]

            share = sorted_distribution[i][1]/float(tmp_total)

            if share*value_to_distribute < distributer.minimum_amount:
                del sorted_distribution[i]
            else:
                optimal.append({'address': sorted_distribution[i][0], 'value': int(share*value_to_distribute)})

        return optimal