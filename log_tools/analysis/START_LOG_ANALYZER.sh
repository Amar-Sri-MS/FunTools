#!/bin/bash

# Setting up elasticsearch
elastic_setup/SETUP_ELASTICSEARCH.sh

cd view
gunicorn --workers 3 --bind 0.0.0.0:5000 --capture-output --timeout 300 --log-level debug wsgi:app