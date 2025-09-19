# Südtirolmobil MCP Server

## Overview

This repository contains a Model Context Protocol (MCP) server that exposes the Südtirol/Südtirolmobil public transport data set to MCP compliant clients.  It wraps the Open Data Hub REST endpoints and turns them into structured tools that large language model agents can call to look up stops, departures, and plan multimodal journeys across South Tyrol.  The server focuses on:

- **Unified access** – abstracting the heterogeneous Open Data Hub resources behind a consistent tool interface for MCP clients.
- **Result curation** – normalising stop, departure, and trip responses, pruning noisy attributes, and enriching payloads with calculated hints (distance, interchange windows, disruption flags).
- **Caching & rate control** – sharing responses across sessions to reduce the number of requests to the upstream API while keeping information fresh.
- **Observability** – structured logging and metrics around tool execution times and cache hit rates.

The MCP server can be embedded inside an MCP host (for example Claude Desktop, Cursor, or any other compatible orchestrator) or run as a standalone process that communicates over stdio, TCP sockets, or WebSockets depending on your integration needs.

## Architecture

### High-level flow

```
MCP client → Tool invocation → Node.js MCP server → Transit API client → Südtirolmobil Open Data Hub
                                           ↘ cache + metrics layer ↙
```

1. An MCP client invokes one of the tools exposed by this server.
2. The Node.js process validates the request payload with Zod schemas, enriches it with defaults, and forwards it to the transit API client.
3. The client queries the Südtirolmobil Open Data Hub REST endpoints.  Responses are cached in-memory (or Redis) based on cache keys derived from the request parameters.
4. The server transforms the raw JSON payload into a tool-friendly structure and returns it to the MCP client together with metadata (latency, cache state, source URL).

### Components

| Component | Responsibility | Key technologies |
| --- | --- | --- |
| **MCP Tool Registry** | Registers tools, performs schema validation, routes invocations | Node.js 20+, TypeScript, `@modelcontextprotocol/sdk`, `zod` |
| **Transit API client** | Handles HTTP requests, retries, throttling, pagination | `axios`, `p-retry`, `bottleneck`, `qs` |
| **Caching layer** | Stores responses for configurable TTL, optional Redis backend | `keyv`, `@keyv/redis` |
| **Configuration manager** | Loads `.env` variables, merges with defaults per environment | `dotenv`, `zod` |
| **Structured logging** | Emits JSON logs and human-readable traces | `pino`, `pino-pretty` |
| **Test harness** | Integration & contract tests against the live sandbox | Python 3.11, `pytest`, `httpx`, `respx` |

The TypeScript server lives in `src/` (tool definitions), `clients/` (API adapters), and `lib/` (shared utilities).  The Python harness under `tests/` is optional but recommended for validating queries against staging data before shipping changes.

## Runtime requirements & dependencies

### Node.js

- **Runtime**: Node.js >= 20.10 (enables fetch API, AbortController, and stable `Intl` features used by the server).
- **Package manager**: `pnpm` >= 8.15 is recommended (alternatively `npm` or `yarn`).
- **Core dependencies**:
  - `@modelcontextprotocol/sdk` – MCP server primitives and tool registration helpers.
  - `axios` – HTTP client tuned for the Open Data Hub endpoints.
  - `zod` – runtime schema validation for tool inputs/outputs.
  - `dotenv` – load environment variables from `.env` files.
  - `keyv` / `@keyv/redis` – pluggable caching adapter.
  - `pino` – structured logging.
  - `bottleneck` – request throttling to respect upstream rate limits.
- **Dev dependencies**:
  - `typescript`, `ts-node`, `tsx` – compiling and running TS sources.
  - `esbuild` – bundling for deployment targets.
  - `eslint`, `@typescript-eslint/eslint-plugin`, `prettier` – linting & formatting.
  - `vitest` – lightweight unit testing framework for Node.

