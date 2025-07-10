# suedtirolmobilAI

A small FastAPI service that interprets natural language queries for public
transport and forwards them to a Mentz EFA backend. See `docs/EFA_XML_API.md`.

## Features
- Parse queries in German, English and Italian.
- Search connections and monitor departures.
- Use stateless stop IDs for better accuracy.
- Automatically detect the desired action.
- Optional ChatGPT summaries.
- Verifies stops before requesting trips or departures.
- ChatGPT uses trimmed EFA data for concise responses.
- Plugin manifest for ChatGPT integration.
- Interactive console chat.
- Simple Telegram bot.

## Requirements
Python 3.8 or newer is required.

## Installation
### Quick start
```bash
./install.sh
```
The script reuses an existing `venv` if it already runs on Python 3.8 or newer
and automatically recreates it when an older interpreter is detected. It works
on systems using `apt-get` or `yum` by detecting the available package
manager automatically.

## Running the API
Start the server with:
```bash
uvicorn src.main:app --host 0.0.0.0 --reload
```
Append `--debug` for verbose logging.
Alternatively run `python -m src.main` for the default settings.

## Configuration
The service can be configured via the following environment variables:

- `EFA_BASE_URL` – base URL of the Mentz‑EFA endpoint
  ```bash
  EFA_BASE_URL=https://efa.sta.bz.it/apb
  ```
- `OPENAI_API_KEY` – API key for ChatGPT.
```bash
OPENAI_API_KEY=sk-...
```
- `OPENAI_MODEL` – OpenAI model name used for LLM features
```bash
OPENAI_MODEL=gpt-4
```
`OPENAI_MAX_TOKENS` – maximum tokens for ChatGPT replies (default 100)
```bash
OPENAI_MAX_TOKENS=120
```
- `TELEGRAM_TOKEN` – required for the Telegram bot
  ```bash
  TELEGRAM_TOKEN=your_token
  ```
- `API_URL` – base URL of the API used by the Telegram bot
  ```bash
  API_URL=http://localhost:8000
  ```
- `SERVER_URL` – public URL used in `/.well-known/openapi.yaml`
  ```bash
  SERVER_URL=https://api.example.com
  ```

Environment variables can also be stored in a `.env` file in the project root.
A `.env.example` file is included as a template. Copy it to `.env` and fill in
your credentials. The `.env` file is loaded automatically and should not be
committed.

## Prompt templates
Two text files under `prompts/` define how the LLM features interact with
OpenAI. `parser_prompt.txt` instructs the parser which fields to extract from a
query, while `formatter_prompt.txt` formats a trip using a chosen language.
Both templates contain placeholders that are replaced automatically:

- `{text}` in `parser_prompt.txt`
- `{data}` and `{language}` in `formatter_prompt.txt`

Edit the files to change the wording or add additional instructions.

`parser_prompt.txt` now returns the date expression literally, for example
"heute", "tomorrow" or "next sunday". The parser translates these phrases into
a proper ISO timestamp when processing the response.

## Console chat
Start a minimal interactive chat loop. Combine `--llm-parser` and `--llm-format` to use OpenAI for parsing and formatting.
Add `--debug` to print the parsed query JSON.
```bash
python -m src.chat --llm-parser --llm-format --debug
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
All endpoints accept POST requests. Use the query parameter `format` to control
the output:

- `format=json` (default) returns a JSON object.
- `format=text` returns plain text.

### `/search`
Parse a natural language query for a trip.
```bash
curl -X POST http://localhost:8000/search \
     -H 'Content-Type: application/json' \
     -d '{"text": "Wie komme ich von Bozen nach Meran um 14:30?"}'
```

### `/departures`
List upcoming departures for a stop. Use the optional `language` parameter to
choose `de`, `it`, or `en`. The optional `limit` parameter controls how many
results are returned (default `10`).
```bash
curl -X POST http://localhost:8000/departures \
     -H 'Content-Type: application/json' \
     -d '{"stop": "Bozen", "language": "it", "limit": 5}'
```

### `/stops`
Return stop name suggestions. You can specify a `language` of `de`, `it`, or
`en`.
```bash
curl -X POST http://localhost:8000/stops \
     -H 'Content-Type: application/json' \
     -d '{"query": "Brixen", "language": "it"}'
```
Append `?format=text` or `?format=json` to change the response.

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
Add `--start-server` to launch the API with `uvicorn` automatically. Use
`--token` to pass a token explicitly and `--debug` for verbose logging.
```bash
export TELEGRAM_TOKEN=your_token
python -m src.telegram_bot --api-url http://localhost:8000 --start-server
```
Use `--api-url` to specify the address of the running API. The option
defaults to the value of the `API_URL` environment variable or
`http://localhost:8000` if unset.

When selecting a command from the bot's keyboard without additional text,
the bot will ask for the required input before sending the request.


## Autostart on Linux
See [docs/autostart.md](docs/autostart.md) for details on creating a
`systemd` service. The templates in the [systemd/](systemd/) directory can be
copied to `/etc/systemd/system/` or installed automatically with
`sudo ./install_services.sh`. The script also starts the units immediately.
Once created the services can be controlled with `systemctl start`, `stop`
and `restart`.

## Testing
```bash
pytest
```

## License
MIT License. See [LICENSE](LICENSE) for details.
