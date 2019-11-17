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

###### [Installation](#installation) | [How It Works](#how-it-works) | [Development](#development) | [Contributing](#contributing)

> Dysco is a lightweight Python library that brings [dynamic scoping](https://en.wikipedia.org/wiki/Scope_(computer_science)#Dynamic_scoping) capabilities to Python in a highly configurable way.


## Installation

Dysco can be installed from [pypy](https://pypi.org/project/dysco/) using `pip` or any compatible Python package manager.

```bash
# Installation with pip.
pip install dysco

# Or, installation with poetry.
poetry add dysco
```

## How It Works

The basic mechanics are fairly simple.
Python includes an [`inspect`](https://docs.python.org/3/library/inspect.html) module for reflection, and the [`inspect.stack()`](https://docs.python.org/3/library/inspect.html#inspect.stack) method makes it possible to access the full stack of frame records from the caller all the way up to the outermost call on the stack.
Creating a mapping of variables, and associating it with the scope of a frame, allows us to climb up the stack whenever a variable is accessed to see if there are any variables with the same name defined in a higher scope.
You can get fancy with the API and configurability, but a rough sketch of an implementation only takes a few lines of code.

```python
import inspect
import weakref

variables_by_frame_id = {}


def get_variable(name):
    # Exclude this frame we're in now from the stack.
    stack = inspect.stack()[1:]

    # Search up the stack for a matching variable.
    for frame_info in stack:
        variables = variables_by_frame_id.get(id(frame_info.frame))
        if variables and name in variables:
            return variables[name]

    # Raise an excpetion if the variable wasn't found.
    raise Exception(f'Variable "{name}" not found.')


def set_variable(name, value):
    # Exclude this frame we're in now from the stack.
    stack = inspect.stack()[1:]

    # Search up the stack for a matching variable.
    for frame_info in stack:
        variables = variables_by_frame_id.get(id(frame_info.frame))
        if variables and name in variables:
            variables[name] = value
            return

    # Insert it into the current scope if no matches were found.
    frame_id = id(stack[0].frame)
    variable_map_existed = frame_id in variables_by_frame_id
    if variable_map_existed:
        variables[name] = value
    else:
        variables_by_frame_id[frame_id] = {name: value}
```

This has roughly correct behavior, but the `variables_by_frame_id` accumulates more and more variable sets over time as variables get set in new execution frames.
Frames are getting created and destroyed every time a new scope is entered or exited, but our `variables_by_frame_id` is never cleaned up.
To make this code usable, we need to find a way to track the destruction of frames and remove any references to their corresponding variables so that they can be garbage collected.

Python provides another useful and relevant module called [`weakref`](https://docs.python.org/3/library/weakref.html) that's designed for use cases like this.
It includes a [`weakref.finalize()`](https://docs.python.org/3/library/weakref.html#weakref.finalize) function that can be used to register a callback that's fired when an object gets garbage collected.
Adding something like

```python
    if not variable_map_existed:
        weakref.finalize(
            frame,
            lambda frame_id: del variables_by_frame_id[frame_id],
            frame_id,
        )
```

to the end of our `set_variable()` method should, in principle, result in the lambda function being called with the frame ID after the frame no longer exists.
The lambda function would then remove the corresponding variable map from `variables_by_frame_id`, and since this is the only reference to the variable map, the garbage collector would be free to clean up the variables as needed.
There's just one problem with that...

```
TypeError: cannot create weak reference to 'frame' object
```

The `weakref.finalize()` method is just sugar on top of weak references, and Python doesn't support these for builtin types.
This is presumably due to the overhead incurred by supporting weak references (*e.g.* needing to allocate space for an extra pointer in every instance).
Maybe we could track one of the frame's attributes instead of the frame itself?
Well, it turns out that all of the frame's attributes are either builtin types that similarly don't support weak references (`bytes`, `dict`, `int`, `str`) or objects that outlive the frame (`f_code`, `f_trace`).

Only one of the frame attributes provides us with a glimmer of hope: `f_locals`, a dictionary representation of the variable namespace seen by the frame.
This is the only attribute that is both mutable and owned by the frame, so it provides us with a potential opportunity to inject something that can be weakly referenced and used to trigger a callback when the frame is garbage collected.
That said, the behavior of this dictionary is *interesting* to say the least.
So much so that [PEP 558 -- Defined semantics for locals()](https://www.python.org/dev/peps/pep-0558/) was written to address some of its issues, "spooky action-at-a-distance" has been used on the [Python-Dev mailing list](https://mail.python.org/pipermail/python-dev/2019-May/157749.html) to describe some aspects of how it behaves, and the majority of the StackOverflow answers about it seem to be flat out wrong.

Updating `f_locals` will sometimes update the local namespace, and it sometimes won't.
Other times updating it will update the global namespace as well.
Mutations to `f_locals` can be overwritten the next time the dictionary is synced, but they won't always.
Oh, and using a debugger or a code coverage tool will also [change how it behaves](https://nedbatchelder.com/blog/201211/tricky_locals.html).
And it should go without saying that it's implementation-specific, so let's not even get into anything outside of the [CPython](https://github.com/python/cpython) reference implementation.

A lot of the weirdness around `f_locals` stems from the fact that CPython optimizes variable lookups whenever possible with what are called "fast locals."
In function scopes, all of the local variable names are generally known once the code has been compiled to byte code.
This allows CPython to index all of the variables that will be seen in the frame, and handle access by index rather than by name (*i.e* pointer arithmetic can be used instead of a hash table).
The approach allows for dramatically faster code execution, but it means that fast locals need to be synced with `f_locals` for it to accurately represent the current state of the namespace.
Throw in the facts that not all frames are optimized and that sometimes `f_locals` is the same object as `f_globals`, and, well, things can start seeming spooky pretty fast.

The way that fast locals are synced to `f_locals` in CPython is the [`PyFrame_FastToLocalsWithError()`](https://github.com/python/cpython/blob/bed4817d52d7b5a383b1b61269c1337b61acc493/Objects/frameobject.c#L871) function.
This method basically invokes [`map_to_dict()`](https://github.com/python/cpython/blob/bed4817d52d7b5a383b1b61269c1337b61acc493/Objects/frameobject.c#L786) with the "map" part being `frame.f_code.co_varnames`, `frame.f_code.co_cellvars`, or `frame.f_code.co_freevars`, and the "dict" part being `frame.f_locals`.
It's not that important for the purpose of this discussion to know the difference between those three "map" parts, you can just think of them as a tuple containing the names of the variables in the local namespace.
Looking at the implementation of `map_to_dict()`, we can see that only keys in `map` are even considered when updating the `f_locals` dictionary.

```c
static int
map_to_dict(PyObject *map, Py_ssize_t nmap, PyObject *dict, PyObject **values,
            int deref)
{
    Py_ssize_t j;
    assert(PyTuple_Check(map));
    assert(PyDict_Check(dict));
    assert(PyTuple_Size(map) >= nmap);
    for (j=0; j < nmap; j++) {
        PyObject *key = PyTuple_GET_ITEM(map, j);
        PyObject *value = values[j];
        assert(PyUnicode_Check(key));
        if (deref && value != NULL) {
            assert(PyCell_Check(value));
            value = PyCell_GET(value);
        }
        if (value == NULL) {
            if (PyObject_DelItem(dict, key) != 0) {
                if (PyErr_ExceptionMatches(PyExc_KeyError))
                    PyErr_Clear();
                else
                    return -1;
            }
        }
        else {
            if (PyObject_SetItem(dict, key, value) != 0)
                return -1;
        }
    }
    return 0;
}
```

That means that we can put whatever we want in there without needing to worry about it being deleted or overwritten the next time that `f_locals` is updated... as long as it doesn't collide with the name of a variable that's in the local scope.
There's also the caveat that any variables we put in there actually *could* be written to the local scope if the code object isn't optimized.

One of the many nice things about Python dictionaries is that their keys don't have to be strings.
Any hashable type is supported as a dictionary key, so we can simply use any other hashable object as the key in order to completely eliminate the possibility of a collision with an actual variable name (in both the optimized and non-optimized cases).
Sure, that violates the type definition of `f_locals`, but those are type *hints* not type *rules* 😈.

This trick is the key piece of how Dysco works.
Dysco stores all of the variables associated with a `dysco.dysco.Dysco` instance and a specific frame in a `dysco.scope.Scope` instance.
The scope has a `scope.name` string that includes identifying information necessary to namespace everything, and then it wraps this in a tuple to use as a key when interacting with `f_locals` on a frame.
The `Scope.__init__()` method includes code that looks something like this:

```python
        frame.f_locals[self.name_tuple] = self  # type: ignore
        weakref.finalize(self, destructor, id(frame.f_locals), self.name)
```

No additional hard references to the scope are stored anywhere, so the scope is orphaned once `f_locals` is dereferenced and the corresponding destructor is called after the scope is garbage collected.
The destructor unregisters the scope name from some local data structures that are used for faster scope lookups, and nothing is left hanging around in memory.
The rest is just bookkeeping!

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

## Versioning

The Dysco library will use [semantic versioning](https://semver.org/) once the version reaches version 0.1.0.
Until then, you can expect breaking changes in the patch version.


## Contributing

Contributions are welcome, but please follow these contributor guidelines outlined in [CONTRIBUTING.md](CONTRIBUTING.md).


## License

Exodus is licensed under a [BSD 2-Clause License](LICENSE.md) and is copyright [Intoli, LLC](https://intoli.com).
