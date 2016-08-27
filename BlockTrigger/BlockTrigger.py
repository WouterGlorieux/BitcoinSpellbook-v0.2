#!/usr/bin/env python
# -*- coding: utf-8 -*-


from validators import validators as validator
import BlockData.BlockData as BlockData
import datastore.datastore as datastore

import time
import logging
import urllib2
import json
import urllib

from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from google.appengine.api import mail
urlfetch.set_default_fetch_deadline(60)


REQUIRED_CONFIRMATIONS = 3  # must be at least 3


def triggerToDict(trigger):
    trigger_dict = {'name': trigger.key.id(),
                    'triggerType': trigger.triggerType,
                    'address': trigger.address,
                    'amount': trigger.amount,
                    'confirmations': trigger.confirmations,
                    'triggered': trigger.triggered,
                    'description': trigger.description,
                    'creator': trigger.creator,
                    'creatorEmail': trigger.creatorEmail,
                    'youtube': trigger.youtube,
                    'status': trigger.status,
                    'visibility': trigger.visibility,
                    'date': int(time.mktime(trigger.date.timetuple()))}

    actions_query = datastore.Action.query(ancestor=trigger.key)
    actions = actions_query.fetch()

    trigger_dict['actions'] = []
    for action in actions:
        trigger_dict['actions'].append(actionToDict(action))

    return trigger_dict


def actionToDict(action):
    action_dict = {'triggerName': action.trigger,
                   'actionName': action.key.id(),
                   'actionType': action.actionType,
                   'description': action.description}

    if action.actionType == 'RevealText' and action.revealAllowed is True:
        action_dict['revealText'] = action.revealText
    elif action.actionType == 'RevealLink' and action.revealAllowed is True:
        action_dict['revealLinkText'] = action.revealLinkText
        action_dict['revealLinkURL'] = action.revealLinkURL
    elif action.actionType == 'SendMail':
        action_dict['mailTo'] = action.mailTo
        action_dict['mailSubject'] = action.mailSubject
        action_dict['mailBody'] = action.mailBody
        action_dict['mailSent'] = action.mailSent
    elif action.actionType == 'Webhook':
        action_dict['webhook'] = action.webhook

    return action_dict


def getTriggers():
    response = {'success': 0}
    triggers = []

    triggers_query = datastore.Trigger.query(datastore.Trigger.visibility == 'Public',
                                             datastore.Trigger.status == 'Active',
                                             ancestor=datastore.triggers_key()).order(-datastore.Trigger.date)
    data = triggers_query.fetch()
    for trigger in data:
        triggers.append(triggerToDict(trigger))

    response['triggers'] = triggers
    response['success'] = 1

    return response


