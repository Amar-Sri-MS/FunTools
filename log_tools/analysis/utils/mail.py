#!/usr/bin/env python3

#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

import logging
import subprocess


def Mail(owner_email, subject, mail_body, cc_list=[]):
    """Send completion mail to job submitter.

        Returns True if successful.

    owner_email is the e-mail address(es) where results should be sent.
        This can be either a str or a list.
    subject is subject line.
    mail_body is contents of mail.
    cc_list is the list of email addresses.
    """

    if owner_email is None:
        logging.error('Owner mail unexpectedly None')
        return False

    recipient_emails = None
    if type(owner_email) == list:
        recipient_emails = ','.join(owner_email)
    elif type(owner_email) == str:
        if not owner_email.endswith('@fungible.com'):
            logging.error(f'Owner mail {owner_email} not a fungible account.')
            return False
        recipient_emails = owner_email
    else:
        logging.error(f'Owner mail {owner_email} is not a list or str but {type(owner_email)}')
        return False

    logging.info(f'Preparing to send email to {recipient_emails}')

    from_email = 'Log Analyzer<localadmin@funlogs01.fungible.local>'

    cmd = f'/usr/bin/mail -s "{subject}" "{recipient_emails}" -aFrom:"{from_email}"'

    if len(cc_list) > 0:
        cc_emails = ','.join(cc_list)
        cmd = f'{cmd} -c {cc_emails}'

    cmd = f'{cmd} <<< {mail_body}'

    logging.info(f'Will execute {cmd}')
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        logging.exception(f'Send mail failed: {e.output}')
        return False

    return True