#!/usr/bin/env python
# -*- coding: utf-8 -*-


from validators import validators as validator
from BIP44 import BIP44 as BIP44
import Blockchaindata.Blockchaindata as blockchaindata
from Blocklinker import Blocklinker as Blocklinker

import datastore.datastore as datastore
import TxFactory.TxFactory as TxFactory

import time
import bitcoin
import logging

from google.appengine.ext import ndb
from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(60)


REQUIRED_CONFIRMATIONS = 3 #must be at least 3
TRANSACTION_FEE = 10000 #in Satoshis

def getNextIndex():
    forwarders_query = datastore.Forwarder.query(ancestor=datastore.forwarders_key()).order(-datastore.Forwarder.walletIndex)
    forwarders = forwarders_query.fetch()

    if len(forwarders) > 0:
        i = forwarders[0].walletIndex + 1
    else:
        i = 1

    return i

def forwarderToDict(forwarder):
    forwarderDict = {}
    forwarderDict['name'] = forwarder.key.id()
    forwarderDict['address'] = forwarder.address
    forwarderDict['description'] = forwarder.description
    forwarderDict['creator'] = forwarder.creator
    forwarderDict['creatorEmail'] = forwarder.creatorEmail
    forwarderDict['youtube'] = forwarder.youtube
    forwarderDict['status'] = forwarder.status
    forwarderDict['confirmAmount'] = forwarder.confirmAmount
    forwarderDict['feeAddress'] = forwarder.feeAddress
    forwarderDict['feePercent'] = forwarder.feePercent
    forwarderDict['minimumAmount'] = forwarder.minimumAmount
    forwarderDict['xpub'] = forwarder.xpub
    forwarderDict['visibility'] = forwarder.visibility
    forwarderDict['date'] = int(time.mktime(forwarder.date.timetuple()))

    return forwarderDict


def getForwarders():
    response = {'success': 0}
    forwarders = []

    forwarders_query = datastore.Forwarder.query(datastore.Forwarder.visibility == 'Public', datastore.Forwarder.status == 'Active', ancestor=datastore.forwarders_key()).order(-datastore.Forwarder.date)
    data = forwarders_query.fetch()
    for forwarder in data:
        forwarders.append(forwarderToDict(forwarder))

    response['forwarders'] = forwarders
    response['success'] = 1

    return response

