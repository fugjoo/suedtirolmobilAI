# Agent Contribution Guidelines

This repository stores a small Python project that provides a command line
interface to the Suedtirol public transport API via OpenAI's GPT service.
When contributing, please follow these rules.

## Code Style

- Follow [PEP8](https://peps.python.org/pep-0008/) for formatting.
- Ensure all functions and public classes include docstrings.
- Use type hints for function signatures.
- Prefer f-strings for string interpolation.

## Development Workflow

1. Create a Python virtual environment and install dependencies from
   `requirements.txt`.
2. Add or modify tests under `tests/` to cover your changes.
3. Run tests locally using:

   ```bash
   pytest -q
   ```

   All tests should pass before committing.

## Pull Request Expectations

- Keep pull requests focused and limit them to a single topic or fix.
- Provide a concise description of what was changed and why.
- Include test output in the PR description if tests are added or updated.

