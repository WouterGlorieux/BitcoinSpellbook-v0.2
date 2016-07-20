import logging
import bitcoin



from bitcoin.transaction import *

def makeCustomTransaction(privkeys, inputs, outputs, fee=0, op_return_data=''):
    #input format= txid:i
    tx = None
    totalInputValue = 0
    UTXOs = []
    for tx_input in inputs:
        if 'spend' not in tx_input:
            totalInputValue += tx_input['value']
            UTXOs.append(tx_input)

    totalOutputValue = 0
    for tx_output in outputs:
        totalOutputValue += tx_output['value']

    diff = totalInputValue - totalOutputValue
    if fee != diff:
        logging.error("Fee incorrect! aborting transaction! " + str(fee) + " != " + str(diff))
    else:
        allKeysPresent = True
        allInputsConfirmed = True
        for tx_input in UTXOs:
            if tx_input['address'] not in privkeys:
                allKeysPresent = False

            if tx_input['block_height'] == None:
                allInputsConfirmed = False

        if allKeysPresent == True and allInputsConfirmed == True:
            tx = bitcoin.mktx(UTXOs, outputs)

            if op_return_data != '' and len(op_return_data) <= 80:
                tx = addOP_RETURN(op_return_data, tx)

            for i in range(0, len(UTXOs)):
                tx = bitcoin.sign(tx, i, str(privkeys[UTXOs[i]['address']]))

        elif allKeysPresent == False:
            logging.error("At least 1 private key is missing.")
        elif allInputsConfirmed == False:
            logging.error("At least 1 input is unconfirmed.")

    return tx

def sendTransaction(tx):
    response = bitcoin.pushtx(tx)
    return response



def decodeOP_RETURN(hexdata):
    return binascii.unhexlify(hexdata)

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

def addOP_RETURN(msg, txhex=None):
    """Makes OP_RETURN script from msg, embeds in Tx hex"""
    hexdata = binascii.hexlify(b'\x6a' + wrap_script(msg))
    if txhex is None:
        return hexdata
    else:
        if not re.match("^[0-9a-fA-F]*$", txhex):
            return binascii.unhexlify(addOP_RETURN(msg, binascii.hexlify(txhex)))
        elif isinstance(txhex, dict):
            txo = txhex
            outs = txo.get('outs')
        else:
            outs = deserialize(txhex).get('outs')

        txo = deserialize(txhex)
        assert (len(outs) > 0) and sum(multiaccess(outs, 'value')) > 0 \
                and not any([o for o in outs if o.get("script")[:2] == '6a']), "Tx limited to *1* OP_RETURN, and only whilst the other outputs send funds"
        txo['outs'].append({
                    'script': hexdata,
                    'value': 0
                    })
        return serialize(txo)