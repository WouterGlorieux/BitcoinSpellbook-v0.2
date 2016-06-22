
import logging



from google.appengine.ext import ndb
from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(60)

import blockexplorers.Blocktrail_com as Blocktrail_com
import blockexplorers.Blockchain_info as Blockchain_info
import blockexplorers.Insight as Insight

from validators import validators as validator


class Providers(ndb.Model):
    #Model for 3rd party data providers parameters
    priority = ndb.IntegerProperty(indexed=True, default=0)
    providerType = ndb.StringProperty(indexed=True, choices=['Blocktrail.com', 'Blockchain.info', 'Insight'], default='Blocktrail.com')
    blocktrail_key = ndb.StringProperty(indexed=False, default="")
    insight_url = ndb.StringProperty(indexed=False, default="")


def getProviderAPI(name):
    provider = Providers.get_by_id(name)

    if provider and provider.providerType == 'Blocktrail.com':
        providerAPI = Blocktrail_com.API(provider.blocktrail_key)
    elif provider and provider.providerType == 'Blockchain.info':
        providerAPI = Blockchain_info.API()
    elif provider and  provider.providerType == 'Insight':
        providerAPI = Insight.API(provider.insight_url)
    else:
        providerAPI = None

    return providerAPI

def getProviderNames():
    providers_query = Providers.query().order(Providers.priority)
    providers = providers_query.fetch()

    providerNames = []
    for provider in providers:
        providerNames.append(provider.key.string_id())

    return providerNames


def getProvidersList():
    providers_query = Providers.query().order(Providers.priority)
    providers = providers_query.fetch()

    providersList = []
    for provider in providers:
        tmpProvider = {}
        tmpProvider['name'] = provider.key.string_id()
        tmpProvider['priority'] = provider.priority
        tmpProvider['providerType'] = provider.providerType
        if provider.providerType == 'Blocktrail.com':
            tmpProvider['Blocktrail_key'] = provider.blocktrail_key
        elif provider.providerType == 'Insight':
            tmpProvider['Insight_url'] = provider.insight_url

        providersList.append(tmpProvider)

    return providersList

def saveProvider(name, priority, providerType, param=''):

    provider = Providers.get_or_insert(name)
    provider.priority = priority
    provider.providerType = providerType

    providerDict = {}
    providerDict['name'] = name
    providerDict['priority'] = priority
    providerDict['providerType'] = providerType

    if providerType == 'Blocktrail.com':
        provider.blocktrail_key = param
        providerDict['blocktrail_key'] = param
    elif providerType == 'Insight':
        provider.insight_url = param
        providerDict['insight_url'] = param

    try:
        provider.put()
        return True

    except:
        return False


def deleteProvider(name):
    try:
        provider = Providers.get_by_id(name)
        provider.key.delete()
        return True
    except:
        return False


def query(queryType, param='', provider=''):
    response = {'success': 0}
    providers = getProviderNames()

    if provider != '' and provider in providers:
        providers = [provider]
    elif provider != '':
        response['error'] = 'Unknown data provider.'
        return response

    for i in range(0, len(providers)):
        providerAPI = getProviderAPI(providers[i])
        if providerAPI:
            data = {}
            if queryType == 'block':
                data = providerAPI.getBlock(param)
            elif queryType == 'latestBlock':
                data = providerAPI.getLatestBlock()
            elif queryType == 'primeInputAddress':
                data = providerAPI.getPrimeInputAddress(param)
            elif queryType == 'balances':
                data = providerAPI.getBalances(param)
            elif queryType == 'transactions':
                data = providerAPI.getTXS(param)
            elif queryType == 'utxos':
                data = providerAPI.getUTXOs(param)

            if 'success' in data and data['success'] == 1:
                response = data
                response['provider'] = providers[i]
                break
            else:
                message = str(providers[i]) + 'failed to provide data for query: ' + str(queryType)
                if param != '':
                    message += ' param: ' + str(param)
                logging.warning(message)


    if response['success'] == 0 and provider == '':
        response['error'] = 'All data providers failed.'
    elif response['success'] == 0 and provider != '':
        response['error'] = provider + ' failed to provide data.'



    return response


def Block(blockHeight, provider=''):
    response = {'success': 0}
    if isinstance(blockHeight, int) and blockHeight >= 0:
        response = query('block', blockHeight, provider)
    else:
        response['error'] = 'blockHeight must be a positive integer.'

    return response



def LatestBlock(provider=''):
    response = query('latestBlock', '', provider)
    return response

def PrimeInputAddress(txid, provider=''):
    response = {'success': 0}
    if validator.validTxid(txid):
        response = query('primeInputAddress', txid, provider)
    else:
        response['error'] = 'Invalid txid'

    return response


def Transactions(address, provider=''):
    response = {'success': 0}
    if validator.validAddress(address):
        response = query('transactions', address, provider)
    else:
        response['error'] = 'Invalid address'

    return response

def Balances(addresses, provider=''):
    response = {'success': 0}
    if validator.validAddresses(addresses):
        response = query('balances', addresses, provider)
    else:
        response['error'] = 'Invalid addresses'

    return response

def UTXOs(addresses, provider=''):
    response = {'success': 0}
    if validator.validAddresses(addresses):
        response = query('utxos', addresses, provider)
    else:
        response['error'] = 'Invalid addresses'

    return response



def TXS2JSON(self, TXS, address):
    jsonObj = []
    for i in range(0, len(TXS)):
        tx = TXS[i]
        jsonObj.append(tx.toDict(address))
    return jsonObj




