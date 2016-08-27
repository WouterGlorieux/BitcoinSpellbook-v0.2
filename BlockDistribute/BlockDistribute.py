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


REQUIRED_CONFIRMATIONS = 3 #must be at least 3
TRANSACTION_FEE = 10000 #in Satoshis

def getNextIndex():
    distributers_query = datastore.Distributer.query(ancestor=datastore.distributers_key()).order(-datastore.Distributer.walletIndex)
    distributers = distributers_query.fetch()

    if len(distributers) > 0:
        i = distributers[0].walletIndex + 1
    else:
        i = 1

    return i

def distributerToDict(distributer):
    distributerDict = {}

    distributerDict['name'] = distributer.key.id()
    distributerDict['address'] = distributer.address

    distributerDict['distributionSource'] = distributer.distributionSource
    distributerDict['registrationAddress'] = distributer.registrationAddress
    distributerDict['registrationBlockHeight'] = distributer.registrationBlockHeight
    distributerDict['registrationXPUB'] = distributer.registrationXPUB
    distributerDict['distribution'] = distributer.distribution

    distributerDict['minimumAmount'] = distributer.minimumAmount
    distributerDict['threshold'] = distributer.threshold

    distributerDict['status'] = distributer.status
    distributerDict['visibility'] = distributer.visibility

    distributerDict['description'] = distributer.description
    distributerDict['creator'] = distributer.creator
    distributerDict['creatorEmail'] = distributer.creatorEmail
    distributerDict['youtube'] = distributer.youtube

    distributerDict['feeAddress'] = distributer.feeAddress
    distributerDict['feePercent'] = distributer.feePercent

    distributerDict['maxTransactionFee'] = distributer.maxTransactionFee

    distributerDict['date'] = int(time.mktime(distributer.date.timetuple()))

    return distributerDict


