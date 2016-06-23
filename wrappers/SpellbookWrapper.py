

from BlockchainDataWrapper import BlockchainDataWrapper
from SimplifiedInputsListWrapper import SimplifiedInputsListWrapper

class SpellbookWrapper():

    def __init__(self, url='http://bitcoinspellbook.appspot.com'):
        self.url = url

    def BlockchainData(self):
        return BlockchainDataWrapper(self.url)

    def SimplifiedInputsList(self):
        return SimplifiedInputsListWrapper(self.url)