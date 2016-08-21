
from Blockchaindata import Blockchaindata
from SimplifiedInputsList import SimplifiedInputsList
import bitcoin


from validators import validators as validator

class BlockLinker():

    def __init__(self, address, xpub, blockHeight=0):

        self.address = address
        self.xpub = xpub
        self.blockHeight = blockHeight

        self.SIL = []
        self.balances = {}
        self.addressList = []

        self.error = ''

        if validator.validAddress(self.address) and validator.validXPUB(self.xpub):
            SIL_data = SimplifiedInputsList.SIL(self.address, self.blockHeight)

            if 'success' in SIL_data and SIL_data['success'] == 1:
                self.SIL = SIL_data['SIL']

                self.addressList = getAddressesFromXPUB(self.xpub, len(self.SIL))

                balances_data = Blockchaindata.balances(concatAddresses(self.addressList))
                if 'success' in balances_data and balances_data['success'] == 1:
                    self.balances = balances_data['balances']
                else:
                    self.error = 'Unable to retrieve balances'

            else:
                self.error = 'Unable to retrieve SIL'
        elif not validator.validAddress(self.address):
            self.error = 'Invalid address: ' + self.address
        elif not validator.validXPUB(self.xpub):
            self.error = 'Invalid xpub: ' + self.xpub



    def LBL(self):
        response = {'success': 0}
        LBL = []
        if self.error == '':
            for i in range(0, len(self.SIL)):
                LBL.append([self.SIL[i][0], self.balances[self.addressList[i]]['balance']])

            total = float(totalValue(LBL))
            for row in LBL:
                row.append(row[1]/total)

            response['LBL'] = LBL
            response['success'] = 1
        else:
            response['error'] = self.error





        return response

    def LRL(self):
        response = {'success': 0}
        LRL = []
        if self.error == '':
            for i in range(0, len(self.SIL)):
                LRL.append([self.SIL[i][0], self.balances[self.addressList[i]]['received']])

            total = float(totalValue(LRL))
            for row in LRL:
                row.append(row[1]/total)

            response['LRL'] = LRL
            response['success'] = 1
        else:
            response['error'] = self.error

        return response

    def LSL(self):
        response = {'success': 0}
        LSL = []
        if self.error == '':
            for i in range(0, len(self.SIL)):
                LSL.append([self.SIL[i][0], self.balances[self.addressList[i]]['sent']])

            total = float(totalValue(LSL))
            for row in LSL:
                row.append(row[1]/total)

            response['LSL'] = LSL
            response['success'] = 1
        else:
            response['error'] = self.error

        return response

    def LAL(self):
        response = {'success': 0}
        LAL = []
        if self.error == '':
            for i in range(0, len(self.SIL)):
                LAL.append([self.SIL[i][0], self.addressList[i]])

            response['LAL'] = LAL
            response['success'] = 1
        else:
            response['error'] = self.error

        return response

def totalValue(linkedList):
    total = 0
    for row in linkedList:
        total += row[1]

    return total



#getAddressesFromXPUB will return an array of addresses generated from an XPUB key
#optional parameters:
#i          the amount of addresses to be generated
#addrType   0: Receiving addresses, 1: Change addresses, ...
def getAddressesFromXPUB(xpub, i=10, addrType=0):
    addressList = []
    pub0 = bitcoin.bip32_ckd(xpub, addrType)

    for i in range (0, i):
        publicKey = bitcoin.bip32_ckd(pub0, i)
        hexKey = bitcoin.encode_pubkey(bitcoin.bip32_extract_key(publicKey), 'hex_compressed')
        address_fromPub =  bitcoin.pubtoaddr(hexKey)
        addressList.append(address_fromPub)

    return addressList


#this function will concatenate all adresses and put '|' between them
def concatAddresses(addresses):
    addrString = ''
    for address in addresses:
        addrString += address + '|'

    addrString = addrString[:-1]
    return addrString



