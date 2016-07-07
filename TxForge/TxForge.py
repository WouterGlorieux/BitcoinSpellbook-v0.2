import logging
import bitcoin

def sendCustomTransaction(privkeys, inputs, outputs, fee=0):
    #input format= txid:i

    success = False
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
            for i in range(0, len(UTXOs)):
                tx = bitcoin.sign(tx, i, str(privkeys[UTXOs[i]['address']]))

            #bitcoin.pushtx(tx)
            success = True

        elif allKeysPresent == False:
            logging.error("At least 1 private key is missing.")
        elif allInputsConfirmed == False:
            logging.error("At least 1 input is unconfirmed.")

    return success


