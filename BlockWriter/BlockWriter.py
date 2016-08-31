#!/usr/bin/env python
# -*- coding: utf-8 -*-
from validators import validators as validator
from BIP44 import BIP44 as BIP44
import BlockData.BlockData as BlockData

import datastore.datastore as datastore
import TxFactory.TxFactory as TxFactory

import time
import bitcoin
import logging
import datetime
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(60)


REQUIRED_CONFIRMATIONS = 3  # must be at least 3
TRANSACTION_FEE = 10000  # in Satoshis


def get_available_address_index():
    check_active_addresses()
    wallet_address_query = datastore.WalletAddress.query(datastore.WalletAddress.module == 'BlockWriter',
                                                         datastore.WalletAddress.status == 'Available',
                                                         ancestor=datastore.address_key()).order(datastore.WalletAddress.i)
    wallet_address = wallet_address_query.fetch(limit=1)

    if len(wallet_address) == 1:
        index = wallet_address[0].i
        wallet_address[0].status = 'InUse'
        wallet_address[0].put()
    else:
        wallet_address_query = datastore.WalletAddress.query(datastore.WalletAddress.module == 'BlockWriter',
                                                             ancestor=datastore.address_key()).order(-datastore.WalletAddress.i)
        wallet_address = wallet_address_query.fetch(limit=1)
        if len(wallet_address) == 1:
            index = wallet_address[0].i+1
        else:
            index = 1

        address = datastore.initializeWalletAddress('BlockWriter', index)
        logging.info("Initializing new wallet address for module BlockWriter: %i %s" % (index, address))

    return index


def check_active_addresses():
    writers_query = datastore.Writer.query(datastore.Writer.address_type == 'BIP44',
                                           datastore.Writer.status == 'Active',
                                           ancestor=datastore.writers_key()).order(datastore.Writer.wallet_index)
    writers = writers_query.fetch()

    for writer in writers:
        wallet_address = datastore.WalletAddress.get_by_id(u'BlockWriter_{0:d}'.format(writer.wallet_index),
                                                           parent=datastore.address_key())
        if wallet_address and wallet_address.status != 'InUse':
            logging.warning("Found active writer with address not InUse status! {0:d} {1:s}".format(wallet_address.i,
                                                                                                    wallet_address.address))
            wallet_address.status = 'InUse'
            wallet_address.put()


def writer_to_dict(writer):
    writer_dict = {'name': str(writer.key.id()),
                   'address': writer.address,
                   'outputs': writer.outputs,
                   'message': writer.message,
                   'amount': writer.amount,
                   'recommended_fee': writer.recommended_fee,
                   'maximum_transaction_fee': writer.maximum_transaction_fee,
                   'transaction_fee': writer.transaction_fee,
                   'total_amount': writer.total_amount,
                   'status': writer.status,
                   'visibility': writer.visibility}

    if writer.description:
        writer_dict['description'] = writer.description

    if writer.creator:
        writer_dict['creator'] = writer.creator

    if writer.creator_email:
        writer_dict['creator_email'] = writer.creator_email

    if writer.youtube:
        writer_dict['youtube'] = writer.youtube

    if writer.fee_address:
        writer_dict['fee_address'] = writer.fee_address

    if writer.fee_percentage:
        writer_dict['fee_percentage'] = writer.fee_percentage

    writer_dict['date'] = int(time.mktime(writer.date.timetuple()))

    return writer_dict


def get_writers():
    response = {'success': 0}
    writers = []

    writers_query = datastore.Writer.query(datastore.Writer.visibility == 'Public',
                                           datastore.Writer.status == 'Active',
                                           ancestor=datastore.writers_key()).order(-datastore.Writer.date)
    data = writers_query.fetch()
    for writer in data:
        writers.append(writer_to_dict(writer))

    response['writers'] = writers
    response['success'] = 1

    return response


def estimate_tx_size(outputs, message):
    dummy_outputs = []
    total_output_value = 0
    for output in outputs:
        dummy_outputs.append({'address': output[0], 'value': output[1]})
        total_output_value += output[1]

    dummy_inputs = [{u'address': u'1C7X7j98ge3mMkGLwpxaVfChuNoMMCERP7',
                     u'block_height': 421304,
                     u'confirmations': 1209,
                     u'output': u'6304cda7fcd3507dd4bcc5e41a249f8b11bb6a4d53f43b9b6a5da49352dd899c:1',
                     u'value': total_output_value + 15000}]

    private_keys = {'1C7X7j98ge3mMkGLwpxaVfChuNoMMCERP7': 'L2i45ALZv9Zpx2Mvmz27ASpMWzNY5877f6cLCkbcymXPYvbfs2cA'}
    fee = dummy_inputs[0]['value'] - total_output_value
    tx = TxFactory.makeCustomTransaction(private_keys, dummy_inputs, dummy_outputs, fee, message)

    tx_size = 0
    if tx is not None:
        tx_size = len(tx)/2

    return tx_size


