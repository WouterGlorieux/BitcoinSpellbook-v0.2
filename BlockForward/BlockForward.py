#!/usr/bin/env python
# -*- coding: utf-8 -*-


from validators import validators as validator
from BIP44 import BIP44 as BIP44
import BlockData.BlockData as BlockData
from BlockLinker import BlockLinker as BlockLinker

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
    forwarders_query = datastore.Forwarder.query(ancestor=datastore.forwarders_key()).order(
        -datastore.Forwarder.walletIndex)
    forwarders = forwarders_query.fetch()

    if len(forwarders) > 0:
        i = forwarders[0].walletIndex + 1
    else:
        i = 1

    return i


def forwarderToDict(forwarder):
    forwarder_dict = {'name': forwarder.key.id(),
                      'address': forwarder.address,
                      'description': forwarder.description,
                      'creator': forwarder.creator,
                      'creatorEmail': forwarder.creatorEmail,
                      'youtube': forwarder.youtube,
                      'status': forwarder.status,
                      'confirmAmount': forwarder.confirmAmount,
                      'feeAddress': forwarder.feeAddress,
                      'feePercent': forwarder.feePercent,
                      'minimumAmount': forwarder.minimumAmount,
                      'xpub': forwarder.xpub,
                      'visibility': forwarder.visibility,
                      'date': int(time.mktime(forwarder.date.timetuple()))}

    return forwarder_dict


def getForwarders():
    response = {'success': 0}
    forwarders = []

    forwarders_query = datastore.Forwarder.query(datastore.Forwarder.visibility == 'Public',
                                                 datastore.Forwarder.status == 'Active',
                                                 ancestor=datastore.forwarders_key()).order(-datastore.Forwarder.date)
    data = forwarders_query.fetch()
    for forwarder in data:
        forwarders.append(forwarderToDict(forwarder))

    response['forwarders'] = forwarders
    response['success'] = 1

    return response


