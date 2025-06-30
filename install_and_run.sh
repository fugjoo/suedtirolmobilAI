#!/bin/bash
set -e

# Install required Python packages
pip install --user -r requirements.txt

# Execute the main program with all passed arguments
python src/main.py "$@"
