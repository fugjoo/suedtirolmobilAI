#!/usr/bin/env bash
set -e


# Install build tools if missing (for spaCy dependencies)
if command -v apt-get >/dev/null; then
    sudo apt-get update
    sudo apt-get install -y build-essential python3-dev
elif command -v yum >/dev/null; then
    sudo yum groupinstall -y "Development Tools"
    sudo yum install -y python3-devel
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

# Upgrade pip and install requirements
pip install --upgrade pip
pip install -r requirements.txt
pip install pytest
pip install httpx==0.24.1

# Download spaCy model (ignore failures if already installed)
python -m spacy download de_core_news_sm || true

echo "\nInstallation complete."
echo "Activate the environment with 'source venv/bin/activate'."
echo "Run the server using: uvicorn src.main:app --host 0.0.0.0 --reload"
