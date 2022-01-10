#!/usr/bin/env python3

#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

import logging
import subprocess


# Max log length before truncating the log file in the email message.
MAX_LOG_LENGTH = 20000
MAX_LOG_LENGTH_HALF = int(MAX_LOG_LENGTH / 2)


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

    # Mail only the first MAX_LOG_LENGTH/2 and last MAX_LOG_LENGTH/2 characters of the log file
    # if it is over MAX_LOG_LENGTH characters long.
    log_length = len(mail_body)
    if log_length > MAX_LOG_LENGTH:
        shrunk_by = log_length - MAX_LOG_LENGTH
        output_text = mail_body[:MAX_LOG_LENGTH_HALF]
        output_text += "\n\n...\n=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n"
        output_text += "= Skipping this part of the log because it is too long for email.\n"
        output_text += "= Only the first and last %6d lines are included.\n" % MAX_LOG_LENGTH_HALF
        output_text += "= A total of %8d lines in the middle were skipped.\n" % shrunk_by
        output_text += "= Go to URL above to view the entire log.\n"
        output_text += "=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n...\n\n"
        output_text += mail_body[-MAX_LOG_LENGTH_HALF:]

        mail_body = output_text

    cmd = f'echo "{mail_body}" | /usr/bin/mail -s "{subject}" "{recipient_emails}" -aFrom:"{from_email}"'

    if len(cc_list) > 0:
        cc_emails = ','.join(cc_list)
        cmd = f'{cmd} -cc {cc_emails}'

    logging.info(f'Will execute {cmd}')
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        logging.exception(f'Send mail failed: {e.output}')
        return False

    return True