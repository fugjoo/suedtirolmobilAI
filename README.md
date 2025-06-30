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

```bash
# optional: create a virtual environment
python -m venv .venv
source .venv/bin/activate

# install requirements if any
pip install -r requirements.txt
```

## Usage
Run the command-line interface to start interacting with the service:

```bash
python cli.py --query "When is the next bus to Bolzano?"
```

Replace the example query with your own question about local transit.

## Contributing
We welcome contributions! Report bugs or request features using the templates under `.github/ISSUE_TEMPLATE`. For code changes, create a feature branch and open a pull request using the [template](.github/PULL_REQUEST_TEMPLATE.md).

Ensure Python code follows [PEP 8](https://peps.python.org/pep-0008/) and is formatted with [black](https://black.readthedocs.io/en/stable/). Lint your changes with [flake8](https://flake8.pycqa.org/).

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

## License

This project is licensed under the [MIT License](LICENSE).
