#!/usr/bin/env python
# -*- coding: utf-8 -*-


import urllib2
import json
import urllib



class BlockVoterWrapper():
    def __init__(self, url):
        self.url = url


    def proposal(self, address, proposal, options=[], voteCost=0, weights='', registrationAddress="", registrationBlockHeight=0, registrationXPUB=""):
        response = {'success': 0}
        parameters = {}
        parameters['address'] = address
        parameters['proposal'] = proposal

        if options != []:
            strOptions = ""
            for option in options:
                strOptions += option + "|"

            strOptions = strOptions[:-1]
            parameters['options'] = strOptions

        if voteCost != 0:
            parameters['voteCost'] = str(voteCost)

        if weights != '':
            parameters['weights'] = weights

        if registrationAddress != "":
            parameters['regAddress'] = str(registrationAddress)

        if registrationBlockHeight != 0:
            parameters['regBlockHeight'] = str(registrationBlockHeight)

        if registrationXPUB != "":
            parameters['regXPUB'] = str(registrationXPUB)


        queryString  = urllib.urlencode(parameters)
        url = self.url + "/voter/proposal?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve proposal'

        return response

    def results(self, address, proposal, options=[], voteCost=0, blockHeight=0, weights='Equal', registrationAddress="", registrationBlockHeight=0, registrationXPUB=""):
        response = {'success': 0}
        parameters = {}
        parameters['address'] = address

        if proposal != "":
            parameters['proposal'] = str(proposal)

        if options != []:
            strOptions = ""
            for option in options:
                strOptions += option + "|"

            strOptions = strOptions[:-1]
            parameters['options'] = strOptions

        if voteCost != 0:
            parameters['voteCost'] = str(voteCost)

        if weights != '':
            parameters['weights'] = weights

        if blockHeight != 0:
            parameters['blockHeight'] = str(blockHeight)

        if registrationAddress != "":
            parameters['regAddress'] = str(registrationAddress)

        if registrationBlockHeight != 0:
            parameters['regBlock'] = str(registrationBlockHeight)

        if registrationXPUB != "":
            parameters['regXPUB'] = str(registrationXPUB)


        queryString  = urllib.urlencode(parameters)
        url = self.url + "/voter/results?" + queryString

        try:
            ret = urllib2.urlopen(urllib2.Request(url))
            response = json.loads(ret.read())
        except:
            response['error'] = 'Unable to retrieve results'

        return response