class HDForwarder():
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
                forwardingRelation = {'relation': 'unrelated address'}
                if forwarder.address == address:
                    forwardingRelation['relation'] = 'forwarding address'
                else:
                    linker = Blocklinker.Blocklinker(forwarder.address, forwarder.xpub)
                    LAL_data = linker.LAL()
                    if 'success' in LAL_data and LAL_data['success'] == 1:
                        LAL = LAL_data['LAL']

                    LBL_data = linker.LBL()
                    if 'success' in LBL_data and LBL_data['success'] == 1:
                        LBL = LBL_data['LBL']

                    for i in range(0, len(LAL)):
                        if LAL[i][0] == address:
                            forwardingRelation['relation'] = 'sending address'
                            forwardingRelation['sentTo'] = LAL[i][1]
                            forwardingRelation['balance'] = LBL[i][1]
                            forwardingRelation['share'] = LBL[i][2]
                            break

                        elif LAL[i][1] == address:
                            forwardingRelation['relation'] = 'receiving address'
                            forwardingRelation['sentFrom'] = LAL[i][0]
                            forwardingRelation['balance'] = LBL[i][1]
                            forwardingRelation['share'] = LBL[i][2]
                            break

                response[address] = forwardingRelation
                response['success'] = 1

            else:
                response['error'] = 'No forwarder with that name found.'

        return response



    def saveForwarder(self, settings={}):
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

            if 'youtube' in settings and validator.validYoutube(settings['youtube']):
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
                parameters = datastore.Parameters.get_by_id('DefaultConfig')
                if parameters and parameters.HDForwarder_walletseed != "":
                    if forwarder.walletIndex == 0:
                        forwarder.walletIndex = getNextIndex()

                    xpub = BIP44.getXPUBKeys(parameters.HDForwarder_walletseed)[0]
                    forwarder.address = BIP44.getAddressFromXPUB(xpub, forwarder.walletIndex)
                else:
                    self.error = 'Unable to retrieve wallet seed'
            else:
                self.error = 'No private key supplied'


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
        utxos_data = blockchaindata.utxos(forwarder.address)
        if 'success' in utxos_data and utxos_data['success'] == 1:
            UTXOs = utxos_data['UTXOs']
        else:
            self.error = 'Unable to retrieve UTXOs'

        linker = Blocklinker.Blocklinker(forwarder.address, forwarder.xpub)
        LAL_data = linker.LAL()
        if 'success' in LAL_data and LAL_data['success'] == 1:
            LAL = LAL_data['LAL']
        else:
            self.error = 'Unable to retrieve LAL for address ' + forwarder.address


        for UTXO in UTXOs:
            to_addresses = []
            amounts = []

            primeInputAddress_data = blockchaindata.primeInputAddress(UTXO['output'].split(":")[0])
            if 'success' in primeInputAddress_data and primeInputAddress_data['success'] == 1:
                primeInputAddress = primeInputAddress_data['PrimeInputAddress']


                for i in range(0, len(LAL)):
                    if LAL[i][0] == primeInputAddress:
                        to_addresses.append(LAL[i][1])
                        amounts.append(UTXO['value'])

                logging.info(forwarder.key.id() + ' : Starting forward from address '+ primeInputAddress + ', value: ' + str(amounts[0]) + ' Satoshis')


                privKeys = {}
                if forwarder.addressType == 'PrivKey':
                    privKeys = {forwarder.address: forwarder.privateKey}
                elif forwarder.addressType == 'BIP44':
                    parameters = datastore.Parameters.get_or_insert('DefaultConfig')
                    if parameters and parameters.HDForwarder_walletseed != '' and parameters.HDForwarder_walletseed != None:
                        xprivKeys = BIP44.getXPRIVKeys(parameters.HDForwarder_walletseed, "", 1)
                        privKeys = BIP44.getPrivKey(xprivKeys[0], forwarder.walletIndex)




                if len(amounts) > 0 and forwarder.minimumAmount > 0 and amounts[0] < forwarder.minimumAmount+TRANSACTION_FEE:
                    logging.warning(str(amounts[0]) + " is below minimum of " + str(forwarder.minimumAmount) + " + transaction fee of " + str(TRANSACTION_FEE) + "! returning btc to sender")
                    to_addresses = [primeInputAddress]

                    #if there is enough btc, subtract network fee, otherwise log a warning
                    if amounts[0] > TRANSACTION_FEE:
                        #subtract network fee in satoshis from first amount
                        amounts[0] = amounts[0] - TRANSACTION_FEE

                        outputs = []
                        outputs.append({'address': to_addresses[0], 'value': amounts[0]})
                        logging.info("Returning " + str(amounts[0]) + " to " + to_addresses[0] + " transaction fee: " + str(TRANSACTION_FEE))
                        tx = TxFactory.makeCustomTransaction(privKeys, [UTXO], outputs, TRANSACTION_FEE)
                        if tx != None:
                           success = TxFactory.sendTransaction(tx)

                    else:
                        logging.error("Insufficient amount to send, please remove UTXO manually as soon as possible.")



                elif len(to_addresses) > 0:
                    if forwarder.feePercent > 0.0 and forwarder.feeAddress != '':
                        fee = int(amounts[0] * forwarder.feePercent/100)
                        amounts = [amounts[0] - fee, fee]
                        to_addresses.append(forwarder.feeAddress)
                        logging.info("Forwarding Fee: " + str(amounts[1]) + " -> " + str(to_addresses[1]))

                    if forwarder.confirmAmount > 0:
                        amounts[0] -= forwarder.confirmAmount
                        amounts.append(forwarder.confirmAmount)
                        to_addresses.append(primeInputAddress)
                        logging.info("Origin: " + str(forwarder.confirmAmount) + " -> " + primeInputAddress)


                    #subtract transaction fee in satoshis from first amount
                    amounts[0] = amounts[0] - TRANSACTION_FEE

                    logging.info("Destination: " + str(amounts[0]) + " -> " + to_addresses[0])
                    logging.info("Transaction fee: " + str(TRANSACTION_FEE))

                    if amounts[0] > 0:
                        outputs = []
                        for i in range(0, len(amounts)):
                            outputs.append({'address': to_addresses[i], 'value': amounts[i]})

                        tx = TxFactory.makeCustomTransaction(privKeys, [UTXO], outputs, TRANSACTION_FEE)
                        if tx != None:
                           success = TxFactory.sendTransaction(tx)
                    else:
                        logging.error("Not enough balance left to send Transaction")


                    if success == True:
                        logging.info("Success")
                    else:
                        logging.error("Failed to send transaction")

        return success
