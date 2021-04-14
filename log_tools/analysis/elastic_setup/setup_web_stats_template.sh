#
# Sets up (or modifies) the index template for web stats data.
#
# The primary use is to set the type of fields in web events data.
# Any index created with the prefix "web_stats" will get this template.
#

curl -X PUT "localhost:9200/_index_template/web_stats_template" -H 'Content-Type: application/json' -d'
{
    "index_patterns": ["web_stats*"],
    "template": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": {
                "timestamp": {
                    "type": "date"
                },
                "event": {
                    "type": "keyword"
                },
                "logID": {
                    "type": "keyword"
                },
                "data": {
                    "type": "nested",
                    "properties": {
                        "level": { "type": "keyword" },
                        "link": { "type": "text" },
                        "filters": { "type": "nested" }
                    }
                }
            }
        }
    },
    "composed_of": []
}
'