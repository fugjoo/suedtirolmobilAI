#!/usr/bin/env bash
set -e

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

# Upgrade pip and install requirements
pip install --upgrade pip
pip install -r requirements.txt

# Download spaCy model (ignore failures if already installed)
python -m spacy download de_core_news_sm || true

echo "\nInstallation complete."
echo "Activate the environment with 'source venv/bin/activate'."
echo "Run the server using: uvicorn src.main:app --reload"
