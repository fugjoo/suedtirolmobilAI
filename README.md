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

This also installs `uvicorn`, which runs the FastAPI server.

If you upgrade to a newer release of this project, reinstall the dependencies
by running the above command again.

## Running the server

Start the API using `uvicorn` so that code changes are picked up automatically:

```bash
uvicorn src.main:app --reload
```

Running `python -m src.main` also starts the server but does not enable
auto‑reloading.


## Configuration

The Mentz‑EFA endpoint can be configured via the `EFA_BASE_URL`
environment variable. By default this project uses
`https://efa-api.asw.io`, an aggregator for the official
South Tyrol endpoint `https://efa.sta.bz.it/apb/`. You can point the
API to any compatible service by setting `EFA_BASE_URL`.

```bash
EFA_BASE_URL=https://efa.sta.bz.it/apb/ uvicorn src.main:app --reload
```

=======

## Example request

After the server is running, you can query it with a POST request:

```bash
curl -X POST http://localhost:8000/search \
     -H 'Content-Type: application/json' \
     -d '{"text": "Wie komme ich von Bozen nach Meran um 14:30?"}'
```

The response JSON mirrors the data returned by the underlying EFA service. Important fields include:

- `from_stop`: the detected origin stop
- `to_stop`: the detected destination stop
- `time`: the requested departure time, if any
- `trips`: a list of connection options with departure and arrival details


## Testing

Run the unit tests with `pytest`:

```bash
pytest
```
