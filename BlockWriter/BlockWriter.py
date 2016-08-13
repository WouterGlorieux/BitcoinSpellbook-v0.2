#!/usr/bin/env python
# -*- coding: utf-8 -*-
from validators import validators as validator
from BIP44 import BIP44 as BIP44
import Blockchaindata.Blockchaindata as blockchaindata

import datastore.datastore as datastore
import TxFactory.TxFactory as TxFactory

import time
import bitcoin
import logging
import datetime
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(60)


REQUIRED_CONFIRMATIONS = 3 #must be at least 3
TRANSACTION_FEE = 10000 #in Satoshis

def getAvailableAddressIndex():
    checkActiveAddresses()
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

def checkActiveAddresses():
    writers_query = datastore.Writer.query(datastore.Writer.addressType == 'BIP44',
                                           datastore.Writer.status == 'Active',
                                           ancestor=datastore.writers_key()).order(datastore.Writer.walletIndex)
    writers = writers_query.fetch()

    for writer in writers:
        wallet_address = datastore.WalletAddress.get_by_id('BlockWriter_%i' % writer.walletIndex, parent=datastore.address_key())
        if wallet_address and wallet_address.status != 'InUse':
            logging.warning("Found active writer with address not InUse status! %i %s" % (wallet_address.i, wallet_address.address))
            wallet_address.status = 'InUse'
            wallet_address.put()




def writerToDict(writer):
    writerDict = {}

    writerDict['name'] = str(writer.key.id())
    writerDict['address'] = writer.address
    writerDict['outputs'] = writer.outputs
    writerDict['message'] = writer.message
    writerDict['amount'] = writer.amount
    writerDict['recommendedFee'] = writer.recommendedFee
    writerDict['maxTransactionFee'] = writer.maxTransactionFee
    writerDict['transactionFee'] = writer.transactionFee
    writerDict['totalAmount'] = writer.totalAmount

    writerDict['status'] = writer.status
    writerDict['visibility'] = writer.visibility

    if writer.description:
        writerDict['description'] = writer.description

    if writer.creator:
        writerDict['creator'] = writer.creator

    if writer.creatorEmail:
        writerDict['creatorEmail'] = writer.creatorEmail

    if writer.youtube:
        writerDict['youtube'] = writer.youtube

    if writer.feeAddress:
        writerDict['feeAddress'] = writer.feeAddress

    if writer.feePercent:
        writerDict['feePercent'] = writer.feePercent



    writerDict['date'] = int(time.mktime(writer.date.timetuple()))

    return writerDict


def getWriters():
    response = {'success': 0}
    writers = []

    writers_query = datastore.Writer.query(datastore.Writer.visibility == 'Public', datastore.Writer.status == 'Active', ancestor=datastore.writers_key()).order(-datastore.Writer.date)
    data = writers_query.fetch()
    for writer in data:
        writers.append(writerToDict(writer))

    response['writers'] = writers
    response['success'] = 1

    return response