class Writer():
    @ndb.transactional(xg=True)
    def __init__(self, name):
        self.error = ''

        try:
            self.name = int(name)
        except:
            self.name = name

        if isinstance(self.name, (str, unicode)) and len(name) > 0:
            logging.info('string name found')
        elif isinstance(self.name, (int, long)) and self.name > 0:
            logging.info('numeric name found')
        else:
            writer = datastore.Writer(parent=datastore.writers_key())
            writer.put()
            self.name = writer.key.id()

    def get(self):
        response = {'success': 0}
        if self.error == '':
            writer = datastore.Writer.get_by_id(self.name, parent=datastore.writers_key())

            if writer:
                response['writer'] = writer_to_dict(writer)
                response['success'] = 1
            else:
                response['error'] = 'No writer with that name found.'

        return response

    def save_writer(self, settings=None):
        if not settings:
            settings = {}
        response = {'success': 0}

        if self.error == '':
            parameters = datastore.Parameters.get_by_id('DefaultConfig')
            writer = datastore.Writer.get_by_id(self.name, parent=datastore.writers_key())

            if 'message' in settings and validator.valid_op_return(settings['message']):
                writer.message = settings['message']
            elif 'message' in settings:
                self.error = 'Invalid message'

            if 'outputs' in settings and validator.valid_outputs(eval(settings['outputs'])):
                writer.outputs = eval(settings['outputs'])

                total_output_value = 0
                for output in writer.outputs:
                    total_output_value += output[1]

                writer.amount = total_output_value
                writer.recommended_fee = int((estimate_tx_size(writer.outputs, writer.message)/1000.0) * parameters.optimal_fee_per_kb)

                if writer.recommended_fee > writer.maximum_transaction_fee:
                    writer.transaction_fee = writer.maximum_transaction_fee
                else:
                    writer.transaction_fee = writer.recommended_fee

                writer.total_amount = writer.amount + writer.transaction_fee

            elif 'outputs' in settings:
                self.error = 'Invalid outputs: ' + settings['outputs'] + ' (must be a list of address-value tuples)'

            if 'status' in settings and settings['status'] in ['Pending', 'Active', 'Disabled', 'Cooldown']:
                writer.status = settings['status']
            elif 'status' in settings:
                self.error = 'status must be Pending, Active or Disabled'

            if 'visibility' in settings and settings['visibility'] in ['Public', 'Private']:
                writer.visibility = settings['visibility']
            elif 'visibility' in settings:
                self.error = 'visibility must be Public or Private'

            if 'description' in settings and validator.valid_description(settings['description']):
                writer.description = settings['description']
            elif 'description' in settings:
                self.error = 'Invalid description'

            if 'creator' in settings and validator.valid_creator(settings['creator']):
                writer.creator = settings['creator']
            elif 'creator' in settings:
                self.error = 'Invalid creator'

            if 'creator_email' in settings and validator.valid_email(settings['creator_email']):
                writer.creator_email = settings['creator_email']
            elif 'creator_email' in settings:
                self.error = 'Invalid email address'

            if 'youtube' in settings and validator.valid_youtube_id(settings['youtube']):
                writer.youtube = settings['youtube']
            elif 'youtube' in settings:
                self.error = 'Invalid youtube video ID'

            if 'fee_percentage' in settings and validator.valid_percentage(settings['fee_percentage']):
                writer.fee_percentage = settings['fee_percentage']
            elif 'fee_percentage' in settings:
                self.error = 'fee_percentage must be greater than or equal to 0'

            if 'fee_address' in settings and (validator.valid_address(settings['fee_address']) or settings['fee_address'] == ''):
                writer.fee_address = settings['fee_address']
            elif 'fee_address' in settings:
                self.error = 'Invalid fee_address'

            if 'maximum_transaction_fee' in settings and validator.valid_amount(settings['maximum_transaction_fee']):
                writer.maximum_transaction_fee = settings['maximum_transaction_fee']
            elif 'maximum_transaction_fee' in settings:
                self.error = 'maximum_transaction_fee must be a positive integer or equal to 0 (in Satoshis)'

            if 'address_type' in settings and settings['address_type'] in ['PrivKey', 'BIP44']:
                writer.address_type = settings['address_type']
            elif 'address_type' in settings:
                self.error = 'address_type must be BIP44 or PrivKey'

            if 'wallet_index' in settings and validator.valid_amount(settings['wallet_index']):
                writer.wallet_index = settings['wallet_index']
            elif 'wallet_index' in settings:
                self.error = 'wallet_index must be greater than or equal to 0'

            if 'private_key' in settings and validator.valid_private_key(settings['private_key']):
                writer.private_key = settings['private_key']
            elif 'private_key' in settings:
                self.error = 'Invalid private_key'

            if writer.address_type == 'PrivKey' and writer.private_key != '':
                writer.address = bitcoin.privtoaddr(writer.private_key)

            elif writer.address_type == 'BIP44':
                if writer.wallet_index == 0:
                    writer.wallet_index = get_available_address_index()
                writer.address = datastore.get_service_address(datastore.Services.blockwriter, writer.wallet_index)

            if not validator.valid_address(writer.address):
                self.error = 'Unable to get address for writer'
            else:
                writer.extra_value_address = writer.address

            if not datastore.consistencyCheck('BlockWriter'):
                self.error = 'Unable to assign address.'

            if self.error == '':
                writer.put()
                response['writer'] = writer_to_dict(writer)
                response['success'] = 1

            else:
                response['error'] = self.error

        return response

    def delete_writer(self):
        response = {'success': 0}

        if self.error == '':
            writer = datastore.Writer.get_by_id(self.name, parent=datastore.writers_key())

            if writer:
                writer.key.delete()
                response['success'] = 1
            else:
                response['error'] = 'No writer with that name found.'

        return response


