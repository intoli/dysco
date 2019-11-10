"""Task definitions for use with ``invoke``."""
from invoke import task


@task()
def docs(c):
    """Generate the project documentation."""
    c.run('rm -rf docs/reference/')
    c.run('sphinx-apidoc -e -f -o docs/reference dysco')
    c.run('docs/add_doctest_imports.py docs/reference')
    c.run('sphinx-build -E -b doctest docs dist/docs')
    c.run('sphinx-build -E -b html docs dist/docs')
    c.run('sphinx-build -b linkcheck docs dist/docs')


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
