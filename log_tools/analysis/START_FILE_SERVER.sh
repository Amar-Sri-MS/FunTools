#!/bin/bash

cd file_server
gunicorn --workers 3 --bind 0.0.0.0:11000 wsgi:app