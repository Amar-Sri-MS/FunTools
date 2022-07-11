#!/bin/bash

BASEDIR=$(dirname $0)

# Setting up index template for logs
$BASEDIR/setup_index.sh

# Setting up index template for metadata
$BASEDIR/setup_metadata_index_template.sh

# Setting up index template for web_stats
$BASEDIR/setup_web_stats_template.sh