# Dysco


## Development

To install the dependencies locally, you need [poetry](https://poetry.eustace.io/docs/#installation) to be installed.
You can then run

```bash
# This is only required if you're not using poetry v1.0.0 or greater.
# It tells poetry to place the virtual environment in `.venv`.
poetry config settings.virtualenvs.in-project true

# Install all of the dependencies.
poetry install
```

to install the project dependencies.

The library is tested against Python versions 3.7 and 3.8.
These are most easily installed using [pyenv](https://github.com/pyenv/pyenv#installation) with the following command.

```bash
# Install the supported Python versions.
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

## Deployment

You first need to configure your credentials with poetry.

```bash
poetry config http-basic.pypi intoli <pypi-password>
```

You can then use invoke to bump the version number, commit the changes, tag the version, and deploy to pypi.

```bash
# Bumps the patch version and deploys the package.
# Valid options are major, minor, and patch.
invoke bump patch
```
