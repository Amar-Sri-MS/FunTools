#!/bin/sh
#
# Sets up (or modifies) the Index Lifecycle Management Policy for logs
# ingested from Fun-on-demand jobs.
#
# The primary use is to set the policies based on the retention policy
# for managing the lifecycle of all logs with a prefix "log_fod-".
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2021 Fungible Inc.  All rights reserved.

# Fetching elasticsearch URL from env
if [[ -z "${ELASTICSEARCH_URL}" ]]; then
  URL="localhost:9200"
else
  URL="${ELASTICSEARCH_URL}"
fi

curl -X PUT "${URL}/_ilm/policy/fod" -H 'Content-Type: application/json' -d'
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
        "min_age" : "7d",
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
        "min_age" : "14d",
        "actions": {
          "delete" : { },
          "wait_for_snapshot" : {
            "policy": "fod"
          }
        }
      }
    }
  }
}
'

# Attaching the created policy with the Fun-on-demand ingested logs
curl -X PUT "${URL}/log_fod-*/_settings" -H 'Content-Type: application/json' -d'
{
  "index": {
    "lifecycle": {
      "name": "fod"
    }
  }
}
'