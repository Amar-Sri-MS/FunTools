#
# Sets up (or modifies) the index template for metadata of ingested job.
#
# The primary use is to set the type of fields in the metadata.
# Any index created with the prefix "metadata" will get this template.
#

# Fetching elasticsearch URL from env
if [[ -z "${ELASTICSEARCH_URL}" ]]; then
  URL="localhost:9200"
else
  URL="${ELASTICSEARCH_URL}"
fi

curl -X PUT "${URL}/_index_template/metadata_template" -H 'Content-Type: application/json' -d'
{
    "index_patterns": ["metadata*"],
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
                "tags": {
                    "type": "keyword",
                    "index_options": "docs",
                    "doc_values": false
                },
                "notes": {
                    "type": "object",
                    "enabled": false
                },
                "download_time": {
                    "type": "float"
                },
                "filters": {
                    "type": "object",
                    "dynamic": true
                },
                "ingest_type": {
                    "type": "keyword"
                },
                "ingestion_error": {
                    "type": "text"
                },
                "ingestion_status": {
                    "type": "keyword"
                },
                "ingestion_time": {
                    "type": "float"
                },
                "is_partial_ingestion": {
                    "type": "boolean"
                },
                "job_id": {
                    "type": "text"
                },
                "metadata": {
                    "type": "object",
                    "dynamic": true,
                    "enabled": false
                },
                "mount_path": {
                    "type": "text"
                },
                "sources": {
                    "type": "text"
                },
                "submitted_by": {
                    "type": "keyword"
                }
            }
        }
    },
    "composed_of": []
}
'