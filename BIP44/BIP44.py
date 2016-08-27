import bitcoin
from binascii import hexlify, unhexlify
import json
import urllib2
from pprint import pprint
import time

HARDENED = 2**31


def _bundle_addresses(addresses):
    bundle = ''
    for address in addresses:
        bundle += address + '|'

    bundle = bundle[:-1]
    return bundle


class Wallet():
    def __init__(self, mnemonic, passphrase="", account=0, n=100):
        self.mnemonic = mnemonic
        self.passphrase = passphrase
        self.account = account
        self.xpub_keys = getXPUBKeys(self.mnemonic, self.passphrase, account+1)
        self.xpriv_keys = getXPRIVKeys(self.mnemonic, self.passphrase, account+1)

        self.n = n
        self.addresses = getAddressesFromXPUB(self.xpub_keys[account], self.n)
        self.change_addresses = getChangeAddressesFromXPUB(self.xpub_keys[account], self.n)
        #showDetails(self.mnemonic, self.passphrase, 3)

    def scan(self):
        unspent_outputs = {}
        bundle_size = 200
        k = 0
        for addressList in [self.addresses, self.change_addresses]:
            i = 0
            while i < self.n:
                chuck = addressList[i:i+bundle_size]

                url = 'https://blockchain.info/multiaddr?active={0}'.format(_bundle_addresses(chuck))
                ret = urllib2.urlopen(urllib2.Request(url))
                data = json.loads(ret.read())

                for j in range(0, len(data['addresses'])):
                    if data['addresses'][j]['final_balance'] > 0:
                        key_index = addressList.index(data['addresses'][j]['address'])
                        private_key = getPrivKey(self.xpriv_keys[self.account], key_index, k)
                        unspent_outputs[data['addresses'][j]['address']] = {'value': data['addresses'][j]['final_balance'],
                                                                            'i': key_index,
                                                                            'private_key': private_key[data['addresses'][j]['address']],
                                                                            'change': k,
                                                                            "account": self.account}

                i += bundle_size
                time.sleep(1)

            k += 1

        pprint(unspent_outputs)

        total_value = 0
        for address in unspent_outputs:
            total_value += unspent_outputs[address]['value']

        print 'Total value:', total_value/1e8, 'BTC'

        return unspent_outputs



    def sweep(self, to_address):
        pass


def getAddressFromXPUB(xpub, i):
    pub0 = bitcoin.bip32_ckd(xpub, 0)
    public_key = bitcoin.bip32_ckd(pub0, i)
    hex_key = bitcoin.encode_pubkey(bitcoin.bip32_extract_key(public_key), 'hex_compressed')
    address = bitcoin.pubtoaddr(hex_key)

    return address


def getAddressesFromXPUB(xpub, i=100):
    address_list = []
    pub0 = bitcoin.bip32_ckd(xpub, 0)

    for i in range(0, i):
        public_key = bitcoin.bip32_ckd(pub0, i)
        hex_key = bitcoin.encode_pubkey(bitcoin.bip32_extract_key(public_key), 'hex_compressed')
        address_from_public_key = bitcoin.pubtoaddr(hex_key)
        address_list.append(address_from_public_key)

    return address_list


def getChangeAddressesFromXPUB(xpub, i=100):
    address_list = []
    pub0 = bitcoin.bip32_ckd(xpub, 1)

    for i in range(0, i):
        public_key = bitcoin.bip32_ckd(pub0, i)
        hex_key = bitcoin.encode_pubkey(bitcoin.bip32_extract_key(public_key), 'hex_compressed')
        address_from_public_key = bitcoin.pubtoaddr(hex_key)
        address_list.append(address_from_public_key)

    return address_list


def getXPRIVKeys(mnemonic, passphrase="", i=1):

    seed = hexlify(bitcoin.mnemonic_to_seed(mnemonic, passphrase=passphrase))
    private_key = bitcoin.bip32_master_key(unhexlify(seed))
    xprivs = []
    for i in range(0, i):
        derived_private_key = bitcoin.bip32_ckd(bitcoin.bip32_ckd(bitcoin.bip32_ckd(private_key, 44+HARDENED), HARDENED), HARDENED+i)
        xprivs.append(derived_private_key)

    return xprivs


