#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import bitcoin

from bitcoin.transaction import *


def make_custom_tx(private_keys, inputs, outputs, fee=0, op_return_data=''):
    #input format= txid:i
    tx = None
    total_input_value = 0
    utxos = []
    for tx_input in inputs:
        if 'spend' not in tx_input:
            total_input_value += tx_input['value']
            utxos.append(tx_input)

    total_output_value = 0
    for tx_output in outputs:
        total_output_value += tx_output['value']

    diff = total_input_value - total_output_value
    if fee != diff:
        logging.error("Fee incorrect! aborting transaction! " + str(fee) + " != " + str(diff))
    elif fee < 0:
        logging.error('Fee cannot be lower than zero! aborting transaction! fee: ' + str(fee))
    else:
        all_keys_present = True
        all_inputs_confirmed = True
        for tx_input in utxos:
            if tx_input['address'] not in private_keys:
                all_keys_present = False

            if tx_input['block_height'] is None:
                all_inputs_confirmed = False

        if all_keys_present is True and all_inputs_confirmed is True:
            tx = bitcoin.mktx(utxos, outputs)

            if op_return_data != '' and len(op_return_data) <= 80:
                tx = add_op_return(op_return_data, tx)
            else:
                logging.error('OP_RETURN data is longer than 80 characters')
                return None

            for i in range(0, len(utxos)):
                tx = bitcoin.sign(tx, i, str(private_keys[utxos[i]['address']]))

        elif not all_keys_present:
            logging.error("At least 1 private key is missing.")
        elif not all_inputs_confirmed:
            logging.error("At least 1 input is unconfirmed.")

    return tx


def send_tx(tx):
    success = False
    response = {}
    try:
        retval = bitcoin.blockr_pushtx(tx)
        logging.info("TX broadcast succeeded, Blockr response: %s" % str(retval))
        response = json.loads(retval)
    except Exception as e:
        logging.error("TX broadcast failed: %s" % str(e))

    if 'status' in response and response['status'] == 'success':
        success = True

    return success


def decode_op_return(hex_data):
    unhex_data = None
    if hex_data[:2] == '6a':
        if hex_data[2:4] == '4c':
            data = hex_data[6:]
            check_length = hex_data[4:6]
        elif hex_data[2:4] == '4d':
            data = hex_data[8:]
            check_length = hex_data[4:8]
        elif hex_data[2:4] == '4e':
            data = hex_data[10:]
            check_length = hex_data[4:10]
        else:
            data = hex_data[4:]
            check_length = hex_data[2:4]

        unhex_data = binascii.unhexlify(data)

        if len(unhex_data) != int(check_length, 16):
            logging.error('OP_RETURN data is not the correct length! {0} -> should be {1}'.format(str(len(unhex_data)),
                                                                                                  str(int(check_length,
                                                                                                          16))))
            unhex_data = None

    return unhex_data


#extra functions for op_return from a fork of pybitcointools
#https://github.com/wizardofozzie/pybitcointools


def num_to_op_push(x):
    x = int(x)
    if 0 <= x <= 75:
        pc = ''
        num = encode(x, 256, 1)
    elif x < 0xff:
        pc = from_int_to_byte(0x4c)
        num = encode(x, 256, 1)
    elif x < 0xffff:
        pc = from_int_to_byte(0x4d)
        num = encode(x, 256, 2)[::-1]
    elif x < 0xffffffff:
        pc = from_int_to_byte(0x4e)
        num = encode(x, 256, 4)[::-1]
    else:
        raise ValueError("0xffffffff > value >= 0")
    return pc + num


def wrap_script(hexdata):
    if re.match('^[0-9a-fA-F]*$', hexdata):
        return binascii.hexlify(wrap_script(binascii.unhexlify(hexdata)))
    return num_to_op_push(len(hexdata)) + hexdata


def add_op_return(msg, tx_hex=None):
    """Makes OP_RETURN script from msg, embeds in Tx hex"""
    hex_data = binascii.hexlify(b'\x6a' + wrap_script(msg))

    if tx_hex is None:
        return hex_data
    else:
        if not re.match("^[0-9a-fA-F]*$", tx_hex):
            return binascii.unhexlify(add_op_return(msg, binascii.hexlify(tx_hex)))
        elif isinstance(tx_hex, dict):
            txo = tx_hex
            outs = txo.get('outs')
        else:
            outs = deserialize(tx_hex).get('outs')

        txo = deserialize(tx_hex)
        assert (len(outs) > 0) and sum(multiaccess(outs, 'value')) > 0 \
            and not any([o for o in outs if o.get("script")[:2] == '6a']), \
            "Tx limited to *1* OP_RETURN, and only whilst the other outputs send funds"
        txo['outs'].append({'script': hex_data, 'value': 0})
        return serialize(txo)