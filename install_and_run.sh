#!/bin/bash
set -e

# Install dependencies if a requirements file exists
if [ -f requirements.txt ]; then
    echo "Installing Python dependencies..."
    python3 -m pip install -r requirements.txt
fi

# Execute the main program with all passed arguments
python3 src/main.py "$@"