class BlockTrigger():
    @ndb.transactional(xg=True)
    def __init__(self, name):
        self.error = ''
        if isinstance(name, (str, unicode)) and len(name) > 0:
            self.name = name
        else:
            self.error = 'Name cannot be empty'

    def get(self):
        response = {'success': 0}
        if self.error == '':
            trigger = datastore.Trigger.get_by_id(self.name, parent=datastore.triggers_key())

            if trigger:
                response['trigger'] = triggerToDict(trigger)
                response['success'] = 1
            else:
                response['error'] = 'No trigger with that name found.'

        return response

    def saveTrigger(self, settings=None):
        if not settings:
            settings = {}
        response = {'success': 0}

        if self.error == '':
            trigger = datastore.Trigger.get_or_insert(self.name, parent=datastore.triggers_key())

            if 'triggerType' in settings and settings['triggerType'] in ['Balance', 'Received', 'Sent', 'BlockHeight']:
                trigger.triggerType = settings['triggerType']
            elif 'triggerType' in settings:
                self.error = 'triggerType must be Balance, Received or Sent'

            if 'address' in settings and (validator.validAddress(settings['address']) or settings['address'] == ''):
                trigger.address = settings['address']
            elif 'address' in settings:
                self.error = 'Invalid address'

            if 'amount' in settings and validator.validAmount(settings['amount']):
                trigger.amount = settings['amount']
            elif 'amount' in settings:
                self.error = 'amount must be greater than or equal to 0 (in Satoshis)'

            if 'confirmations' in settings and validator.validAmount(settings['confirmations']):
                trigger.confirmations = settings['confirmations']
            elif 'confirmations' in settings:
                self.error = 'confirmations must be a positive integer or equal to 0'

            if 'description' in settings and validator.validDescription(settings['description']):
                trigger.description = settings['description']
            elif 'description' in settings:
                self.error = 'Invalid description'

            if 'creator' in settings and validator.validCreator(settings['creator']):
                trigger.creator = settings['creator']
            elif 'creator' in settings:
                self.error = 'Invalid creator'

            if 'creatorEmail' in settings and validator.validEmail(settings['creatorEmail']):
                trigger.creatorEmail = settings['creatorEmail']
            elif 'creatorEmail' in settings:
                self.error = 'Invalid email address'

            if 'youtube' in settings and validator.validYoutubeID(settings['youtube']):
                trigger.youtube = settings['youtube']
            elif 'youtube' in settings:
                self.error = 'Invalid youtube video ID'

            if 'visibility' in settings and settings['visibility'] in ['Public', 'Private']:
                trigger.visibility = settings['visibility']
            elif 'visibility' in settings:
                self.error = 'visibility must be Public or Private'

            if 'status' in settings and settings['status'] in ['Pending', 'Active', 'Disabled']:
                trigger.status = settings['status']
            elif 'status' in settings:
                self.error = 'status must be Pending, Active or Disabled'

            if 'triggered' in settings and settings['triggered'] in [True, False]:
                trigger.triggered = settings['triggered']
            elif 'triggered' in settings:
                self.error = 'invalid triggered'

            if self.error == '':
                trigger.put()
                response['trigger'] = triggerToDict(trigger)
                response['success'] = 1

            else:
                response['error'] = self.error

        return response

    def deleteTrigger(self):
        response = {'success': 0}

        if self.error == '':
            trigger = datastore.Trigger.get_by_id(self.name, parent=datastore.triggers_key())

            if trigger:
                trigger.key.delete()
                response['success'] = 1
            else:
                response['error'] = 'No trigger with that name found.'

        return response

    def saveAction(self, action_name, settings=None):
        if not settings:
            settings = {}
        response = {'success': 0}

        if self.error == '':
            trigger = datastore.Trigger.get_by_id(self.name, parent=datastore.triggers_key())
            action = datastore.Action.get_or_insert(action_name, parent=trigger.key)

            action.trigger = trigger.key.id()

            if 'actionType' in settings and settings['actionType'] in ['RevealText', 'RevealLink', 'SendMail', 'Webhook']:
                action.actionType = settings['actionType']
            elif 'actionType' in settings:
                self.error = 'actionType must be RevealText, RevealLink, SendMail or Webhook'

            if 'description' in settings and validator.validDescription(settings['description']):
                action.description = settings['description']
            elif 'description' in settings:
                self.error = 'invalid description'

            if 'revealText' in settings and validator.validText(settings['revealText']):
                action.revealText = settings['revealText']
            elif 'revealText' in settings:
                self.error = 'invalid revealText'

            if 'revealLinkText' in settings and validator.validText(settings['revealLinkText']):
                action.revealLinkText = settings['revealLinkText']
            elif 'revealLinkText' in settings:
                self.error = 'invalid revealLinkText'

            if 'revealLinkURL' in settings and validator.validURL(settings['revealLinkURL']):
                action.revealLinkURL = settings['revealLinkURL']
            elif 'revealLinkURL' in settings:
                self.error = 'invalid revealLinkURL'

            if 'mailTo' in settings and validator.validEmail(settings['mailTo']):
                action.mailTo = settings['mailTo']
            elif 'mailTo' in settings:
                self.error = 'invalid mailTo address'

            if 'mailSubject' in settings and validator.validText(settings['mailSubject']):
                action.mailSubject = settings['mailSubject']
            elif 'mailSubject' in settings:
                self.error = 'invalid mailSubject'

            if 'mailBody' in settings and validator.validText(settings['mailBody']):
                action.mailBody = settings['mailBody']
            elif 'mailBody' in settings:
                self.error = 'invalid mailBody'

            if 'mailSent' in settings and settings['mailSent'] in [True, False]:
                action.mailSent = settings['mailSent']
            elif 'mailSent' in settings:
                self.error = 'invalid mailSent'

            if 'webhook' in settings and validator.validURL(settings['webhook']):
                action.webhook = settings['webhook']
            elif 'webhook' in settings:
                self.error = 'invalid webhook'

            if self.error == '':
                action.put()
                response['action'] = actionToDict(action)
                response['success'] = 1

            else:
                response['error'] = self.error

        return response

    def deleteAction(self, action_name):
        response = {'success': 0}

        if self.error == '':
            trigger = datastore.Trigger.get_by_id(self.name, parent=datastore.triggers_key())
            action = datastore.Action.get_by_id(action_name,  parent=trigger.key)

            if action:
                action.key.delete()
                response['success'] = 1
            else:
                response['error'] = 'No action with that name found.'

        return response


