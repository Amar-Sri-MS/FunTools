#
# Sets up (or modifies) the index template for our logs.
#
# The primary use is to set the type of the extracted fields in our
# logs to something appropriate. Any index created with the prefix "log"
# will get this template.
#

# Fetching elasticsearch URL from env
if [[ -z "${ELASTICSEARCH_URL}" ]]; then
  URL="localhost:9200"
else
  URL="${ELASTICSEARCH_URL}"
fi

curl -X PUT "${URL}/_index_template/log_template" -H 'Content-Type: application/json' -d'
{
    "index_patterns": ["log*"],
    "template": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 1
        },
        "mappings": {
            "properties": {
                "@timestamp": {
                    "type": "date_nanos"
                },
                "system_type": {
                    "type": "keyword",
                    "null_value": "N/A"
                },
                "system_id": {
                    "type": "keyword",
                    "null_value": "N/A"
                },
                "src": {
                    "type": "keyword"
                },
                "level": {
                    "type": "keyword",
                    "null_value": "INFO"
                },
                "msg": {
                    "type": "text"
                }
            }
        }
    },
    "composed_of": []
}
'



