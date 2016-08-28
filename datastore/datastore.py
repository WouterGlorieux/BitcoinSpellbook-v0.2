from google.appengine.api import mail
from google.appengine.ext import ndb
from BIP44 import BIP44
import logging


MAX_TRANSACTION_FEE = 10000  # in Satoshis


class Services:
    BlockForward = 1
    BlockDistribute = 2
    BlockWriter = 3
    BlockTrigger = 4


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
    provider_type = ndb.StringProperty(indexed=True, choices=['Blocktrail.com', 'Blockchain.info', 'Insight'], default='Blocktrail.com')
    blocktrail_key = ndb.StringProperty(indexed=False, default="")
    insight_url = ndb.StringProperty(indexed=False, default="")


class Forwarder(ndb.Model):
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
    confirmAmount = ndb.IntegerProperty(indexed=False, default=0)
    maximum_transaction_fee = ndb.IntegerProperty(default=MAX_TRANSACTION_FEE)


def forwarders_key():
    #Constructs a Datastore key for a Forwarder entity
    return ndb.Key('BlockForward', 'BlockForward')


class Distributer(ndb.Model):
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
    registrationBlockHeight = ndb.IntegerProperty(default=0)
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
    triggerType = ndb.StringProperty(choices=['Balance', 'Received', 'Sent', 'BlockHeight'], default='Received')
    blockHeight = ndb.IntegerProperty(default=0)
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
    actionType = ndb.StringProperty(choices=['RevealText', 'RevealLink', 'SendMail', 'Webhook'])
    description = ndb.TextProperty(default='')
    revealText = ndb.TextProperty(default='')
    revealLinkText = ndb.StringProperty(default='')
    revealLinkURL = ndb.StringProperty(default='')
    revealAllowed = ndb.BooleanProperty(default=False)
    mailTo = ndb.StringProperty(default='')
    mailSubject = ndb.StringProperty(default='')
    mailBody = ndb.TextProperty(default='')
    mailSent = ndb.BooleanProperty(default=False)
    webhook = ndb.StringProperty(default='')
    webhookActivated = ndb.BooleanProperty(default=False)


def trigger_key(trigger):
    #Constructs a Datastore key for a Action entity
    return ndb.Key('Action', str(trigger.key.id()))


class Writer(ndb.Model):
    message = ndb.StringProperty(default='')
    outputs = ndb.JsonProperty(default=[])
    amount = ndb.IntegerProperty(default=0)
    recommendedFee = ndb.IntegerProperty(default=0)
    maximum_transaction_fee = ndb.IntegerProperty(default=MAX_TRANSACTION_FEE)
    transactionFee = ndb.IntegerProperty(default=0)
    totalAmount = ndb.IntegerProperty(default=0)
    extraValueAddress = ndb.StringProperty(indexed=True, default='')

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
    module = ndb.StringProperty(indexed=True, choices=[None, 'BlockWriter', 'BlockForwarder', 'BlockDistributer'], default=None)
    address = ndb.StringProperty(indexed=True)
    i = ndb.IntegerProperty(indexed=True)
    k = ndb.IntegerProperty(indexed=True, default=0)
    status = ndb.StringProperty(indexed=True, choices=['Available', 'InUse', 'Cooldown', 'Unavailable'], default='InUse')
    balance = ndb.IntegerProperty(default=0)
    received = ndb.IntegerProperty(default=0)
    sent = ndb.IntegerProperty(default=0)
    cooldownEnd = ndb.DateTimeProperty(auto_now_add=True)


def address_key():
    #Constructs a Datastore key for a WalletAddress entity
    return ndb.Key('WalletAddress', 'WalletAddress')


def consistencyCheck(module):
    success = True
    if module == 'BlockWriter':
        writers_query = Writer.query(Writer.status == 'Active', Writer.wallet_index != 0, ancestor=writers_key()).order(Writer.wallet_index)
        writers = writers_query.fetch()

        if len(writers) > 0:
            tmpIndex = 0
            for i in range(0, len(writers)):
                if writers[i].wallet_index == tmpIndex:
                    message = 'Consistency check failed: multiple active writers with same wallet_index! wallet_index = %i' % tmpIndex
                    logging.error(message)
                    parameters = Parameters.get_by_id('DefaultConfig')
                    mail.send_mail(parameters.mail_from, 'wouter.glorieux@gmail.com', 'BlockWriter consistency check failed!', message)
                    success = False

                tmpIndex = writers[i].wallet_index

    return success


def get_service_address(service, index):
    parameters = Parameters.get_by_id('DefaultConfig')
    address = None
    if parameters.master_seed:
        xpub_key = BIP44.get_xpub_key(parameters.master_seed, '', service)
        address = BIP44.getAddressFromXPUB(xpub_key, index)

    return address


def get_service_private_key(service, index):
    parameters = Parameters.get_by_id('DefaultConfig')
    private_key = None
    if parameters.master_seed:
        xpriv_key = BIP44.get_xpriv_key(parameters.master_seed, '', service)
        private_key = BIP44.getPrivKey(xpriv_key, index)

    return private_key