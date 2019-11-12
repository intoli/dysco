![Dysco](https://github.com/intoli/dysco/raw/master/media/dysco.png)

<h1 vertical-align="middle">Dysco - Dynamic Scoping in Python
    <a targe="_blank" href="https://twitter.com/share?url=https%3A%2F%2Fgithub.com%2Fintoli%2Fdysco%2F&text=Dysco%20-%20Configurable%20dynamic%20scoping%20for%20Python">
        <img height="26px" src="https://simplesharebuttons.com/images/somacro/twitter.png"
 +          alt="Tweet"></a>
    <a target="_blank" href="https://www.facebook.com/sharer/sharer.php?u=https%3A//github.com/intoli/dysco">
        <img height="26px" src="https://simplesharebuttons.com/images/somacro/facebook.png"
            alt="Share on Facebook"></a>
    <a target="_blank" href="http://reddit.com/submit?url=https%3A%2F%2Fgithub.com%2Fintoli%2Fdysco%2F&title=Dysco%20%E2%80%94%20Configurable%20dynamic%20scoping%20for%20Python">
        <img height="26px" src="https://simplesharebuttons.com/images/somacro/reddit.png"
            alt="Share on Reddit"></a>
    <a target="_blank" href="https://news.ycombinator.com/submitlink?u=https://github.com/intoli/dysco&t=Dysco%20%E2%80%94%20Configurable%20dynamic%20scoping%20for%20Python">
        <img height="26px" src="https://github.com/intoli/dysco/raw/master/media/ycombinator.png"
            alt="Share on Hacker News"></a>
</h1>

<p align="left">
    <a href="https://circleci.com/gh/intoli/dysco/tree/master">
        <img src="https://img.shields.io/circleci/project/github/intoli/dysco/master.svg"
            alt="Build Status"></a>
    <a href="https://circleci.intoli.com/artifacts/intoli/dysco/coverage-report/index.html">
        <img src="https://img.shields.io/badge/dynamic/json.svg?label=coverage&colorB=ff69b4&query=$.coverage&uri=https://circleci.intoli.com/artifacts/intoli/dysco/coverage-report/total-coverage.json"
          alt="Coverage"></a>
    <a href="https://github.com/intoli/dysco/blob/master/LICENSE.md">
        <img src="https://img.shields.io/pypi/l/dysco.svg"
            alt="License"></a>
    <a href="https://pypi.python.org/pypi/dysco/">
        <img src="https://img.shields.io/pypi/v/dysco.svg"
            alt="PyPI Version"></a>
</p>

###### [Installation](#installation) | [Development](#development) | [Contributing](#contributing)

> Dysco is a lightweight Python library that brings [dynamic scoping](https://en.wikipedia.org/wiki/Scope_(computer_science)#Dynamic_scoping) capabilities to Python in a highly configurable way.


## Installation

Dysco can be installed from [pypy](https://pypi.org/project/dysco/) using `pip` or any compatible Python package manager.

```bash
# Installation with pip.
pip install dysco

# Or, installation with poetry.
poetry add dysco
```

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

## Contributing

Contributions are welcome, but please follow these contributor guidelines outlined in [CONTRIBUTING.md](CONTRIBUTING.md).


## License

Exodus is licensed under a [BSD 2-Clause License](LICENSE.md) and is copyright [Intoli, LLC](https://intoli.com).
