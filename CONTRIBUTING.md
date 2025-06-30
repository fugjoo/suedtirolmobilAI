# Contributing

Thank you for considering contributing to this project!

Please review the [Code of Conduct](.github/CODE_OF_CONDUCT.md) before participating.

## Reporting Issues
Use the templates under `.github/ISSUE_TEMPLATE` to report bugs or request features. Provide as much detail as possible so we can reproduce the issue or understand the enhancement.

## Code Style
- Follow [PEP 8](https://peps.python.org/pep-0008/).
- Format code using [black](https://black.readthedocs.io/en/stable/):
  ```bash
  black .
  ```
- Check for linting errors with [flake8](https://flake8.pycqa.org/):
  ```bash
  flake8
  ```

## Pull Request Workflow
1. Create a feature branch from `main`.
2. Make your changes and ensure formatting and linting pass.
3. Commit with a clear message and push your branch.
4. Open a pull request and fill out the [PR template](.github/PULL_REQUEST_TEMPLATE.md).
5. Address any review feedback until the PR is approved.

Make sure to respect the `.gitignore` rules when committing files. Line endings are normalized using `.gitattributes`.
