# suedtirolmobilAI

`suedtirolmobilAI` interprets natural language requests about public transport in South Tyrol and forwards them to a Mentz EFA server.  All EFA access now happens exclusively through a Model Context Protocol (MCP) server.  A lightweight Telegram bot acts as a client to this MCP server and lets users ask for trips, departures and stop suggestions in German, Italian or English.

## Features
- Trip search, departure monitor and stop suggestions
- MCP server exposing `search`, `departures`, `stops`, `update_query` and `reset_session`
- Telegram bot working purely as an MCP client
- Optional ChatGPT formatting for human friendly summaries

## Project structure
```
src/             application code
src/stubs/       minimal stand-ins for optional dependencies
prompts/         prompt templates for the LLM
tests/           unit and integration tests
```

## Requirements
Python 3.8 or later.

## Installation
```bash
./install.sh
```
The script creates a virtual environment if necessary and installs missing packages.

## Running
### MCP server
```bash
python -m src.mcp_server
```
The server offers high level tools for LLMs and other clients.

### Telegram bot
```bash
python -m src.telegram_bot --api-url ws://localhost:8000 --token <TOKEN>
```
The bot connects to an MCP server via WebSocket and relays user messages.

## Configuration
Environment variables:
- `EFA_BASE_URL` – base URL of the Mentz EFA endpoint
- `OPENAI_API_KEY` – API key for ChatGPT
- `OPENAI_MODEL` – model name used for LLM features
- `OPENAI_MAX_TOKENS` – maximum token count for ChatGPT responses (default 100)
- `TELEGRAM_TOKEN` – token for the Telegram bot (can also be passed via `--token`)
- `API_URL` – MCP WebSocket URL (can also be passed via `--api-url`)
- `LOG_LEVEL` – set to `DEBUG` for verbose service logging

Variables can also be stored in a `.env` file in the project directory.

## Tests
```bash
pytest -q
```

## License
MIT License – see [LICENSE](LICENSE).

