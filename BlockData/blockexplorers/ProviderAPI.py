#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import abstractmethod, ABCMeta


class ProviderAPI(object):
    __metaclass__ = ABCMeta

    def __init__(self, url='', key='', secret=''):
        self.error = ''
        self.url = url
        self.key = key
        self.secret = secret

    @abstractmethod
    def get_txs(self, address):
        pass

    @abstractmethod
    def get_latest_block(self):
        pass

    @abstractmethod
    def get_block(self, height):
        pass

    @abstractmethod
    def get_balances(self, addresses):
        pass

    @abstractmethod
    def get_utxos(self, addresses, confirmations=3):
        pass

    @abstractmethod
    def get_prime_input_address(self, txid):
        pass