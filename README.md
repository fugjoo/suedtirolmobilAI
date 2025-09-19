# suedtirolmobilAI

Utilities for normalising responses coming from the Südtirol EFA (Elektronische Fahrplanauskunft) backend. The project exposes helper functions that transform raw stop finder and departure monitor payloads into application level Pydantic models.

## Development

The project uses [poetry? no], we use `pyproject.toml` with setuptools. To work on the project create a virtual environment and install the package in editable mode with the development extras:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Running the test suite

Recorded fixtures for the EFA backend live under `tests/fixtures`. Tests validate the normalised outputs against the Pydantic schemas and assert contract behaviour for:

- stop finder responses,
- departures versus arrivals monitors,
- realtime delay handling,
- error mapping.

Execute the full suite with:

```bash
pytest
```

## Continuous Integration

A GitHub Actions workflow is provided at `.github/workflows/tests.yml`. It installs the package with development dependencies and runs the `pytest` suite on every push and pull request.
