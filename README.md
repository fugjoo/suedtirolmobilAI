# suedtirolmobilAI

## Overview
This project provides an NLP interface to the EFA/Mentz API, allowing users to query mobility information in natural language.

## Installation
You can simply clone this repository. Using a Python virtual environment is optional but recommended to keep dependencies isolated.

```bash
# optional: create a virtual environment
python -m venv .venv
source .venv/bin/activate

# install requirements if any
pip install -r requirements.txt
```

## Usage
Run the command-line interface to start interacting with the service. The
examples below assume you are in the project root.

```bash
python cli.py --query "When is the next bus to Bolzano?"

# another example querying train connections
python cli.py --query "Is there a train from Merano to Brunico tomorrow?"
```

Replace the example queries with your own questions about local transit.
