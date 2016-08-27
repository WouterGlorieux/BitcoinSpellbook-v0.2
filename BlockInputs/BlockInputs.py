

from BlockData import BlockData
from validators import validators as validator


def SIL(address, block=0):
    response = {'success': 0}
    SIL = []

    if validator.validAddress(address):
        if block == 0:
            latest_block = BlockData.latestBlock()

            if 'success' in latest_block and latest_block['success'] == 1:
                block = latest_block['latestBlock']['height']
            else:
                response['error'] = 'Unable to retrieve latest block'

        txs_data = BlockData.transactions(address)
        if 'success' in txs_data and txs_data['success'] == 1:
            txs = txs_data['TXS']
            SIL = txs_2_SIL(txs, block)
        else:
            response['error'] = 'Unable to retrieve transactions'

    else:
        response['error'] = 'Invalid address: ' + address

    if 'error' not in response:
        response['SIL'] = SIL
        response['success'] = 1

    return response


def txs_2_SIL(txs, block=0):

    sorted_txs = sortTXS(txs)
    SIL = []
    for tx in sorted_txs:
        if tx['receiving'] == True and (block == 0 or tx['block_height'] <= block) and tx['block_height'] is not None:
            recurring = False
            for i in range(0, len(SIL)):
                if SIL[i][0] == tx['primeInputAddress']:
                    SIL[i][1] += tx['receivedValue']
                    recurring = True

            if not recurring:
                SIL.append([tx['primeInputAddress'], tx['receivedValue'], 0, tx['block_height']])

    total = float(totalReceived(SIL))

    for row in SIL:
        row[2] = row[1]/total

    return SIL


def totalReceived(SIL):
    total = 0
    for tx_input in SIL:
        total += tx_input[1]

    return total


def sortTXS(txs):
    block_txs = {}
    for tx in txs:
        if tx['block_height'] in block_txs:
            block_txs[tx['block_height']].append(tx)
        else:
            block_txs[tx['block_height']] = [tx]

    sorted_txs = []
    for block in sorted(block_txs):
        for tx in sorted(block_txs[block], key=lambda x: x['txid']):
            sorted_txs.append(tx)

    return sorted_txs