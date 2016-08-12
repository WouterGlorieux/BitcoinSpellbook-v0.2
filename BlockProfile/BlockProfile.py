
import logging
from Blockchaindata import Blockchaindata
from validators import validators as validator


def Profile(address, block=0):
    response = {'success': 0}
    profile = []

    if validator.validAddress(address):
        if block == 0:
            latestBlock = Blockchaindata.latestBlock()

            if 'success' in latestBlock and latestBlock['success'] == 1:
                block = latestBlock['latestBlock']['height']
            else:
                response['error'] = 'Unable to retrieve latest block'

        txsData = Blockchaindata.transactions(address)
        if 'success' in txsData and txsData['success'] == 1:
            txs = txsData['TXS']
            profile = TXS2profile(txs, block)
        else:
            response['error'] = 'Unable to retrieve transactions'

    else:
        response['error'] = 'Invalid address: ' + address

    if 'error' not in response:
        response['profile'] = profile
        response['success'] = 1

    return response


def TXS2profile(txs, block=0):
    sortedTXS = sortTXS(txs)
    profile = {}
    for tx in sortedTXS:
        if (block == 0 or tx['blockHeight'] <= block) and tx['blockHeight'] != None:
            for output in tx['outputs']:
                if 'OP_RETURN' in output:
                    primeInputAddress = tx['primeInputAddress']
                    blockHeight = tx['blockHeight']
                    data = [blockHeight, output['OP_RETURN']]
                    logging.info('found op return: %s from %s' % (data, primeInputAddress))

                    if primeInputAddress in profile:
                        profile[primeInputAddress].append(data)
                    else:
                        profile[primeInputAddress] = [data]


    return profile


def sortTXS(txs):
    blockTXS = {}
    for tx in txs:
        if tx['blockHeight'] in blockTXS:
            blockTXS[tx['blockHeight']].append(tx)
        else:
            blockTXS[tx['blockHeight']] = [tx]

    sortedTXS = []
    for block in sorted(blockTXS):
        for tx in sorted(blockTXS[block], key= lambda x: x['txid']):
            sortedTXS.append(tx)

    return sortedTXS



