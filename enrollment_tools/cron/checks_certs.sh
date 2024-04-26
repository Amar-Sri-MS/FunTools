#!/usr/bin/env bash 

#######
# Check certificates on f1reg: ESRP signer certificate, SSL certificate
#
# Copyright (c) 2023. Microsoft Corporation. All Rights Reserved.
#


# user variables
ssl_target="f1reg.fungible.com:443"
esrp_target="https://f1reg.fungible.com:4443/cgi-bin/signing_server.cgi?cmd=esrp_signer_cert"
expiration_days_threshold="500"

mail_subject="Signing Server $ssl_target - some certificates are about to expire"
mail_from="F1Reg Cert Checker <f1reg-checker@fungible.com>"
mail_to="fferino@microsoft.com"

#set -x

###
# functions

days_before_expiration() {
    date_epoch=$(date -d "$1" '+%s')
    now_epoch=$(date '+%s')
    echo $(( (date_epoch - now_epoch) / 86400 ))
}

create_mail_body() {
  mail_body="Hi,

this email is to let your know that some of the certificates
on the signing server $ssl_target are about to expire:

The SSL Certificate will expire in ${days_left_ssl} days (exactly on ${expiration_date_ssl}).

The ESRP Signer Certificate will expire in ${days_left_esrp} days (exactly on ${expiration_date_esrp}).

Please make sure to renew these certificates before their deadline.
Otherwise, the signing server will no longer work and engineers will
no longer be able to test their software.

Thanks,
Bartleby"
}

send_mail() {
  echo "${mail_body}" | mailx -s "${mail_subject}" -r "${mail_from}" "${mail_to}"
}

check_if_expired() {
    [[ ${days_left_ssl} -lt ${expiration_days_threshold} || \
	   ${days_left_esrp} -lt ${expiration_days_threshold} ]] && \
	create_mail_body && send_mail
}

###
# program variables (do not edit)
expiration_date_ssl=$(openssl s_client -connect ${ssl_target} 2>&- \
                    | openssl x509 -enddate -noout \
                    | awk -F= '{print $2}')

expiration_date_esrp=$(curl "${esrp_target}" \
                      | openssl x509 -enddate -noout \
                      | awk -F= '{print $2}')

days_left_ssl=$(days_before_expiration "${expiration_date_ssl}")
days_left_esrp=$(days_before_expiration "${expiration_date_esrp}")

###
# main()

check_if_expired

