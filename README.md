# suedtirolmobilAI

Utilities for normalising responses returned by the Südtirolmobil EFA (Elektronische Fahrplanauskunft) backend.
The repository provides both pure data transformation helpers and an asynchronous client that can be embedded
into other applications or exposed through a Model Context Protocol (MCP) server.

## Features

- **Response normalisation** – utilities in `suedtirolmobilai.handlers` turn raw stop finder, departure monitor and
  error payloads into well defined Pydantic models found in `suedtirolmobilai.schemas`.
- **Asynchronous HTTP client** – `EfaClient` wraps the official EFA endpoints with httpx, rate limiting, caching and
  timezone aware datetime handling.
- **MCP integration** – `src/server.py` exposes MCP tools (`stop.find`, `departures.board`, `trip.plan`) so AI agents
  can query Südtirolmobil data.
- **Contract tests** – pytest suites backed by recorded fixtures ensure schema compatibility with the upstream service.

## Requirements

- Python 3.10 or newer
- Access to the Südtirolmobil EFA endpoints (defaults to the public base URL)

## Installation

Create a virtual environment and install the runtime dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For local development (running tests, linting, etc.) install the package in editable mode with the optional
`dev` extras:

```bash
pip install -e .[dev]
```

## Usage

### Normalising recorded responses

If you already have JSON payloads from the EFA backend you can normalise them without touching the network:

```python
import json
from pathlib import Path
from suedtirolmobilai.handlers import normalize_stop_finder

payload = json.loads(Path("tests/fixtures/stop_finder_success.json").read_text())
stops = normalize_stop_finder(payload)
for stop in stops:
    print(stop.name, stop.products)
```

Every helper returns Pydantic models so you benefit from validation and rich type information.

### Querying the EFA backend directly

`EfaClient` provides asynchronous helpers for stop search, departure monitoring and trip planning:

```python
import asyncio
from suedtirolmobilai.efa_client import EfaClient, TripEndpoint

async def main() -> None:
    async with EfaClient() as client:
        stops = await client.stop_finder("Bolzano")
        board = await client.departures("de:84000:1")
        trip = await client.plan_trip(
            origin=TripEndpoint(stop_id="de:84000:1"),
            destination=TripEndpoint(stop_id="de:84000:200"),
        )

asyncio.run(main())
```

### Running the MCP server

The optional MCP server exposes the client functionality to MCP compatible hosts:

```bash
# Ensure the environment is activated and dependencies are installed
PYTHONPATH=src python -m server  # defaults to stdio transport
```

Set the environment variable `MCP_TRANSPORT` to `tcp` and provide `MCP_PORT` if you prefer a socket transport.

## Tests

Recorded fixtures live under `tests/fixtures`. Execute the automated test suite with:

```bash
pytest
```

The tests validate the normalised outputs against the Pydantic schemas and cover stop finder, departure monitor and
error mapping behaviour.

## Project structure

- `src/efa_client.py` – asynchronous client with caching and normalisation logic.
- `src/suedtirolmobilai/handlers.py` – pure functions that normalise raw payloads into Pydantic models.
- `src/suedtirolmobilai/schemas.py` – schema definitions shared across the project and tests.
- `src/server.py` – MCP server exposing the normalised tools.
- `tests/` – contract tests and recorded fixtures for the EFA backend.
