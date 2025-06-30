# suedtirolmobilAI

## Overview
SuedtirolmobilAI is a cross-platform command line tool for querying the
EFA/Mentz API using natural language. It lets you ask simple questions like
"When is the next bus to Bolzano?" and returns the relevant schedule
information. The application targets Linux, macOS and Windows systems and
runs anywhere Python 3.8 or newer is available.

## Installation
Clone this repository and install the Python dependencies. Using a virtual
environment is optional but recommended to keep packages isolated from the
rest of your system.

The tool depends on a few third‑party packages:

- `openai`
- `requests`

Install them with `pip`:

```bash
# optional: create a virtual environment
python -m venv .venv
source .venv/bin/activate

# install the required packages
pip install -r requirements.txt
```

## Usage
Use the helper script to install dependencies and run the program:

```bash
bash install_and_run.sh "Wann fährt der nächste Bus von Meran nach Bozen?"
```

Replace the example query with your own question about local transit.

## Contributing
We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines. Below is a short overview.

### Opening issues
- Use the templates under `.github/ISSUE_TEMPLATE` to report bugs or request features.
- Provide enough detail so we can reproduce or understand the request.

### Proposing pull requests
- Create a feature branch from `main`.
- Run formatting and linting checks before committing.
- Push your branch and open a pull request using the [PR template](.github/PULL_REQUEST_TEMPLATE.md).

### Coding style
- Follow [PEP 8](https://peps.python.org/pep-0008/).
- Format code with [black](https://black.readthedocs.io/en/stable/).
- Check for issues with [flake8](https://flake8.pycqa.org/).

## License

This project is licensed under the [MIT License](LICENSE).
