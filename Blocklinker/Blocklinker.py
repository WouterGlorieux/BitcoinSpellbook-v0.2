
from BlockData import BlockData
from BlockInputs import BlockInputs
import bitcoin
from BIP44 import BIP44 as BIP44

from validators import validators as validator


class BlockLinker():

    def __init__(self, address, xpub, block_height=0):

        self.address = address
        self.xpub = xpub
        self.block_height = block_height

        self.SIL = []
        self.balances = {}
        self.address_list = []

        self.error = ''

        if validator.validAddress(self.address) and validator.validXPUB(self.xpub):
            SIL_data = BlockInputs.SIL(self.address, self.block_height)

            if 'success' in SIL_data and SIL_data['success'] == 1:
                self.SIL = SIL_data['SIL']

                self.address_list = BIP44.get_addresses_from_xpub(self.xpub, len(self.SIL))

                balances_data = BlockData.balances(concatAddresses(self.address_list))
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
                LBL.append([self.SIL[i][0], self.balances[self.address_list[i]]['balance']])

            total = float(total_value(LBL))
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
                LRL.append([self.SIL[i][0], self.balances[self.address_list[i]]['received']])

            total = float(total_value(LRL))
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
                LSL.append([self.SIL[i][0], self.balances[self.address_list[i]]['sent']])

            total = float(total_value(LSL))
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
                LAL.append([self.SIL[i][0], self.address_list[i]])

            response['LAL'] = LAL
            response['success'] = 1
        else:
            response['error'] = self.error

        return response


def total_value(linked_list):
    total = 0
    for row in linked_list:
        total += row[1]

    return total


#this function will concatenate all adresses and put '|' between them
def concatAddresses(addresses):
    address_string = ''
    for address in addresses:
        address_string += address + '|'

    address_string = address_string[:-1]
    return address_string