
from validators import validators as validator
from BlockData import BlockData
from SimplifiedInputsList import SimplifiedInputsList
from BlockLinker import BlockLinker


class Random():
    def __init__(self, address='', blockHeight=0, xpub=''):
        self.error = ''
        self.address = ''
        self.xpub = ''

        if address != '' and not validator.validAddress(address):
            self.error = 'Invalid address: ' + address
        else:
            self.address = address

        if isinstance(blockHeight, int) and blockHeight >= 0:
            self.blockHeight = blockHeight
        else:
            self.error = 'blockHeight must be an integer greater than or equal to zero'

        if xpub != '' and not validator.validXPUB(xpub):
            self.error = 'Invalid xpub: ' + xpub
        else:
            self.xpub = xpub

    def fromBlock(self, rngBlockHeight=0):
        response = {'success': 0}
        random = self.RNG(rngBlockHeight)

        if self.error == '':
            response['random'] = random
            response['success'] = 1
        else:
            response['error'] = self.error

        return response

    def proportionalRandom(self, source, rngBlockHeight=0):
        response = {'success': 0}
        distribution = self.getDistribution(source)
        rand = self.RNG(rngBlockHeight)
        winner = self.winner(distribution, rand)

        if self.error == '':
            response['winner'] = winner
            response['success'] = 1
        else:
            response['error'] = self.error

        return response


    def RNG(self, rngBlockHeight=0):
        rand = 0.0

        if rngBlockHeight != 0:
            block_data = BlockData.block(rngBlockHeight)
        else:
            block_data = BlockData.latestBlock()

        if 'success' in block_data and block_data['success'] == 1:
            if rngBlockHeight != 0:
                rngHash = block_data['block']['hash']
            else:
                rngHash = block_data['latestBlock']['hash']

            intHash = int(rngHash, 16)

            strFloat = '0.'
            for i in range(len(str(intHash))-1, -1, -1):
                strFloat += str(intHash)[i]

            rand = float(strFloat)

        else:
            self.error = 'Unable to retrieve block for rng'

        return rand


    def getDistribution(self, source):
        distribution = []
        if self.error == '':
            data = {}
            if source == 'SIL':
                data = SimplifiedInputsList.SIL(self.address, self.blockHeight)
            elif source == 'LBL':
                data = BlockLinker.BlockLinker(self.address, self.xpub, self.blockHeight).LBL()
            elif source == 'LRL':
                data = BlockLinker.BlockLinker(self.address, self.xpub, self.blockHeight).LRL()
            elif source == 'LBL':
                data = BlockLinker.BlockLinker(self.address, self.xpub, self.blockHeight).LSL()
            else:
                self.error = 'Unknown distribution source'


            if 'success' in data and data['success'] == 1:
                distribution = data[source]
                distribution = self.addCumulative(distribution)
            else:
                self.error = 'Unable to retrieve distribution'

        return distribution

    def addCumulative(self, distribution):
        cumul = 0
        for i in range(0, len(distribution)):
            cumul += distribution[i][1]
            distribution[i].append(cumul)

        return distribution


    def winner(self, distribution, rand):
        nDistribution = len(distribution)

        winnerIndex = -1
        winnerAddress = ''
        totalValue = 0
        if nDistribution > 0:
            values = self.extractValues(distribution)
            totalValue = sum(values)
            winnerIndex = self.getWinnerIndex(rand, values)
            winnerAddress = distribution[winnerIndex][0]

        winner = {'distribution': distribution, 'winnerAddress': winnerAddress, 'winnerIndex': winnerIndex, 'random': rand, 'target': totalValue*rand}

        return winner



    def extractValues(self, distribution):
        values = []
        for i in range(0, len(distribution)):
            values.append(distribution[i][1])

        return values


    def getWinnerIndex(self, rand, values):

        choice = 0
        total = sum(values)

        if(total > 0):
            cumulative = 0.0
            for i in range(0, len(values)):
                cumulative = cumulative + values[i]
                if (cumulative >= (rand*total) ):
                    choice = i
                    break
        return choice


