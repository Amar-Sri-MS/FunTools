#
# Sets up (or modifies) the Snapshot Repository for storing the
# snapshots of logs ingested.
#
# All the snapshots stored using "logs_snapshots" as repository will
# reside in the mentioned "location". At least one of the parent
# directory of the location needs to be mentioned as "path.repo" in
# elasticsearch.yml files of the Elasticsearch nodes.
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

# Fetching elasticsearch URL from env
if [[ -z "${ELASTICSEARCH_URL}" ]]; then
  URL="localhost:9200"
else
  URL="${ELASTICSEARCH_URL}"
fi

curl -X PUT "${URL}/_snapshot/logs_snapshots" -H 'Content-Type: application/json' -d'
{
    "type": "fs",
    "settings": {
        "location": "/archive2/users/sourabhj/snapshots/logs",
        "compress": true
    }
}
'