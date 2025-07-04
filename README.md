# suedtirolmobilAI

A small FastAPI service that interprets natural language queries for public
transport and forwards them to a Mentz‑EFA backend.

## Features
- Parse queries in German, English and Italian.
- Search for public transport connections.
- Monitor departures for a stop.
- Return stop suggestions.
- Automatically decide between trip search, departures and stop search
  based on the entered text.
- Optional ChatGPT summaries for nicer text output.
- ChatGPT plugin manifest for webhook integration.
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
The service can be configured via the following environment variables:

- `EFA_BASE_URL` – base URL of the Mentz‑EFA endpoint
  ```bash
  EFA_BASE_URL=https://efa.sta.bz.it/apb uvicorn src.main:app --reload
  ```
- `OPENAI_API_KEY` – enable ChatGPT features
  ```bash
  OPENAI_API_KEY=sk-... python -m src.cli search "Bozen" --chatgpt
  ```
- `TELEGRAM_TOKEN` – required for the Telegram bot
  ```bash
  TELEGRAM_TOKEN=your_token python -m src.telegram_bot
  ```
- `API_URL` – base URL of the API used by the Telegram bot
  ```bash
  API_URL=http://localhost:8000 python -m src.telegram_bot
  ```

Environment variables can also be stored in a `.env` file in the project root.
The file is loaded automatically and should not be committed to version control.

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

### Automatic query detection
When text is entered without explicitly choosing a command, the service tries to
infer the best action automatically.  For example:

* `Neumarkt Busbahnhof` → departures
* `Bozen-Meran` → trip search

Queries in German, English and Italian are supported.

### Flags
- `--format` – choose the output format (`text`, `json` or `legs`)
  ```bash
  python -m src.cli search "Bozen Meran" --format json
  ```
- `--debug` – enable verbose logging
  ```bash
  python -m src.cli departures "Bozen" --debug
  ```
- `--chatgpt` – generate ChatGPT summaries
  ```bash
  python -m src.cli search "Brixen Meran" --chatgpt
  ```
- `--api-url` – API endpoint for the Telegram bot
  ```bash
  python -m src.telegram_bot --api-url http://localhost:8000
  ```
- `--start-server` – start the API automatically for the Telegram bot
  ```bash
  python -m src.telegram_bot --api-url http://localhost:8000 --start-server
  ```

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

## ChatGPT plugin
The repository includes a plugin manifest and OpenAPI file in the
`.well-known/` directory. When the server is running they are served under
`/.well-known/ai-plugin.json` and `/.well-known/openapi.yaml` for easy
integration with ChatGPT.

## Telegram bot
Forward messages to the API using the example bot:
```bash
export TELEGRAM_TOKEN=your_token
python -m src.telegram_bot --api-url http://localhost:8000
```
Add `--start-server` to launch the API with `uvicorn` automatically:
```bash
export TELEGRAM_TOKEN=your_token
python -m src.telegram_bot --api-url http://localhost:8000 --start-server
```
Use `--api-url` to specify the address of the running API. The option
defaults to the value of the `API_URL` environment variable or
`http://localhost:8000` if unset.

When selecting a command from the bot's keyboard without additional text,
the bot will ask for the required input before sending the request.

## Testing
```bash
pytest
```

## License
MIT License. See [LICENSE](LICENSE) for details.
