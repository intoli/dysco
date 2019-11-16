"""Houses the implementation of the main ``Dysco`` class and project API."""
import inspect
from threading import Lock
from typing import Any, Hashable, Iterator, Tuple

from dysco.scope import Scope, find_parent_scope


class Dysco:
    def __init__(self, read_only: bool = False, stacklevel: int = 1):
        self.__read_only = read_only
        self.__stacklevel = stacklevel
        self.__stacklevel_lock = Lock()

    def __contains__(self, key: Hashable) -> bool:
        try:
            current_frame = inspect.currentframe()
            self.__stacklevel_lock.acquire()
            self.__stacklevel += 1
            self[key]
            return True
        except KeyError:
            return False
        finally:
            self.__stacklevel -= 1
            self.__stacklevel_lock.release()
            # Delete the current frame to avoid reference cycles.
            del current_frame

    def __delattr__(self, attribute: str):
        if attribute.startswith('_Dysco_'):
            return super().__delattr__(attribute)

        try:
            current_frame = inspect.currentframe()
            self.__stacklevel_lock.acquire()
            self.__stacklevel += 1
            del self[attribute]
        except KeyError as key_error:
            raise AttributeError(key_error.args[0].replace('key', 'attribute', count=1))
        finally:
            self.__stacklevel -= 1
            self.__stacklevel_lock.release()
            # Delete the current frame to avoid reference cycles.
            del current_frame

    def __delitem__(self, key: Hashable):
        stack = inspect.stack()
        current_frame = stack[0].frame
        stack = stack[self.__stacklevel :]
        try:
            initial_scope = Scope(stack[0].frame, namespace=hex(id(self)))
            scope = initial_scope
            while scope:
                if key in scope.variables:
                    if self.__read_only and scope is not initial_scope:
                        raise KeyError(
                            f'The key "{key}" is defined in a higher scope, but is read-only.'
                        )
                    else:
                        del scope.variables[key]
                    return
                scope, stack = find_parent_scope(scope, stack)
            raise KeyError(f'The key "{key}" was not found in any scope.')
        finally:
            # Delete the current frame to avoid reference cycles.
            del current_frame

    def __getattr__(self, attribute: str) -> Any:
        if attribute.startswith('_Dysco_'):
            return super().__getattribute__(attribute)

        try:
            current_frame = inspect.currentframe()
            self.__stacklevel_lock.acquire()
            self.__stacklevel += 1
            return self[attribute]
        except KeyError:
            raise AttributeError(f'The attribute {attribute} was not found in any scope.')
        finally:
            self.__stacklevel -= 1
            self.__stacklevel_lock.release()
            # Delete the current frame to avoid reference cycles.
            del current_frame

    def __getitem__(self, key: Hashable) -> Any:
        stack = inspect.stack()
        current_frame = stack[0].frame
        stack = stack[self.__stacklevel :]
        try:
            scope = Scope(stack[0].frame, namespace=hex(id(self)))
            while scope:
                if key in scope.variables:
                    return scope.variables[key]
                scope, stack = find_parent_scope(scope, stack)
            raise KeyError(f'The key "{key}" was not found in any scope.')
        finally:
            # Delete the current frame to avoid reference cycles.
            del current_frame

    def __iter__(self) -> Iterator[Tuple[Hashable, Any]]:
        stack = inspect.stack()
        current_frame = stack[0].frame
        stack = stack[self.__stacklevel :]
        try:
            scope = Scope(stack[0].frame, namespace=hex(id(self)))
            while scope:
                for key_value_pair in scope.variables.items():
                    yield key_value_pair
                scope, stack = find_parent_scope(scope, stack)
        finally:
            # Delete the current frame to avoid reference cycles.
            del current_frame

    def __setattr__(self, attribute: str, value: Any) -> None:
        if attribute.startswith('_Dysco_'):
            super().__setattr__(attribute, value)
            return

        try:
            current_frame = inspect.currentframe()
            self.__stacklevel_lock.acquire()
            self.__stacklevel += 1
            self[attribute] = value
        finally:
            self.__stacklevel -= 1
            self.__stacklevel_lock.release()
            # Delete the current frame to avoid reference cycles.
            del current_frame

    def __setitem__(self, key: str, value: Any) -> None:
        stack = inspect.stack()
        current_frame = stack[0].frame
        stack = stack[self.__stacklevel :]
        try:
            initial_scope = Scope(stack[0].frame, namespace=hex(id(self)))
            scope = initial_scope
            while not self.__read_only and scope:
                if key in scope.variables:
                    scope.variables[key] = value
                    return
                scope, stack = find_parent_scope(scope, stack)
            initial_scope.variables[key] = value
        finally:
            # Delete the current frame to avoid reference cycles.
            del current_frame
