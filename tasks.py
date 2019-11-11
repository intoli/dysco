"""Task definitions for use with ``invoke``."""
import os
import re

from invoke import task
from invoke.exceptions import ParseError

import dysco

root_directory = os.path.dirname(os.path.realpath(__file__))


@task()
def docs(c):
    """Generate the project documentation."""
    c.run('rm -rf docs/reference/')
    c.run('sphinx-apidoc -e -f -o docs/reference dysco')
    c.run('docs/add_doctest_imports.py docs/reference')
    c.run('sphinx-build -E -b doctest docs dist/docs')
    c.run('sphinx-build -E -b html docs dist/docs')
    c.run('sphinx-build -b linkcheck docs dist/docs')


@task(help={'part': 'Whether to bump the major, minor, or patch portion of the version number.'})
def bump(c, part):
    current_version = dysco.__version__
    major, minor, patch = map(int, current_version.split('.'))
    if part == 'major':
        major += 1
    elif part == 'minor':
        minor += 1
    elif part == 'patch':
        patch += 1
    else:
        raise ParseError(f'The "part" argument must be one of major, minor, or patch.')
    new_version = f'{major}.{minor}.{patch}'

    # Update the version in `__init__.py`.
    path = os.path.join(root_directory, 'dysco', '__init__.py')
    with open(path, 'r') as f:
        lines = f.readlines()
    lines = [
        re.sub(f'__version__ = \'{current_version}\'', f'__version__ = \'{new_version}\'', line)
        for line in lines
    ]
    with open(path, 'w') as f:
        f.write(''.join(lines))

    # Update the version in `pyproject.toml`.
    path = os.path.join(root_directory, 'pyproject.toml')
    with open(path, 'r') as f:
        lines = f.readlines()
    lines = [
        re.sub(f'version = "{current_version}"', f'version = "{new_version}"', line)
        for line in lines
    ]
    with open(path, 'w') as f:
        f.write(''.join(lines))


@task(
    help={
        'all': 'Run all linting checks regardless of the other flags.',
        'black': 'Check the code formatting using black.',
        'flake8': 'Lint the codebase using flake8.',
        'isort': 'Check the import formatting using isort.',
        'mypy': 'Perform type checking using mypy.',
    }
)
def lint(c, all=True, black=True, flake8=False, isort=False, mypy=False):
    """Run miscellaneous linting tasks."""
    if all or black:
        c.run('black --check --diff dysco tests')
    if all or isort:
        c.run('isort --verbose --check-only --diff --recursive src tests')
    if all or flake8:
        c.run('flake8 dysco tests')
    if all or mypy:
        c.run('mypy --ignore-missing-imports dysco tests')


@task(help={'coverage': 'Generate a coverage report.'})
def test(c, coverage=False):
    """Run the dysco test suite."""
    if coverage:
        c.run('pytest --cov --cov-report=term-missing -vv')
        c.run('coverage report')
        c.run('coverage html')
    else:
        c.run('pytest')
