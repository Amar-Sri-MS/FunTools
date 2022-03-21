#
# Sets up (or modifies) the index template for scale stats.
#
# The primary use is to set the type of the extracted fields in the
# stats collected for the Scale Dashboard. Any index created with
# the prefix "scale_stats" will get this template.
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2022 Fungible Inc.  All rights reserved.

# Fetching elasticsearch URL from env
if [[ -z "${ELASTICSEARCH_URL}" ]]; then
  URL="localhost:9200"
else
  URL="${ELASTICSEARCH_URL}"
fi


curl -X PUT "${URL}/_index_template/scale_stats_template" -H 'Content-Type: application/json' -d'
{
    "index_patterns": ["scale_stats*"],
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
                "fs": {
                    "properties": {
                        "cc_alive_status": {
                            "type": "integer"
                        },
                        "cpu": {
                            "properties": {
                                "hi": {
                                    "type": "float"
                                },
                                "id": {
                                    "type": "float"
                                },
                                "ni": {
                                    "type": "float"
                                },
                                "si": {
                                    "type": "float"
                                },
                                "st": {
                                    "type": "float"
                                },
                                "sy": {
                                    "type": "float"
                                },
                                "us": {
                                    "type": "float"
                                },
                                "wa": {
                                    "type": "float"
                                }
                            }
                        },
                        "memory": {
                            "properties": {
                                "buff/cache": {
                                    "type": "float"
                                },
                                "free": {
                                    "type": "float"
                                },
                                "total": {
                                    "type": "float"
                                },
                                "used": {
                                    "type": "float"
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    "composed_of": []
}
'