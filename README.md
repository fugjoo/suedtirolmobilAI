# suedtirolmobilAI

A small FastAPI service that interprets natural language queries for public
transport and forwards them to a Mentz‑EFA backend.

## Features
- Parse queries in German, English and Italian.
- Search for public transport connections.
- Monitor departures for a stop.
- Return stop suggestions.
- Optional ChatGPT summaries for nicer text output.
- Command line client for quick access.
- Simple Telegram bot for chat interaction.
- Configurable Mentz‑EFA base URL via `EFA_BASE_URL`.

## Requirements
Python 3.8 or newer is required.

## Installation
### Quick start
```bash
./install.sh
source venv/bin/activate
```
The script reuses an existing `venv` if it already runs on Python 3.8 or newer
and automatically recreates it when an older interpreter is detected.
### Manual setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download de_core_news_sm  # optional
```
spaCy is pinned to versions below 3.8 for compatibility.

## Running the API
Start the server with:
```bash
uvicorn src.main:app --host 0.0.0.0 --reload
```

## Configuration
- `EFA_BASE_URL` – base URL of the Mentz‑EFA endpoint
- `OPENAI_API_KEY` – enable ChatGPT features

Example:
```bash
EFA_BASE_URL=https://efa.sta.bz.it/apb \
uvicorn src.main:app --host 0.0.0.0 --reload
```

## Command line usage
### Search for a trip
```bash
python -m src.cli search "Wie komme ich von Bozen nach Meran um 14:30?"
```
### Departure monitor
```bash
python -m src.cli departures "Bozen"
```
### Stop suggestions
```bash
python -m src.cli stops "Brixen"
```
Add `--format json` for JSON output, `--debug` for verbose logs and
`--chatgpt` for ChatGPT summaries.

## API endpoints
All endpoints accept POST requests.

### `/search`
Parse a natural language query for a trip.
```bash
curl -X POST http://localhost:8000/search \
     -H 'Content-Type: application/json' \
     -d '{"text": "Wie komme ich von Bozen nach Meran um 14:30?"}'
```

### `/departures`
List upcoming departures for a stop.
```bash
curl -X POST http://localhost:8000/departures \
     -H 'Content-Type: application/json' \
     -d '{"stop": "Bozen", "limit": 5}'
```

### `/stops`
Return stop name suggestions.
```bash
curl -X POST http://localhost:8000/stops \
     -H 'Content-Type: application/json' \
     -d '{"query": "Brixen"}'
```
Append `?format=text` or `?format=json` to change the response and use
`chatgpt=true` for ChatGPT summaries.

## ChatGPT summaries
Set `OPENAI_API_KEY` and use `--chatgpt` or `chatgpt=true`:
```bash
OPENAI_API_KEY=sk-... python -m src.cli search "Bozen nach Meran" --chatgpt
# or for the server
OPENAI_API_KEY=sk-... uvicorn src.main:app --host 0.0.0.0 --reload
```

## Telegram bot
Forward messages to the API using the example bot:
```bash
export TELEGRAM_TOKEN=your_token
python -m src.telegram_bot --api-url http://localhost:8000 --chatgpt
```
Use `--api-url` to specify the address of the running API. Pass `--chatgpt`
for nicer ChatGPT summaries. Options default to the `API_URL` environment
variable and plain text output if unset.

## Testing
```bash
pytest
```

## License
MIT License. See [LICENSE](LICENSE) for details.
