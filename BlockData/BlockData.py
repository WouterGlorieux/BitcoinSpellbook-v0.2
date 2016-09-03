#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from google.appengine.api import urlfetch
urlfetch.set_default_fetch_deadline(60)

import datastore.datastore as datastore
import blockexplorers.Blocktrail_com as Blocktrail_com
import blockexplorers.Blockchain_info as Blockchain_info
import blockexplorers.Insight as Insight
from validators import validators as validator


def get_provider_api(name):
    provider = datastore.Providers.get_by_id(name)

    if provider and provider.provider_type == 'Blocktrail.com':
        provider_api = Blocktrail_com.API(provider.blocktrail_key)
    elif provider and provider.provider_type == 'Blockchain.info':
        provider_api = Blockchain_info.API()
    elif provider and provider.provider_type == 'Insight':
        provider_api = Insight.API(provider.insight_url)
    else:
        provider_api = None

    return provider_api


def get_provider_names():
    providers_query = datastore.Providers.query().order(datastore.Providers.priority)
    providers = providers_query.fetch()

    provider_names = []
    for provider in providers:
        provider_names.append(provider.key.string_id())

    return provider_names


def get_providers():
    providers_query = datastore.Providers.query().order(datastore.Providers.priority)
    providers = providers_query.fetch()

    providers_list = []
    for provider in providers:
        tmp_provider = {'name': provider.key.string_id(),
                        'priority': provider.priority,
                        'provider_type': provider.provider_type}

        if provider.provider_type == 'Blocktrail.com':
            tmp_provider['blocktrail_key'] = provider.blocktrail_key
        elif provider.provider_type == 'Insight':
            tmp_provider['insight_url'] = provider.insight_url

        providers_list.append(tmp_provider)

    return providers_list


def save_provider(name, priority, provider_type, param=''):

    provider = datastore.Providers.get_or_insert(name)
    provider.priority = priority
    provider.provider_type = provider_type

    if provider_type == 'Blocktrail.com':
        provider.blocktrail_key = param
    elif provider_type == 'Insight':
        provider.insight_url = param

    try:
        provider.put()
        return True
    except Exception as ex:
        logging.warning(str(ex))
        return False


def delete_provider(name):
    try:
        provider = datastore.Providers.get_by_id(name)
        provider.key.delete()
        return True
    except Exception as ex:
        logging.warning(str(ex))
        return False


def query(query_type, param='', provider=''):
    response = {'success': 0}
    providers = get_provider_names()

    if provider != '' and provider in providers:
        providers = [provider]
    elif provider != '':
        response['error'] = 'Unknown data provider.'
        return response

    for i in range(0, len(providers)):
        provider_api = get_provider_api(providers[i])
        if provider_api:
            data = {}
            if query_type == 'block':
                data = provider_api.get_block(param)
            elif query_type == 'latest_block':
                data = provider_api.get_latest_block
            elif query_type == 'prime_input_address':
                data = provider_api.get_prime_input_address(param)
            elif query_type == 'balances':
                data = provider_api.get_balances(param)
            elif query_type == 'transactions':
                data = provider_api.get_txs(param)
            elif query_type == 'utxos':
                data = provider_api.get_utxos(param)

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
    if validator.valid_block_height(block_height):
        response = query('block', block_height, provider)
    else:
        response['error'] = 'block_height must be a positive integer.'

    return response


def latest_block(provider=''):
    response = query('latest_block', '', provider)
    return response


def prime_input_address(txid, provider=''):
    response = {'success': 0}
    if validator.valid_txid(txid):
        response = query('prime_input_address', txid, provider)
    else:
        response['error'] = 'Invalid txid'

    return response


def transactions(address, provider=''):
    response = {'success': 0}
    if validator.valid_address(address):
        response = query('transactions', address, provider)
    else:
        response['error'] = 'Invalid address'

    if 'success' in response and response['success'] == 1:
        response['txs'] = sorted(response['txs'], key=lambda k: (k['block_height'], k['txid']))

    return response


def balances(addresses, provider=''):
    response = {'success': 0}
    if validator.valid_addresses(addresses):
        response = query('balances', addresses, provider)
    else:
        response['error'] = 'Invalid addresses'

    return response


def utxos(addresses, provider=''):
    response = {'success': 0}
    if validator.valid_addresses(addresses):
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
        json_obj.append(tx.to_dict(address))
    return json_obj
