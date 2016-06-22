import re

def validAddress(address):
    valid = False
    if re.match("^[13][a-km-zA-HJ-NP-Z0-9]{26,33}$", address):
        valid = True

    return valid

def validAddresses(addresses):
    valid = False
    for address in addresses.split("|"):
        if validAddress(address):
            valid = True
        else:
            valid = False
            break

    return valid


def validTxid(txid):
    valid = False
    try:
        int(txid, 16)
        valid = True
    except ValueError:
        valid = False

    if len(txid) != 64:
        valid = False

    return valid