def estimateTXsize(outputs, message):
    dummyOutputs = []
    totalOutputValue = 0
    for output in outputs:
        dummyOutputs.append({'address': output[0], 'value': output[1]})
        totalOutputValue += output[1]

    dummyInputs = [{u'address': u'1C7X7j98ge3mMkGLwpxaVfChuNoMMCERP7',
             u'block_height': 421304,
             u'confirmations': 1209,
             u'output': u'6304cda7fcd3507dd4bcc5e41a249f8b11bb6a4d53f43b9b6a5da49352dd899c:1',
             u'value': totalOutputValue + 15000}]

    privKeys = {'1C7X7j98ge3mMkGLwpxaVfChuNoMMCERP7': 'L2i45ALZv9Zpx2Mvmz27ASpMWzNY5877f6cLCkbcymXPYvbfs2cA'}
    fee = dummyInputs[0]['value'] - totalOutputValue
    tx = TxFactory.makeCustomTransaction(privKeys, dummyInputs, dummyOutputs, fee, message)

    txSize = 0
    if tx is not None:
        txSize = len(tx)/2

    return txSize

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
                response['writer'] = writerToDict(writer)
                response['success'] = 1
            else:
                response['error'] = 'No writer with that name found.'

        return response


    def saveWriter(self, settings={}):
        response = {'success': 0}

        if self.error == '':
            parameters = datastore.Parameters.get_by_id('DefaultConfig')
            writer = datastore.Writer.get_by_id(self.name, parent=datastore.writers_key())

            if 'message' in settings and validator.validOP_RETURN(settings['message']):
                writer.message = settings['message']
            elif 'message' in settings:
                self.error = 'Invalid message'


            if 'outputs' in settings and validator.validOutputs(eval(settings['outputs'])):
                writer.outputs = eval(settings['outputs'])

                totalOutputValue = 0
                for output in writer.outputs:
                    totalOutputValue += output[1]

                writer.amount = totalOutputValue
                writer.recommendedFee = int((estimateTXsize(writer.outputs, writer.message)/1000.0) * parameters.optimalFeePerKB)

                if writer.recommendedFee > writer.maxTransactionFee:
                    writer.transactionFee = writer.maxTransactionFee
                else:
                    writer.transactionFee = writer.recommendedFee

                writer.totalAmount = writer.amount + writer.transactionFee

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


            if 'description' in settings and validator.validDescription(settings['description']):
                writer.description = settings['description']
            elif 'description' in settings:
                self.error = 'Invalid description'

            if 'creator' in settings and validator.validCreator(settings['creator']):
                writer.creator = settings['creator']
            elif 'creator' in settings:
                self.error = 'Invalid creator'

            if 'creatorEmail' in settings and validator.validEmail(settings['creatorEmail']):
                writer.creatorEmail = settings['creatorEmail']
            elif 'creatorEmail' in settings:
                self.error = 'Invalid email address'

            if 'youtube' in settings and validator.validYoutube(settings['youtube']):
                writer.youtube = settings['youtube']
            elif 'youtube' in settings:
                self.error = 'Invalid youtube video ID'


            if 'feePercent' in settings and validator.validPercentage(settings['feePercent']):
                writer.feePercent = settings['feePercent']
            elif 'feePercent' in settings:
                self.error = 'FeePercent must be greater than or equal to 0'

            if 'feeAddress' in settings and (validator.validAddress(settings['feeAddress']) or settings['feeAddress'] == ''):
                writer.feeAddress = settings['feeAddress']
            elif 'feeAddress' in settings:
                self.error = 'Invalid feeAddress'


            if 'maxTransactionFee' in settings and validator.validAmount(settings['maxTransactionFee']):
                writer.maxTransactionFee = settings['maxTransactionFee']
            elif 'maxTransactionFee' in settings:
                self.error = 'maxTransactionFee must be a positive integer or equal to 0 (in Satoshis)'


            if 'addressType' in settings and settings['addressType'] in ['PrivKey', 'BIP44']:
                writer.addressType = settings['addressType']
            elif 'addressType' in settings:
                self.error = 'AddressType must be BIP44 or PrivKey'

            if 'walletIndex' in settings and validator.validAmount(settings['walletIndex']):
                writer.walletIndex = settings['walletIndex']
            elif 'walletIndex' in settings:
                self.error = 'walletIndex must be greater than or equal to 0'

            if 'privateKey' in settings and validator.validPrivateKey(settings['privateKey']):
                writer.privateKey = settings['privateKey']
            elif 'privateKey' in settings:
                self.error = 'Invalid privateKey'


            if writer.addressType == 'PrivKey' and writer.privateKey != '':
                writer.address = bitcoin.privtoaddr(writer.privateKey)
                writer.extraValueAddress = writer.address
            elif writer.addressType == 'BIP44':
                parameters = datastore.Parameters.get_by_id('DefaultConfig')
                if parameters and parameters.BlockWriter_walletseed != "":
                    if writer.walletIndex == 0:
                        writer.walletIndex = getAvailableAddressIndex()

                    xpub = BIP44.getXPUBKeys(parameters.BlockWriter_walletseed)[0]
                    writer.address = BIP44.getAddressFromXPUB(xpub, writer.walletIndex)
                    writer.extraValueAddress = writer.address
                else:
                    self.error = 'Unable to retrieve wallet seed'
            else:
                self.error = 'No private key supplied'

            if not datastore.consistencyCheck('BlockWriter'):
                self.error = 'Unable to assign address.'

            if self.error == '':
                writer.put()
                response['writer'] = writerToDict(writer)
                response['success'] = 1

            else:
                response['error'] = self.error

        return response

    def deleteWriter(self):
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

            for writer in writers:
                self.run(writer)


    def run(self, writer):
        success = False

        if not validator.validOP_RETURN(writer.message):
            logging.error('Invalid OP_RETURN message: ' + writer.message)
            return None

        if not validator.validOutputs(writer.outputs):
            logging.error('Invalid outputs: ' + str(writer.outputs))
            return None

        utxos_data = blockchaindata.utxos(writer.address)
        if 'success' in utxos_data and utxos_data['success'] == 1:
            UTXOs = utxos_data['UTXOs']
        else:
            logging.error('Unable to retrieve UTXOs for address ' + writer.address)
            return None

        totalInputValue = 0
        for UTXO in UTXOs:
            totalInputValue += UTXO['value']

        if totalInputValue >= writer.totalAmount:
            logging.info('Detected ' + str(totalInputValue) + ' Satoshis on address ' + writer.address)
            logging.info('Starting OP_RETURN transaction with message: ' + writer.message)

            totalOutputValue = 0
            outputs = []
            for output in writer.outputs:
                totalOutputValue += output[1]
                outputs.append({'address': output[0], 'value': output[1]})

            #check for extra value
            if totalInputValue > writer.totalAmount:
                extraValue = totalInputValue-writer.totalAmount
                totalOutputValue += extraValue
                logging.info('Extra value detected: '+ str(extraValue) + ', sending it to ' + writer.extraValueAddress)
                outputs.append({'address': writer.extraValueAddress, 'value': extraValue})

            logging.info("outputs: " + str(outputs))
            transactionFee = totalInputValue - totalOutputValue
            logging.info('transaction fee: ' + str(transactionFee))

            privKeys = {}
            if writer.addressType == 'PrivKey':
                privKeys = {writer.address: writer.privateKey}
            elif writer.addressType == 'BIP44':
                parameters = datastore.Parameters.get_by_id('DefaultConfig')
                if parameters and parameters.BlockWriter_walletseed not in ['', None]:
                    xprivKeys = BIP44.getXPRIVKeys(parameters.BlockWriter_walletseed, "", 1)
                    privKeys = BIP44.getPrivKey(xprivKeys[0], writer.walletIndex)

            logging.info("Sending " + str(totalInputValue) + ' Satoshis to ' + str(len(outputs)) + ' recipients with a total fee of ' + str(transactionFee) + ' with OP_RETURN message: ' + writer.message)
            tx = TxFactory.makeCustomTransaction(privKeys, UTXOs, outputs, transactionFee, writer.message)
            if tx is not None:
                success = TxFactory.sendTransaction(tx)

            if success:
                logging.info("Success")
                writer.status = 'Complete'
                writer.put()
                wallet_address = datastore.WalletAddress.get_by_id('BlockWriter_%i' % writer.walletIndex, parent=datastore.address_key())
                if wallet_address:
                    wallet_address.status = 'Cooldown'
                    wallet_address.cooldownEnd = datetime.datetime.now() + datetime.timedelta(days=7)
                    wallet_address.put()
            else:
                logging.error("Failed to send transaction")

        return success