def get_xpriv_key(mnemonic, passphrase="", account=0):
    seed = hexlify(bitcoin.mnemonic_to_seed(mnemonic, passphrase=passphrase))
    master_key = bitcoin.bip32_master_key(unhexlify(seed))
    xpriv_key = bitcoin.bip32_ckd(bitcoin.bip32_ckd(bitcoin.bip32_ckd(master_key, 44+HARDENED), HARDENED), HARDENED+account)

    return xpriv_key


def getPrivKey(xpriv, i, k=0):
    private_keys = {}
    priv0 = bitcoin.bip32_ckd(xpriv, k)

    private_key = bitcoin.bip32_ckd(priv0, i)
    wif_key = bitcoin.encode_privkey(bitcoin.bip32_extract_key(private_key), 'wif_compressed')
    address_from_private_key = bitcoin.privtoaddr(wif_key)
    private_keys[address_from_private_key] = wif_key

    return private_keys


def getXPUBKeys(mnemonic, passphrase="", i=1):

    seed = hexlify(bitcoin.mnemonic_to_seed(mnemonic, passphrase=passphrase))
    priv = bitcoin.bip32_master_key(unhexlify(seed))
    xpubs = []
    for i in range(0, i):
        derived_private_key = bitcoin.bip32_ckd(bitcoin.bip32_ckd(bitcoin.bip32_ckd(priv, 44+HARDENED), HARDENED), HARDENED+i)
        xpub = bitcoin.bip32_privtopub(derived_private_key)
        xpubs.append(xpub)

    return xpubs


def get_xpub_key(mnemonic, passphrase="", account=0):
    xpriv_key = get_xpriv_key(mnemonic=mnemonic, passphrase=passphrase, account=account)
    xpub_key = bitcoin.bip32_privtopub(xpriv_key)
    return xpub_key


def showDetails(mnemonic, passphrase="", i=1):

    seed = hexlify(bitcoin.mnemonic_to_seed(mnemonic, passphrase=passphrase))
    print 'Seed:\t\t\t\t', seed

    priv = bitcoin.bip32_master_key(unhexlify(seed))
    print 'Xpriv:\t\t\t\t', priv

    key = bitcoin.encode_privkey(bitcoin.bip32_extract_key(priv), 'wif_compressed')
    print 'Key:\t\t\t\t', key

    pub = bitcoin.bip32_privtopub(priv)
    print 'Derived public key:\t', pub
    pub_hex = bitcoin.bip32_extract_key(pub)
    print 'public key (hex):\t', pub_hex
    print 'Master Key address:\t', bitcoin.pubtoaddr(pub_hex)

    print ""
    print "TREZOR Keys:"

    account = 0
    derived_private_key = bitcoin.bip32_ckd(bitcoin.bip32_ckd(bitcoin.bip32_ckd(priv, 44+HARDENED), HARDENED), HARDENED+account)
    print 'Derived private key:', derived_private_key

    private_key = bitcoin.encode_privkey(bitcoin.bip32_extract_key(derived_private_key), 'wif_compressed')
    print 'private key (wif):\t', private_key

    derived_public_key = bitcoin.bip32_privtopub(derived_private_key)
    print 'Derived public key:', derived_public_key

    public_key_hex = bitcoin.privtopub(private_key)
    print 'public key (hex):\t', public_key_hex

    address = bitcoin.pubtoaddr(public_key_hex)
    print 'address:\t\t\t', address

    print ""
    print "Account public keys (XPUB)"
    xpubs = []
    for i in range(0, i):
        derived_private_key = bitcoin.bip32_ckd(bitcoin.bip32_ckd(bitcoin.bip32_ckd(priv, 44+HARDENED), HARDENED), HARDENED+i)
        xpub = bitcoin.bip32_privtopub(derived_private_key)
        print 'Account', i, 'xpub:', xpub
        xpubs.append(xpub)

    return xpubs