### Python (test utilities)

- **Runtime**: Python 3.11+
- **Package manager**: `uv` or `pip`
- **Packages**:
  - `pytest` – orchestrate integration tests.
  - `httpx` – async HTTP client for hitting the MCP server locally.
  - `respx` – mock outbound calls during contract tests.
  - `python-dotenv` – environment variable loading for tests.
  - `pydantic` – mirroring schemas in Python side assertions.

## Getting started

1. **Clone the repository**
   ```bash
   git clone git@github.com:<your-org>/suedtirolmobilAI.git
   cd suedtirolmobilAI
   ```
2. **Install Node dependencies**
   ```bash
   corepack enable   # enables pnpm that ships with Node 20+
   pnpm install
   ```
   If you prefer npm, run `npm install` instead.
3. **Install Python tooling (optional)**
   ```bash
   uv sync
   # or
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Configure environment variables**
   - Copy the example file:
     ```bash
     cp .env.example .env
     ```
   - Adjust the values documented below.  Environment variables can also be provided through your MCP host configuration if that is more convenient.

### Environment variables

| Variable | Description | Default |
| --- | --- | --- |
| `TRANSIT_BASE_URL` | Base URL for the Südtirolmobil Open Data Hub transit API.  Use the staging endpoint during testing. | `https://api.opendatahub.bz.it/v2/flat/transit` |
| `TRANSIT_API_KEY` | Optional API key if you obtained elevated quota from the data provider.  Leave empty for public endpoints. | _empty_ |
| `TRANSIT_USER_AGENT` | Custom User-Agent header to identify your application. | `suedtirolmobil-mcp-server/<version>` |
| `CACHE_BACKEND` | `memory` or `redis`.  Determines the Keyv adapter used for caching. | `memory` |
| `CACHE_MAX_AGE` | TTL (in seconds) for cache entries. | `30` |
| `CACHE_MAX_SIZE` | Maximum number of cache records when using the in-memory backend. | `500` |
| `REDIS_URL` | Redis connection string.  Required when `CACHE_BACKEND=redis`. | _empty_ |
| `REQUEST_TIMEOUT_MS` | HTTP request timeout in milliseconds. | `10000` |
| `LOG_LEVEL` | Logging verbosity (`silent`, `error`, `warn`, `info`, `debug`, `trace`). | `info` |
| `ENABLE_METRICS` | When `true`, expose Prometheus metrics on the port defined below. | `false` |
| `METRICS_PORT` | Port for the metrics server when metrics are enabled. | `9000` |

Example `.env`:

```
TRANSIT_BASE_URL=https://api.opendatahub.bz.it/v2/flat/transit
TRANSIT_API_KEY=
TRANSIT_USER_AGENT=suedtirolmobil-mcp-server/dev
CACHE_BACKEND=memory
CACHE_MAX_AGE=45
REQUEST_TIMEOUT_MS=12000
LOG_LEVEL=debug
ENABLE_METRICS=true
METRICS_PORT=9300
```

## Running the MCP server locally

### Development mode

```bash
pnpm dev        # runs src/index.ts with hot-reload via tsx
```

The dev command starts the MCP server in stdio mode by default.  If you wish to expose it over a TCP socket for debugging, set `MCP_TRANSPORT=tcp` and `MCP_PORT=5100` in your environment.

### Production build

```bash
pnpm build      # transpile TypeScript to dist/
pnpm start      # run the compiled JavaScript from dist/
```

When packaging for deployment you can also build a single-file bundle:

```bash
pnpm bundle     # outputs dist/server.mjs using esbuild
```

### Python integration tests

After the server is running locally on `localhost:5100` in TCP mode, execute:

```bash
pytest -m "integration"
```

Tests tagged `integration` will hit live APIs (respecting your rate limits).  Use `pytest -m "not integration"` to run only mocked tests.

## Tool catalogue

