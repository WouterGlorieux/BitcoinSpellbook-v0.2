#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import time
import logging

from google.appengine.ext import ndb
from google.appengine.api import urlfetch

import bitcoin
from validators import validators as validator
import BlockData.BlockData as BlockData
from BlockLinker import BlockLinker as BlockLinker
import datastore.datastore as datastore
import TxFactory.TxFactory as TxFactory


urlfetch.set_default_fetch_deadline(60)

REQUIRED_CONFIRMATIONS = 3  # must be at least 3
TRANSACTION_FEE = 10000  # in Satoshis


def get_next_index():
    forwarders_query = datastore.Forwarder.query(ancestor=datastore.forwarders_key()).order(
        -datastore.Forwarder.wallet_index)
    forwarders = forwarders_query.fetch()

    if len(forwarders) > 0:
        i = forwarders[0].wallet_index + 1
    else:
        i = 1

    return i


def forwarder_to_dict(forwarder):
    forwarder_dict = {'name': forwarder.key.id(),
                      'address': forwarder.address,
                      'description': forwarder.description,
                      'creator': forwarder.creator,
                      'creator_email': forwarder.creator_email,
                      'youtube': forwarder.youtube,
                      'status': forwarder.status,
                      'confirm_amount': forwarder.confirm_amount,
                      'fee_address': forwarder.fee_address,
                      'fee_percentage': forwarder.fee_percentage,
                      'minimum_amount': forwarder.minimum_amount,
                      'xpub': forwarder.xpub,
                      'visibility': forwarder.visibility,
                      'date': int(time.mktime(forwarder.date.timetuple()))}

    return forwarder_dict


def get_forwarders():
    response = {'success': 0}
    forwarders = []

    forwarders_query = datastore.Forwarder.query(datastore.Forwarder.visibility == 'Public',
                                                 datastore.Forwarder.status == 'Active',
                                                 ancestor=datastore.forwarders_key()).order(-datastore.Forwarder.date)
    data = forwarders_query.fetch()
    for forwarder in data:
        forwarders.append(forwarder_to_dict(forwarder))

    response['forwarders'] = forwarders
    response['success'] = 1

    return response


