# Dysco


## Development

To install the dependencies locally, you need [poetry](https://poetry.eustace.io/docs/#installation) to be installed.
You can then run

```bash
# This is optional, but highly recommended.
# It tells poetry to place the virtual environment in `.venv`.
poetry config settings.virtualenvs.in-project true

# Install all of the dependencies.
poetry install
```

to install the project dependencies.

The library is tested against Python versions 3.6, 3.7, and 3.8.
These are most easily installed using [pyenv](https://github.com/pyenv/pyenv#installation) with the following command.

```bash
# Install the supported Python versions.
pyenv install --skip-existing 3.6.9
pyenv install --skip-existing 3.7.5
pyenv install --skip-existing 3.8.0
```

Testing, linting, and document generation can then be run via [tox](https://tox.readthedocs.io/en/latest/).
The bare `tox` command will run everything in all environments, or you can break it down by Python version and task.
For example, you could run the individual Python 3.8 tasks manually by running the following.

```bash
# Install the project dependencies in `.tox/py38/`.
tox -e py38-init

# Run black, flake8, isort, and mypy.
tox -e py38-lint

# Run the tests and generate a coverage report.
tox -e py38-test --coverage

## Build the project documentation.
tox -e py38-docs
```
