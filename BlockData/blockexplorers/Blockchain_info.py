
import urllib2
import json
import logging
import TxFactory.TxFactory as TxFactory
from BlockData import TX as TX

from pprint import pprint

API_VERSION = 'v1'


class API:
    def __init__(self, key='', secret=''):
        self.key = key
        self.secret = secret

    def get_txs(self, address):
        response = {'success': 0}
        limit = 50  # max number of tx given by blockchain.info is 50

        latest_block_height = -1
        try:
            latest_block_height = self.get_latest_block()['latestBlock']['height']
        except:
            logging.warning('Blockchain.info: unable to retrieve latest block')
            response = {'success': 0, 'error': 'unable to retrieve latest block'}

        url = 'https://blockchain.info/address/' + address + '?format=json&limit=' + str(limit)
        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            data = json.loads(ret.read())
        except:
            data = {}

        transactions = data['txs']
        n_tx = data['n_tx']

        if 'n_tx' in data:
            n_tx = data['n_tx']
            if n_tx > limit:
                for i in range(1, int(n_tx/limit)+1):
                    url = 'https://blockchain.info/address/' + address + '?format=json&limit=' + str(limit) + '&offset=' + str(limit*i)
                    try:
                        ret = urllib2.urlopen(urllib2.Request(url))
                        data = json.loads(ret.read())
                        transactions += data['txs']
                    except:
                        logging.warning('Blockchain.info: unable to retrieve next page')
                        response = {'success': 0, 'error': 'unable to retrieve next page '}

        txs = []
        for transaction in transactions:

            tx = TX.TX()
            tx.txid = transaction['hash']

            if 'block_height' in transaction:
                tx.block_height = transaction['block_height']
                tx.confirmations = (latest_block_height - tx.block_height) + 1
            else:
                tx.block_height = None
                tx.confirmations = 0

            for tx_input in transaction['inputs']:
                tx_in = {'address': tx_input['prev_out']['addr'],
                         'value': tx_input['prev_out']['value']}
                tx.inputs.append(tx_in)

            for out in transaction['out']:
                tx_out = {}

                if 'addr' in out:
                    tx_out['address'] = out['addr']
                else:
                    tx_out['address'] = None
                    if out['script'][:2] == '6a':
                        tx_out['OP_RETURN'] = TxFactory.decodeOP_RETURN(out['script'])

                tx_out['value'] = out['value']
                tx_out['spent'] = out['spent']
                tx.outputs.append(tx_out)

            txs.insert(0, tx.to_dict(address))

        if n_tx != len(txs):
            logging.warning('Blockchain.info: Warning: not all transactions are retrieved! ' + str(len(txs)) + ' of ' + str(n_tx))
            response = {'success': 0, 'error': 'Not all transactions are retrieved ' + str(len(txs)) + ' of ' + str(n_tx)}
        else:
            response = {'success': 1, 'TXS': txs}

        return response

    @staticmethod
    def get_latest_block():
        response = {'success': 0}
        latest_block = {}
        data = {}
        url = 'https://blockchain.info/nl/latestblock'
        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            data = json.loads(ret.read())
        except:
            logging.warning('Blockchain.info: unable to retrieve latest block')
            response = {'success': 0, 'error': 'unable to retrieve latest block'}

        if 'height' in data:
            latest_block['height'] = data['height']
            latest_block['hash'] = data['hash']
            latest_block['time'] = data['time']

            url = 'https://blockchain.info/nl/rawblock/' + latest_block['hash']
            data = {}
            try:
                ret = urllib2.urlopen(urllib2.Request(url))
                data = json.loads(ret.read())
            except:
                logging.warning('Blockchain.info: unable to retrieve block ' + str(latest_block['height']))
                response = {'success': 0, 'error': 'unable to retrieve block ' + str(latest_block['height'])}

            if 'hash' in data and data['hash'] == latest_block['hash']:
                latest_block['merkleroot'] = data['mrkl_root']
                latest_block['size'] = data['size']

            response = {'success': 1, 'latestBlock': latest_block}

        return response

    @staticmethod
    def get_block(height):
        response = {'success': 0}
        block = {}
        data = {}
        url = 'https://blockchain.info/nl/block-height/' + str(height) + '?format=json'
        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            data = json.loads(ret.read())
        except:
            logging.warning('Blockchain.info: unable to retrieve block ' + str(height))
            response = {'success': 0, 'error': 'unable to retrieve block ' + str(height)}

        if 'blocks' in data:
            blocks = data['blocks']

            for i in range(0, len(blocks)):
                if blocks[i]['main_chain'] is True and blocks[i]['height'] == height:
                    block['height'] = blocks[i]['height']
                    block['hash'] = blocks[i]['hash']
                    block['time'] = blocks[i]['time']
                    block['merkleroot'] = blocks[i]['mrkl_root']
                    block['size'] = blocks[i]['size']

            response = {'success': 1, 'block': block}

        return response

    #(Multiple addresses divided by |)
    def get_balances(self, addresses):
        response = {'success': 0}
        self.error = ''
        data = {}
        balances = {}
        url = 'https://blockchain.info/nl/multiaddr?active=' + addresses
        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            data = json.loads(ret.read())
        except:
            logging.warning('Blockchain.info: unable to retrieve data for addresses ' + addresses)
            self.error = 'Unable to retrieve data for addresses ' + addresses

        if 'addresses' in data:
            for i in range(0, len(data['addresses'])):
                address = data['addresses'][i]
                balances[address['address']] = {}
                balances[address['address']]['balance'] = address['final_balance']
                balances[address['address']]['received'] = address['total_received']
                balances[address['address']]['sent'] = address['total_sent']

        #reverse unconfirmed transactions for security reasons
        if 'txs' in data:
            for i in range(0, len(data['txs'])):
                tx = data['txs'][i]
                if 'block_height' not in tx:
                    for address in addresses.split('|'):
                        is_sending_tx = False
                        is_receiving_tx = False

                        for j in range(0, len(tx['inputs'])):
                            if tx['inputs'][j]['prev_out']['addr'] == address:
                                is_sending_tx = True

                        if is_sending_tx:
                            balances[address]['sent'] += tx['result']
                            balances[address]['balance'] -= tx['result']
                        else:
                            for j in range(0, len(tx['out'])):
                                if tx['out'][j]['addr'] == address:
                                    is_receiving_tx = True

                            if is_receiving_tx:
                                balances[address]['received'] -= tx['result']
                                balances[address]['balance'] -= tx['result']

        if self.error == '':
            response = {'success': 1, 'balances': balances}
        else:
            response['error'] = self.error

        return response

    def get_prime_input_address(self, txid):
        url = 'https://blockchain.info/nl/rawtx/' + str(txid)
        data = {}
        response = {'success': 0}
        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            data = json.loads(ret.read())
        except:
            logging.warning('Blockchain.info: unable to retrieve prime input address of tx ' + txid)
            response = {'success': 0, 'error': 'unable to retrieve prime input address of tx ' + txid}

        if 'hash' in data and data['hash'] == txid:
            tx_inputs = data['inputs']

            input_addresses = []
            for i in range(0, len(tx_inputs)):
                input_addresses.append(tx_inputs[i]['prev_out']['addr'])

            prime_input_address = []
            if len(input_addresses) > 0:
                prime_input_address = sorted(input_addresses)[0]

            response = {'success': 1, 'PrimeInputAddress': prime_input_address}

        return response

    #Multiple bitcoin addresses, separated by "|"
    def get_utxos(self, addresses, confirmations=3):
        response = {'success': 0}
        utxos = []
        url = 'https://blockchain.info/nl/unspent?active=' + addresses
        data = {}
        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            data = json.loads(ret.read())
        except:
            logging.warning('Blockchain.info: unable to retrieve utxos')
            response = {'success': 0, 'error': 'unable to retrieve utxos'}

        if 'unspent_outputs' in data:
            for i in range(0, len(data['unspent_outputs'])):
                utxo = {'confirmations': int(data['unspent_outputs'][i]['confirmations']),
                        'output': data['unspent_outputs'][i]['tx_hash_big_endian'] + ":" + str(
                            data['unspent_outputs'][i]['tx_output_n']),
                        'value': data['unspent_outputs'][i]['value']}

                if utxo['confirmations'] >= confirmations:
                    utxos.append(utxo)

                url = 'https://blockchain.info/nl/rawtx/' + data['unspent_outputs'][i]['tx_hash_big_endian']
                tx = {}
                try:
                    ret = urllib2.urlopen(urllib2.Request(url))
                    tx = json.loads(ret.read())
                except:
                    logging.warning('Blockchain.info: unable to retrieve utxos')
                    response = {'success': 0, 'error': 'unable to retrieve utxos'}

                if 'block_height' in tx and 'hash' in tx and tx['hash'] == data['unspent_outputs'][i]['tx_hash_big_endian']:
                    utxo['block_height'] = tx['block_height']
                    for tx_output in tx['out']:
                        if tx_output['n'] == data['unspent_outputs'][i]['tx_output_n']:
                            utxo['address'] = tx_output['addr']

            response = {'success': 1, 'UTXOs': utxos}
        return response