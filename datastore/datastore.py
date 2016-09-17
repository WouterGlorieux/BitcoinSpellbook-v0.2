#!/usr/bin/env python
# -*- coding: utf-8 -*-

from google.appengine.api import mail
from google.appengine.ext import ndb
from BIP44 import BIP44
import logging


MAX_TRANSACTION_FEE = 10000  # in Satoshis


class Services(object):
    default = 0
    blockforward_by_name = 1
    blockforward_by_index = 2
    blockdistribute_by_name = 3
    blockdistribute_by_index = 4
    blockwriter_by_name = 5
    blockwriter_by_index = 6
    blocktrigger_by_name = 7
    blocktrigger_by_index = 8

    names = ['Default',
             'NamedForward', 'IndexedForward',
             'NamedDistribute', 'IndexedDistribute',
             'NamedWriter', 'IndexedWriter',
             'NamedTrigger', 'IndexedTrigger']


class APIKeys(ndb.Model):
    api_key = ndb.StringProperty(indexed=True, default='')
    api_secret = ndb.StringProperty(indexed=True, default='')


class Parameters(ndb.Model):
    master_seed = ndb.StringProperty(indexed=False, default="")
    mail_from = ndb.StringProperty(indexed=False, default="Bitcoin Spellbook <wouter.glorieux@gmail.com>")
    optimal_fee_per_kb = ndb.IntegerProperty(indexed=False, default=0)


class Providers(ndb.Model):
    #Model for 3rd party data providers parameters
    priority = ndb.IntegerProperty(indexed=True, default=0)
    provider_type = ndb.StringProperty(indexed=True,
                                       choices=['Blocktrail.com', 'Blockchain.info', 'Insight'],
                                       default='Blocktrail.com')
    blocktrail_key = ndb.StringProperty(indexed=False, default="")
    insight_url = ndb.StringProperty(indexed=False, default="")


class Forwarder(ndb.Model):
    id_type = ndb.StringProperty(choices=['name', 'index'], default='name')
    address_type = ndb.StringProperty(choices=['BIP44', 'PrivKey'], default='BIP44')
    wallet_index = ndb.IntegerProperty(indexed=True, default=0)
    private_key = ndb.StringProperty(indexed=False, default='')
    creator = ndb.StringProperty(default='')
    creator_email = ndb.StringProperty(default='')
    address = ndb.StringProperty(indexed=True, default='')
    xpub = ndb.StringProperty(indexed=True, default='')
    minimum_amount = ndb.IntegerProperty(default=0)
    date = ndb.DateTimeProperty(auto_now_add=True)
    description = ndb.TextProperty(default='')
    youtube = ndb.StringProperty(default='')
    status = ndb.StringProperty(choices=['Pending', 'Active', 'Disabled'], default='Pending')
    visibility = ndb.StringProperty(choices=['Public', 'Private'], default='Private')
    fee_percentage = ndb.FloatProperty(default=0.0)
    fee_address = ndb.StringProperty(default='')
    confirm_amount = ndb.IntegerProperty(indexed=False, default=0)
    maximum_transaction_fee = ndb.IntegerProperty(default=MAX_TRANSACTION_FEE)


def forwarders_key():
    #Constructs a Datastore key for a Forwarder entity
    return ndb.Key('BlockForward', 'BlockForward')


class Distributer(ndb.Model):
    id_type = ndb.StringProperty(choices=['name', 'index'], default='name')
    address_type = ndb.StringProperty(choices=['BIP44', 'PrivKey'], default='BIP44')
    wallet_index = ndb.IntegerProperty(indexed=True, default=0)
    private_key = ndb.StringProperty(indexed=False, default='')
    creator = ndb.StringProperty(default='')
    creator_email = ndb.StringProperty(default='')
    address = ndb.StringProperty(indexed=True)
    distribution_source = ndb.StringProperty(choices=['Custom', 'SIL', 'LBL', 'LRL', 'LSL'], default='Custom')
    distribution = ndb.JsonProperty(default=[])
    registration_address = ndb.StringProperty(default='')
    registration_xpub = ndb.StringProperty(default='')
    registration_block_height = ndb.IntegerProperty(default=0)
    threshold = ndb.IntegerProperty(default=0)
    minimum_amount = ndb.IntegerProperty(default=0)
    date = ndb.DateTimeProperty(auto_now_add=True)
    description = ndb.TextProperty(default='')
    youtube = ndb.StringProperty(default='')
    status = ndb.StringProperty(choices=['Pending', 'Active', 'Disabled'], default='Pending')
    visibility = ndb.StringProperty(choices=['Public', 'Private'], default='Private')
    maximum_transaction_fee = ndb.IntegerProperty(default=MAX_TRANSACTION_FEE)
    fee_percentage = ndb.FloatProperty(default=0.0)
    fee_address = ndb.StringProperty(default='')


