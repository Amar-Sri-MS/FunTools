#!/usr/bin/env python3

#
# Email Alerter. Sends out alerts via email.
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2022 Fungible Inc.  All rights reserved.

import json
import subprocess

import logger

from alerts.alert import AlertType


log_handler = logger.get_logger(filename='alerter.log')

# Max log length before truncating the log file in the email message.
MAX_LOG_LENGTH = 20000
MAX_LOG_LENGTH_HALF = int(MAX_LOG_LENGTH / 2)


class EmailAlert(AlertType):
    """
    Email alerter to send alerts via emails.
    """
    def __init__(self):
        super().__init__()
        self.config = {
            'email_addresses': ['sourabh.jain@fungible.com']
        }

    def process(self, alert):
        """
        Takes input dict, returns bool status of alert.

        Dict should contain the following keys:
        - context_title (str)
        - context_message (str)
        - tags (list)
        - hits
        """
        log_handler.info('*'*100)
        # log_handler.info(alert.get('alert_name'))
        # log_handler.info(alert.get('context_title'))
        # log_handler.info(alert.get('context_message'))
        # log_handler.info(alert.get('tags'))

        email_addresses = self._get_email_addresses_from_tags(alert.get('tags'))
        email_addresses.extend(self.config.get('email_addresses'))
        recipient_emails = ','.join(email_addresses)
        cc_list = list()

        log_handler.info(f'Preparing to send email to {recipient_emails}')

        subject = alert.get('context_title')
        from_email = 'Log Analyzer<localadmin@funlogs01.fungible.local>'

        mail_body = f"""{alert.get('context_message')}"""
        mail_body += '\n' + json.dumps(alert.get('hits'), sort_keys=True, indent=2)

        log_handler.info(mail_body)
        log_handler.info('-'*100)

        # Mail only the first MAX_LOG_LENGTH/2 and last MAX_LOG_LENGTH/2 characters of the log file
        # if it is over MAX_LOG_LENGTH characters long.
        # log_length = len(mail_body)
        # if log_length > MAX_LOG_LENGTH:
        #     shrunk_by = log_length - MAX_LOG_LENGTH
        #     output_text = mail_body[:MAX_LOG_LENGTH_HALF]
        #     output_text += "\n\n...\n=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n"
        #     output_text += "= Skipping this part of the log because it is too long for email.\n"
        #     output_text += "= Only the first and last %6d lines are included.\n" % MAX_LOG_LENGTH_HALF
        #     output_text += "= A total of %8d lines in the middle were skipped.\n" % shrunk_by
        #     output_text += "= Go to URL above to view the entire log.\n"
        #     output_text += "=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n...\n\n"
        #     output_text += mail_body[-MAX_LOG_LENGTH_HALF:]

        #     mail_body = output_text

        cmd = f'echo "{mail_body}" | /usr/bin/mail -s "{subject}" "{recipient_emails}" -aFrom:"{from_email}"'

        if len(cc_list) > 0:
            cc_emails = ','.join(cc_list)
            cmd = f'{cmd} -aCC:"{cc_emails}"'

        log_handler.info(f'Will execute {cmd}')
        try:
            out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        except subprocess.CalledProcessError as e:
            log_handler.exception(f'Send mail failed: {e.output}')
            return False

        return True

    def set_config(self, config):
        """ Sets the config for this alert """
        self.config = config

    def _get_email_addresses_from_tags(self, tags, domains=['fungible.com']):
        # Converting domains list into a tuple since endswith only supports
        # checking with tuple.
        if type(domains) == list:
            domains = tuple(domains)

        email_addresses = list()
        for tag in tags:
            if tag.endswith(domains):
                email_addresses.append(tag)
        return email_addresses