class DoWriting():
    def __init__(self, name=''):
        self.error = ''

        if name != '':
            writer = datastore.Writer.get_by_id(name, parent=datastore.writers_key())
            if writer:
                self.run(writer)

        else:
            writers_query = datastore.Writer.query(datastore.Writer.status == 'Active')
            writers = writers_query.fetch()
            if writers:
                logging.info("Found %i active writers:" % len(writers))
                for writer in writers:
                    logging.info("Writer address: %s Message: %s" % (writer.address, writer.message))

            for writer in writers:
                logging.info("Starting writer %s" % writer.address)
                self.run(writer)

    @staticmethod
    def run(writer):
        success = False

        if not validator.valid_op_return(writer.message):
            logging.error('Invalid OP_RETURN message: ' + writer.message)
            return None

        if not validator.valid_outputs(writer.outputs):
            logging.error('Invalid outputs: ' + str(writer.outputs))
            return None

        utxos_data = BlockData.utxos(writer.address)
        if 'success' in utxos_data and utxos_data['success'] == 1:
            utxos = utxos_data['UTXOs']
        else:
            logging.error('Unable to retrieve UTXOs for address ' + writer.address)
            return None

        total_input_value = 0
        for UTXO in utxos:
            total_input_value += UTXO['value']

        if total_input_value >= writer.total_amount:
            logging.info('Detected ' + str(total_input_value) + ' Satoshis on address ' + writer.address)
            logging.info('Starting OP_RETURN transaction with message: ' + writer.message)

            total_output_value = 0
            outputs = []
            for output in writer.outputs:
                total_output_value += output[1]
                outputs.append({'address': output[0], 'value': output[1]})

            #check for extra value
            if total_input_value > writer.total_amount:
                extra_value = total_input_value - writer.total_amount
                total_output_value += extra_value
                logging.info('Extra value detected: ' + str(extra_value) + ', sending it to ' + writer.extra_value_address)
                outputs.append({'address': writer.extra_value_address, 'value': extra_value})

            logging.info("outputs: " + str(outputs))
            transaction_fee = total_input_value - total_output_value
            logging.info('transaction fee: ' + str(transaction_fee))

            private_keys = {}
            if writer.address_type == 'PrivKey':
                private_keys = {writer.address: writer.private_key}
            elif writer.address_type == 'BIP44':
                private_keys = datastore.get_service_private_key(datastore.Services.blockwriter, writer.wallet_index)

            logging.info("Sending " + str(total_input_value) + ' Satoshis to ' + str(len(outputs)) + ' recipients with a total fee of ' + str(transaction_fee) + ' with OP_RETURN message: ' + writer.message)
            tx = TxFactory.makeCustomTransaction(private_keys, utxos, outputs, transaction_fee, writer.message)
            if tx is not None:
                success = TxFactory.sendTransaction(tx)

            if success:
                logging.info("Success")
                writer.status = 'Complete'
                writer.put()
                wallet_address = datastore.WalletAddress.get_by_id('BlockWriter_%i' % writer.wallet_index, parent=datastore.address_key())
                if wallet_address:
                    wallet_address.status = 'Cooldown'
                    wallet_address.cooldown_end = datetime.datetime.now() + datetime.timedelta(days=7)
                    wallet_address.put()
            else:
                logging.error("Failed to send transaction")

        return success