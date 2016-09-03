#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import json
from decimal import *
import logging

import TxFactory.TxFactory as TxFactory
from BlockData import TX


API_URL = 'https://blockexplorer.com/api'


class API:
    def __init__(self, url=API_URL):
        self.url = url
        self.error = ''

    def get_txs(self, address):
        response = {'success': 0}
        txs = []
        limit = 10  # number of tx given by insight is 10

        latest_block_height = -1
        try:
            latest_block_data = self.get_latest_block()
            if 'success' in latest_block_data and latest_block_data['success'] == 1:
                latest_block = latest_block_data['latest_block']
                if isinstance(latest_block, dict):
                    latest_block_height = latest_block['height']
                else:
                    self.error = "latest_block is not a dictionary"
        except Exception as ex:
            logging.warning(str(ex))
            logging.error('Insight: Unable to retrieve latest block')
            self.error = 'Unable to retrieve latest block'

        url = self.url + '/addrs/' + address + '/txs'
        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            data = json.loads(ret.read())
        except Exception as ex:
            logging.warning(str(ex))
            self.error = 'Unable to retrieve transactions'

        if 'totalItems' in data:
            transactions = data['items']
            n_tx = data['totalItems']

            if n_tx > limit:
                for i in range(1, int(n_tx/limit)+1):
                    url = self.url + '/addrs/' + address + '/txs?from=' + str(limit*i) + '&to=' + str(limit*(i+1))
                    try:
                        ret = urllib2.urlopen(urllib2.Request(url))
                        data = json.loads(ret.read())
                        transactions += data['items']
                    except Exception as ex:
                        logging.warning(str(ex))
                        self.error = 'Unable to retrieve next page'

        for transaction in transactions:

            tx = TX.TX()
            tx.txid = transaction['txid']
            tx.confirmations = transaction['confirmations']
            if transaction['confirmations'] >= 1:
                tx.block_height = latest_block_height - tx.confirmations + 1
            else:
                tx.block_height = None

            for tx_input in transaction['vin']:
                tx_in = {'address': tx_input['addr'],
                         'value': tx_input['valueSat']}
                tx.inputs.append(tx_in)

            for out in transaction['vout']:
                tx_out = {}
                if 'addresses' in out['scriptPubKey']:
                    tx_out['address'] = out['scriptPubKey']['addresses'][0]
                else:
                    tx_out['address'] = None
                    if out['scriptPubKey']['hex'][:2] == '6a':
                        tx_out['op_return'] = TxFactory.decode_op_return(out['scriptPubKey']['hex'])

                tx_out['value'] = int(Decimal(out['value']) * Decimal(1e8))
                if 'spentTxId' in out and out['spentTxId'] is not None:
                    tx_out['spent'] = True
                else:
                    tx_out['spent'] = False

                tx.outputs.append(tx_out)

            txs.insert(0, tx.to_dict(address))

        if n_tx != len(txs):
            logging.error('Insight: Warning: not all transactions are retrieved! ' + str(len(txs)) + ' of ' + str(n_tx))
            self.error = 'Warning: not all transactions are retrieved! ' + str(len(txs)) + ' of ' + str(n_tx)

        if self.error == '':
            response['success'] = 1
            response['txs'] = txs
        else:
            response['error'] = self.error

        return response

    def get_latest_block(self):
        response = {'success': 0}
        latest_block = {}
        data = {}
        url = self.url + '/status?q=getInfo'
        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            data = json.loads(ret.read())
        except Exception as ex:
            logging.warning(str(ex))
            self.error = 'Unable to retrieve latest block'

        if 'info' in data:
            latest_block['height'] = data['info']['blocks']
            block_data = {}
            try:
                block_data = self.get_block(latest_block['height'])
            except Exception as ex:
                logging.warning(str(ex))
                self.error = 'Unable to retrieve block'

            if 'success' in block_data and block_data['success'] == 1:
                block = block_data['block']
                if isinstance(block, dict):
                    latest_block['hash'] = block['hash']
                    latest_block['time'] = block['time']
                    latest_block['merkleroot'] = block['merkleroot']
                    latest_block['size'] = block['size']
                else:
                    self.error = "block is not a dictionary"
            else:
                self.error = 'Unable to retrieve block'
        else:
            self.error = 'Could not find info on latest block'

        if self.error == '':
            response['success'] = 1
            response['latest_block'] = latest_block
        else:
            response['error'] = self.error

        return response

    def get_block(self, height):
        response = {'success': 0}
        block = {}
        data = {}
        url = self.url + '/block-index/' + str(height)
        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            data = json.loads(ret.read())
        except Exception as ex:
            logging.warning(str(ex))
            self.error = 'unable to retrieve block {0}'.format(str(height))

        if 'blockHash' in data:
            block['height'] = height
            block['hash'] = data['blockHash']

            url = self.url + '/block/' + block['hash']
            try:
                ret = urllib2.urlopen(urllib2.Request(url))
                data = json.loads(ret.read())
            except Exception as ex:
                logging.warning(str(ex))
                self.error = 'Unable to retrieve block ' + block['hash']

            if 'hash' in data and data['hash'] == block['hash']:
                block['time'] = data['time']
                block['merkleroot'] = data['merkleroot']
                block['size'] = data['size']
        else:
            self.error = 'Unable to retrieve block {0}'.format(str(height))

        if self.error == '':
            response['success'] = 1
            response['block'] = block
        else:
            response['error'] = self.error

        return response

    def get_balances(self, addresses):
        response = {'success': 0}

        if len(addresses.split("|")) > 10:
            self.error = 'Max 10 addresses, api function for multiple address lookup not available at ' + self.url
        else:
            balances = {}
            for address in addresses.split("|"):
                data = {}

                url = self.url + '/addr/' + address
                try:
                    ret = urllib2.urlopen(urllib2.Request(url))
                    data = json.loads(ret.read())
                except Exception as ex:
                    logging.warning(str(ex))
                    self.error = 'Unable to retrieve data for addresses ' + addresses

                if 'addrStr' in data and data['addrStr'] == address:
                    balances[data['addrStr']] = {}
                    balances[data['addrStr']]['balance'] = data['balanceSat']

                    txs_data = self.get_txs(address)
                    received = 0
                    sent = 0
                    if 'success' in txs_data and txs_data['success'] == 1:
                        txs = txs_data['txs']
                        if isinstance(txs, list):
                            for tx in txs:
                                if tx['receiving'] is True and tx['confirmations'] > 0:
                                    received += tx['receivedValue']

                                elif tx['receiving'] is False and tx['confirmations'] > 0:
                                    sent += tx['sentValue']
                        else:
                            self.error = 'txs is not a list of transactions'

                        balances[data['addrStr']]['received'] = received
                        balances[data['addrStr']]['sent'] = sent
                    else:
                        self.error = txs_data['error']

        if self.error == '':
            response['success'] = 1
            response['balances'] = balances
        else:
            response['error'] = self.error

        return response

    def get_prime_input_address(self, txid):
        response = {'success': 0}
        url = self.url + '/tx/' + str(txid)
        data = {}
        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            data = json.loads(ret.read())
        except Exception as ex:
            logging.warning(str(ex))
            self.error = 'Unable to retrieve prime input address of tx ' + txid

        if 'txid' in data and data['txid'] == txid:
            tx_inputs = data['vin']

            input_addresses = []
            for i in range(0, len(tx_inputs)):
                input_addresses.append(tx_inputs[i]['addr'])

            prime_input_address = []
            if len(input_addresses) > 0:
                prime_input_address = sorted(input_addresses)[0]

        if self.error == '':
            response['success'] = 1
            response['PrimeInputAddress'] = prime_input_address
        else:
            response['error'] = self.error

        return response

    #Multiple bitcoin addresses, separated by ","
    def get_utxos(self, addresses, confirmations=3):
        response = {'success': 0}
        addresses = addresses.replace('|', ',')

        latest_block_height = 0
        try:
            latest_block_data = self.get_latest_block()
            if 'success' in latest_block_data and latest_block_data['success'] == 1:
                latest_block = latest_block_data['latest_block']
                if isinstance(latest_block, dict):
                    latest_block_height = latest_block['height']
                else:
                    self.error = 'latest_block is not a dictionary'
        except Exception as ex:
            logging.warning(str(ex))
            self.error = 'Unable to retrieve latest block'

        utxos = []
        url = self.url + '/addrs/' + addresses + '/utxo'
        data = {}
        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            data = json.loads(ret.read())
        except Exception as ex:
            logging.warning(str(ex))
            self.error = 'Unable to retrieve utxos'

        for i in range(0, len(data)):
            utxo = {'address': data[i]['address']}

            url = self.url + '/tx/' + data[i]['txid']
            tx = {}
            try:
                ret = urllib2.urlopen(urllib2.Request(url))
                tx = json.loads(ret.read())
            except Exception as ex:
                logging.warning(str(ex))
                self.error = 'Unable to retrieve tx' + data[i]['txid']

            if 'txid' in tx and tx['txid'] == data[i]['txid']:
                utxo['confirmations'] = int(tx['confirmations'])
                utxo['block_height'] = latest_block_height - utxo['confirmations'] + 1

            utxo['output'] = data[i]['txid'] + ":" + str(data[i]['vout'])
            utxo['value'] = int(data[i]['satoshis'])

            if utxo['confirmations'] >= confirmations:
                utxos.append(utxo)

        if self.error == '':
            response['success'] = 1
            response['UTXOs'] = utxos
        else:
            response['error'] = self.error

        return response