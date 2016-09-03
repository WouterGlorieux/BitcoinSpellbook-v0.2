#!/usr/bin/env python
# -*- coding: utf-8 -*-

from validators import validators
from BlockData import BlockData
from BlockInputs import BlockInputs
from BlockLinker import BlockLinker


class Random():
    def __init__(self, address='', block_height=0, xpub=''):
        self.error = ''
        self.address = ''
        self.xpub = ''

        if address != '' and not validators.valid_address(address):
            self.error = 'Invalid address: ' + address
        else:
            self.address = address

        if isinstance(block_height, int) and block_height >= 0:
            self.block_height = block_height
        else:
            self.error = 'block_height must be an integer greater than or equal to zero'

        if xpub != '' and not validators.valid_xpub(xpub):
            self.error = 'Invalid xpub: ' + xpub
        else:
            self.xpub = xpub

    def from_block(self, rng_block_height=0):
        response = {'success': 0}
        random = self.rng(rng_block_height)

        if self.error == '':
            response['random'] = random
            response['success'] = 1
        else:
            response['error'] = self.error

        return response

    def proportional_random(self, source, rng_block_height=0):
        response = {'success': 0}
        distribution = self.get_distribution(source)
        rand = self.rng(rng_block_height)
        winner = self.winner(distribution, rand)

        if self.error == '':
            response['winner'] = winner
            response['success'] = 1
        else:
            response['error'] = self.error

        return response

    def rng(self, rng_block_height=0):
        rand = 0.0

        if rng_block_height != 0:
            block_data = BlockData.block(rng_block_height)
        else:
            block_data = BlockData.latest_block()

        if 'success' in block_data and block_data['success'] == 1:
            if rng_block_height != 0:
                rng_hash = block_data['block']['hash']
            else:
                rng_hash = block_data['latest_block']['hash']

            int_hash = int(rng_hash, 16)

            str_float = '0.'
            for i in range(len(str(int_hash))-1, -1, -1):
                str_float += str(int_hash)[i]

            rand = float(str_float)

        else:
            self.error = 'Unable to retrieve block for rng'

        return rand

    def get_distribution(self, source):
        distribution = []
        if self.error == '':
            data = {}
            if source == 'SIL':
                data = BlockInputs.get_sil(self.address, self.block_height)
            elif source == 'LBL':
                data = BlockLinker.BlockLinker(self.address, self.xpub, self.block_height).get_lbl()
            elif source == 'LRL':
                data = BlockLinker.BlockLinker(self.address, self.xpub, self.block_height).get_lrl()
            elif source == 'LBL':
                data = BlockLinker.BlockLinker(self.address, self.xpub, self.block_height).get_lsl()
            else:
                self.error = 'Unknown distribution source'

            if 'success' in data and data['success'] == 1:
                distribution = data[source]
                distribution = self.add_cumulative(distribution)
            else:
                self.error = 'Unable to retrieve distribution'

        return distribution

    @staticmethod
    def add_cumulative(distribution):
        cumulative = 0
        for i in range(0, len(distribution)):
            cumulative += distribution[i][1]
            distribution[i].append(cumulative)

        return distribution

    def winner(self, distribution, rand):
        n_distribution = len(distribution)

        winner_index = -1
        winner_address = ''
        total_value = 0
        if n_distribution > 0:
            values = self.extract_values(distribution)
            total_value = sum(values)
            winner_index = self.get_winner_index(rand, values)
            winner_address = distribution[winner_index][0]

        winner = {'distribution': distribution,
                  'winner_address': winner_address,
                  'winner_index': winner_index,
                  'random': rand,
                  'target': total_value*rand}

        return winner

    @staticmethod
    def extract_values(distribution):
        values = []
        for i in range(0, len(distribution)):
            values.append(distribution[i][1])

        return values

    @staticmethod
    def get_winner_index(rand, values):

        choice = 0
        total = sum(values)

        if total > 0:
            cumulative = 0.0
            for i in range(0, len(values)):
                cumulative = cumulative + values[i]
                if cumulative >= (rand*total):
                    choice = i
                    break
        return choice