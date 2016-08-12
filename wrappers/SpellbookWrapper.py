

from BlockchainDataWrapper import BlockchainDataWrapper
from SimplifiedInputsListWrapper import SimplifiedInputsListWrapper
from BlocklinkerWrapper import BlocklinkerWrapper
from BlockRandomWrapper import BlockRandomWrapper
from BlockVoterWrapper import BlockVoterWrapper
from HDForwarderWrapper import HDForwarderWrapper
from DistributeBTCWrapper import DistributeBTCWrapper
from BlockTriggerWrapper import BlockTriggerWrapper
from BlockWriterWrapper import BlockWriterWrapper
from BlockProfileWrapper import BlockProfileWrapper



class SpellbookWrapper():

    def __init__(self, url='http://bitcoinspellbook.appspot.com'):
        self.url = url

    def BlockchainData(self):
        return BlockchainDataWrapper(self.url)

    def SimplifiedInputsList(self):
        return SimplifiedInputsListWrapper(self.url)

    def Blocklinker(self):
        return BlocklinkerWrapper(self.url)

    def BlockRandom(self):
        return BlockRandomWrapper(self.url)

    def BlockVoter(self):
        return BlockVoterWrapper(self.url)

    def HDForwarder(self):
        return HDForwarderWrapper(self.url)

    def DistributeBTC(self):
        return DistributeBTCWrapper(self.url)

    def BlockTrigger(self):
        return BlockTriggerWrapper(self.url)

    def BlockWriter(self):
        return BlockWriterWrapper(self.url)

    def BlockProfile(self):
        return BlockProfileWrapper(self.url)