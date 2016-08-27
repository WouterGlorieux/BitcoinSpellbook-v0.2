
import logging



from google.appengine.ext import ndb
from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(60)

import datastore.datastore as datastore
import blockexplorers.Blocktrail_com as Blocktrail_com
import blockexplorers.Blockchain_info as Blockchain_info
import blockexplorers.Insight as Insight

from validators import validators as validator


def getProviderAPI(name):
    provider = datastore.Providers.get_by_id(name)

    if provider and provider.providerType == 'Blocktrail.com':
        provider_api = Blocktrail_com.API(provider.blocktrail_key)
    elif provider and provider.providerType == 'Blockchain.info':
        provider_api = Blockchain_info.API()
    elif provider and provider.providerType == 'Insight':
        provider_api = Insight.API(provider.insight_url)
    else:
        provider_api = None

    return provider_api


def getProviderNames():
    providers_query = datastore.Providers.query().order(datastore.Providers.priority)
    providers = providers_query.fetch()

    provider_names = []
    for provider in providers:
        provider_names.append(provider.key.string_id())

    return provider_names


def getProvidersList():
    providers_query = datastore.Providers.query().order(datastore.Providers.priority)
    providers = providers_query.fetch()

    providers_list = []
    for provider in providers:
        tmp_provider = {'name': provider.key.string_id(),
                        'priority': provider.priority,
                        'providerType': provider.providerType}

        if provider.providerType == 'Blocktrail.com':
            tmp_provider['Blocktrail_key'] = provider.blocktrail_key
        elif provider.providerType == 'Insight':
            tmp_provider['Insight_url'] = provider.insight_url

        providers_list.append(tmp_provider)

    return providers_list


def saveProvider(name, priority, provider_type, param=''):

    provider = datastore.Providers.get_or_insert(name)
    provider.priority = priority
    provider.providerType = provider_type

    if provider_type == 'Blocktrail.com':
        provider.blocktrail_key = param
    elif provider_type == 'Insight':
        provider.insight_url = param

    try:
        provider.put()
        return True
    except Exception:
        return False


def deleteProvider(name):
    try:
        provider = datastore.Providers.get_by_id(name)
        provider.key.delete()
        return True
    except:
        return False


def query(query_type, param='', provider=''):
    response = {'success': 0}
    providers = getProviderNames()

    if provider != '' and provider in providers:
        providers = [provider]
    elif provider != '':
        response['error'] = 'Unknown data provider.'
        return response

    for i in range(0, len(providers)):
        provider_api = getProviderAPI(providers[i])
        if provider_api:
            data = {}
            if query_type == 'block':
                data = provider_api.getBlock(param)
            elif query_type == 'latestBlock':
                data = provider_api.getLatestBlock()
            elif query_type == 'primeInputAddress':
                data = provider_api.getPrimeInputAddress(param)
            elif query_type == 'balances':
                data = provider_api.getBalances(param)
            elif query_type == 'transactions':
                data = provider_api.getTXS(param)
            elif query_type == 'utxos':
                data = provider_api.getUTXOs(param)

            if 'success' in data and data['success'] == 1:
                response = data
                response['provider'] = providers[i]
                break
            else:
                message = '{0} failed to provide data for query: {1}'.format(str(providers[i]), str(query_type))
                if param != '':
                    message += ' param: ' + str(param)
                logging.warning(message)

    if response['success'] == 0 and provider == '':
        response['error'] = 'All data providers failed.'
    elif response['success'] == 0 and provider != '':
        response['error'] = provider + ' failed to provide data.'

    return response


def block(block_height, provider=''):
    response = {'success': 0}
    if validator.validBlockHeight(block_height):
        response = query('block', block_height, provider)
    else:
        response['error'] = 'block_height must be a positive integer.'

    return response


def latestBlock(provider=''):
    response = query('latestBlock', '', provider)
    return response


def primeInputAddress(txid, provider=''):
    response = {'success': 0}
    if validator.validTxid(txid):
        response = query('primeInputAddress', txid, provider)
    else:
        response['error'] = 'Invalid txid'

    return response


def transactions(address, provider=''):
    response = {'success': 0}
    if validator.validAddress(address):
        response = query('transactions', address, provider)
    else:
        response['error'] = 'Invalid address'

    if 'success' in response and response['success'] == 1:
        response['TXS'] = sorted(response['TXS'], key=lambda k: (k['block_height'], k['txid']))

    return response


def balances(addresses, provider=''):
    response = {'success': 0}
    if validator.validAddresses(addresses):
        response = query('balances', addresses, provider)
    else:
        response['error'] = 'Invalid addresses'

    return response


def utxos(addresses, provider=''):
    response = {'success': 0}
    if validator.validAddresses(addresses):
        response = query('utxos', addresses, provider)
    else:
        response['error'] = 'Invalid addresses'

    if 'success' in response and response['success'] == 1:
        response['UTXOs'] = sorted(response['UTXOs'], key=lambda k: (k['address'], k['block_height'], k['output']))

    return response


def txs_2_json(txs, address):
    json_obj = []
    for i in range(0, len(txs)):
        tx = txs[i]
        json_obj.append(tx.toDict(address))
    return json_obj
