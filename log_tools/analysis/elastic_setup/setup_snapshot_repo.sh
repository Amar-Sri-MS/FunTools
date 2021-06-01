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

curl -X PUT "localhost:9200/_snapshot/logs_snapshots" -H 'Content-Type: application/json' -d'
{
    "type": "fs",
    "settings": {
        "location": "/archive/users/sourabhj/snapshots/logs",
        "compress": true
    }
}
'