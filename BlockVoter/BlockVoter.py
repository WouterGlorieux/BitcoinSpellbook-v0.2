

from Blockchaindata import Blockchaindata
from SimplifiedInputsList import SimplifiedInputsList
from BlockLinker import BlockLinker
from validators import validators as validator

import hashlib

MINIMUM_VOTE_COST = 40000

class BlockVoter():
    def __init__(self, address, proposal, options=[], voteCost=MINIMUM_VOTE_COST):
        self.error = ''

        if address != '' and validator.validAddress(address):
            self.address = address
        else:
            self.error = 'Invalid address'

        if isinstance(proposal, (str, unicode)) and len(proposal) > 0:
            self.proposal = proposal
        else:
            self.error = 'Proposal cannot be empty'

        if isinstance(options, list):
            self.options = options
        else:
            self.error = 'Options must be of type: List'

        if isinstance(voteCost, int) and voteCost >= MINIMUM_VOTE_COST:
            self.voteCost = voteCost
        else:
            self.error = 'Invalid voteCost, must be minimum ' + str(MINIMUM_VOTE_COST) + ' Satoshis'

        self.weights = ''
        self.registrationAddress = ''
        self.registrationBlockHeight = 0
        self.registrationXPUB = ''

        self.weightValues = []


    def setWeights(self, weights='Equal', registrationAddress="", registrationBlockHeight=0, registrationXPUB=""):
        if weights in ['Value', 'Equal', 'SIL', 'LBL', 'LRL', 'LSL']:
            self.weights = weights

            if weights in ['SIL', 'LBL', 'LRL', 'LSL'] and validator.validAddress(registrationAddress):

                if isinstance(registrationBlockHeight, int) and registrationBlockHeight >= 0:
                    self.registrationAddress = registrationAddress
                    self.registrationBlockHeight = registrationBlockHeight

                    if weights in ['LBL', 'LRL', 'LSL'] and validator.validXPUB(registrationXPUB):
                        self.registrationXPUB = registrationXPUB
                    elif weights in ['LBL', 'LRL', 'LSL']:
                        self.error = 'Invalid registration XPUB'
                else:
                    self.error = 'Registration BlockHeight must be a integer greater than or equal to zero.'

            elif weights in ['SIL', 'LBL', 'LRL', 'LSL']:
                self.error = 'Invalid registration address'

    def getOptions(self):
        optionsDict = {}
        for i in range(0, len(self.options)):
            option = {}
            option['description'] = self.options[i]
            option['amount'] = self.voteCost + i
            option['QR'] = "http://www.btcfrog.com/qr/bitcoinPNG.php?address=" + str(self.address) + "&amount=" + str(option['amount']/1e8) + "&error=H"
            optionsDict[i] = option

        return sorted(optionsDict.iteritems())

    def getProposalHash(self):
        proposalData = self.address + self.proposal + str(self.options)
        proposalHash = hashlib.sha256(proposalData).hexdigest()
        return proposalHash


    def getProposal(self):
        response = {'success': 0}
        if self.error == '':
            proposal = {}
            proposal['address'] = self.address
            proposal['proposal'] = self.proposal
            proposal['options'] = self.getOptions()
            proposal['voteCost'] = self.voteCost

            if self.weights != '':
                proposal['weights'] = self.weights
            if self.registrationAddress != '':
                proposal['regAddress'] = self.registrationAddress
            if self.registrationXPUB != '':
                proposal['regXPUB'] = self.registrationXPUB
            if self.registrationBlockHeight != 0:
                proposal['regBlockHeight'] = self.registrationBlockHeight

            proposal['proposalHash'] = self.getProposalHash()

            response['proposal'] = proposal
            response['success'] = 1
        else:
            response['error'] = self.error

        return response


    def getResults(self, blockHeight=0):
        response = {'success': 0}

        digits = len(str(len(self.options)))

        if blockHeight==0:
            latestBlock_data = Blockchaindata.latestBlock()
            if 'success' in latestBlock_data and latestBlock_data['success'] == 1:
                blockHeight = latestBlock_data['latestBlock']['height']
            else:
                self.error = latestBlock_data['error']

        if self.weights in ['SIL', 'LBL', 'LRL', 'LSL']:
            if self.weights == 'SIL':
                weights_data = SimplifiedInputsList.SIL(self.registrationAddress, self.registrationBlockHeight)
            elif self.weights == 'LBL':
                weights_data = BlockLinker.BlockLinker(self.registrationAddress, self.registrationXPUB, self.registrationBlockHeight).LBL()
            elif self.weights == 'LRL':
                weights_data = BlockLinker.BlockLinker(self.registrationAddress, self.registrationXPUB, self.registrationBlockHeight).LRL()
            elif self.weights == 'LSL':
                weights_data = BlockLinker.BlockLinker(self.registrationAddress, self.registrationXPUB, self.registrationBlockHeight).LSL()

            if 'success' in weights_data and weights_data['success'] == 1:
                self.weightValues = weights_data[self.weights]
            else:
                self.error = weights_data['error']

        TXS = []
        TXS_data = Blockchaindata.transactions(self.address)

        if 'success' in TXS_data and TXS_data['success'] == 1:
            TXS = TXS_data['TXS']
        else:
            self.error = 'Unable to retrieve transactions for address ' + self.address


        votes = self.convertTXS2Votes(TXS, blockHeight, digits)
        results = self.calcResults(votes)


        if self.error == '':
            response['votes'] = votes
            response['results'] = results
            response['options'] = self.getOptions()
            response['voteCost'] = self.voteCost
            response['blockHeight'] = blockHeight
            response['proposal'] = self.proposal
            response['address'] = self.address
            response['proposalHash'] = self.getProposalHash()

            if self.weights != '':
                response['weights'] = self.weights
            if self.registrationAddress != '':
                response['regAddress'] = self.registrationAddress
            if self.registrationBlockHeight != '':
                response['regBlockHeight'] = self.registrationBlockHeight
            if self.registrationXPUB != '':
                response['regXPUB'] = self.registrationXPUB

            response['success'] = 1

        else:
            response['error'] = self.error

        return response


    def convertTXS2Votes(self, TXS, blockHeight, significantDigits=1):
        votes = {}
        if self.error == '':
            for i in range(0, len(TXS)):
                if TXS[i]['blockHeight'] <= blockHeight and TXS[i]['receiving'] == True:
                    voter = TXS[i]['primeInputAddress']
                    vote = str(TXS[i]['receivedValue'])[-significantDigits:]
                    value = TXS[i]['receivedValue'] - int(vote)

                    if (self.weights == 'Value' and value >= self.voteCost) or value == self.voteCost:
                        if voter in votes:
                            votes[voter]['lastVote'] = vote
                            votes[voter]['value'] += value
                        else:
                            votes[voter] = {'lastVote': vote, 'value': value}

        return votes


    def calcResults(self, votes):
        results = {}
        for voter in votes:

            if int(votes[voter]['lastVote']) == 0:
                option = "0"
            else:
                option = str(votes[voter]['lastVote']).lstrip("0")

            if self.weights == 'Value':
                if option in results:
                    results[option] += votes[voter]['value']
                else:
                    results[option] = votes[voter]['value']

            elif self.weights == 'Equal':
                if option in results:
                    results[option] += 1
                else:
                    results[option] = 1

            elif self.weights in ['SIL', 'LBL', 'LRL', 'LSL']:
                value = 0
                for tx_input in self.weightValues:
                    if tx_input[0] == voter:
                        value = tx_input[1]
                        break

                if option in results:
                    results[option] += value
                else:
                    results[option] = value

        return results




