#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re


ALL_CHARACTERS_REGEX = "^[a-zA-Z0-9àáâäãåąčćęèéêëėįìíîïłńòóôöõøùúûüųūÿýżźñçčšžÀÁÂÄÃÅĄĆČĖĘÈÉÊËÌÍÎÏĮŁŃÒÓÔÖÕØÙÚÛÜŲŪŸÝŻŹÑßÇŒÆČŠŽ∂ð ,.'-]+$"
YOUTUBE_REGEX = "^(http(s?):\/\/)?(www\.)?youtu(be)?\.([a-z])+\/(watch(.*?)(\?|\&)v=)?(.*?)(&(.)*)?$"
YOUTUBE_ID_REGEX = "^[a-zA-Z0-9_-]{11}$"
URL_REGEX = "((([A-Za-z]{3,9}:(?:\/\/)?)(?:[\-;:&=\+\$,\w]+@)?[A-Za-z0-9\.\-]+|(?:www\.|[\-;:&=\+\$,\w]+@)[A-Za-z0-9\.\-]+)((?:\/[\+~%\/\.\w\-_]*)?\??(?:[\-\+=&;%@\.\w_]*)#?(?:[\.\!\/\\\w]*))?)"
ADDRESS_REGEX = "^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$"
TXID_REGEX = "^[a-f0-9]{64}$"
BLOCKPROFILE_REGEX = "^[0-9]*@[0-9]+:[a-zA-Z0-9]+=[a-zA-Z0-9 ]+$"
EMAIL_REGEX = r"[^@]+@[^@]+\.[^@]+"


def valid_address(address):
    valid = False

    if isinstance(address, (str, unicode)) and re.match(ADDRESS_REGEX, address):
        valid = True

    return valid


def valid_addresses(addresses):
    valid = False

    if isinstance(addresses, (str, unicode)):
        for address in addresses.split("|"):
            if valid_address(address):
                valid = True
            else:
                valid = False
                break

    return valid


def valid_txid(txid):
    valid = False

    if isinstance(txid, (str, unicode)) and re.match(TXID_REGEX, txid):
        valid = True

    return valid


def valid_xpub(xpub):
    valid = False
    if isinstance(xpub, (str, unicode)) and xpub[:4] == "xpub":
        valid = True

    return valid


def valid_description(description):
    valid = False

    if isinstance(description, (str, unicode)) and len(description) <= 250:
        valid = True

    return valid


def valid_op_return(message):
    valid = False

    if isinstance(message, (str, unicode)) and 0 < len(message) <= 80:
        valid = True

    return valid


def valid_blockprofile_message(message):
    valid = False
    all_valid = True
    if isinstance(message, (str, unicode)):
        for message_part in message.split("|"):
            if re.match(BLOCKPROFILE_REGEX, message_part):
                valid = True
            else:
                all_valid = False

    return valid and all_valid


def valid_text(text):
    valid = False

    if isinstance(text, (str, unicode)):
        valid = True

    return valid


def valid_url(url):
    valid = False

    if isinstance(url, (str, unicode)) and re.match(URL_REGEX, url):
        valid = True

    return valid


def valid_creator(creator):
    valid = False

    if isinstance(creator, (str, unicode)) and re.match(ALL_CHARACTERS_REGEX, creator):
        valid = True

    return valid


def valid_email(email):
    valid = False
    if isinstance(email, (str, unicode)) and re.match(EMAIL_REGEX, email):
        valid = True

    return valid


def valid_amount(amount):
    valid = False

    if isinstance(amount, int) and amount >= 0:
        valid = True

    return valid


def valid_block_height(block_height):
    valid = False

    if isinstance(block_height, int) and block_height >= 0:
        valid = True

    return valid


def valid_percentage(percentage):
    valid = False

    if isinstance(percentage, (int, float)) and 0.0 <= percentage <= 100.0:
        valid = True

    return valid


def valid_youtube(youtube):
    valid = False

    if isinstance(youtube, (str, unicode)) and re.match(YOUTUBE_REGEX, youtube):
        valid = True

    return valid


def valid_youtube_id(youtube):
    valid = False

    if isinstance(youtube, (str, unicode)) and re.match(YOUTUBE_ID_REGEX, youtube):
        valid = True

    return valid


def valid_private_key(private_key):
    valid = False

    if isinstance(private_key, (str, unicode)) and len(private_key) > 0:
        valid = True

    return valid


def valid_distribution(distribution):
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


def valid_outputs(outputs):
    valid = False

    if isinstance(outputs, list):
        if len(outputs) >= 1:
            for recipient in outputs:
                if isinstance(recipient, (tuple, list)):
                    if len(recipient) == 2:
                        if valid_address(recipient[0]) and isinstance(recipient[1], int) and recipient[1] > 0:
                            valid = True
                        else:
                            valid = False
                            break
                    else:
                        valid = False
                        break
    return valid