class BlockForward():
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
            forwarder = datastore.Forwarder.get_by_id(self.name, parent=datastore.forwarders_key())

            if forwarder:
                response['forwarder'] = forwarderToDict(forwarder)
                response['success'] = 1
            else:
                response['error'] = 'No forwarder with that name found.'

        return response

    def checkAddress(self, address):
        response = {'success': 0}
        if self.error == '':
            forwarder = datastore.Forwarder.get_by_id(self.name, parent=datastore.forwarders_key())

            if forwarder:
                forwarding_relation = {'relation': 'unrelated address'}
                if forwarder.address == address:
                    forwarding_relation['relation'] = 'forwarding address'
                else:
                    linker = BlockLinker.BlockLinker(forwarder.address, forwarder.xpub)
                    LAL_data = linker.LAL()
                    if 'success' in LAL_data and LAL_data['success'] == 1:
                        LAL = LAL_data['LAL']

                    LBL_data = linker.LBL()
                    if 'success' in LBL_data and LBL_data['success'] == 1:
                        LBL = LBL_data['LBL']

                    for i in range(0, len(LAL)):
                        if LAL[i][0] == address:
                            forwarding_relation['relation'] = 'sending address'
                            forwarding_relation['sentTo'] = LAL[i][1]
                            forwarding_relation['balance'] = LBL[i][1]
                            forwarding_relation['share'] = LBL[i][2]
                            break

                        elif LAL[i][1] == address:
                            forwarding_relation['relation'] = 'receiving address'
                            forwarding_relation['sentFrom'] = LAL[i][0]
                            forwarding_relation['balance'] = LBL[i][1]
                            forwarding_relation['share'] = LBL[i][2]
                            break

                response[address] = forwarding_relation
                response['success'] = 1

            else:
                response['error'] = 'No forwarder with that name found.'

        return response

    def saveForwarder(self, settings=None):
        if not settings:
            settings = {}
        response = {'success': 0}

        if self.error == '':
            forwarder = datastore.Forwarder.get_or_insert(self.name, parent=datastore.forwarders_key())

            if 'xpub' in settings and validator.validXPUB(settings['xpub']):
                forwarder.xpub = settings['xpub']
            elif 'xpub' in settings:
                self.error = 'Invalid xpub key'

            if 'description' in settings and validator.validDescription(settings['description']):
                forwarder.description = settings['description']
            elif 'description' in settings:
                self.error = 'Invalid description'

            if 'creator' in settings and validator.validCreator(settings['creator']):
                forwarder.creator = settings['creator']
            elif 'creator' in settings:
                self.error = 'Invalid creator'

            if 'creatorEmail' in settings and validator.validEmail(settings['creatorEmail']):
                forwarder.creatorEmail = settings['creatorEmail']
            elif 'creatorEmail' in settings:
                self.error = 'Invalid email address'

            if 'minimumAmount' in settings and validator.validAmount(settings['minimumAmount']):
                forwarder.minimumAmount = settings['minimumAmount']
            elif 'minimumAmount' in settings:
                self.error = 'minimumAmount must be a positive integer or equal to 0 (in Satoshis)'

            if 'youtube' in settings and validator.validYoutubeID(settings['youtube']):
                forwarder.youtube = settings['youtube']
            elif 'youtube' in settings:
                self.error = 'Invalid youtube video ID'

            if 'visibility' in settings and settings['visibility'] in ['Public', 'Private']:
                forwarder.visibility = settings['visibility']
            elif 'visibility' in settings:
                self.error = 'visibility must be Public or Private'

            if 'status' in settings and settings['status'] in ['Pending', 'Active', 'Disabled']:
                forwarder.status = settings['status']
            elif 'status' in settings:
                self.error = 'status must be Pending, Active or Disabled'

            if 'feePercent' in settings and validator.validPercentage(settings['feePercent']):
                forwarder.feePercent = settings['feePercent']
            elif 'feePercent' in settings:
                self.error = 'FeePercent must be greater than or equal to 0'

            if 'feeAddress' in settings and (validator.validAddress(settings['feeAddress']) or settings['feeAddress'] == ''):
                forwarder.feeAddress = settings['feeAddress']
            elif 'feeAddress' in settings:
                self.error = 'Invalid feeAddress'

            if 'confirmAmount' in settings and validator.validAmount(settings['confirmAmount']):
                forwarder.confirmAmount = settings['confirmAmount']
            elif 'confirmAmount' in settings:
                self.error = 'confirmAmount must be greater than or equal to 0 (in Satoshis)'

            if 'addressType' in settings and settings['addressType'] in ['PrivKey', 'BIP44']:
                forwarder.addressType = settings['addressType']
            elif 'addressType' in settings:
                self.error = 'AddressType must be BIP44 or PrivKey'

            if 'walletIndex' in settings and validator.validAmount(settings['walletIndex']):
                forwarder.walletIndex = settings['walletIndex']
            elif 'walletIndex' in settings:
                self.error = 'walletIndex must be greater than or equal to 0'

            if 'privateKey' in settings and validator.validPrivateKey(settings['privateKey']):
                forwarder.privateKey = settings['privateKey']
            elif 'privateKey' in settings:
                self.error = 'Invalid privateKey'

            if forwarder.addressType == 'PrivKey' and forwarder.privateKey != '':
                forwarder.address = bitcoin.privtoaddr(forwarder.privateKey)
            elif forwarder.addressType == 'BIP44':
                if forwarder.walletIndex == 0:
                    forwarder.walletIndex = getNextIndex()
                forwarder.address = datastore.get_service_address(datastore.Services.BlockForward,
                                                                  forwarder.walletIndex)

            if not validator.validAddress(forwarder.address):
                self.error = 'Unable to get address for forwarder'

            if self.error == '':
                forwarder.put()
                response['forwarder'] = forwarderToDict(forwarder)
                response['success'] = 1

            else:
                response['error'] = self.error

        return response

    def deleteForwarder(self):
        response = {'success': 0}

        if self.error == '':
            forwarder = datastore.Forwarder.get_by_id(self.name, parent=datastore.forwarders_key())

            if forwarder:
                forwarder.key.delete()
                response['success'] = 1
            else:
                response['error'] = 'No forwarder with that name found.'

        return response


