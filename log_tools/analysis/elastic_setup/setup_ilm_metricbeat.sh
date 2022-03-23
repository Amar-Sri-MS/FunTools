#!/bin/sh
#
# Sets up (or modifies) the Index Lifecycle Management Policy for stats
# collected by Metricbeat.
#
# The primary use is to set the policies based on the retention policy
# for managing the lifecycle of all stats with a prefix "metricbeat*".
#
# Owner: Sourabh Jain (sourabh.jain@fungible.com)
# Copyright (c) 2022 Fungible Inc.  All rights reserved.

# Fetching elasticsearch URL from env
if [[ -z "${ELASTICSEARCH_URL}" ]]; then
  URL="localhost:9200"
else
  URL="${ELASTICSEARCH_URL}"
fi

curl -X PUT "${URL}/_ilm/policy/metricbeat" -H 'Content-Type: application/json' -d'
{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": {
            "max_age": "30d",
            "max_size": "50gb"
          },
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
          "delete" : { }
        }
      }
    }
  }
}
'

# Attaching the created policy with the metricbeat* index
curl -X PUT "${URL}/metricbeat*/_settings" -H 'Content-Type: application/json' -d'
{
  "index": {
    "lifecycle": {
      "name": "metricbeat"
    }
  }
}
'