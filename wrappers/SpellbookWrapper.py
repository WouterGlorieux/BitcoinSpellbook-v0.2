

from BlockDataWrapper import BlockDataWrapper
from BlockInputsWrapper import BlockInputsWrapper
from BlockLinkerWrapper import BlockLinkerWrapper
from BlockRandomWrapper import BlockRandomWrapper
from BlockVoterWrapper import BlockVoterWrapper
from BlockForwardWrapper import BlockForwardWrapper
from BlockDistributeWrapper import BlockDistributeWrapper
from BlockTriggerWrapper import BlockTriggerWrapper
from BlockWriterWrapper import BlockWriterWrapper
from BlockProfileWrapper import BlockProfileWrapper


class SpellbookWrapper():

    def __init__(self, url='http://bitcoinspellbook.appspot.com'):
        self.url = url

    def blockdata(self):
        return BlockDataWrapper(self.url)

    def blockinputs(self):
        return BlockInputsWrapper(self.url)

    def blocklinker(self):
        return BlockLinkerWrapper(self.url)

    def blockrandom(self):
        return BlockRandomWrapper(self.url)

    def blockvoter(self):
        return BlockVoterWrapper(self.url)

    def blockforward(self):
        return BlockForwardWrapper(self.url)

    def blockdistribute(self):
        return BlockDistributeWrapper(self.url)

    def blocktrigger(self):
        return BlockTriggerWrapper(self.url)

    def blockwriter(self):
        return BlockWriterWrapper(self.url)

    def blockprofile(self):
        return BlockProfileWrapper(self.url)