class DoForwarding():
    def __init__(self, name=''):
        self.error = ''

        if name != '':
            forwarder = datastore.Forwarder.get_by_id(name, parent=datastore.forwarders_key())
            if forwarder:
                self.run(forwarder)

        else:
            forwarders_query = datastore.Forwarder.query(datastore.Forwarder.status == 'Active')
            forwarders = forwarders_query.fetch()

            for forwarder in forwarders:
                self.run(forwarder)

    def run(self, forwarder):
        success = False
        utxos_data = BlockData.utxos(forwarder.address)
        if 'success' in utxos_data and utxos_data['success'] == 1:
            utxos = utxos_data['UTXOs']
        else:
            self.error = 'Unable to retrieve UTXOs'

        for utxo in utxos:
            to_addresses = []
            amounts = []

            prime_input_address_data = BlockData.primeInputAddress(utxo['output'].split(":")[0])
            if 'success' in prime_input_address_data and prime_input_address_data['success'] == 1:
                primeInputAddress = prime_input_address_data['PrimeInputAddress']
                if primeInputAddress != forwarder.address:

                    linker = BlockLinker.BlockLinker(forwarder.address, forwarder.xpub)
                    LAL_data = linker.LAL()
                    if 'success' in LAL_data and LAL_data['success'] == 1:
                        LAL = LAL_data['LAL']
                    else:
                        self.error = 'Unable to retrieve LAL for address ' + forwarder.address

                    for i in range(0, len(LAL)):
                        if LAL[i][0] == primeInputAddress:
                            to_addresses.append(LAL[i][1])
                            amounts.append(utxo['value'])

                    logging.info(forwarder.key.id() + ' : Starting forward from address ' + primeInputAddress
                                 + ', value: ' + str(amounts[0]) + ' Satoshis')

                    private_keys = {}
                    if forwarder.addressType == 'PrivKey':
                        private_keys = {forwarder.address: forwarder.privateKey}
                    elif forwarder.addressType == 'BIP44':
                        private_keys = datastore.get_service_private_key(datastore.Services.BlockForward,
                                                                         forwarder.walletIndex)

                    if len(amounts) > 0 and forwarder.minimumAmount > 0 and amounts[0] < forwarder.minimumAmount + TRANSACTION_FEE:
                        logging.warning(
                            "{0} is below minimum of {1} + transaction fee of {2}! returning btc to sender".format(
                                str(amounts[0]), str(forwarder.minimumAmount), str(TRANSACTION_FEE)))
                        to_addresses = [primeInputAddress]

                        #if there is enough btc, subtract network fee, otherwise log a warning
                        if amounts[0] > TRANSACTION_FEE:
                            #subtract network fee in satoshis from first amount
                            amounts[0] -= TRANSACTION_FEE

                            outputs = [{'address': to_addresses[0], 'value': amounts[0]}]
                            logging.info(
                                "Returning " + str(amounts[0]) + " to " + to_addresses[0] + " transaction fee: " + str(
                                    TRANSACTION_FEE))
                            tx = TxFactory.makeCustomTransaction(private_keys, [utxo], outputs, TRANSACTION_FEE)
                            if tx is not None:
                                success = TxFactory.sendTransaction(tx)
                        else:
                            logging.error(
                                "Insufficient amount to send, please remove UTXO manually as soon as possible.")

                    elif len(to_addresses) > 0:
                        if forwarder.feePercent > 0.0 and forwarder.feeAddress != '':
                            fee = int(amounts[0] * forwarder.feePercent / 100)
                            amounts = [amounts[0] - fee, fee]
                            to_addresses.append(forwarder.feeAddress)
                            logging.info("Forwarding Fee: " + str(amounts[1]) + " -> " + str(to_addresses[1]))

                        if forwarder.confirmAmount > 0:
                            amounts[0] -= forwarder.confirmAmount
                            amounts.append(forwarder.confirmAmount)
                            to_addresses.append(primeInputAddress)
                            logging.info("Origin: " + str(forwarder.confirmAmount) + " -> " + primeInputAddress)

                        #subtract transaction fee in satoshis from first amount
                        amounts[0] -= TRANSACTION_FEE

                        logging.info("Destination: " + str(amounts[0]) + " -> " + to_addresses[0])
                        logging.info("Transaction fee: " + str(TRANSACTION_FEE))

                        if amounts[0] > 0:
                            outputs = []
                            for i in range(0, len(amounts)):
                                outputs.append({'address': to_addresses[i], 'value': amounts[i]})

                            tx = TxFactory.makeCustomTransaction(private_keys, [utxo], outputs, TRANSACTION_FEE)
                            if tx is not None:
                                success = TxFactory.sendTransaction(tx)
                        else:
                            logging.error("Not enough balance left to send Transaction")

                        if success:
                            logging.info("Success")
                        else:
                            logging.error("Failed to send transaction")

                else:
                    logging.warning(
                        'Found UTXO originating from the forwarder address itself, please remove UTXO manually as soon as possible')

        return success