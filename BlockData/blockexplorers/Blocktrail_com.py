#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import json
import time
import datetime
import logging

from BlockData import TX as TX
import TxFactory.TxFactory as TxFactory

API_URL = 'https://api.blocktrail.com/'
API_VERSION = 'v1'


class API:
    def __init__(self, key='', secret=''):
        self.error = ''
        self.key = key
        self.secret = secret

    def get_txs(self, address):
        limit = 200  # max 200 for Blocktrail.com
        pages = 0
        response = {'success': 0}
        url = 'https://api.blocktrail.com/{0}/btc/address/{1}/transactions?api_key={2}&limit={3}&sort_dir=asc'.format(
            str(API_VERSION), str(address), str(self.key), str(limit))
        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            json_obj = json.loads(ret.read())
            data = json_obj['data']
            n_tx = json_obj['total']

            if n_tx <= int(json_obj['per_page']):
                pages = 1
            else:
                pages = int((n_tx-1) / json_obj['per_page'])+1

        except Exception as ex:
            logging.warning(str(ex))
            data = []
            n_tx = 0
            self.error = 'Unable to retrieve transactions'

        txs = []

        for page in range(1, pages+1):
            for i in range(0, len(data)):
                tx = TX.TX()
                tx.txid = data[i]['hash']
                tx.block_height = data[i]['block_height']
                tx.confirmations = data[i]['confirmations']

                for tx_input in data[i]['inputs']:
                    tx_in = {'address': tx_input['address'],
                             'value': tx_input['value']}
                    tx.inputs.append(tx_in)

                for tx_output in data[i]['outputs']:
                    tx_out = {'address': tx_output['address'],
                              'value': tx_output['value']}
                    if tx_output['script_hex'][:2] == '6a':
                        tx_out['OP_RETURN'] = TxFactory.decodeOP_RETURN(tx_output['script_hex'])

                    if tx_output['spent_hash'] is None:
                        tx_out['spent'] = False
                    else:
                        tx_out['spent'] = True

                    tx.outputs.append(tx_out)

                txs.append(tx.to_dict(address))

            if page < pages:
                url = 'https://api.blocktrail.com/{0}/btc/address/{1}/transactions?api_key={2}&page={3}&limit={4}&sort_dir=asc'.format(
                    str(API_VERSION), str(address), str(self.key), str(page + 1), str(limit))
                try:
                    ret = urllib2.urlopen(urllib2.Request(url))
                    json_obj = json.loads(ret.read())
                    data = json_obj['data']
                except Exception as ex:
                    logging.warning(str(ex))
                    data = []
                    self.error = 'Unable to retrieve page ' + str(page)

        if n_tx != len(txs):
            logging.warning(
                'Blocktrail.com: Warning: not all transactions are retrieved! {0} of {1}'.format(str(len(txs)),
                                                                                                 str(n_tx)))
            response['error'] = 'Warning: not all transactions are retrieved! {0} of {1}'.format(str(len(txs)),
                                                                                                 str(n_tx))
        elif self.error == '':
            response = {'success': 1, 'txs': txs}
        else:
            response['error'] = self.error

        return response

    def get_latest_block(self):
        response = {'success': 0}
        latest_block = {}
        data = {}
        url = 'https://api.blocktrail.com/' + API_VERSION + '/btc/block/latest?api_key=' + self.key
        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            data = json.loads(ret.read())
        except Exception as ex:
            logging.warning(str(ex))
            response['error'] = 'Unable to retrieve latest block'

        if 'height' in data:
            latest_block['height'] = data['height']
            latest_block['hash'] = data['hash']
            latest_block['time'] = int(time.mktime(datetime.datetime.strptime(data['block_time'],
                                                                              "%Y-%m-%dT%H:%M:%S+0000").timetuple()))
            latest_block['merkleroot'] = data['merkleroot']
            latest_block['size'] = data['byte_size']
            response = {'success': 1, 'latestBlock': latest_block}

        return response

    def get_block(self, height):
        response = {'success': 0}
        block = {}
        data = {}
        url = 'https://api.blocktrail.com/' + API_VERSION + '/btc/block/' + str(height) + '?api_key=' + self.key
        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            data = json.loads(ret.read())
        except Exception as ex:
            logging.warning(str(ex))
            response['error'] = 'unable to retrieve block ' + str(height)

        if 'height' in data:
            block['height'] = data['height']
            block['hash'] = data['hash']
            block['time'] = int(time.mktime(datetime.datetime.strptime(data['block_time'],
                                                                       "%Y-%m-%dT%H:%M:%S+0000").timetuple()))
            block['merkleroot'] = data['merkleroot']
            block['size'] = data['byte_size']
            response = {'success': 1, 'block': block}

        return response

    def get_balances(self, addresses):
        response = {'success': 0}
        if len(addresses.split("|")) > 10:
            response['error'] = 'Max 10 addresses, api function for multiple address lookup not available at ' + API_URL
        else:
            balances = {}

            for address in addresses.split("|"):
                data = {}
                url = 'https://api.blocktrail.com/' + API_VERSION + '/btc/address/' + address + '?api_key=' + self.key
                try:
                    ret = urllib2.urlopen(urllib2.Request(url))
                    data = json.loads(ret.read())
                except Exception as ex:
                    logging.warning(str(ex))
                    self.error = 'Unable to retrieve data for address ' + address

                response['success'] = 0
                if 'address' in data:
                    balances[data['address']] = {}
                    balances[data['address']]['balance'] = data['balance']
                    balances[data['address']]['received'] = data['received']
                    balances[data['address']]['sent'] = data['sent']

        if self.error == '':
            response['success'] = 1
            response['balances'] = balances
        else:
            response['error'] = self.error

        return response

    def get_utxos(self, addresses, confirmations=3):
        utxos = []
        response = {'success': 0}
        if len(addresses.split("|")) > 10:
            self.error = 'Max 10 addresses, api function for multiple address utxo lookup not available at ' + API_URL
        else:

            limit = 200

            try:
                latest_block = self.get_latest_block()['latestBlock']['height']
            except Exception as ex:
                logging.warning(str(ex))
                self.error = 'Unable to retrieve latest block'

            counter = 0
            unconfirmed_counter = 0
            for address in addresses.split('|'):
                response['success'] = 0
                url = 'https://api.blocktrail.com/{0}/btc/address/{1}/unspent-outputs?api_key={2}&limit={3}&sort_dir=asc'.format(
                    str(API_VERSION), str(address), str(self.key), str(limit))
                n_utxo = 0
                pages = 1
                try:
                    ret = urllib2.urlopen(urllib2.Request(url))
                    json_obj = json.loads(ret.read())
                    data = json_obj['data']
                    n_utxo = json_obj['total']

                    if n_utxo <= int(json_obj['per_page']):
                        pages = 1
                    else:
                        pages = int((n_utxo-1) / json_obj['per_page'])+1

                except Exception as ex:
                    logging.warning(str(ex))
                    data = []
                    self.error = 'Unable to retrieve UTXOs'

                for page in range(1, pages+1):

                    for i in range(0, len(data)):
                        utxo = {'address': data[i]['address']}
                        if data[i]['confirmations'] != 0:
                            block_height = latest_block - int(data[i]['confirmations']) + 1

                        else:
                            block_height = None
                        utxo['block_height'] = block_height
                        utxo['confirmations'] = int(data[i]['confirmations'])
                        utxo['output'] = data[i]['hash'] + ":" + str(data[i]['index'])
                        utxo['value'] = data[i]['value']

                        if utxo['confirmations'] >= confirmations:
                            utxos.append(utxo)
                        else:
                            unconfirmed_counter += 1

                    if page < pages:
                        url = 'https://api.blocktrail.com/{0}/btc/address/{1}/unspent-outputs?api_key={2}&page={3}&limit={4}&sort_dir=asc'.format(
                            str(API_VERSION), str(address), str(self.key), str(page + 1), str(limit))
                        try:
                            ret = urllib2.urlopen(urllib2.Request(url))
                            json_obj = json.loads(ret.read())
                            data = json_obj['data']
                        except Exception as ex:
                            logging.warning(str(ex))
                            data = []
                            self.error = 'Unable to retrieve page ' + str(page) + ' of UTXOs'

                if n_utxo != len(utxos)-counter + unconfirmed_counter:
                    logging.warning('Blocktrail.com: Warning: not all utxos are retrieved! {0} of {1}'.format(
                        str(len(utxos) - counter), str(n_utxo)))
                    self.error = 'Warning: not all utxos are retrieved! {0} of {1}'.format(str(len(utxos) - counter),
                                                                                           str(n_utxo))
                else:
                    counter += n_utxo

        if self.error == '':
            response['success'] = 1
            response['UTXOs'] = utxos
        else:
            response['error'] = self.error

        return response

    def get_prime_input_address(self, txid):
        url = 'https://api.blocktrail.com/' + API_VERSION + '/btc/transaction/' + str(txid) + '?api_key=' + self.key
        data = {}
        response = {'success': 0}
        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            data = json.loads(ret.read())
        except Exception as ex:
            logging.warning(str(ex))
            response['error'] = 'Unable to retrieve prime input address of tx ' + str(txid)

        if 'inputs' in data:
            tx_inputs = data['inputs']

            input_addresses = []
            for i in range(0, len(tx_inputs)):
                input_addresses.append(tx_inputs[i]['address'])

            prime_input_address = ''
            if len(input_addresses) > 0:
                prime_input_address = sorted(input_addresses)[0]

            response = {'success': 1, 'PrimeInputAddress': prime_input_address}

        return response