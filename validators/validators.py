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

def validXPUB(xpub):
    valid =False
    if xpub[:4] == "xpub":
        valid = True

    return valid

def validDescription(description):
    valid = False

    if isinstance(description, (str, unicode)) and len(description) <= 250:
        valid = True

    return valid

def validCreator(creator):
    valid = False

    if isinstance(creator, (str, unicode)) and len(creator) <= 50:
        valid = True

    return valid

def validEmail(email):
    valid = False
    if re.match(r"[^@]+@[^@]+\.[^@]+", email):
        valid = True

    return valid

def validAmount(amount):
    valid = False

    if isinstance(amount, int) and amount >= 0:
        valid = True

    return valid


def validBlockHeight(blockHeight):
    valid = False

    if isinstance(blockHeight, int) and blockHeight >= 0:
        valid = True

    return valid


def validPercentage(percentage):
    valid = False

    if isinstance(percentage, float) and percentage >= 0.0 and percentage <= 100.0:
        valid = True

    return valid


def validYoutube(youtube):
    valid = False

    if isinstance(youtube, (str, unicode)) and len(youtube) <= 11:
        valid = True

    return valid


def validPrivateKey(privKey):
    valid = False

    if isinstance(privKey, (str, unicode)) and len(privKey) > 0:
        valid = True

    return valid


def validDistribution(distribution):
    valid = False

    if isinstance(distribution, list):
        if len(distribution) >= 1:
            for recipient in distribution:
                if isinstance(recipient, list):
                    if len(recipient) >= 2:
                        if (isinstance(recipient[0], str) or isinstance(recipient[0], unicode)) and isinstance(recipient[1], int):
                            valid = True
                        else:
                            valid = False
                            break
                    else:
                        valid = False
                        break


    return valid


