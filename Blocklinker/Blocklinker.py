#!/usr/bin/env python
# -*- coding: utf-8 -*-

from BlockData import BlockData
from BlockInputs import BlockInputs
from BIP44 import BIP44 as BIP44
from validators import validators as validator


class BlockLinker():

    def __init__(self, address, xpub, block_height=0):

        self.address = address
        self.xpub = xpub
        self.block_height = block_height

        self.sil = []
        self.balances = {}
        self.address_list = []

        self.error = ''

        if validator.valid_address(self.address) and validator.valid_xpub(self.xpub):
            sil_data = BlockInputs.get_sil(self.address, self.block_height)

            if 'success' in sil_data and sil_data['success'] == 1:
                self.sil = sil_data['SIL']

                self.address_list = BIP44.get_addresses_from_xpub(self.xpub, len(self.sil))

                balances_data = BlockData.balances(concat_addresses(self.address_list))
                if 'success' in balances_data and balances_data['success'] == 1:
                    self.balances = balances_data['balances']
                else:
                    self.error = 'Unable to retrieve balances'

            else:
                self.error = 'Unable to retrieve sil'
        elif not validator.valid_address(self.address):
            self.error = 'Invalid address: ' + self.address
        elif not validator.valid_xpub(self.xpub):
            self.error = 'Invalid xpub: ' + self.xpub

    def get_lbl(self):
        response = {'success': 0}
        lbl = []
        if self.error == '':
            for i in range(0, len(self.sil)):
                lbl.append([self.sil[i][0], self.balances[self.address_list[i]]['balance']])

            total = float(total_value(lbl))
            for row in lbl:
                row.append(row[1]/total)

            response['lbl'] = lbl
            response['success'] = 1
        else:
            response['error'] = self.error

        return response

    def get_lrl(self):
        response = {'success': 0}
        lrl = []
        if self.error == '':
            for i in range(0, len(self.sil)):
                lrl.append([self.sil[i][0], self.balances[self.address_list[i]]['received']])

            total = float(total_value(lrl))
            for row in lrl:
                row.append(row[1]/total)

            response['lrl'] = lrl
            response['success'] = 1
        else:
            response['error'] = self.error

        return response

    def get_lsl(self):
        response = {'success': 0}
        lsl = []
        if self.error == '':
            for i in range(0, len(self.sil)):
                lsl.append([self.sil[i][0], self.balances[self.address_list[i]]['sent']])

            total = float(total_value(lsl))
            for row in lsl:
                row.append(row[1]/total)

            response['lsl'] = lsl
            response['success'] = 1
        else:
            response['error'] = self.error

        return response

    def get_lal(self):
        response = {'success': 0}
        lal = []
        if self.error == '':
            for i in range(0, len(self.sil)):
                lal.append([self.sil[i][0], self.address_list[i]])

            response['lal'] = lal
            response['success'] = 1
        else:
            response['error'] = self.error

        return response


def total_value(linked_list):
    total = 0
    for row in linked_list:
        total += row[1]

    return total


#this function will concatenate all addresses and put '|' between them
def concat_addresses(addresses):
    address_string = ''
    for address in addresses:
        address_string += address + '|'

    address_string = address_string[:-1]
    return address_string