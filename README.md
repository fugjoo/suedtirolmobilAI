# suedtirolmobilAI

suedtirolmobilAI is a small FastAPI service that interprets natural language
requests about public transport in South Tyrol. It detects the desired action
and forwards the query to a Mentz EFA server. ChatGPT can optionally summarize
the results. The interface is trilingual (German, Italian, English) and can also
act as a Model Context Protocol (MCP) server.

## Features
- Understands German, Italian and English
- Journey search, departure monitor and stop suggestions
- Stateless stop IDs for more precise results
- Automatically selects the appropriate action
- Optional ChatGPT summaries
- MCP server exposing tools for LLMs

## Project structure
```
src/             FastAPI application and helper modules
prompts/         Prompt templates for the LLM
docs/            Additional documentation
tests/           Unit and integration tests
```

## Requirements
Python 3.8 or later.

## Installation
```bash
./install.sh
```
The script creates a virtual environment if necessary and attempts to install
missing packages via `apt-get` or `yum`.

## Running the service
Start the HTTP API:
```bash
uvicorn src.main:app --host 0.0.0.0 --reload
```
Use `--debug` for verbose logging. Alternatively, run `python -m src.main` with
the default settings.

### MCP server
```bash
python -m src.mcp_server
```
The MCP server provides tools such as `search`, `departures` and `stops` for
LLM clients.

## Configuration
Important environment variables:

- `EFA_BASE_URL` – base URL of the Mentz EFA endpoint
  ```bash
  EFA_BASE_URL=https://efa.sta.bz.it/apb
  ```
- `OPENAI_API_KEY` – API key for ChatGPT
  ```bash
  OPENAI_API_KEY=sk-...
  ```
- `OPENAI_MODEL` – model name used for LLM features
  ```bash
  OPENAI_MODEL=gpt-4
  ```
- `OPENAI_MAX_TOKENS` – maximum token count for ChatGPT responses (default 100)
  ```bash
  OPENAI_MAX_TOKENS=120
  ```

Variables can also be stored in a `.env` file in the project directory. A
template is available as `.env.example`.

## Prompt templates
Two text files under `prompts/` control LLM behavior:
- `parser_prompt.txt` – defines which fields are extracted from a request
  (`{text}` placeholder)
- `formatter_prompt.txt` – formats the answer in the desired language
  (`{data}`, `{language}` placeholders)

The parser initially returns date expressions verbatim (“today”, “tomorrow”).
Processing converts them into ISO timestamps.

## API endpoints
All endpoints expect POST requests. The `format` parameter controls the output
(`json` or `text`).

### `/search`
Example:
```bash
curl -X POST http://localhost:8000/search \
     -H 'Content-Type: application/json' \
     -d '{"text": "How do I get from Bolzano to Merano at 14:30?"}'
```

### `/departures`
```bash
curl -X POST http://localhost:8000/departures \
     -H 'Content-Type: application/json' \
     -d '{"stop": "Bozen", "language": "it", "limit": 5}'
```
Optional `language` (`de`, `it`, `en`) and `limit` (default 10).

### `/stops`
```bash
curl -X POST http://localhost:8000/stops \
     -H 'Content-Type: application/json' \
     -d '{"query": "Brixen", "language": "it"}'
```

## Using the MCP server with Claude Desktop
1. Start the server:
   ```bash
   python -m src.mcp_server
   ```
2. Edit the Claude Desktop configuration file (e.g.
   `~/Library/Application Support/Claude/config.json` on macOS or
   `~/.config/Claude/config.json` on Linux) and add an entry under
   `mcpServers`:
   ```json
   {
     "mcpServers": {
       "suedtirolmobil": {
         "command": "python",
         "args": ["-m", "src.mcp_server"],
         "cwd": "/absolute/path/to/suedtirolmobilAI",
         "env": {
           "EFA_BASE_URL": "https://efa.sta.bz.it/apb",
           "OPENAI_API_KEY": "sk-..."
         }
       }
     }
   }
   ```
3. Restart Claude Desktop. The `suedtirolmobil` server appears in the tools
   list and offers the `search`, `departures` and `stops` tools.

## Autostart on Linux
See [docs/autostart.md](docs/autostart.md) for setting up a `systemd` service.
Templates in `systemd/` can be copied to `/etc/systemd/system/` or installed
with `sudo ./install_services.sh`.

## Tests
```bash
pytest -q
```

## License
MIT License – see [LICENSE](LICENSE).

