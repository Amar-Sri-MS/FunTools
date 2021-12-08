#!/bin/sh
#
# Sets up (or modifies) the Index Lifecycle Management Policy for logs
# ingested other than QA or FoD jobs.
#
# The primary use is to set the policies based on the retention policy
# for managing the lifecycle of all logs with a prefix "log_".
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

# Fetching elasticsearch URL from env
if [[ -z "${ELASTICSEARCH_URL}" ]]; then
  URL="localhost:9200"
else
  URL="${ELASTICSEARCH_URL}"
fi

curl -X PUT "${URL}:9200/_ilm/policy/logs" -H 'Content-Type: application/json' -d'
{
  "policy": {
    "phases": {
      "hot" : {
        "min_age" : "0ms",
        "actions" : {
          "set_priority" : {
            "priority" : 100
          }
        }
      },
      "warm" : {
        "min_age" : "1d",
        "actions" : {
          "readonly" : { },
          "forcemerge" : {
            "max_num_segments" : 1
          },
          "migrate": { },
          "set_priority" : {
            "priority" : 50
          }
        }
      },
      "cold" : {
        "min_age" : "14d",
        "actions" : {
          "freeze" : { },
          "migrate": { },
          "allocate" : {
            "number_of_replicas" : 0,
            "include" : { },
            "exclude" : { },
            "require" : { }
          },
          "set_priority" : {
            "priority" : 0
          }
        }
      },
      "delete": {
        "min_age" : "28d",
        "actions": {
          "delete" : { }
        }
      }
    }
  }
}
'

# Attaching the created policy with all the logs
curl -X PUT "${URL}/log_*/_settings" -H 'Content-Type: application/json' -d'
{
  "index": {
    "lifecycle": {
      "name": "logs"
    }
  }
}
'