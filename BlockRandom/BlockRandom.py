
from validators import validators as validator
from BlockData import BlockData
from BlockInputs import BlockInputs
from BlockLinker import BlockLinker


class Random():
    def __init__(self, address='', block_height=0, xpub=''):
        self.error = ''
        self.address = ''
        self.xpub = ''

        if address != '' and not validator.validAddress(address):
            self.error = 'Invalid address: ' + address
        else:
            self.address = address

        if isinstance(block_height, int) and block_height >= 0:
            self.block_height = block_height
        else:
            self.error = 'block_height must be an integer greater than or equal to zero'

        if xpub != '' and not validator.validXPUB(xpub):
            self.error = 'Invalid xpub: ' + xpub
        else:
            self.xpub = xpub

    def fromBlock(self, rng_block_height=0):
        response = {'success': 0}
        random = self.RNG(rng_block_height)

        if self.error == '':
            response['random'] = random
            response['success'] = 1
        else:
            response['error'] = self.error

        return response

    def proportionalRandom(self, source, rng_block_height=0):
        response = {'success': 0}
        distribution = self.getDistribution(source)
        rand = self.RNG(rng_block_height)
        winner = self.winner(distribution, rand)

        if self.error == '':
            response['winner'] = winner
            response['success'] = 1
        else:
            response['error'] = self.error

        return response

    def RNG(self, rng_block_height=0):
        rand = 0.0

        if rng_block_height != 0:
            block_data = BlockData.block(rng_block_height)
        else:
            block_data = BlockData.latestBlock()

        if 'success' in block_data and block_data['success'] == 1:
            if rng_block_height != 0:
                rng_hash = block_data['block']['hash']
            else:
                rng_hash = block_data['latestBlock']['hash']

            int_hash = int(rng_hash, 16)

            str_float = '0.'
            for i in range(len(str(int_hash))-1, -1, -1):
                str_float += str(int_hash)[i]

            rand = float(str_float)

        else:
            self.error = 'Unable to retrieve block for rng'

        return rand

    def getDistribution(self, source):
        distribution = []
        if self.error == '':
            data = {}
            if source == 'SIL':
                data = BlockInputs.SIL(self.address, self.block_height)
            elif source == 'LBL':
                data = BlockLinker.BlockLinker(self.address, self.xpub, self.block_height).LBL()
            elif source == 'LRL':
                data = BlockLinker.BlockLinker(self.address, self.xpub, self.block_height).LRL()
            elif source == 'LBL':
                data = BlockLinker.BlockLinker(self.address, self.xpub, self.block_height).LSL()
            else:
                self.error = 'Unknown distribution source'

            if 'success' in data and data['success'] == 1:
                distribution = data[source]
                distribution = self.addCumulative(distribution)
            else:
                self.error = 'Unable to retrieve distribution'

        return distribution

    def addCumulative(self, distribution):
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
            values = self.extractValues(distribution)
            total_value = sum(values)
            winner_index = self.getWinnerIndex(rand, values)
            winner_address = distribution[winner_index][0]

        winner = {'distribution': distribution, 'winnerAddress': winner_address, 'winnerIndex': winner_index, 'random': rand, 'target': total_value*rand}

        return winner

    def extractValues(self, distribution):
        values = []
        for i in range(0, len(distribution)):
            values.append(distribution[i][1])

        return values

    def getWinnerIndex(self, rand, values):

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