#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging
import datetime
import re

import bitcoin
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(60)

from validators import validators as validator
import BlockData.BlockData as BlockData
import datastore.datastore as datastore
import TxFactory.TxFactory as TxFactory


REQUIRED_CONFIRMATIONS = 3  # must be at least 3
TRANSACTION_FEE = 10000  # in Satoshis


def check_active_addresses():
    writers_query = datastore.Writer.query(datastore.Writer.address_type == 'BIP44',
                                           datastore.Writer.status == 'Active',
                                           ancestor=datastore.writers_key()).order(datastore.Writer.wallet_index)
    writers = writers_query.fetch()

    for writer in writers:
        wallet_address = datastore.WalletAddress.get_by_id(u'BlockWriter_{0:d}'.format(writer.wallet_index),
                                                           parent=datastore.address_key())
        if wallet_address and wallet_address.status != 'InUse':
            logging.warning("active writer with address not InUse status! {0:d} {1:s}".format(wallet_address.i,
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
                   'visibility': writer.visibility,
                   'date': int(time.mktime(writer.date.timetuple()))}

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
    tx = TxFactory.make_custom_tx(private_keys, dummy_inputs, dummy_outputs, fee, message)

    tx_size = 0
    if tx is not None:
        tx_size = len(tx)/2

    return tx_size


class Writer():
    @ndb.transactional(xg=True)
    def __init__(self, name):
        self.error = ''
        self.writer = None
        self.name = ''

        if re.match('^[0-9]{16}$', name):
            self.name = int(name)
            self.writer = datastore.Writer.get_by_id(self.name, parent=datastore.writers_key())
            logging.info('Initialized writer by numeric name: %s' % self.name)
        elif re.match('^[0-9]{1,15}$', name):
            self.name = name
            self.writer = datastore.Writer.get_or_insert(self.name, parent=datastore.writers_key())
            index = int(name)
            wallet_address = datastore.initialize_wallet_address(datastore.Services.blockwriter_by_index, index)
            if self.writer.wallet_index != index and wallet_address:
                self.writer.wallet_index = index
                self.writer.address = wallet_address.address
                self.writer.id_type = 'index'
                self.writer.put()
            logging.info('Initialized writer by wallet index: %s' % self.name)
        elif name:
            self.name = name
            self.writer = datastore.Writer.get_or_insert(self.name, parent=datastore.writers_key())
            logging.info('Initialized writer by string name: %s' % self.name)
        elif name == '':
            self.writer = datastore.Writer(parent=datastore.writers_key())
            self.writer.put()
            self.name = self.writer.key.id()
            logging.info('Initialized new writer: %s' % self.name)

        if not self.writer:
            self.error = 'Unable to initialize writer'

    def get(self):
        response = {'success': 0}
        if self.writer:
            response['writer'] = writer_to_dict(self.writer)
            response['success'] = 1
        else:
            response['error'] = "No writer initialized"

        return response

    def save_writer(self, settings=None):
        if not settings:
            settings = {}
        response = {'success': 0}

        if self.writer:
            if 'message' in settings and validator.valid_op_return(settings['message']):
                self.writer.message = settings['message']
            elif 'message' in settings:
                self.error = 'Invalid message'

            if 'outputs' in settings and validator.valid_outputs(eval(settings['outputs'])):
                self.writer.outputs = eval(settings['outputs'])

                total_output_value = 0
                for output in self.writer.outputs:
                    total_output_value += output[1]

                self.writer.amount = total_output_value
                parameters = datastore.Parameters.get_by_id('DefaultConfig')
                self.writer.recommended_fee = int((estimate_tx_size(self.writer.outputs, self.writer.message)/1000.0) * parameters.optimal_fee_per_kb)

                if self.writer.recommended_fee > self.writer.maximum_transaction_fee:
                    self.writer.transaction_fee = self.writer.maximum_transaction_fee
                else:
                    self.writer.transaction_fee = self.writer.recommended_fee

                self.writer.total_amount = self.writer.amount + self.writer.transaction_fee

            elif 'outputs' in settings:
                self.error = 'Invalid outputs: ' + settings['outputs'] + ' (must be a list of address-value tuples)'

            if 'status' in settings and settings['status'] in ['Pending', 'Active', 'Disabled', 'Cooldown']:
                self.writer.status = settings['status']
            elif 'status' in settings:
                self.error = 'status must be Pending, Active or Disabled'

            if 'visibility' in settings and settings['visibility'] in ['Public', 'Private']:
                self.writer.visibility = settings['visibility']
            elif 'visibility' in settings:
                self.error = 'visibility must be Public or Private'

            if 'description' in settings and validator.valid_description(settings['description']):
                self.writer.description = settings['description']
            elif 'description' in settings:
                self.error = 'Invalid description'

            if 'creator' in settings and validator.valid_creator(settings['creator']):
                self.writer.creator = settings['creator']
            elif 'creator' in settings:
                self.error = 'Invalid creator'

            if 'creator_email' in settings and validator.valid_email(settings['creator_email']):
                self.writer.creator_email = settings['creator_email']
            elif 'creator_email' in settings:
                self.error = 'Invalid email address'

            if 'youtube' in settings and validator.valid_youtube_id(settings['youtube']):
                self.writer.youtube = settings['youtube']
            elif 'youtube' in settings:
                self.error = 'Invalid youtube video ID'

            if 'fee_percentage' in settings and validator.valid_percentage(settings['fee_percentage']):
                self.writer.fee_percentage = settings['fee_percentage']
            elif 'fee_percentage' in settings:
                self.error = 'fee_percentage must be greater than or equal to 0'

            if 'fee_address' in settings and (validator.valid_address(settings['fee_address']) or settings['fee_address'] == ''):
                self.writer.fee_address = settings['fee_address']
            elif 'fee_address' in settings:
                self.error = 'Invalid fee_address'

            if 'maximum_transaction_fee' in settings and validator.valid_amount(settings['maximum_transaction_fee']):
                self.writer.maximum_transaction_fee = settings['maximum_transaction_fee']
            elif 'maximum_transaction_fee' in settings:
                self.error = 'maximum_transaction_fee must be a positive integer or equal to 0 (in Satoshis)'

            if 'address_type' in settings and settings['address_type'] in ['PrivKey', 'BIP44']:
                self.writer.address_type = settings['address_type']
            elif 'address_type' in settings:
                self.error = 'address_type must be BIP44 or PrivKey'

            if 'wallet_index' in settings and validator.valid_amount(settings['wallet_index']) and self.writer.id_type == 'name':
                self.writer.wallet_index = settings['wallet_index']
            elif 'wallet_index' in settings:
                self.error = 'wallet_index must be greater than or equal to 0'

            if 'private_key' in settings and validator.valid_private_key(settings['private_key']):
                self.writer.private_key = settings['private_key']
            elif 'private_key' in settings:
                self.error = 'Invalid private_key'

            if self.writer.address_type == 'PrivKey' and self.writer.private_key != '':
                self.writer.address = bitcoin.privtoaddr(self.writer.private_key)
            elif self.writer.address_type == 'BIP44':
                if self.writer.wallet_index == 0 and self.writer.id_type == 'name':
                    self.writer.wallet_index = datastore.get_available_address_index(datastore.Services.blockwriter_by_name)
                if self.writer.id_type == 'name':
                    self.writer.address = datastore.get_service_address(datastore.Services.blockwriter_by_name, self.writer.wallet_index)

            if not validator.valid_address(self.writer.address):
                self.error = 'Unable to get address for writer'
            else:
                self.writer.extra_value_address = self.writer.address

            # if not datastore.consistency_check('BlockWriter'):
            #     self.error = 'Unable to assign address.'
        else:
            self.error = 'No writer initialized'

        if self.error == '':
            self.writer.put()
            response['writer'] = writer_to_dict(self.writer)
            response['success'] = 1
        else:
            response['error'] = self.error

        return response

    def delete_writer(self):
        response = {'success': 0}

        if self.writer:
            try:
                datastore.cooldown_address(self.writer.address)
                self.writer.key.delete()
            except Exception as ex:
                logging.warning(str(ex))
                self.error = 'Unable to delete writer'
        else:
            self.error = "No writer initialized"

        if self.error == '':
            response['success'] = 1
        else:
            response['error'] = self.error

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
            utxos = utxos_data['utxos']
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
                logging.info('Extra value detected: {0}, sending it to {1}'.format(str(extra_value),
                                                                                   str(writer.extra_value_address)))
                outputs.append({'address': writer.extra_value_address, 'value': extra_value})

            logging.info("outputs: " + str(outputs))
            transaction_fee = total_input_value - total_output_value
            logging.info('transaction fee: ' + str(transaction_fee))

            private_keys = {}
            if writer.address_type == 'PrivKey':
                private_keys = {writer.address: writer.private_key}
            elif writer.address_type == 'BIP44' and writer.id_type == 'name':
                private_keys = datastore.get_service_private_key(datastore.Services.blockwriter_by_name, writer.wallet_index)
            elif writer.address_type == 'BIP44' and writer.id_type == 'index':
                private_keys = datastore.get_service_private_key(datastore.Services.blockwriter_by_index, writer.wallet_index)

            logging.info(
                "Sending {0} Satoshis to {1} recipients with a total fee of {2} with OP_RETURN message: {3}".format(
                    str(total_input_value), str(len(outputs)), str(transaction_fee), str(writer.message)))
            tx = TxFactory.make_custom_tx(private_keys, utxos, outputs, transaction_fee, writer.message)
            if tx is not None:
                success = TxFactory.send_tx(tx)

            if success:
                logging.info("Success")
                writer.status = 'Complete'
                writer.put()
                wallet_address = datastore.WalletAddress.get_by_id('BlockWriter_%i' % writer.wallet_index,
                                                                   parent=datastore.address_key())
                if wallet_address:
                    wallet_address.status = 'Cooldown'
                    wallet_address.cooldown_end = datetime.datetime.now() + datetime.timedelta(days=7)
                    wallet_address.put()
            else:
                logging.error("Failed to send transaction")

        return success