def getDistributers():
    response = {'success': 0}
    distributers = []

    distributers_query = datastore.Distributer.query(datastore.Distributer.visibility == 'Public', datastore.Distributer.status == 'Active', ancestor=datastore.distributers_key()).order(-datastore.Distributer.date)
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
                distributingRelation = {'relation': 'unrelated address'}
                if distributer.address == address:
                    distributingRelation['relation'] = 'distributing address'
                else:
                    share = 0
                    for recipient in distributer.distribution:
                        if recipient[0] == address:
                            distributingRelation['relation'] = 'receiving address'
                            if len(recipient) >= 3:
                                share += recipient[2]

                    if distributingRelation['relation'] == 'receiving address':
                        distributingRelation['share'] = share

                    if distributer.registrationAddress == address and distributer.distributionSource in ['SIL', 'LBL', 'LRL', 'LSL']:
                        distributingRelation['relation'] = 'registration address'


                response[address] = distributingRelation
                response['success'] = 1

            else:
                response['error'] = 'No distributer with that name found.'

        return response



    def saveDistributer(self, settings={}):
        response = {'success': 0}

        if self.error == '':
            distributer = datastore.Distributer.get_or_insert(self.name, parent=datastore.distributers_key())

            if 'distributionSource' in settings and settings['distributionSource'] in ['LBL', 'LRL', 'LSL', 'SIL', 'Custom']:
                distributer.distributionSource = settings['distributionSource']
            elif 'distributionSource' in settings:
                self.error = 'Invalid distributionSource'


            if 'registrationAddress' in settings and (validator.validAddress(settings['registrationAddress']) or settings['registrationAddress'] == ''):
                distributer.registrationAddress = settings['registrationAddress']
            elif 'registrationAddress' in settings:
                self.error = 'Invalid registrationAddress'

            if 'registrationXPUB' in settings and (validator.validXPUB(settings['registrationXPUB']) or settings['registrationXPUB'] == ''):
                distributer.registrationXPUB = settings['registrationXPUB']
            elif 'registrationXPUB' in settings:
                self.error = 'Invalid registrationXPUB'


            if 'registrationBlockHeight' in settings and (validator.validBlockHeight(settings['registrationBlockHeight'])):
                distributer.registrationBlockHeight = settings['registrationBlockHeight']
            elif 'registrationBlockHeight' in settings:
                self.error = 'Invalid registrationBlockHeight: ' + str(settings['registrationBlockHeight'])


            if 'distribution' in settings and validator.validDistribution(eval(settings['distribution'])):
                distributer.distribution = eval(settings['distribution'])
            elif 'distribution' in settings and settings['distribution'] == u'[]':
                distributer.distribution = []
            elif 'distribution' in settings:
                self.error = 'Invalid distribution: ' + settings['distribution']


            if 'minimumAmount' in settings and validator.validAmount(settings['minimumAmount']):
                distributer.minimumAmount = settings['minimumAmount']
            elif 'minimumAmount' in settings:
                self.error = 'minimumAmount must be a positive integer or equal to 0 (in Satoshis)'

            if 'threshold' in settings and validator.validAmount(settings['threshold']):
                distributer.minimumAmount = settings['threshold']
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

            if 'creatorEmail' in settings and validator.validEmail(settings['creatorEmail']):
                distributer.creatorEmail = settings['creatorEmail']
            elif 'creatorEmail' in settings:
                self.error = 'Invalid email address'

            if 'youtube' in settings and validator.validYoutube(settings['youtube']):
                distributer.youtube = settings['youtube']
            elif 'youtube' in settings:
                self.error = 'Invalid youtube video ID'


            if 'feePercent' in settings and validator.validPercentage(settings['feePercent']):
                distributer.feePercent = settings['feePercent']
            elif 'feePercent' in settings:
                self.error = 'FeePercent must be greater than or equal to 0'

            if 'feeAddress' in settings and (validator.validAddress(settings['feeAddress']) or settings['feeAddress'] == ''):
                distributer.feeAddress = settings['feeAddress']
            elif 'feeAddress' in settings:
                self.error = 'Invalid feeAddress'


            if 'maxTransactionFee' in settings and validator.validAmount(settings['maxTransactionFee']):
                distributer.maxTransactionFee = settings['maxTransactionFee']
            elif 'maxTransactionFee' in settings:
                self.error = 'maxTransactionFee must be a positive integer or equal to 0 (in Satoshis)'


            if 'addressType' in settings and settings['addressType'] in ['PrivKey', 'BIP44']:
                distributer.addressType = settings['addressType']
            elif 'addressType' in settings:
                self.error = 'AddressType must be BIP44 or PrivKey'

            if 'walletIndex' in settings and validator.validAmount(settings['walletIndex']):
                distributer.walletIndex = settings['walletIndex']
            elif 'walletIndex' in settings:
                self.error = 'walletIndex must be greater than or equal to 0'

            if 'privateKey' in settings and validator.validPrivateKey(settings['privateKey']):
                distributer.privateKey = settings['privateKey']
            elif 'privateKey' in settings:
                self.error = 'Invalid privateKey'

            if distributer.addressType == 'PrivKey' and distributer.privateKey != '':
                distributer.address = bitcoin.privtoaddr(distributer.privateKey)
            elif distributer.addressType == 'BIP44':
                if distributer.walletIndex == 0:
                    distributer.walletIndex = getNextIndex()
                distributer.address = datastore.get_service_address(datastore.Services.BlockDistribute, distributer.walletIndex)

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
                    linker = BlockLinker.BlockLinker(distributer.registrationAddress, distributer.registrationXPUB, distributer.registrationBlockHeight)

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
            UTXOs = utxos_data['UTXOs']
        else:
            self.error = 'Unable to retrieve UTXOs'


        totalInputValue = 0
        for UTXO in UTXOs:
            totalInputValue += UTXO['value']


        if totalInputValue >= distributer.threshold:
            logging.info('Starting distribution of ' + str(totalInputValue) + ' Satoshis, minimum output value: ' + str(distributer.minimumAmount))


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
                optimalOutputs = self.optimalOutputs(totalInputValue, distribution, distributer)
                logging.info("optimal outputs: " + str(optimalOutputs))

                privKeys = {}
                if distributer.addressType == 'PrivKey':
                    privKeys = {distributer.address: distributer.privateKey}

                elif distributer.addressType == 'BIP44':
                    privKeys = datastore.get_service_private_key(datastore.Services.BlockDistribute, distributer.walletIndex)

                if distributer.distributionSource == 'SIL' and distributer.address == distributer.registrationAddress:
                    self.error = 'Dark magic detected! Ponzi schemes are illegal!!'

                if len(optimalOutputs) > 0 and self.error == '':
                    totalOutputValue = 0
                    for tx_output in optimalOutputs:
                        totalOutputValue += tx_output['value']

                    totalFee = totalInputValue - totalOutputValue
                    logging.info("Sending " + str(totalInputValue) + ' Satoshis to ' + str(len(optimalOutputs)) + ' recipients with a total fee of ' + str(totalFee))
                    tx = TxFactory.makeCustomTransaction(privKeys, UTXOs, optimalOutputs, totalFee)
                    if tx != None:
                        TxFactory.sendTransaction(tx)
                else:
                    logging.error(self.error)


                if success == True:
                    logging.info("Success")
                else:
                    logging.error("Failed to send transaction")




            else:
                self.error = 'Invalid distribution: ' + str(distribution)

        return success


    def optimalOutputs(self, amount, distribution, distributer):
        optimal = []
        valueToDistribute = amount-distributer.maxTransactionFee

        if distributer.feePercent != 0 and distributer.feeAddress != '':
            distributingFee = int(valueToDistribute * (distributer.feePercent / 100.0))
            if distributingFee < 10000:
                distributingFee = 10000

            valueToDistribute -= distributingFee
            optimal.append({'address': distributer.feeAddress, 'value': distributingFee})


        if valueToDistribute < distributer.minimumAmount:
            self.error = 'minimumAmount is lower than the amount available to distribute.'

        sortedDistribution = sorted(distribution, key=lambda  x: x[1], reverse=True)

        for i in range(len(sortedDistribution)-1, -1, -1):
            tmpTotal = 0
            for j in range(0, len(sortedDistribution)):
                tmpTotal += sortedDistribution[j][1]

            share = sortedDistribution[i][1]/float(tmpTotal)

            if share*valueToDistribute < distributer.minimumAmount:
                del sortedDistribution[i]
            else:
                optimal.append({'address': sortedDistribution[i][0], 'value': int(share*valueToDistribute)})

        return optimal
