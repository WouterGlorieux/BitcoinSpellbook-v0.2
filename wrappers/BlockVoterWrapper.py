#!/usr/bin/env python
# -*- coding: utf-8 -*-


import urllib2
import json
import urllib


class BlockVoterWrapper():
    def __init__(self, url):
        self.url = url

    def proposal(self, address, proposal, options=None, vote_cost=0, weights='', registration_address="",
                 registration_block_height=0, registration_xpub=""):
        if not options:
            options = []
        response = {'success': 0}
        parameters = {'address': address,
                      'proposal': proposal}

        if options:
            str_options = ""
            for option in options:
                str_options += option + "|"

            str_options = str_options[:-1]
            parameters['options'] = str_options

        if vote_cost != 0:
            parameters['vote_cost'] = str(vote_cost)

        if weights != '':
            parameters['weights'] = weights

        if registration_address != "":
            parameters['registration_address'] = str(registration_address)

        if registration_block_height != 0:
            parameters['registration_block_height'] = str(registration_block_height)

        if registration_xpub != "":
            parameters['registration_xpub'] = str(registration_xpub)

        query_string = urllib.urlencode(parameters)
        url = self.url + "/voter/proposal?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve proposal'

        return response

    def results(self, address, proposal, options=None, vote_cost=0, block_height=0, weights='Equal',
                registration_address="", registration_block_height=0, registration_xpub=""):
        if not options:
            options = []
        response = {'success': 0}
        parameters = {'address': address}

        if proposal != "":
            parameters['proposal'] = str(proposal)

        if options:
            str_options = ""
            for option in options:
                str_options += option + "|"

            str_options = str_options[:-1]
            parameters['options'] = str_options

        if vote_cost != 0:
            parameters['vote_cost'] = str(vote_cost)

        if weights != '':
            parameters['weights'] = weights

        if block_height != 0:
            parameters['block_height'] = str(block_height)

        if registration_address != "":
            parameters['registration_address'] = str(registration_address)

        if registration_block_height != 0:
            parameters['registration_block_height'] = str(registration_block_height)

        if registration_xpub != "":
            parameters['registration_xpub'] = str(registration_xpub)

        query_string = urllib.urlencode(parameters)
        url = self.url + "/voter/results?" + query_string

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve results'

        return response