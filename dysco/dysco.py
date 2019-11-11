"""Houses the implementation of the main ``Dysco`` class and project API."""
import inspect
from typing import Any

from dysco.scope import Scope, find_parent_scope


class Dysco:
    def __init__(self, read_only: bool = False):
        self.__read_only = read_only

    def __getattr__(self, attribute: str) -> Any:
        if attribute.startswith('_Dysco_'):
            return super().__getattribute__(attribute)
        stack = inspect.stack()
        current_frame = stack.pop(0).frame
        try:
            scope = Scope(stack[0].frame, namespace=hex(id(self)))
            while scope:
                if attribute in scope.variables:
                    return scope.variables[attribute]
                scope, stack = find_parent_scope(scope, stack)
            raise AttributeError(f'The attribute {attribute} was not found in any scope.')
        finally:
            # Delete the current frame to avoid reference cycles.
            del current_frame

    def __setattr__(self, attribute: str, value: Any) -> None:
        if attribute.startswith('_Dysco_'):
            super().__setattr__(attribute, value)
        read_only = getattr(self, '_Dysco_read_only', False)
        stack = inspect.stack()
        current_frame = stack.pop(0).frame
        try:
            initial_scope = Scope(stack[0].frame, namespace=hex(id(self)))
            scope = initial_scope
            while not read_only and scope:
                if attribute in scope.variables:
                    scope.variables[attribute] = value
                    return
                scope, stack = find_parent_scope(scope, stack)
            initial_scope.variables[attribute] = value
        finally:
            # Delete the current frame to avoid reference cycles.
            del current_frame
