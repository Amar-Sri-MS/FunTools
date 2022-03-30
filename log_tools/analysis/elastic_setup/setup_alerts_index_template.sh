#
# Sets up (or modifies) the index template for storing Kibana alerts.
#
# The primary use is to set the type of the extracted fields in the
# alerts from Kibana. Any index created with the prefix "alerts"
# will get this template.
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2022 Fungible Inc.  All rights reserved.

# Fetching elasticsearch URL from env
if [[ -z "${ELASTICSEARCH_URL}" ]]; then
  URL="localhost:9200"
else
  URL="${ELASTICSEARCH_URL}"
fi

curl -X PUT "${URL}:9200/_index_template/metadata_template" -H 'Content-Type: application/json' -d'
{
    "index_patterns": ["alerts*"],
    "template": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 1
        },
        "mappings": {
            "properties": {
                "@timestamp": {
                    "type": "date"
                },
                "hits": {
                    "type": "text",
                    "index": false
                }
            }
        }
    }
}
'