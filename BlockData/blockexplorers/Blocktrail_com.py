__author__ = 'Wouter'
import urllib2
import json
import binascii
from BlockData import TX as TX
import TxFactory.TxFactory as TxFactory
import time
import datetime
import logging
API_URL = 'https://api.blocktrail.com/'
API_VERSION = 'v1'

class API:
    def __init__(self, key='', secret=''):
        self.error = ''
        self.key = key
        self.secret = secret


    def getTXS(self, address):
        LIMIT = 200 #max 200 for Blocktrail.com
        pages = 0
        response = {'success': 0}
        url = 'https://api.blocktrail.com/' + API_VERSION + '/btc/address/' + address + '/transactions?api_key=' + self.key + '&limit=' + str(LIMIT) + '&sort_dir=asc'
        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            jsonObj = json.loads(ret.read())
            data = jsonObj['data']
            nTx = jsonObj['total']

            if (nTx <= int(jsonObj['per_page'])):
                pages = 1
            else:
                pages = int((nTx-1) / jsonObj['per_page'])+1

        except:
            data = []
            nTx = 0
            logging.warning('Blocktrail.com: unable to retrieve transactions')
            self.error = 'Unable to retrieve transactions'

        txs = []

        for page in range(1, pages+1):
            for i in range(0, len(data)):
                tx = TX.TX()
                tx.txid = data[i]['hash']
                tx.block_height = data[i]['block_height']
                tx.confirmations = data[i]['confirmations']

                for tx_input in data[i]['inputs']:
                    tx_in = {}
                    tx_in['address'] = tx_input['address']
                    tx_in['value'] = tx_input['value']
                    tx.inputs.append(tx_in)

                for tx_output in data[i]['outputs']:
                    tx_out = {}
                    tx_out['address'] = tx_output['address']
                    tx_out['value'] = tx_output['value']
                    if tx_output['script_hex'][:2] == '6a':
                        tx_out['OP_RETURN'] = TxFactory.decodeOP_RETURN(tx_output['script_hex'])

                    if tx_output['spent_hash'] == None:
                        tx_out['spent'] = False
                    else:
                        tx_out['spent'] = True

                    tx.outputs.append(tx_out)

                txs.append(tx.to_dict(address))

            if page < pages:
                url = 'https://api.blocktrail.com/' + API_VERSION + '/btc/address/' + address + '/transactions?api_key=' + self.key + '&page=' + str(page+1) + '&limit=' + str(LIMIT) + '&sort_dir=asc'
                try:
                    ret = urllib2.urlopen(urllib2.Request(url))
                    jsonObj = json.loads(ret.read())
                    data = jsonObj['data']
                except:
                    data = []
                    logging.warning('Blocktrail.com: Unable to retrieve page ' + str(page))
                    self.error = 'Unable to retrieve page ' + str(page)

        if nTx != len(txs):
            logging.warning('Blocktrail.com: Warning: not all transactions are retrieved! ' + str(len(txs)) + ' of ' +  str(nTx))
            response['error'] = 'Warning: not all transactions are retrieved! ' + str(len(txs)) + ' of ' +  str(nTx)
        elif self.error == '':
            response = {'success': 1, 'TXS': txs}
        else:
            response['error'] = self.error

        return response

    def getLatestBlock(self):
        response = {'success': 0}
        latestBlock = {}
        data = {}
        url = 'https://api.blocktrail.com/' + API_VERSION + '/btc/block/latest?api_key=' + self.key
        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            data = json.loads(ret.read())
        except:
            logging.warning('Blocktrail.com: Unable to retrieve latest block')
            response['error'] = 'Unable to retrieve latest block'

        if 'height' in data:
            latestBlock['height'] = data['height']
            latestBlock['hash'] = data['hash']
            latestBlock['time'] = int(time.mktime(datetime.datetime.strptime(data['block_time'], "%Y-%m-%dT%H:%M:%S+0000").timetuple()))
            latestBlock['merkleroot'] = data['merkleroot']
            latestBlock['size'] = data['byte_size']
            response = {'success': 1, 'latestBlock': latestBlock}

        return response

    def getBlock(self, height):
        response = {'success': 0}
        block = {}
        data = {}
        url = 'https://api.blocktrail.com/' + API_VERSION + '/btc/block/' + str(height) + '?api_key=' + self.key
        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            data = json.loads(ret.read())
        except:
            logging.warning('Blocktrail.com: unable to retrieve block ' + str(height))
            response['error'] = 'unable to retrieve block ' + str(height)

        if 'height' in data:
            block['height'] = data['height']
            block['hash'] = data['hash']
            block['time'] = int(time.mktime(datetime.datetime.strptime(data['block_time'], "%Y-%m-%dT%H:%M:%S+0000").timetuple()))
            block['merkleroot'] = data['merkleroot']
            block['size'] = data['byte_size']
            response = {'success': 1, 'block': block}

        return response

    def getBalances(self, addresses):
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
                except:
                    logging.warning('Blocktrail.com: Unable to retrieve data for address ' + address)
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

    def getUTXOs(self, addresses, confirmations=3):
        UTXOs = []
        response = {'success': 0}
        if len(addresses.split("|")) > 10:
            self.error = 'Max 10 addresses, api function for multiple address utxo lookup not available at ' + API_URL
        else:

            LIMIT = 200

            try:
                latestBlock = self.getLatestBlock()['latestBlock']['height']
            except:
                logging.warning('Blocktrail.com: Unable to retrieve latest block')
                self.error = 'Unable to retrieve latest block'

            counter = 0
            unconfirmedCounter = 0
            for address in addresses.split('|'):
                response['success'] = 0
                url = 'https://api.blocktrail.com/' + API_VERSION + '/btc/address/' + address + '/unspent-outputs?api_key=' + self.key + '&limit=' + str(LIMIT) + '&sort_dir=asc'
                nUTXO = 0
                pages = 1
                try:
                    ret = urllib2.urlopen(urllib2.Request(url))
                    jsonObj = json.loads(ret.read())
                    data = jsonObj['data']
                    nUTXO = jsonObj['total']

                    if (nUTXO <= int(jsonObj['per_page'])):
                        pages = 1
                    else:
                        pages = int((nUTXO-1) / jsonObj['per_page'])+1

                except:
                    data = []
                    logging.warning('Blocktrail.com: Unable to retrieve UTXOs')
                    self.error = 'Unable to retrieve UTXOs'


                for page in range(1, pages+1):

                    for i in range(0, len(data)):
                        utxo = {}
                        utxo['address'] = data[i]['address']
                        if data[i]['confirmations'] != 0:
                            block_height = latestBlock - int(data[i]['confirmations']) + 1

                        else:
                            block_height = None
                        utxo['block_height'] = block_height
                        utxo['confirmations'] = int(data[i]['confirmations'])
                        utxo['output'] = data[i]['hash'] + ":" + str(data[i]['index'])
                        utxo['value'] = data[i]['value']


                        if utxo['confirmations'] >= confirmations:
                            UTXOs.append(utxo)
                        else:
                            unconfirmedCounter += 1


                    if page < pages:
                        url = 'https://api.blocktrail.com/' + API_VERSION + '/btc/address/' + address + '/unspent-outputs?api_key=' + self.key + '&page=' + str(page+1) + '&limit=' + str(LIMIT) + '&sort_dir=asc'
                        try:
                            ret = urllib2.urlopen(urllib2.Request(url))
                            jsonObj = json.loads(ret.read())
                            data = jsonObj['data']
                        except:
                            data = []
                            logging.warning('Blocktrail.com: Unable to retrieve page ' + str(page) + ' of UTXOs')
                            self.error = 'Unable to retrieve page ' + str(page) + ' of UTXOs'


                if nUTXO != len(UTXOs)-counter + unconfirmedCounter:
                    logging.warning('Blocktrail.com: Warning: not all utxos are retrieved! ' + str(len(UTXOs)-counter) + ' of ' +  str(nUTXO))
                    self.error = 'Warning: not all utxos are retrieved! ' + str(len(UTXOs)-counter) + ' of ' +  str(nUTXO)
                else:
                    counter += nUTXO


        if self.error == '':
            response['success'] = 1
            response['UTXOs'] = UTXOs
        else:
            response['error'] = self.error


        return response

    def getPrimeInputAddress(self, txid):
        url = 'https://api.blocktrail.com/' + API_VERSION + '/btc/transaction/' + str(txid) + '?api_key=' + self.key
        data = {}
        response = {'success': 0}
        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            data = json.loads(ret.read())
        except:
            logging.warning('Blocktrail.com: Unable to retrieve prime input address of tx ' + str(txid))
            response['error'] = 'Unable to retrieve prime input address of tx ' + str(txid)

        if 'inputs' in data:
            tx_inputs = data['inputs']

            inputAddresses = []
            for i in range(0, len(tx_inputs)):
                inputAddresses.append(tx_inputs[i]['address'])

            primeInputAddress = ''
            if len(inputAddresses) > 0:
                primeInputAddress = sorted(inputAddresses)[0]

            response = {'success': 1, 'PrimeInputAddress': primeInputAddress}

        return response