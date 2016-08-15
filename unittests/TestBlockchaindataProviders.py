

from wrappers import SpellbookWrapper
import difflib



#local parameters, these will need to be changed
url = 'http://localhost:33080'
key = '2B5PVW4I6O6TN5SJ'
secret = '3I97DV6TQOWF6DD1'

#test parameters
address = '1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8'
xpub = 'xpub6CUvzHsNLcxthhGJesNDPSh2gicdHLPAAeyucP2KW1vBKEMxvDWCYRJZzM4g7mNiQ4Zb9nG4y25884SnYAr1P674yQipYLU8pP5z8AmahmD'
txid = '39bb5f5d50882227f93b980df15ea676414f0363770a0174a13c8f55c877b598'
addresses = ['1Robbk6PuJst6ot6ay2DcVugv8nxfJh5y', '1SansacmMr38bdzGkzruDVajEsZuiZHx9', '1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8']


def compareData(data):
    if len(data) >= 2:
        result = 'OK'
        baseline = data[0]

        for i in range(1, len(data)):
            if baseline != data[i]:
                result = 'Not OK !!!!!!!!!!!!!!'
                difference(baseline, data[i])

        print result

def difference(a, b):
    print('{} => {}'.format(a,b))
    for i,s in enumerate(difflib.ndiff(str(a), str(b))):
        if s[0]==' ': continue
        elif s[0]=='-':
            print(u'Delete "{}" from position {}'.format(s[-1],i))
        elif s[0]=='+':
            print(u'Add "{}" to position {}'.format(s[-1],i))




api = SpellbookWrapper.SpellbookWrapper(url).BlockchainData()


print '=============get providers========================'
providers = api.getProviders()
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

compareData(blockData)


print '==============latestBlock======================='
latestBlockData = []
for i in range(0, len(providerNames)):
    data = api.latestBlock(providerNames[i])
    if 'success' in data and data['success'] == 1:
        latestBlockData.append(data['latestBlock'])
        print latestBlockData[i]
    else:
        print providerNames[i] + ' failed!!'

compareData(latestBlockData)



print '===============primeInputAddress======================'
primeInputAddressData = []
for i in range(0, len(providerNames)):
    data = api.primeInputAddress(txid, providerNames[i])
    if 'success' in data and data['success'] == 1:
        primeInputAddressData.append(data['PrimeInputAddress'])
        print primeInputAddressData[i]
    else:
        print providerNames[i] + ' failed!!'

compareData(primeInputAddressData)


print '================transactions====================='
transactionsData = []
for i in range(0, len(providerNames)):
    data = api.transactions(address, providerNames[i])
    if 'success' in data and data['success'] == 1:
        transactionsData.append(data['TXS'])
        print transactionsData[i]
    else:
        print providerNames[i] + ' failed!!'

compareData(transactionsData)



print '================balances====================='
balancesData = []
for i in range(0, len(providerNames)):
    data = api.balances(addresses, providerNames[i])
    if 'success' in data and data['success'] == 1:
        balancesData.append(data['balances'])
        print balancesData[i]
    else:
        print providerNames[i] + ' failed!!'

compareData(balancesData)



print '================utxos====================='
utxosData = []
for i in range(0, len(providerNames)):
    data = api.utxos(addresses, providerNames[i])
    if 'success' in data and data['success'] == 1:
        utxosData.append(data['UTXOs'])
        print utxosData[i]
    else:
        print providerNames[i] + ' failed!!'

compareData(utxosData)
