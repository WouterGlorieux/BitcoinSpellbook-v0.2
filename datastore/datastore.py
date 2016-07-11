
from google.appengine.ext import ndb

TRANSACTION_FEE = 10000 #in Satoshis


class APIKeys(ndb.Model):
    api_key = ndb.StringProperty(indexed=True, default='')
    api_secret = ndb.StringProperty(indexed=True, default='')


class Parameters(ndb.Model):
    HDForwarder_walletseed = ndb.StringProperty(indexed=False, default="")
    DistributeBTC_walletseed = ndb.StringProperty(indexed=False, default="")


class Forwarder(ndb.Model):
    addressType = ndb.StringProperty(choices=['BIP44', 'PrivKey'], default='BIP44')
    walletIndex = ndb.IntegerProperty(indexed=True, default=0)
    privateKey = ndb.StringProperty(indexed=False, default='')
    creator = ndb.StringProperty(default='')
    creatorEmail = ndb.StringProperty(default='')
    address = ndb.StringProperty(indexed=True, default='')
    xpub = ndb.StringProperty(indexed=True, default='')
    minimumAmount = ndb.IntegerProperty(default=0)
    date = ndb.DateTimeProperty(auto_now_add=True)
    description = ndb.TextProperty(default='')
    youtube = ndb.StringProperty(default='')
    status = ndb.StringProperty(choices=['Pending', 'Active', 'Disabled'], default='Pending')
    visibility = ndb.StringProperty(choices=['Public', 'Private'], default='Private')
    feePercent = ndb.FloatProperty(default=0.0)
    feeAddress = ndb.StringProperty(default='')
    confirmAmount = ndb.IntegerProperty(indexed=False, default=0)
    maxTransactionFee = ndb.IntegerProperty(default=TRANSACTION_FEE)

def forwarders_key():
    #Constructs a Datastore key for a Forwarder entity
    return ndb.Key('HDForwarder', 'HDForwarder')


class Distributer(ndb.Model):
    addressType = ndb.StringProperty(choices=['BIP44', 'PrivKey'], default='BIP44')
    walletIndex = ndb.IntegerProperty(indexed=True, default=0)
    privateKey = ndb.StringProperty(indexed=False, default='')
    creator = ndb.StringProperty(default='')
    creatorEmail = ndb.StringProperty(default='')
    address = ndb.StringProperty(indexed=True)
    distributionSource = ndb.StringProperty(choices=['Custom', 'SIL', 'LBL', 'LRL', 'LSL'], default='Custom')
    distribution = ndb.JsonProperty(default=[])
    registrationAddress = ndb.StringProperty(default='')
    registrationXPUB = ndb.StringProperty(default='')
    registrationBlockHeight = ndb.IntegerProperty(default=0)
    threshold = ndb.IntegerProperty(default=0)
    minimumAmount = ndb.IntegerProperty(default=0)
    date = ndb.DateTimeProperty(auto_now_add=True)
    description = ndb.TextProperty(default='')
    youtube = ndb.StringProperty(default='')
    status = ndb.StringProperty(choices=['Pending', 'Active', 'Disabled'], default='Pending')
    visibility = ndb.StringProperty(choices=['Public', 'Private'], default='Private')
    maxTransactionFee = ndb.IntegerProperty(default=TRANSACTION_FEE)
    feePercent = ndb.FloatProperty(default=0.0)
    feeAddress = ndb.StringProperty(default='')


def distributers_key():
    #Constructs a Datastore key for a Distributer entity
    return ndb.Key('DistributeBTC', 'DistributeBTC')