#!/usr/bin/env bash
set -e

# Activate existing virtual environment if present
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Ensure Python 3.8+ and build tools (for spaCy dependencies)
PYTHON_CMD=python3

# check if python3 satisfies the version requirement
if ! $PYTHON_CMD - <<'EOF'
import sys
sys.exit(0 if sys.version_info >= (3, 8) else 1)
EOF
then
    echo "Python 3.8+ not found. Installing..."
    if command -v apt-get >/dev/null; then
        sudo apt-get update
        sudo apt-get install -y build-essential python3.8 python3.8-venv python3.8-dev
        PYTHON_CMD=python3.8
    elif command -v yum >/dev/null; then
        sudo yum install -y gcc gcc-c++ make automake autoconf kernel-devel
        sudo yum install -y python38 python38-devel
        PYTHON_CMD=python3.8
    else
        echo "No supported package manager found. Please install Python 3.8 or newer manually." >&2
        exit 1
    fi
else
    if command -v apt-get >/dev/null; then
        sudo apt-get update
        sudo apt-get install -y build-essential python3-dev
    elif command -v yum >/dev/null; then
        sudo yum install gcc gcc-c++ make automake autoconf kernel-devel
        sudo yum install -y python3-devel
    fi
fi

# Create virtual environment if needed or outdated
if [ -x "venv/bin/python" ]; then
    VENV_VERSION=$(venv/bin/python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    if ! venv/bin/python - <<'EOF'
import sys
sys.exit(0 if sys.version_info >= (3, 8) else 1)
EOF
    then
        NEW_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        echo "Recreating venv with Python $NEW_VERSION (was $VENV_VERSION)"
        rm -rf venv
        $PYTHON_CMD -m venv venv
    fi
else
    $PYTHON_CMD -m venv venv
fi

# Upgrade pip and install requirements
pip install --upgrade pip
pip install -r requirements.txt

# Download spaCy model (ignore failures if already installed)
python -m spacy download de_core_news_sm || true

source venv/bin/activate

echo "\nInstallation complete."
echo "Activate the environment with source venv/bin/activate"
echo "Run the server using: uvicorn src.main:app --host 0.0.0.0 --reload"
