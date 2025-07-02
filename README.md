# suedtirolmobilAI

This project provides a small FastAPI service that parses natural language
queries for public transport connections and forwards them to a Mentz-EFA
backend.

## Installation

Run the provided `install.sh` script for a one-click setup:

```bash
./install.sh
```

The script creates a virtual environment, installs all dependencies and
downloads the German spaCy model. If you prefer the manual steps, run:

```bash
pip install -r requirements.txt
python -m spacy download de_core_news_sm  # optional
```

If you upgrade to a newer release of this project, reinstall the dependencies
by running the above command again.

## Running the server

Start the API using `uvicorn` so that code changes are picked up automatically:

```bash
uvicorn src.main:app --reload
```

Running `python -m src.main` also starts the server but does not enable
auto‑reloading.

## Testing

Run the unit tests with `pytest`:

```bash
pytest
```
