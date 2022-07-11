#
# Sets up (or modifies) the index template for automated test result data.
#
# The primary use is to set the type of fields in the test result data.
# Any index created with the prefix "testdata" will get this template.
#

# Fetching elasticsearch URL from env
if [[ -z "${ELASTICSEARCH_URL}" ]]; then
  URL="localhost:9200"
else
  URL="${ELASTICSEARCH_URL}"
fi

curl -X PUT "${URL}/_index_template/testdata_template" -H 'Content-Type: application/json' -d'
{
    "index_patterns": ["testdata*"],
    "template": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 1
        },
        "mappings": {
            "dynamic": false,
            "properties": {
                "logID": {
                    "type": "keyword"
                },
                "@timestamp": {
                    "type": "date"
                },
                "ingest_type": {
                    "type": "keyword"
                },
                "ingestion_msg": {
                    "type": "text"
                },
                "ingestion_status": {
                    "type": "keyword"
                },
                "validation_msg": {
                    "type": "text"
                },
                "validation_status": {
                    "type": "keyword"
                },
                "job_id": {
                    "type": "text"
                }
            }
        }
    },
    "composed_of": []
}
'