The MCP server currently publishes the following tools.  All inputs/outputs are validated with `zod` before being sent to or returned from the upstream API.

### `stop.find`

- **Purpose**: Search for stops by name, ID, or proximity.
- **Input schema**:
  ```json
  {
    "type": "object",
    "required": ["query"],
    "properties": {
      "query": { "type": "string", "description": "Free-text search term or stop ID." },
      "limit": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 },
      "focus": {
        "type": "object",
        "required": ["lat", "lon"],
        "properties": {
          "lat": { "type": "number" },
          "lon": { "type": "number" },
          "radius": { "type": "integer", "minimum": 100, "maximum": 5000, "default": 1000 }
        }
      },
      "transport_modes": {
        "type": "array",
        "items": { "type": "string", "enum": ["bus", "train", "cable_car", "ferry"] },
        "description": "Restrict results to specific transport modes."
      }
    }
  }
  ```
- **Output payload**:
  ```json
  {
    "stops": [
      {
        "id": "string",
        "name": "string",
        "latitude": 46.498,
        "longitude": 11.354,
        "municipality": "Bolzano",
        "transport_modes": ["bus"],
        "distance_m": 120,
        "platforms": [
          { "code": "A", "name": "Bin 1", "isWheelchairAccessible": true }
        ],
        "sources": ["https://api.opendatahub.bz.it/v2/flat/transit/stops?id=..."]
      }
    ],
    "took_ms": 132,
    "from_cache": false
  }
  ```
- **Notes**: If both `query` and `focus` are supplied, the server first performs a textual match and then sorts by distance using the focus point.

### `departures.board`

- **Purpose**: Retrieve upcoming departures for a stop or platform.
- **Input schema**:
  ```json
  {
    "type": "object",
    "required": ["stop_id"],
    "properties": {
      "stop_id": { "type": "string" },
      "when": { "type": "string", "format": "date-time", "description": "Reference time in ISO 8601." },
      "duration": { "type": "integer", "minimum": 5, "maximum": 120, "default": 30 },
      "limit": { "type": "integer", "minimum": 1, "maximum": 50, "default": 15 },
      "include_delays": { "type": "boolean", "default": true },
      "platform": { "type": "string", "description": "Optional platform code to filter departures." }
    }
  }
  ```
- **Output payload**:
  ```json
  {
    "stop": { "id": "8501000", "name": "Bolzano/Bozen" },
    "departures": [
      {
        "service": { "id": "SAD-12345", "name": "SAD 170", "mode": "bus" },
        "destination": "Ortisei/Urtijëi",
        "scheduled_time": "2024-05-16T12:15:00+02:00",
        "predicted_time": "2024-05-16T12:17:00+02:00",
        "delay_minutes": 2,
        "platform": "A",
        "remarks": ["Wheelchair accessible"],
        "status": "on_time"
      }
    ],
    "from_cache": true,
    "sources": ["https://api.opendatahub.bz.it/v2/flat/transit/departures?..."],
    "took_ms": 85
  }
  ```
- **Notes**: When `include_delays=false`, the upstream API is queried without real-time updates and `predicted_time` equals `scheduled_time`.

### `trip.plan`

- **Purpose**: Request an itinerary between two locations with multimodal routing.
- **Input schema**:
  ```json
  {
    "type": "object",
    "required": ["origin", "destination"],
    "properties": {
      "origin": {
        "oneOf": [
          { "type": "object", "required": ["stop_id"], "properties": { "stop_id": { "type": "string" } } },
          { "type": "object", "required": ["lat", "lon"], "properties": { "lat": { "type": "number" }, "lon": { "type": "number" } } }
        ]
      },
      "destination": {
        "oneOf": [
          { "type": "object", "required": ["stop_id"], "properties": { "stop_id": { "type": "string" } } },
          { "type": "object", "required": ["lat", "lon"], "properties": { "lat": { "type": "number" }, "lon": { "type": "number" } } }
        ]
      },
      "departure_time": { "type": "string", "format": "date-time" },
      "arrival_time": { "type": "string", "format": "date-time", "description": "Specify to plan an arrive-by trip." },
      "max_transfers": { "type": "integer", "minimum": 0, "maximum": 6, "default": 3 },
      "modes": {
        "type": "array",
        "items": { "type": "string", "enum": ["bus", "train", "tram", "cable_car", "ferry"] },
        "description": "Restrict transport modes."
      },
      "wheelchair": { "type": "boolean", "default": false },
      "language": { "type": "string", "enum": ["de", "it", "en", "lad"], "default": "en" }
    }
  }
  ```
