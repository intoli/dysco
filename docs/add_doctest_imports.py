#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


def add_doctest_imports(directory):
    """Prepends all of the rst files in a directory with doctest imports."""
    for filename in os.listdir(directory):
        module_name, extension = os.path.splitext(filename)

        # Only consider .rst files and skip the modules index.
        if extension != '.rst':
            continue
        if module_name == 'modules':
            continue

        # Read in the current content.
        full_filename = os.path.join(directory, filename)
        with open(full_filename, 'r') as f:
            content = f.read()

        # Prepend it with the doctest imports.
        content = (
            '.. testsetup::\n\n'
            '    from %s import *\n\n' % module_name
        ) + content

        # Write out the modified file.
        with open(full_filename, 'w') as f:
            f.write(content)


if __name__ == '__main__':
    assert len(sys.argv) == 2, 'The directory must be passed as an argument.'
    add_doctest_imports(sys.argv[1])
