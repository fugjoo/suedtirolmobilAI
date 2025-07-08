# suedtirolmobilAI

A small FastAPI service that interprets natural language queries for public
transport and forwards them to a EFA (Mentz GmbH) backend.

## Features
- Parse queries in German, English and Italian.
- Search for public transport connections.
- Monitor departures for a stop.
- Use stopfinder results to send stateless stop IDs for trips and departures.
- Return stop suggestions.
- Automatically decide between trip search, departures and stop search
  based on the entered text.
- ChatGPT summaries for nicer text output.
- ChatGPT plugin manifest for webhook integration.
- Interactive console chat for quick access.
- Simple Telegram bot for chat interaction, including conversation mode
- Configurable EFA base URL via `EFA_BASE_URL` and other API-Keys an Tokens (OpenAI, Telegram).

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

## Running the API
Start the server with:
```bash
uvicorn src.main:app --host 0.0.0.0 --reload
```
Alternatively run `python -m src.main` for the default settings.

## Configuration
The service can be configured via the following environment variables:

- `EFA_BASE_URL` – base URL of the Mentz‑EFA endpoint
  ```bash
  EFA_BASE_URL=https://efa.sta.bz.it/apb uvicorn src.main:app --reload
  ```
- `OPENAI_API_KEY` – API key for ChatGPT. When set the service always uses
  ChatGPT without any `--chatgpt` flag or `chatgpt=true` query parameter.
```bash
OPENAI_API_KEY=sk-... python -m src.chat --llm-parser --llm-format
```
- `TELEGRAM_TOKEN` – required for the Telegram bot
  ```bash
  TELEGRAM_TOKEN=your_token python -m src.telegram_bot
  ```
- `API_URL` – base URL of the API used by the Telegram bot
  ```bash
  API_URL=http://localhost:8000 python -m src.telegram_bot
  ```
- `SERVER_URL` – public URL used in `/.well-known/openapi.yaml`
  ```bash
  SERVER_URL=https://api.example.com uvicorn src.main:app --reload
  ```

Environment variables can also be stored in a `.env` file in the project root.
A `.env.example` file is included as a template. Copy it to `.env` and fill in
your credentials. The `.env` file is loaded automatically and should not be
committed to version control.

## Console chat
Start a minimal interactive chat loop. Combine `--llm-parser` and `--llm-format` to use OpenAI for parsing and formatting:
```bash
python -m src.chat --llm-parser --llm-format
```

### Automatic query detection
When text is entered without explicitly choosing a command, the service tries to
infer the best action automatically.  For example:

* `Abfahrten Neumarkt Busbahnhof` → departures
* `Bozen - Meran` → trip search
* `von Bozen nach Meran morgen um 13:00 Uhr` → trip search
* `Haltestestelle in Meran` → stops

Queries in German, English and Italian are supported.

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
Append `?format=text` or `?format=json` to change the response. ChatGPT
summaries are enabled automatically when `OPENAI_API_KEY` is set. The
`chatgpt` query parameter is no longer required.

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
