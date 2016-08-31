

from BlockData import BlockData
from BlockInputs import BlockInputs
from BlockLinker import BlockLinker
from validators import validators as validator

import hashlib

MINIMUM_VOTE_COST = 40000


class BlockVoter():
    def __init__(self, address, proposal, options=None, vote_cost=MINIMUM_VOTE_COST):
        if not options:
            options = []
        self.error = ''

        if address != '' and validator.valid_address(address):
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

        if isinstance(vote_cost, int) and vote_cost >= MINIMUM_VOTE_COST:
            self.vote_cost = vote_cost
        else:
            self.error = 'Invalid vote_cost, must be minimum ' + str(MINIMUM_VOTE_COST) + ' Satoshis'

        self.weights = ''
        self.registration_address = ''
        self.registration_block_height = 0
        self.registration_xpub = ''

        self.weight_values = []

    def set_weights(self, weights='Equal', registration_address="", registration_block_height=0, registration_xpub=""):
        if weights in ['Value', 'Equal', 'SIL', 'LBL', 'LRL', 'LSL']:
            self.weights = weights

            if weights in ['SIL', 'LBL', 'LRL', 'LSL'] and validator.valid_address(registration_address):

                if isinstance(registration_block_height, int) and registration_block_height >= 0:
                    self.registration_address = registration_address
                    self.registration_block_height = registration_block_height

                    if weights in ['LBL', 'LRL', 'LSL'] and validator.valid_xpub(registration_xpub):
                        self.registration_xpub = registration_xpub
                    elif weights in ['LBL', 'LRL', 'LSL']:
                        self.error = 'Invalid registration XPUB'
                else:
                    self.error = 'Registration block_height must be a integer greater than or equal to zero.'

            elif weights in ['SIL', 'LBL', 'LRL', 'LSL']:
                self.error = 'Invalid registration address'

    def get_options(self):
        options_dict = {}
        for i in range(0, len(self.options)):
            option = {'description': self.options[i],
                      'amount': self.vote_cost + i}
            option['QR'] = "http://www.btcfrog.com/qr/bitcoinPNG.php?address={0}&amount={1}&error=H".format(
                str(self.address), str(option['amount'] / 1e8))
            options_dict[i] = option

        return sorted(options_dict.iteritems())

    def get_proposal_hash(self):
        proposal_data = self.address + self.proposal + str(self.options)
        proposal_hash = hashlib.sha256(proposal_data).hexdigest()
        return proposal_hash

    def get_proposal(self):
        response = {'success': 0}
        if self.error == '':
            proposal = {'address': self.address,
                        'proposal': self.proposal,
                        'options': self.get_options(),
                        'vote_cost': self.vote_cost}

            if self.weights != '':
                proposal['weights'] = self.weights
            if self.registration_address != '':
                proposal['registration_address'] = self.registration_address
            if self.registration_xpub != '':
                proposal['registration_xpub'] = self.registration_xpub
            if self.registration_block_height != 0:
                proposal['registration_block_height'] = self.registration_block_height

            proposal['proposalHash'] = self.get_proposal_hash()

            response['proposal'] = proposal
            response['success'] = 1
        else:
            response['error'] = self.error

        return response

    def get_results(self, block_height=0):
        response = {'success': 0}

        digits = len(str(len(self.options)))

        if block_height == 0:
            latest_block_data = BlockData.latest_block()
            if 'success' in latest_block_data and latest_block_data['success'] == 1:
                block_height = latest_block_data['latestBlock']['height']
            else:
                self.error = latest_block_data['error']

        if self.weights in ['SIL', 'LBL', 'LRL', 'LSL']:
            weights_data = {}
            if self.weights == 'SIL':
                weights_data = BlockInputs.get_sil(self.registration_address, self.registration_block_height)
            elif self.weights == 'LBL':
                weights_data = BlockLinker.BlockLinker(self.registration_address,
                                                       self.registration_xpub,
                                                       self.registration_block_height).get_lbl()
            elif self.weights == 'LRL':
                weights_data = BlockLinker.BlockLinker(self.registration_address,
                                                       self.registration_xpub,
                                                       self.registration_block_height).get_lrl()
            elif self.weights == 'LSL':
                weights_data = BlockLinker.BlockLinker(self.registration_address,
                                                       self.registration_xpub,
                                                       self.registration_block_height).get_lsl()

            if 'success' in weights_data and weights_data['success'] == 1:
                self.weight_values = weights_data[self.weights]
            else:
                self.error = weights_data['error']

        txs = []
        txs_data = BlockData.transactions(self.address)

        if 'success' in txs_data and txs_data['success'] == 1:
            txs = txs_data['TXS']
        else:
            self.error = 'Unable to retrieve transactions for address ' + self.address

        votes = self.txs_to_votes(txs, block_height, digits)
        results = self.calc_results(votes)

        if self.error == '':
            response['votes'] = votes
            response['results'] = results
            response['options'] = self.get_options()
            response['vote_cost'] = self.vote_cost
            response['block_height'] = block_height
            response['proposal'] = self.proposal
            response['address'] = self.address
            response['proposalHash'] = self.get_proposal_hash()

            if self.weights != '':
                response['weights'] = self.weights
            if self.registration_address != '':
                response['registration_address'] = self.registration_address
            if self.registration_block_height != '':
                response['registration_block_height'] = self.registration_block_height
            if self.registration_xpub != '':
                response['registration_xpub'] = self.registration_xpub

            response['success'] = 1

        else:
            response['error'] = self.error

        return response

    def txs_to_votes(self, txs, block_height, significant_digits=1):
        votes = {}
        if self.error == '':
            for i in range(0, len(txs)):
                if txs[i]['block_height'] <= block_height and txs[i]['receiving'] is True:
                    voter = txs[i]['primeInputAddress']
                    vote = str(txs[i]['receivedValue'])[-significant_digits:]
                    value = txs[i]['receivedValue'] - int(vote)

                    if (self.weights == 'Value' and value >= self.vote_cost) or value == self.vote_cost:
                        if voter in votes:
                            votes[voter]['lastVote'] = vote
                            votes[voter]['value'] += value
                        else:
                            votes[voter] = {'lastVote': vote, 'value': value}

        return votes

    def calc_results(self, votes):
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
                for tx_input in self.weight_values:
                    if tx_input[0] == voter:
                        value = tx_input[1]
                        break

                if option in results:
                    results[option] += value
                else:
                    results[option] = value

        return results