

from BlockchainDataWrapper import BlockchainDataWrapper
from SimplifiedInputsListWrapper import SimplifiedInputsListWrapper
from BlocklinkerWrapper import BlocklinkerWrapper
from BlockRandomWrapper import BlockRandomWrapper

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