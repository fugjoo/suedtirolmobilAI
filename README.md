# suedtirolmobilAI

This project provides a small FastAPI service that parses natural language
queries for public transport connections and forwards them to a Mentz-EFA
backend.

## Requirements

This project requires Python 3.8 or newer. We recommend installing it inside a
virtual environment so that dependencies remain isolated.


## Installation

Run the provided `install.sh` script for a one-click setup. The
script creates a virtual environment in `venv/` and installs all required
dependencies:

```bash
./install.sh
source venv/bin/activate
```

If you prefer the manual setup, create and activate a virtual environment
yourself and install the dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
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

All requests automatically enable the EFA location server via
`locationServerActive=1`. Trip and departure monitor queries also send
`odvMacro=true`. Starting with version 0.2 all requests specify
`outputEncoding=UTF-8` to ensure UTF‑8 encoded responses.

### ChatGPT summaries

Set the `OPENAI_API_KEY` environment variable to enable reformatting of the
plain‑text summaries via OpenAI's ChatGPT API. Requests will be sent to
OpenAI's servers, which requires internet access and may incur usage fees.
Use the `--chatgpt` flag in the CLI or pass `chatgpt=true` to any endpoint that
returns plain text:

```bash
OPENAI_API_KEY=sk-... python -m src.cli search "Bozen nach Meran" --chatgpt

# or for the API
OPENAI_API_KEY=sk-... uvicorn src.main:app --host 0.0.0.0 --reload
# POST /search?chatgpt=true
# POST /departures?format=text&chatgpt=true
# POST /stops?format=text&chatgpt=true
```
## API endpoints

The service exposes three POST endpoints:
- `/search` – parse a natural language query for a trip
- `/departures` – list upcoming departures for a stop
- `/stops` – return stop name suggestions


After the server is running, you can query it with a POST request. All endpoints
return JSON by default. The `/search` endpoint instead returns a plain‑text list
of the connection legs. Append `?format=json` if you need the raw JSON. The
other endpoints support `?format=text` for plain‑text output:

```bash
# Trip request (plain text)
curl -X POST http://localhost:8000/search \
     -H 'Content-Type: application/json' \
     -d '{"text": "Wie komme ich von Bozen nach Meran um 14:30?"}'

# Trip request (JSON)
curl -X POST 'http://localhost:8000/search?format=json' \
     -H 'Content-Type: application/json' \
     -d '{"text": "Wie komme ich von Bozen nach Meran um 14:30?"}'

# Departure monitor
curl -X POST http://localhost:8000/departures \
     -H 'Content-Type: application/json' \
     -d '{"stop": "Bozen", "limit": 5}'

# Departure monitor (plain text)
curl -X POST 'http://localhost:8000/departures?format=text' \
     -H 'Content-Type: application/json' \
     -d '{"stop": "Bozen", "limit": 5}'

# Stop suggestions
curl -X POST http://localhost:8000/stops \
     -H 'Content-Type: application/json' \
     -d '{"query": "Brixen"}'

# Stop suggestions (plain text)
curl -X POST 'http://localhost:8000/stops?format=text' \
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

By default the commands print a short text summary. For ``search`` this means
showing only the individual trip legs. To inspect the raw API response you
need to enable debug mode and request the JSON output:

```bash
python -m src.cli search "Bozen nach Meran" --debug --format json
```

The script prints progress updates such as "Searching for stops..." before
showing the results.

### Debug mode

Enable verbose logging for both the CLI and the server by passing
`--debug` to the CLI. Logs are also written to `app.log`:

```bash
python -m src.cli search "Bozen nach Meran" --debug
```

## Telegram bot

A small example bot in `src/telegram_bot.py` forwards incoming Telegram messages to the running API and replies with the plain text result.

Start the bot after setting your token:

```bash
export TELEGRAM_TOKEN=your_token
python -m src.telegram_bot
```

Set `API_URL` if the API is reachable under a different address.



## Testing

Run the unit tests with `pytest`:

```bash
pytest
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
