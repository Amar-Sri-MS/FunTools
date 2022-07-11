#
# Sets up (or modifies) the Snapshot Lifecycle Management Policy for
# managing the snapshots of logs ingested from Fun-on-demand jobs.
#
# The snapshots are taken daily (controlled by the field "schedule").
# They can be used to restore the indicies if and when required.
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

# Fetching elasticsearch URL from env
if [[ -z "${ELASTICSEARCH_URL}" ]]; then
  URL="localhost:9200"
else
  URL="${ELASTICSEARCH_URL}"
fi

curl -X PUT "${URL}/_slm/policy/fod" -H 'Content-Type: application/json' -d'
{
    "schedule": "0 30 1 * * ?",
    "name": "<fod-{now/d}>",
    "repository": "logs_snapshots",
    "config": {
        "indices": ["log_fod-*"],
        "ignore_unavailable": false,
        "include_global_state": false
    },
    "retention": {
        "expire_after": "30d"
    }
}
'