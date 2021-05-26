#
# Sets up (or modifies) the index template for metadata of ingested job.
#
# The primary use is to set the type of fields in the metadata.
# Any index created with the prefix "metadata" will get this template.
#

curl -X PUT "localhost:9200/_index_template/metadata_template" -H 'Content-Type: application/json' -d'
{
    "index_patterns": ["metadata*"],
    "template": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 1
        },
        "mappings": {
            "properties": {
                "logID": {
                    "type": "keyword"
                },
                "@timestamp": {
                    "type": "date"
                },
                "tags": {
                    "type": "keyword",
                    "index_options": "docs",
                    "doc_values": false
                },
                "notes": {
                    "type": "object",
                    "enabled": false
                },
                "metadata": {
                    "type": "object",
                    "enabled": false
                }
            }
        }
    },
    "composed_of": []
}
'