def distributers_key():
    #Constructs a Datastore key for a Distributer entity
    return ndb.Key('BlockDistribute', 'BlockDistribute')


class Trigger(ndb.Model):
    trigger_type = ndb.StringProperty(choices=['Balance', 'Received', 'Sent', 'block_height'], default='Received')
    block_height = ndb.IntegerProperty(default=0)
    address = ndb.StringProperty(indexed=True, default='')
    amount = ndb.IntegerProperty(default=0)
    confirmations = ndb.IntegerProperty(default=0)
    triggered = ndb.BooleanProperty(default=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
    description = ndb.TextProperty(default='')
    youtube = ndb.StringProperty(default='')
    status = ndb.StringProperty(choices=['Pending', 'Active', 'Disabled'], default='Pending')
    visibility = ndb.StringProperty(choices=['Public', 'Private'], default='Private')
    creator = ndb.StringProperty(default='')
    creator_email = ndb.StringProperty(default='')


def triggers_key():
    #Constructs a Datastore key for a Trigger entity
    return ndb.Key('BlockTrigger', 'BlockTrigger')


class Action(ndb.Model):
    trigger = ndb.StringProperty(default='')
    action_type = ndb.StringProperty(choices=['reveal_text', 'reveal_link', 'send_mail', 'webhook'])
    description = ndb.TextProperty(default='')
    reveal_text = ndb.TextProperty(default='')
    reveal_link_text = ndb.StringProperty(default='')
    reveal_link_url = ndb.StringProperty(default='')
    reveal_allowed = ndb.BooleanProperty(default=False)
    mail_to = ndb.StringProperty(default='')
    mail_subject = ndb.StringProperty(default='')
    mail_body = ndb.TextProperty(default='')
    mail_sent = ndb.BooleanProperty(default=False)
    webhook = ndb.StringProperty(default='')
    webhook_activated = ndb.BooleanProperty(default=False)


def trigger_key(trigger):
    #Constructs a Datastore key for a Action entity
    return ndb.Key('Action', str(trigger.key.id()))


class Writer(ndb.Model):
    id_type = ndb.StringProperty(choices=['name', 'index'], default='name')
    message = ndb.StringProperty(default='')
    outputs = ndb.JsonProperty(default=[])
    amount = ndb.IntegerProperty(default=0)
    recommended_fee = ndb.IntegerProperty(default=0)
    maximum_transaction_fee = ndb.IntegerProperty(default=MAX_TRANSACTION_FEE)
    transaction_fee = ndb.IntegerProperty(default=0)
    total_amount = ndb.IntegerProperty(default=0)
    extra_value_address = ndb.StringProperty(indexed=True, default='')

    address = ndb.StringProperty(indexed=True, default='')
    address_type = ndb.StringProperty(choices=['BIP44', 'PrivKey'], default='BIP44')
    wallet_index = ndb.IntegerProperty(indexed=True, default=0)
    private_key = ndb.StringProperty(indexed=False, default='')
    status = ndb.StringProperty(choices=['Pending', 'Active', 'Disabled', 'Complete'], default='Pending')
    visibility = ndb.StringProperty(choices=['Public', 'Private'], default='Private')

    creator = ndb.StringProperty(default='')
    creator_email = ndb.StringProperty(default='')
    date = ndb.DateTimeProperty(auto_now_add=True)
    description = ndb.TextProperty(default='')
    youtube = ndb.StringProperty(default='')

    fee_percentage = ndb.FloatProperty(default=0.0)
    fee_address = ndb.StringProperty(default='')


def writers_key():
    #Constructs a Datastore key for a Writer entity
    return ndb.Key('BlockWriter', 'BlockWriter')


class WalletAddress(ndb.Model):
    service_account = ndb.IntegerProperty(indexed=True, default=None)
    service_name = ndb.StringProperty(indexed=True,
                                      choices=Services.names,
                                      default=None)
    address = ndb.StringProperty(indexed=True)
    i = ndb.IntegerProperty(indexed=True)
    k = ndb.IntegerProperty(indexed=True, default=0)
    status = ndb.StringProperty(indexed=True,
                                choices=['Available', 'InUse', 'Cooldown', 'Unavailable'],
                                default='InUse')
    balance = ndb.IntegerProperty(default=0)
    received = ndb.IntegerProperty(default=0)
    sent = ndb.IntegerProperty(default=0)
    cooldown_end = ndb.DateTimeProperty(auto_now_add=True)


def address_key():
    #Constructs a Datastore key for a WalletAddress entity
    return ndb.Key('WalletAddress', 'WalletAddress')


def consistency_check(module):
    success = True
    if module == 'BlockWriter':
        writers_query = Writer.query(Writer.status == 'Active', Writer.wallet_index != 0, ancestor=writers_key()).order(
            Writer.wallet_index)
        writers = writers_query.fetch()

        if len(writers) > 0:
            tmp_index = 0
            for i in range(0, len(writers)):
                if writers[i].wallet_index == tmp_index:
                    message = u'Warning: multiple active writers with same wallet_index! wallet_index = {0:d}'.format(
                        tmp_index)
                    logging.error(message)
                    parameters = Parameters.get_by_id('DefaultConfig')
                    mail.send_mail(parameters.mail_from,
                                   'wouter.glorieux@gmail.com',  # ToDo: add mail_to to parameters
                                   'BlockWriter consistency check failed!',
                                   message)
                    success = False

                tmp_index = writers[i].wallet_index

    return success


def get_service_address(service, index):
    parameters = Parameters.get_by_id('DefaultConfig')
    address = None
    if parameters.master_seed:
        xpub_key = BIP44.get_xpub_key(parameters.master_seed, '', service)
        address = BIP44.get_address_from_xpub(xpub_key, index)

    return address


def get_service_private_key(service, index):
    parameters = Parameters.get_by_id('DefaultConfig')
    private_key = None
    if parameters.master_seed:
        xpriv_key = BIP44.get_xpriv_key(parameters.master_seed, '', service)
        private_key = BIP44.get_private_key(xpriv_key, index)

    return private_key


def initialize_wallet_address(service, i):
    wallet_address = None
    if service in [Services.blockwriter_by_name, Services.blockwriter_by_index,
                   Services.blockforward_by_name, Services.blockforward_by_index,
                   Services.blockdistribute_by_name, Services.blockdistribute_by_index] and isinstance(i, (int, long)) and i >= 0:
        wallet_address = WalletAddress.get_or_insert("%s_%i" % (Services.names[service], i), parent=address_key())
        wallet_address.service_account = service
        wallet_address.service_name = Services.names[service]
        wallet_address.address = get_service_address(service, i)
        wallet_address.i = i
        wallet_address.k = 0

        # Don't allow index 0 to be used
        if i == 0:
            wallet_address.status = 'Unavailable'
        wallet_address.put()

    return wallet_address


def get_available_address_index(service):
    #check_active_addresses()
    wallet_address_query = WalletAddress.query(WalletAddress.service_name == Services.names[service],
                                               WalletAddress.status == 'Available',
                                               ancestor=address_key()).order(WalletAddress.i)
    wallet_address = wallet_address_query.fetch(limit=1)

    if len(wallet_address) == 1:
        index = wallet_address[0].i
        wallet_address[0].status = 'InUse'
        wallet_address[0].put()
    else:
        wallet_address_query = WalletAddress.query(WalletAddress.service_name == Services.names[service],
                                                   ancestor=address_key()).order(-WalletAddress.i)
        wallet_address = wallet_address_query.fetch(limit=1)
        if len(wallet_address) == 1:
            index = wallet_address[0].i+1
        else:
            index = 1

        wallet_address = initialize_wallet_address(service, index)
        if wallet_address:
            logging.info("Initialized new wallet address for service %s: %i %s" % (Services.names[service], index, wallet_address.address))

    return index


def cooldown_address(address):
    success = False
    wallet_address_query = WalletAddress.query(WalletAddress.address == address, ancestor=address_key())
    wallet_address = wallet_address_query.fetch(limit=1)
    if wallet_address:
        wallet_address[0].status = 'Cooldown'
        wallet_address[0].put()
        success = True

    return success