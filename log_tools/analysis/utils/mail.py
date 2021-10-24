#!/usr/bin/env python3

#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

import logging
import subprocess


def Mail(owner_email, subject, mail_body):
    """Send completion mail to job submitter.

        Returns True if successful.

    owner_email is the e-mail address where results should be sent.
    subject is subject line.
    mail_body is contents of mail.
    """

    if owner_email is None:
        logging.error('Owner mail unexpectedly None')
        return False

    if not owner_email.endswith('@fungible.com'):
        logging.error(f'Owner mail {owner_email} not a fungible account.')
        return False

    logging.debug(f'Preparing to send email to {owner_email}')

    from_email = 'Log Analyzer<localadmin@funlogs01.fungible.local>'

    cmd = f'echo "{mail_body}" | /usr/bin/mail -s "{subject}" {owner_email} -aFrom:"{from_email}"'

    logging.debug(f'Will execute {cmd}')
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        logging.exception(f'Send mail failed: {e.output}')
        return False

    return True