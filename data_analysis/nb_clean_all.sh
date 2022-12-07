#!/bin/bash

echo "Clean notebooks"
nb-clean clean `find . -name '*.ipynb'`
