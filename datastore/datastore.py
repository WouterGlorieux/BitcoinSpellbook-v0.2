
from google.appengine.ext import ndb


class APIKeys(ndb.Model):
    api_key = ndb.StringProperty(indexed=True, default='')
    api_secret = ndb.StringProperty(indexed=True, default='')


class Parameters(ndb.Model):
    HDForwarder_walletseed = ndb.StringProperty(indexed=False, default="")


class Forwarder(ndb.Model):
    userID = ndb.StringProperty(indexed=True)
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

def forwarders_key():
    #Constructs a Datastore key for a Forwarder entity
    return ndb.Key('HDForwarder', 'HDForwarder')
