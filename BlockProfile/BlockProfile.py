import re
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
            profile = TXS2profile(txs, address, block)
        else:
            response['error'] = 'Unable to retrieve transactions'

    else:
        response['error'] = 'Invalid address: ' + address

    if 'error' not in response:
        response['profile'] = profile
        response['success'] = 1

    return response


def TXS2profile(txs, address, block=0):
    sortedTXS = sortTXS(txs)
    profile = {}
    for tx in sortedTXS:
        if (block == 0 or tx['blockHeight'] <= block) and tx['blockHeight'] != None:
            for output in tx['outputs']:
                if 'OP_RETURN' in output:
                    primeInputAddress = tx['primeInputAddress']
                    blockHeight = tx['blockHeight']
                    message = output['OP_RETURN']
                    data = [blockHeight, message]
                    if validator.validOP_RETURN(message) and validator.validBlockProfileMessage(message):
                        for message_part in message.split("|"):
                            (from_index, to_index, variable_name, variable_value) = components(message_part)
                            if from_index:
                                from_address = tx['outputs'][int(from_index)]['address']
                            else:
                                from_address = 'SELF'
                            to_address = tx['outputs'][int(to_index)]['address']

                            if primeInputAddress in profile and to_address == address:
                                if from_address in profile[primeInputAddress]:
                                    if variable_name in profile[primeInputAddress][from_address]:
                                        #variable already exists, overwrite or adjust value
                                        profile[primeInputAddress][from_address][variable_name] = variable_value
                                    else:
                                        profile[primeInputAddress][from_address][variable_name] = variable_value
                                else:
                                    profile[primeInputAddress][from_address] = {variable_name: variable_value}
                            elif to_address == address:
                                profile[primeInputAddress] = {from_address: {variable_name: variable_value}}

    return profile


## @brief splits message into 4 components: from_index, to_index, variable_name, variable_value
def components(message):
    return re.split('[@:=]+', message)


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



