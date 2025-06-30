# suedtirolmobilAI

## Overview
This project provides an NLP interface to the EFA/Mentz API, allowing users to query mobility information in natural language.

## Installation
You can simply clone this repository. Using a Python virtual environment is optional but recommended to keep dependencies isolated.

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
