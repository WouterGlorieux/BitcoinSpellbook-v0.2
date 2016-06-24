

from Blockchaindata import Blockchaindata
from validators import validators as validator



def SIL(address, block=0):
    response = {'success': 0}
    SIL = []

    if validator.validAddress(address):
        if block == 0:
            latestBlock = Blockchaindata.latestBlock()

            if 'success' in latestBlock and latestBlock['success'] == 1:
                block = latestBlock['latestBlock']['height']
            else:
                response['error'] = 'Unable to retrieve latest block'

        txsData = Blockchaindata.transactions(address)
        if 'success' in txsData and txsData['success'] == 1:
            txs = txsData['TXS']
            SIL = TXS2SIL(txs, block)
        else:
            response['error'] = 'Unable to retrieve transactions'

    else:
        response['error'] = 'Invalid address: ' + address

    if 'error' not in response:
        response['SIL'] = SIL
        response['success'] = 1

    return response




def TXS2SIL(txs, block=0):

    sortedTXS = sortTXS(txs)
    SIL = []
    for tx in sortedTXS:
        if tx['receiving'] == True and (block == 0 or tx['blockHeight'] <= block) and tx['blockHeight'] != None:
            recurring = False
            for i in range(0, len(SIL)):
                if SIL[i][0] == tx['primeInputAddress']:
                    SIL[i][1] += tx['receivedValue']
                    recurring = True

            if recurring == False:
                SIL.append( [tx['primeInputAddress'], tx['receivedValue'], 0 ,tx['blockHeight'] ] )

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
    blockTXS = {}
    for tx in txs:
        if tx['blockHeight'] in blockTXS:
            blockTXS[tx['blockHeight']].append(tx)
        else:
            blockTXS[tx['blockHeight']] = [tx]

    sortedTXS = []
    for block in sorted(blockTXS):
        for tx in sorted(blockTXS[block], key= lambda x: x['txid']):
            sortedTXS.append(tx)

    return sortedTXS



