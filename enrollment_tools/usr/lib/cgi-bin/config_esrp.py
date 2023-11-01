#! /usr/bin/env python3
#
# Copyright (c) 2023 Microsoft Corporation
# All Rights Reserved
#

''' Module to get/refresh/store OAuth tokens '''
import os
import time
from fcntl import flock, LOCK_EX, LOCK_UN, LOCK_NB
import json
import traceback

import requests

from common import DPU_REG_PATH


# esrpconfig.json
# {
#     "Endpoint": "https://api.esrp.microsoft.com",
#     "ClientId": "3ca1cde7-b3de-4ee3-a6f2-66c0adfc7c52",
#     "AadTokenPath": "/var/lib/dpu_reg/aadtoken",
#     "RequestSignerPfxPath": "/var/lib/dpu_reg/dpu-signing-openssl.pfx",
#     "RequestSignerPfxPassword": "mypass",
#     "HttpTimeoutSeconds": 30,
#     "RequestTimeoutSeconds": 120,
#     "MaxRetries": 3,
#     "RetrySleepSeconds": 5,
# }
# <clientid>
# {
#      "TokenExpiresOn" : <epoch time>,
#      "ClientSecret": <client_secret>
# }

EXPIRATION_MARGIN_SECS = 600

def read_json(file_path):
    ''' read json from file '''
    with open(file_path, 'r', encoding='utf-8') as file_p:
        return json.load(file_p)

def write_json(file_path, json_data):
    ''' write json to file '''
    with open(file_path, 'w', encoding='utf-8') as file_p:
        return json.dump(json_data, file_p)

def get_new_oauth(esrp_cfg, client_id_cfg):
    ''' send a request for a new access token '''
    post_url='https://login.windows.net/Microsoft.onMicrosoft.com/oauth2/token'

    post_data={
        'grant_type' : 'client_credentials',
        'client_id' : esrp_cfg['ClientId'],
        'client_secret' : client_id_cfg['ClientSecret'],
        'resource' : esrp_cfg['Endpoint']
    }
    response = requests.post(post_url, data = post_data, timeout=60)
    response.raise_for_status()
    return json.loads(response.text)


def check_token(esrp_cfg_path):
    ''' verify/get a valid token in esrpconfig['AddTokenPath'] '''

    esrp_cfg = read_json(esrp_cfg_path)
    # client_id file must exist
    client_id = esrp_cfg['ClientId']
    client_id_cfg_path = os.path.join(DPU_REG_PATH, client_id)

    client_id_cfg = read_json(client_id_cfg_path)

    # if the token is expired, request a new one until it succeeds
    while client_id_cfg['TokenExpiresOn'] < time.time():
        try:
            # write the token to the file and then the new expiration
            with open(client_id_cfg_path,
                      'w', encoding='utf-8') as file_cfg:

                # lock file to this process -- exception if already locked by
                # another process - basically used as a critical section
                flock(file_cfg, LOCK_EX | LOCK_NB)

                oauth_dict = get_new_oauth(esrp_cfg, client_id_cfg)
                expires_on = int(oauth_dict['expires_on'],0)
                client_id_cfg['TokenExpiresOn'] = expires_on - EXPIRATION_MARGIN_SECS

                # write the token
                with open(esrp_cfg['AadTokenPath'],
                          'w', encoding='utf-8') as file_token:
                    file_token.write(oauth_dict['access_token'])

                # write the new expiration
                json.dump(client_id_cfg, file_cfg)
                # not really necessary, lock released when closing file
                flock(file_cfg, LOCK_UN)

        except BlockingIOError:
            pass

        except: #pylint: disable=bare-except
            traceback.print_exc()

        # reread the json
        client_id_cfg = read_json(client_id_cfg_path)
