#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging
import urllib2
import json

from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from google.appengine.api import mail
urlfetch.set_default_fetch_deadline(60)

from validators import validators as validator
import BlockData.BlockData as BlockData
import datastore.datastore as datastore


REQUIRED_CONFIRMATIONS = 3  # must be at least 3


def trigger_to_dict(trigger):
    trigger_dict = {'name': trigger.key.id(),
                    'trigger_type': trigger.trigger_type,
                    'address': trigger.address,
                    'amount': trigger.amount,
                    'confirmations': trigger.confirmations,
                    'triggered': trigger.triggered,
                    'description': trigger.description,
                    'creator': trigger.creator,
                    'creator_email': trigger.creator_email,
                    'youtube': trigger.youtube,
                    'status': trigger.status,
                    'visibility': trigger.visibility,
                    'date': int(time.mktime(trigger.date.timetuple()))}

    actions_query = datastore.Action.query(ancestor=trigger.key)
    actions = actions_query.fetch()

    trigger_dict['actions'] = []
    for action in actions:
        trigger_dict['actions'].append(action_to_dict(action))

    return trigger_dict


def action_to_dict(action):
    action_dict = {'triggerName': action.trigger,
                   'actionName': action.key.id(),
                   'action_type': action.action_type,
                   'description': action.description}

    if action.action_type == 'reveal_text' and action.reveal_allowed is True:
        action_dict['reveal_text'] = action.reveal_text
    elif action.action_type == 'reveal_link' and action.reveal_allowed is True:
        action_dict['reveal_link_text'] = action.reveal_link_text
        action_dict['reveal_link_url'] = action.reveal_link_url
    elif action.action_type == 'send_mail':
        action_dict['mail_to'] = action.mail_to
        action_dict['mail_subject'] = action.mail_subject
        action_dict['mail_body'] = action.mail_body
        action_dict['mail_sent'] = action.mail_sent
    elif action.action_type == 'webhook':
        action_dict['webhook'] = action.webhook

    return action_dict