class BlockForward():
    @ndb.transactional(xg=True)
    def __init__(self, name):
        self.error = ''
        self.forwarder = None
        self.name = ''

        if re.match('^[0-9]{16}$', name):
            self.name = int(name)
            self.forwarder = datastore.Forwarder.get_by_id(self.name, parent=datastore.forwarders_key())
            logging.info('Initialized forwarder by numeric name: %s' % self.name)
        elif re.match('^[0-9]{1,15}$', name):
            self.name = name
            self.forwarder = datastore.Forwarder.get_or_insert(self.name, parent=datastore.forwarders_key())
            index = int(name)
            wallet_address = datastore.initialize_wallet_address(datastore.Services.blockforward_by_index, index)
            if self.forwarder.wallet_index != index and wallet_address:
                self.forwarder.wallet_index = index
                self.forwarder.address = wallet_address.address
                self.forwarder.id_type = 'index'
                self.forwarder.put()
            logging.info('Initialized forwarder by wallet index: %s' % self.name)
        elif name:
            self.name = name
            self.forwarder = datastore.Forwarder.get_or_insert(self.name, parent=datastore.forwarders_key())
            logging.info('Initialized forwarder by string name: %s' % self.name)
        elif name == '':
            self.forwarder = datastore.Forwarder(parent=datastore.forwarders_key())
            self.forwarder.put()
            self.name = self.forwarder.key.id()
            logging.info('Initialized new forwarder: %s' % self.name)

        if not self.forwarder:
            self.error = 'Unable to initialize forwarder'

    def get(self):
        response = {'success': 0}
        if self.forwarder:
            response['forwarder'] = forwarder_to_dict(self.forwarder)
            response['success'] = 1
        else:
            response['error'] = 'No forwarder initialized.'

        return response

    def check_address(self, address):
        response = {'success': 0}

        if self.forwarder:
            forwarding_relation = {'relation': 'unrelated address'}
            lal = []
            lbl = []
            if self.forwarder.address == address:
                forwarding_relation['relation'] = 'forwarding address'
            else:
                linker = BlockLinker.BlockLinker(self.forwarder.address, self.forwarder.xpub)
                lal_data = linker.get_lal()
                if 'success' in lal_data and lal_data['success'] == 1:
                    lal = lal_data['LAL']

                lbl_data = linker.get_lbl()
                if 'success' in lbl_data and lbl_data['success'] == 1:
                    lbl = lbl_data['LBL']

                for i in range(0, len(lal)):
                    if lal[i][0] == address:
                        forwarding_relation['relation'] = 'sending address'
                        forwarding_relation['sentTo'] = lal[i][1]
                        forwarding_relation['balance'] = lbl[i][1]
                        forwarding_relation['share'] = lbl[i][2]
                        break

                    elif lal[i][1] == address:
                        forwarding_relation['relation'] = 'receiving address'
                        forwarding_relation['sentFrom'] = lal[i][0]
                        forwarding_relation['balance'] = lbl[i][1]
                        forwarding_relation['share'] = lbl[i][2]
                        break

            response[address] = forwarding_relation
            response['success'] = 1

        else:
            response['error'] = 'No forwarder initialized.'

        return response

    def save_forwarder(self, settings=None):
        if not settings:
            settings = {}
        response = {'success': 0}

        if self.forwarder:

            if 'xpub' in settings and validator.valid_xpub(settings['xpub']):
                self.forwarder.xpub = settings['xpub']
            elif 'xpub' in settings:
                self.error = 'Invalid xpub key'

            if 'description' in settings and validator.valid_description(settings['description']):
                self.forwarder.description = settings['description']
            elif 'description' in settings:
                self.error = 'Invalid description'

            if 'creator' in settings and validator.valid_creator(settings['creator']):
                self.forwarder.creator = settings['creator']
            elif 'creator' in settings:
                self.error = 'Invalid creator'

            if 'creator_email' in settings and validator.valid_email(settings['creator_email']):
                self.forwarder.creator_email = settings['creator_email']
            elif 'creator_email' in settings:
                self.error = 'Invalid email address'

            if 'minimum_amount' in settings and validator.valid_amount(settings['minimum_amount']):
                self.forwarder.minimum_amount = settings['minimum_amount']
            elif 'minimum_amount' in settings:
                self.error = 'minimum_amount must be a positive integer or equal to 0 (in Satoshis)'

            if 'youtube' in settings and validator.valid_youtube_id(settings['youtube']):
                self.forwarder.youtube = settings['youtube']
            elif 'youtube' in settings:
                self.error = 'Invalid youtube video ID'

            if 'visibility' in settings and settings['visibility'] in ['Public', 'Private']:
                self.forwarder.visibility = settings['visibility']
            elif 'visibility' in settings:
                self.error = 'visibility must be Public or Private'

            if 'status' in settings and settings['status'] in ['Pending', 'Active', 'Disabled']:
                self.forwarder.status = settings['status']
            elif 'status' in settings:
                self.error = 'status must be Pending, Active or Disabled'

            if 'fee_percentage' in settings and validator.valid_percentage(settings['fee_percentage']):
                self.forwarder.fee_percentage = settings['fee_percentage']
            elif 'fee_percentage' in settings:
                self.error = 'fee_percentage must be greater than or equal to 0'

            if 'fee_address' in settings and (validator.valid_address(settings['fee_address']) or settings['fee_address'] == ''):
                self.forwarder.fee_address = settings['fee_address']
            elif 'fee_address' in settings:
                self.error = 'Invalid fee_address'

            if 'confirm_amount' in settings and validator.valid_amount(settings['confirm_amount']):
                self.forwarder.confirm_amount = settings['confirm_amount']
            elif 'confirm_amount' in settings:
                self.error = 'confirm_amount must be greater than or equal to 0 (in Satoshis)'

            if 'address_type' in settings and settings['address_type'] in ['PrivKey', 'BIP44']:
                self.forwarder.address_type = settings['address_type']
            elif 'address_type' in settings:
                self.error = 'address_type must be BIP44 or PrivKey'

            if 'wallet_index' in settings and validator.valid_amount(settings['wallet_index']) and self.forwarder.id_type == 'name':
                self.forwarder.wallet_index = settings['wallet_index']
            elif 'wallet_index' in settings:
                self.error = 'wallet_index must be greater than or equal to 0'

            if 'private_key' in settings and validator.valid_private_key(settings['private_key']):
                self.forwarder.private_key = settings['private_key']
            elif 'private_key' in settings:
                self.error = 'Invalid private_key'

            if self.forwarder.address_type == 'PrivKey' and self.forwarder.private_key != '':
                self.forwarder.address = bitcoin.privtoaddr(self.forwarder.private_key)
            elif self.forwarder.address_type == 'BIP44':
                if self.forwarder.wallet_index == 0 and self.forwarder.id_type == 'name':
                    self.forwarder.wallet_index = datastore.get_available_address_index(datastore.Services.blockforward_by_name)
                if self.forwarder.id_type == 'name':
                    self.forwarder.address = datastore.get_service_address(datastore.Services.blockforward_by_name,
                                                                           self.forwarder.wallet_index)

            if not validator.valid_address(self.forwarder.address):
                self.error = 'Unable to get address for forwarder'

            if self.error == '':
                self.forwarder.put()
                response['forwarder'] = forwarder_to_dict(self.forwarder)
                response['success'] = 1

            else:
                response['error'] = self.error
        else:
            response['error'] = 'No forwarder initialized'

        return response

    def delete_forwarder(self):
        response = {'success': 0}

        if self.forwarder:
            try:
                datastore.cooldown_address(self.forwarder.address)
                self.forwarder.key.delete()
                response['success'] = 1
            except Exception as ex:
                logging.warning(str(ex))
                self.error = 'Unable to delete forwarder'
        else:
            response['error'] = 'No forwarder initialized.'

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
        utxos = []
        utxos_data = BlockData.utxos(forwarder.address)
        if 'success' in utxos_data and utxos_data['success'] == 1:
            utxos = utxos_data['utxos']
        else:
            self.error = 'Unable to retrieve UTXOs'

        for utxo in utxos:
            to_addresses = []
            amounts = []

            prime_input_address_data = BlockData.prime_input_address(utxo['output'].split(":")[0])
            if 'success' in prime_input_address_data and prime_input_address_data['success'] == 1:
                prime_input_address = prime_input_address_data['prime_input_address']
                if prime_input_address != forwarder.address:

                    linker = BlockLinker.BlockLinker(forwarder.address, forwarder.xpub)
                    lal_data = linker.get_lal()
                    if 'success' in lal_data and lal_data['success'] == 1:
                        lal = lal_data['LAL']
                    else:
                        self.error = 'Unable to retrieve LAL for address ' + forwarder.address

                    for i in range(0, len(lal)):
                        if lal[i][0] == prime_input_address:
                            to_addresses.append(lal[i][1])
                            amounts.append(utxo['value'])

                    logging.info(forwarder.key.id() + ' : Starting forward from address ' + prime_input_address
                                 + ', value: ' + str(amounts[0]) + ' Satoshis')

                    private_keys = {}
                    if forwarder.address_type == 'PrivKey':
                        private_keys = {forwarder.address: forwarder.private_key}
                    elif forwarder.address_type == 'BIP44' and forwarder.id_type == 'name':
                        private_keys = datastore.get_service_private_key(datastore.Services.blockforward_by_name, forwarder.wallet_index)
                    elif forwarder.address_type == 'BIP44' and forwarder.id_type == 'index':
                        private_keys = datastore.get_service_private_key(datastore.Services.blockforward_by_index, forwarder.wallet_index)

                    if len(amounts) > 0 and forwarder.minimum_amount > 0 and amounts[0] < forwarder.minimum_amount + TRANSACTION_FEE:
                        logging.warning(
                            "{0} is below minimum of {1} + transaction fee of {2}! returning btc to sender".format(
                                str(amounts[0]), str(forwarder.minimum_amount), str(TRANSACTION_FEE)))
                        to_addresses = [prime_input_address]

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
                        if forwarder.fee_percentage > 0.0 and forwarder.fee_address != '':
                            fee = int(amounts[0] * forwarder.fee_percentage / 100)
                            amounts = [amounts[0] - fee, fee]
                            to_addresses.append(forwarder.fee_address)
                            logging.info("Forwarding Fee: " + str(amounts[1]) + " -> " + str(to_addresses[1]))

                        if forwarder.confirm_amount > 0:
                            amounts[0] -= forwarder.confirm_amount
                            amounts.append(forwarder.confirm_amount)
                            to_addresses.append(prime_input_address)
                            logging.info("Origin: " + str(forwarder.confirm_amount) + " -> " + prime_input_address)

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