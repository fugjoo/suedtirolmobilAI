# suedtirolmobilAI

This project provides a small FastAPI service that parses natural language
queries for public transport connections and forwards them to a Mentz-EFA
backend.

## Installation

Run the provided `install.sh` script for a one-click setup. The
script also tries to install the system build tools required:

```bash
./install.sh
```

If you prefer the manual steps, run:

```bash
pip install -r requirements.txt
python -m spacy download de_core_news_sm  # optional
```

If you upgrade to a newer release of this project, reinstall the dependencies
by running the above command again.

## Running the server

Start the API using `uvicorn` so that code changes are picked up automatically:

```bash
uvicorn src.main:app --host 0.0.0.0 --reload
```

Running `python -m src.main` also starts the server but does not enable
auto‑reloading.


## Configuration

The Mentz‑EFA endpoint can be configured via the `EFA_BASE_URL`
environment variable. By default this project uses the official
South Tyrol endpoint `https://efa.sta.bz.it/apb`. You can point the
API to any compatible service by setting `EFA_BASE_URL`.

For a deeper understanding of the Mentz‑EFA endpoints, see
[docs/EFA_XML_API.md](docs/EFA_XML_API.md).

```bash
EFA_BASE_URL=https://efa.sta.bz.it/apb uvicorn src.main:app --host 0.0.0.0 --reload
```


## Example requests

After the server is running, you can query it with a POST request:

```bash
# Trip request
curl -X POST http://localhost:8000/search \
     -H 'Content-Type: application/json' \
     -d '{"text": "Wie komme ich von Bozen nach Meran um 14:30?"}'

# Departure monitor
curl -X POST http://localhost:8000/departures \
     -H 'Content-Type: application/json' \
     -d '{"stop": "Bozen", "limit": 5}'

# Stop suggestions
curl -X POST http://localhost:8000/stops \
     -H 'Content-Type: application/json' \
     -d '{"query": "Brixen"}'
```

The response JSON mirrors the data returned by the underlying EFA service. Important fields include:

- `from_stop`: the detected origin stop
- `to_stop`: the detected destination stop
- `time`: the requested departure time, if any
- `trips`: a list of connection options with departure and arrival details

## Command line usage

This repository also includes a small helper script that performs a search and
prints feedback messages while processing the query. Run it with Python's
module syntax:

```bash
# Trip request
python -m src.cli search "Wie komme ich von Bozen nach Meran um 14:30?"

# Departure monitor
python -m src.cli departures "Bozen"

# Stop suggestions
python -m src.cli stops "Brixen"
```

The script prints progress updates such as "Searching for stops..." and shows
the raw API response when finished.


## Testing

Run the unit tests with `pytest`:

```bash
pytest
```
