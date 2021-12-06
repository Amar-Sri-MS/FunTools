#!/bin/bash

# Setting up elasticsearch
elastic_setup/SETUP_ELASTICSEARCH.sh

cd view
python es_view.py