- **Output payload**:
  ```json
  {
    "plans": [
      {
        "duration_minutes": 74,
        "transfers": 1,
        "legs": [
          {
            "mode": "bus",
            "service": "SAD 170",
            "origin": { "id": "8501000", "name": "Bolzano Autostazione" },
            "destination": { "id": "8502001", "name": "Ortisei Piazza" },
            "departure_time": "2024-05-16T12:25:00+02:00",
            "arrival_time": "2024-05-16T13:39:00+02:00",
            "real_time": true,
            "geometry": "polyline...",
            "notes": ["Bike transport allowed"],
            "tickets": [
              {
                "name": "Mobilcard 1 day",
                "price_eur": 16.0,
                "currency": "EUR",
                "conditions": ["Valid on SAD buses"]
              }
            ]
          }
        ],
        "fare_summary": {
          "currency": "EUR",
          "total": 16.0,
          "products": ["Mobilcard"]
        }
      }
    ],
    "from_cache": false,
    "sources": ["https://api.opendatahub.bz.it/v2/flat/transit/trips?..."],
    "took_ms": 210
  }
  ```
- **Notes**: Set only one of `departure_time` or `arrival_time`.  The server rejects requests containing both.

### `trip.monitor`

- **Purpose**: Subscribe to real-time updates for a planned trip.
- **Input schema**:
  ```json
  {
    "type": "object",
    "required": ["trip_id"],
    "properties": {
      "trip_id": { "type": "string", "description": "Trip identifier returned by trip.plan" },
      "leg_index": { "type": "integer", "minimum": 0, "description": "Restrict monitoring to a specific leg." },
      "poll_interval": { "type": "integer", "minimum": 15, "maximum": 120, "default": 30 }
    }
  }
  ```
- **Output payload**:
  ```json
  {
    "trip_id": "string",
    "status": "in_progress",
    "legs": [
      {
        "index": 0,
        "mode": "bus",
        "departure_time": "2024-05-16T12:25:00+02:00",
        "predicted_departure_time": "2024-05-16T12:28:00+02:00",
        "arrival_time": "2024-05-16T13:39:00+02:00",
        "predicted_arrival_time": "2024-05-16T13:42:00+02:00",
        "delay_minutes": 3,
        "alerts": [
          {
            "id": "alert-4521",
            "severity": "major",
            "description": "Traffic congestion near Ponte Gardena."
          }
        ]
      }
    ],
    "next_update_in": 30,
    "from_cache": false,
    "sources": ["https://api.opendatahub.bz.it/v2/flat/transit/trip-updates?..."],
    "took_ms": 95
  }
  ```
- **Notes**: The MCP host is responsible for scheduling repeated calls using the suggested `next_update_in` interval.

### `alerts.feed`