def get_triggers():
    response = {'success': 0}
    triggers = []

    triggers_query = datastore.Trigger.query(datastore.Trigger.visibility == 'Public',
                                             datastore.Trigger.status == 'Active',
                                             ancestor=datastore.triggers_key()).order(-datastore.Trigger.date)
    data = triggers_query.fetch()
    for trigger in data:
        triggers.append(trigger_to_dict(trigger))

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
                response['trigger'] = trigger_to_dict(trigger)
                response['success'] = 1
            else:
                response['error'] = 'No trigger with that name found.'

        return response

    def save_trigger(self, settings=None):
        if not settings:
            settings = {}
        response = {'success': 0}

        if self.error == '':
            trigger = datastore.Trigger.get_or_insert(self.name, parent=datastore.triggers_key())

            if 'trigger_type' in settings and settings['trigger_type'] in ['Balance', 'Received', 'Sent', 'block_height']:
                trigger.trigger_type = settings['trigger_type']
            elif 'trigger_type' in settings:
                self.error = 'trigger_type must be Balance, Received or Sent'

            if 'address' in settings and (validator.valid_address(settings['address']) or settings['address'] == ''):
                trigger.address = settings['address']
            elif 'address' in settings:
                self.error = 'Invalid address'

            if 'block_height' in settings and validator.valid_block_height(settings['block_height']):
                trigger.block_height = settings['block_height']
            elif 'block_height' in settings:
                self.error = 'block_height must be an integer greater than 0'

            if 'amount' in settings and validator.valid_amount(settings['amount']):
                trigger.amount = settings['amount']
            elif 'amount' in settings:
                self.error = 'amount must be greater than or equal to 0 (in Satoshis)'

            if 'confirmations' in settings and validator.valid_amount(settings['confirmations']):
                trigger.confirmations = settings['confirmations']
            elif 'confirmations' in settings:
                self.error = 'confirmations must be a positive integer or equal to 0'

            if 'description' in settings and validator.valid_description(settings['description']):
                trigger.description = settings['description']
            elif 'description' in settings:
                self.error = 'Invalid description'

            if 'creator' in settings and validator.valid_creator(settings['creator']):
                trigger.creator = settings['creator']
            elif 'creator' in settings:
                self.error = 'Invalid creator'

            if 'creator_email' in settings and validator.valid_email(settings['creator_email']):
                trigger.creator_email = settings['creator_email']
            elif 'creator_email' in settings:
                self.error = 'Invalid email address'

            if 'youtube' in settings and validator.valid_youtube_id(settings['youtube']):
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
                response['trigger'] = trigger_to_dict(trigger)
                response['success'] = 1

            else:
                response['error'] = self.error

        return response

    def delete_trigger(self):
        response = {'success': 0}

        if self.error == '':
            trigger = datastore.Trigger.get_by_id(self.name, parent=datastore.triggers_key())

            if trigger:
                trigger.key.delete()
                response['success'] = 1
            else:
                response['error'] = 'No trigger with that name found.'

        return response

    def save_action(self, action_name, settings=None):
        if not settings:
            settings = {}
        response = {'success': 0}

        if self.error == '':
            trigger = datastore.Trigger.get_by_id(self.name, parent=datastore.triggers_key())
            action = datastore.Action.get_or_insert(action_name, parent=trigger.key)

            action.trigger = trigger.key.id()

            if 'action_type' in settings and settings['action_type'] in ['reveal_text', 'reveal_link', 'send_mail', 'webhook']:
                action.action_type = settings['action_type']
            elif 'action_type' in settings:
                self.error = 'action_type must be reveal_text, reveal_link, send_mail or webhook'

            if 'description' in settings and validator.valid_description(settings['description']):
                action.description = settings['description']
            elif 'description' in settings:
                self.error = 'invalid description'

            if 'reveal_text' in settings and validator.valid_text(settings['reveal_text']):
                action.reveal_text = settings['reveal_text']
            elif 'reveal_text' in settings:
                self.error = 'invalid reveal_text'

            if 'reveal_link_text' in settings and validator.valid_text(settings['reveal_link_text']):
                action.reveal_link_text = settings['reveal_link_text']
            elif 'reveal_link_text' in settings:
                self.error = 'invalid reveal_link_text'

            if 'reveal_link_url' in settings and validator.valid_url(settings['reveal_link_url']):
                action.reveal_link_url = settings['reveal_link_url']
            elif 'reveal_link_url' in settings:
                self.error = 'invalid reveal_link_url'

            if 'mail_to' in settings and validator.valid_email(settings['mail_to']):
                action.mail_to = settings['mail_to']
            elif 'mail_to' in settings:
                self.error = 'invalid mail_to address'

            if 'mail_subject' in settings and validator.valid_text(settings['mail_subject']):
                action.mail_subject = settings['mail_subject']
            elif 'mail_subject' in settings:
                self.error = 'invalid mail_subject'

            if 'mail_body' in settings and validator.valid_text(settings['mail_body']):
                action.mail_body = settings['mail_body']
            elif 'mail_body' in settings:
                self.error = 'invalid mail_body'

            if 'mail_sent' in settings and settings['mail_sent'] in [True, False]:
                action.mail_sent = settings['mail_sent']
            elif 'mail_sent' in settings:
                self.error = 'invalid mail_sent'

            if 'webhook' in settings and validator.valid_url(settings['webhook']):
                action.webhook = settings['webhook']
            elif 'webhook' in settings:
                self.error = 'invalid webhook'

            if self.error == '':
                action.put()
                response['action'] = action_to_dict(action)
                response['success'] = 1

            else:
                response['error'] = self.error

        return response

    def delete_action(self, action_name):
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
            if trigger.trigger_type == 'block_height':
                latest_block_data = BlockData.latest_block()
                if 'success' in latest_block_data and latest_block_data['success'] == 1:
                    latest_block_height = latest_block_data['latest_block']['height']
                    if trigger.block_height + trigger.confirmations <= latest_block_height:
                        logging.info('{0}: {1} activated: current block_height:{2}'.format(str(trigger.key.id()),
                                                                                           str(trigger.trigger_type),
                                                                                           str(latest_block_height)))
                        trigger.triggered = True
                        trigger.put()
                        self.activate(trigger)
                else:
                    logging.error('Unable to retrieve latest block_height')

            elif trigger.trigger_type in ['Balance', 'Received', 'Sent']:
                balance_data = BlockData.balances(trigger.address)

                if 'success' in balance_data and balance_data['success'] == 1:
                    balances = balance_data['balances'][trigger.address]
                    value = 0
                    if trigger.trigger_type == 'Balance':
                        value = balances['balance']
                    elif trigger.trigger_type == 'Received':
                        value = balances['received']
                    elif trigger.trigger_type == 'Sent':
                        value = balances['sent']

                    if trigger.amount <= value:
                        logging.info('{0}: {1} activated: current value:{2}'.format(str(trigger.key.id()),
                                                                                    str(trigger.trigger_type),
                                                                                    str(value)))
                        trigger.triggered = True
                        trigger.put()
                else:
                    logging.error('Unable to retrieve balances for address: ' + trigger.address)

    @staticmethod
    def activate(trigger):
            actions_query = datastore.Action.query(ancestor=trigger.key)
            actions = actions_query.fetch()

            for action in actions:

                if action.action_type in ['reveal_text', 'reveal_link'] and action.reveal_allowed is False:
                    logging.info('executing action: ' + action.key.id())
                    action.reveal_allowed = True
                    action.put()

                elif action.action_type == 'send_mail' and action.mail_sent is False:
                    if validator.valid_email(action.mail_to):
                        logging.info('executing action: ' + action.key.id())
                        try:
                            parameters = datastore.Parameters.get_by_id('DefaultConfig')
                            mail.send_mail(parameters.mail_from, action.mail_to, action.mail_subject, action.mail_body)
                            action.mail_sent = True
                            action.put()
                            logging.info('Mail sent successfully.')
                        except Exception as ex:
                            logging.warning(str(ex))
                            logging.error("Failed to send mail")
                    else:
                        logging.error("Invalid email address: " + action.mail_to)

                elif action.action_type == 'webhook' and action.webhook_activated is False:

                    if validator.valid_url(action.webhook):
                        logging.info('executing action: ' + action.key.id())
                        try:
                            logging.info('starting webhook')
                            url = action.webhook
                            ret = urllib2.urlopen(urllib2.Request(url))
                            response = json.loads(ret.read())
                            logging.info('webhook executed, response: ' + str(response))
                            action.webhook_activated = True
                            action.put()
                        except Exception as ex:
                            logging.warning(str(ex))
                            logging.error = "Unable to execute webhook"