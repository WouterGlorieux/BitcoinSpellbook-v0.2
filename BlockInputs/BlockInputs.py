#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import logging
from BlockData import BlockData
from validators import validators as validator


def get_sil(address, block=0):
    response = {'success': 0}
    sil = []

    if validator.valid_address(address):
        if block == 0:
            latest_block = BlockData.latest_block()

            if 'success' in latest_block and latest_block['success'] == 1:
                block = latest_block['latest_block']['height']
            else:
                response['error'] = 'Unable to retrieve latest block'

        txs_data = BlockData.transactions(address)
        if 'success' in txs_data and txs_data['success'] == 1:
            txs = txs_data['txs']
            sil = txs_2_sil(txs, block)
        else:
            response['error'] = 'Unable to retrieve transactions'

    else:
        response['error'] = 'Invalid address: ' + address

    if 'error' not in response:
        response['SIL'] = sil
        response['success'] = 1

    return response


def txs_2_sil(txs, block=0):

    sorted_txs = sort_txs(txs)
    sil = []
    for tx in sorted_txs:
        if tx['receiving'] is True and (block == 0 or tx['block_height'] <= block) and tx['block_height'] is not None:
            recurring = False
            for i in range(0, len(sil)):
                if sil[i][0] == tx['prime_input_address']:
                    sil[i][1] += tx['receivedValue']
                    recurring = True

            if not recurring:
                sil.append([tx['prime_input_address'], tx['receivedValue'], 0, tx['block_height']])

    total = float(total_received(sil))

    for row in sil:
        row[2] = row[1]/total

    return sil


def total_received(sil):
    total = 0
    for tx_input in sil:
        total += tx_input[1]

    return total


def sort_txs(txs):
    block_txs = {}
    for tx in txs:
        if tx['block_height'] in block_txs:
            block_txs[tx['block_height']].append(tx)
        else:
            block_txs[tx['block_height']] = [tx]

    sorted_txs = []
    for block in sorted(block_txs):
        for tx in sorted(block_txs[block], key=lambda x: x['txid']):
            sorted_txs.append(tx)

    return sorted_txs


def get_profile(address, block=0):
    response = {'success': 0}
    profile = []

    if validator.valid_address(address):
        if block == 0:
            latest_block = BlockData.latest_block()

            if 'success' in latest_block and latest_block['success'] == 1:
                block = latest_block['latest_block']['height']
            else:
                response['error'] = 'Unable to retrieve latest block'

        txs_data = BlockData.transactions(address)
        if 'success' in txs_data and txs_data['success'] == 1:
            txs = txs_data['txs']
            profile = txs_to_profile(txs, address, block)
        else:
            response['error'] = 'Unable to retrieve transactions'

    else:
        response['error'] = 'Invalid address: ' + address

    if 'error' not in response:
        response['profile'] = profile
        response['success'] = 1

    return response


def txs_to_profile(txs, address, block_height=0):
    sorted_txs = sort_txs(txs)
    profile = {}
    for tx in sorted_txs:
        if (block_height == 0 or tx['block_height'] <= block_height) and tx['block_height'] is not None:
            for output in tx['outputs']:
                if 'op_return' in output:
                    prime_input_address = tx['prime_input_address']
                    tx_block_height = tx['block_height']
                    profile[prime_input_address] = {'lastUpdate': tx_block_height}
                    message = output['op_return']
                    if validator.valid_op_return(message) and validator.valid_blockprofile_message(message):
                        for message_part in message.split("|"):
                            (from_index, to_index, variable_name, variable_value) = components(message_part)
                            if from_index:
                                from_address = tx['outputs'][int(from_index)]['address']
                            else:
                                from_address = 'SELF'
                            to_address = tx['outputs'][int(to_index)]['address']

                            if to_address == address:
                                if from_address in profile[prime_input_address]:
                                    if variable_name in profile[prime_input_address][from_address]:
                                        #variable already exists, overwrite or adjust value
                                        profile[prime_input_address][from_address][variable_name] = variable_value
                                    else:
                                        profile[prime_input_address][from_address][variable_name] = variable_value
                                else:
                                    profile[prime_input_address][from_address] = {variable_name: variable_value}
    return profile


## @brief splits message into 4 components: from_index, to_index, variable_name, variable_value
def components(message):
    return re.split('[@:=]+', message)