- **Purpose**: Retrieve active service disruptions affecting the network.
- **Input schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "modes": {
        "type": "array",
        "items": { "type": "string", "enum": ["bus", "train", "cable_car", "ferry"] }
      },
      "severity": {
        "type": "string",
        "enum": ["info", "minor", "major", "critical"],
        "default": "info"
      }
    }
  }
  ```
- **Output payload**:
  ```json
  {
    "alerts": [
      {
        "id": "alert-4521",
        "severity": "major",
        "mode": "bus",
        "summary": "Traffic congestion on SS12",
        "description": "Expect delays of up to 15 minutes between Bolzano and Laives.",
        "affected_stops": ["8501000", "8501010"],
        "starts_at": "2024-05-16T11:30:00+02:00",
        "ends_at": null,
        "sources": ["https://api.opendatahub.bz.it/v2/flat/transit/alerts?..."],
        "last_updated": "2024-05-16T11:55:00+02:00"
      }
    ],
    "from_cache": true,
    "took_ms": 60
  }
  ```
- **Notes**: Alerts are cached slightly longer (default 2 minutes) because they change less frequently than departures.

### Common error payload

When a tool invocation fails, the MCP server returns a structured error object so hosts can display context-aware feedback:

```json
{
  "error": {
    "type": "UpstreamHttpError",
    "message": "Request failed with status 429",
    "status": 429,
    "retry_after_seconds": 30,
    "sources": ["https://api.opendatahub.bz.it/v2/flat/transit/departures?..."],
    "correlation_id": "d9a5b2a9-1c0d-4ad9-aa42-22833a9a1c31"
  }
}
```

## Testing & quality checks

| Command | Description |
| --- | --- |
| `pnpm lint` | Run ESLint with the TypeScript ruleset. |
| `pnpm typecheck` | Execute `tsc --noEmit` to ensure the codebase is type-safe. |
| `pnpm test` | Run unit tests with Vitest (uses mocked HTTP responses). |
| `pnpm test:e2e` | Launches the server on a random port and runs end-to-end tests. |
| `pytest` | Executes Python-based integration tests. |
| `pytest -m contract` | Runs schema contract tests ensuring the Node and Python schemas remain aligned. |
| `pnpm audit` | Check dependencies for known vulnerabilities. |

### Continuous integration

A GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push and pull request:

1. Install Node & pnpm, then execute `pnpm install`.
2. Run `pnpm lint`, `pnpm typecheck`, `pnpm test`.
3. Set up Python 3.11 and run `pytest -m "not integration"`.
4. Upload coverage reports to Codecov.

Nightly builds additionally run the integration suite with live API calls to detect upstream contract changes early.

## Deployment

### Container image

1. Build the image:
   ```bash
   docker build -t ghcr.io/<your-org>/suedtirolmobil-mcp:latest .
   ```
2. Run the container:
   ```bash
   docker run --rm \
     -e TRANSIT_BASE_URL=https://api.opendatahub.bz.it/v2/flat/transit \
     -e CACHE_BACKEND=redis \
     -e REDIS_URL=redis://redis.internal:6379/0 \
     -e MCP_TRANSPORT=tcp -e MCP_PORT=5100 \
     -p 5100:5100 \
     ghcr.io/<your-org>/suedtirolmobil-mcp:latest
   ```

### Cloud deployment notes

- **Redis**: Provision a managed Redis instance if you plan to enable cache persistence across replicas.
- **Autoscaling**: The server is stateless aside from caches.  Use horizontal autoscaling and rely on Redis-backed caching to avoid duplicate upstream requests.
- **Observability**: Scrape the Prometheus endpoint (enabled with `ENABLE_METRICS=true`) and ship logs to your preferred aggregator.
- **Secrets**: Store sensitive variables (API keys) in your cloud provider’s secret manager.  Avoid committing `.env` files.

## Additional resources

- [Open Data Hub – Mobility API documentation](https://opendatahub.readthedocs.io/) (general reference for endpoints and query parameters).
- [Model Context Protocol specification](https://modelcontextprotocol.io/) for details about tool discovery and invocation semantics.
- [pnpm documentation](https://pnpm.io/) for package management tips.

> _Keep this README up to date as new tools or dependencies are added.  When introducing new endpoints, document their schemas here so that MCP host integrators can adopt them without digging into the code._