class CheckTriggers():
    def __init__(self, name=''):

        if name != '':
            trigger = datastore.Trigger.get_by_id(name, parent=datastore.triggers_key())
            if trigger:
                self.run(trigger)

        else:
            triggers_query = datastore.Trigger.query(datastore.Trigger.status == 'Active')
            triggers = triggers_query.fetch()

            for trigger in triggers:
                self.run(trigger)

    def run(self, trigger):
        if not trigger.triggered:
            if trigger.triggerType == 'BlockHeight':
                latest_block_data = BlockData.latestBlock()
                if 'success' in latest_block_data and latest_block_data['success'] == 1:
                    latest_block_height = latest_block_data['latestBlock']['height']
                    if trigger.blockHeight + trigger.confirmations <= latest_block_height:
                        logging.info(str(trigger.key.id()) + ': ' + str(trigger.triggerType) + ' activated: ' +  ' current block_height:' + str(latest_block_height))
                        trigger.triggered = True
                        trigger.put()
                        self.activate(trigger)
                else:
                    logging.error('Unable to retrieve latest block_height')

            elif trigger.triggerType in ['Balance', 'Received', 'Sent']:
                balance_data = BlockData.balances(trigger.address)

                if 'success' in balance_data and balance_data['success'] == 1:
                    balances = balance_data['balances'][trigger.address]
                    value = 0
                    if trigger.triggerType == 'Balance':
                        value = balances['balance']
                    elif trigger.triggerType == 'Received':
                        value = balances['received']
                    elif trigger.triggerType == 'Sent':
                        value = balances['sent']

                    if trigger.amount <= value:
                        logging.info(str(trigger.key.id()) + ': ' + str(trigger.triggerType) + ' activated: ' +  ' current value:' + str(value))
                        trigger.triggered = True
                        trigger.put()
                else:
                    logging.error('Unable to retrieve balances for address: ' + trigger.address)

    def activate(self, trigger):
            actions_query = datastore.Action.query(ancestor=trigger.key)
            actions = actions_query.fetch()

            for action in actions:

                if action.actionType in ['RevealText', 'RevealLink'] and action.revealAllowed is False:
                    logging.info('executing action: ' + action.key.id())
                    action.revealAllowed = True
                    action.put()

                elif action.actionType == 'SendMail' and action.mailSent is False:
                    if validator.validEmail(action.mailTo):
                        logging.info('executing action: ' + action.key.id())
                        try:
                            parameters = datastore.Parameters.get_by_id('DefaultConfig')
                            mail.send_mail(parameters.mailFrom, action.mailTo, action.mailSubject, action.mailBody)
                            action.mailSent = True
                            action.put()
                            logging.info('Mail sent successfully.')
                        except:
                            logging.error("Failed to send mail")
                    else:
                        logging.error("Invalid email address: " + action.mailTo)

                elif action.actionType == 'Webhook' and action.webhookActivated is False:

                    if validator.validURL(action.webhook):
                        logging.info('executing action: ' + action.key.id())
                        try:
                            logging.info('starting webhook')
                            url = action.webhook
                            ret = urllib2.urlopen(urllib2.Request(url))
                            response = json.loads(ret.read())
                            logging.info('webhook executed, response: ' + str(response))
                            action.webhookActivated = True
                            action.put()
                        except:
                            logging.error = "Unable to execute webhook"