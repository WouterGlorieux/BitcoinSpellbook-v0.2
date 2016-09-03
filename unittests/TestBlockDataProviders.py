#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from wrappers import SpellbookWrapper as SpellbookWrapper
import difflib


#local parameters, these will need to be changed
url = 'http://localhost:34080'
key = 'GW8S1SV40FG4TPDI'
secret = 'EI5IJJBTVL6YGWNE'

#test parameters
address = '1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8'
xpub = 'xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD'
txid = '39bb5f5d50882227f93b980df15ea676414f0363770a0174a13c8f55c877b598'
addresses = ['1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y',
             '1SansacmMr38bdzGkzruDVajEsZuiZHx9',
             '1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8']


def compare_data(response_list):
    if len(response_list) >= 2:
        result = 'OK'
        baseline = response_list[0]

        for response in response_list:
            if baseline != response:
                result = 'Not OK !!!!!!!!!!!!!!'
                difference(baseline, response)

        print result


def difference(a, b):
    print('{} => {}'.format(a, b))
    for counter, s in enumerate(difflib.ndiff(str(a), str(b))):
        if s[0] == ' ':
            continue
        elif s[0] == '-':
            print(u'Delete "{}" from position {}'.format(s[-1], counter))
        elif s[0] == '+':
            print(u'Add "{}" to position {}'.format(s[-1], counter))


api = SpellbookWrapper.SpellbookWrapper(url).blockdata()
print api.save_provider('Blocktrail.com', 0, 'Blocktrail.com', 'a8a84ed2929da8313d75d16e04be2a26c4cc4ea4', key, secret)
print api.save_provider('Blockchain.info', 1, 'Blockchain.info', '', key, secret)
print api.save_provider('Blockexplorer.com', 2, 'Insight', 'https://www.blockexplorer.com/api', key, secret)
print api.save_provider('Bitpay.com', 3, 'Insight', 'https://insight.bitpay.com/api', key, secret)


print '=============get providers========================'
providers = api.get_providers()
providerNames = []
for i in range(0, len(providers['providersList'])):
    providerNames.append(providers['providersList'][i]['name'])

print providerNames


print '===============block======================'
blockData = []
for i in range(0, len(providerNames)):
    data = api.block(350000, providerNames[i])
    if 'success' in data and data['success'] == 1:
        blockData.append(data['block'])
        print blockData[i]
    else:
        print providerNames[i] + ' failed!!'

compare_data(blockData)


print '==============latest_block======================='
latestBlockData = []
for i in range(0, len(providerNames)):
    data = api.latest_block(providerNames[i])
    if 'success' in data and data['success'] == 1:
        latestBlockData.append(data['latest_block'])
        print latestBlockData[i]
    else:
        print providerNames[i] + ' failed!!'

compare_data(latestBlockData)


print '===============prime_input_address======================'
primeInputAddressData = []
for i in range(0, len(providerNames)):
    data = api.prime_input_address(txid, providerNames[i])
    if 'success' in data and data['success'] == 1:
        primeInputAddressData.append(data['PrimeInputAddress'])
        print primeInputAddressData[i]
    else:
        print providerNames[i] + ' failed!!'

compare_data(primeInputAddressData)


print '================transactions====================='
transactionsData = []
for i in range(0, len(providerNames)):
    data = api.transactions(address, providerNames[i])
    if 'success' in data and data['success'] == 1:
        transactionsData.append(data['txs'])
        print transactionsData[i]
    else:
        print providerNames[i] + ' failed!!'

compare_data(transactionsData)


print '================balances====================='
balancesData = []
for i in range(0, len(providerNames)):
    data = api.balances(addresses, providerNames[i])
    if 'success' in data and data['success'] == 1:
        balancesData.append(data['balances'])
        print balancesData[i]
    else:
        print providerNames[i] + ' failed!!'

compare_data(balancesData)


print '================utxos====================='
utxosData = []
for i in range(0, len(providerNames)):
    data = api.utxos(addresses, providerNames[i])
    if 'success' in data and data['success'] == 1:
        utxosData.append(data['UTXOs'])
        print utxosData[i]
    else:
        print providerNames[i] + ' failed!!'

compare_data(utxosData)
