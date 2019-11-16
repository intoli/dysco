import weakref
from inspect import FrameInfo
from types import FrameType
from typing import TYPE_CHECKING, Any, Dict, Hashable, List, Optional, Set
from weakref import WeakValueDictionary

from slugify import slugify

Stack = List[FrameInfo]

if TYPE_CHECKING:
    ScopesByName = WeakValueDictionary[str, 'Scope']
else:
    ScopesByName = WeakValueDictionary


scopes_by_name: ScopesByName = WeakValueDictionary()
name_sets_by_frame_id: Dict[int, Set[str]] = {}


def construct_name(frame: FrameType, namespace: str = '') -> str:
    name: str = '_dysco_'
    if namespace:
        # Slugify limits characters to those matching the `[^-a-zA-Z0-9]+` regex.
        name += slugify(namespace).replace('-', '_') + '_'
    name += hex(id(frame.f_locals))
    return name


def destructor(frame_id: int, name: str):
    name_set = name_sets_by_frame_id[frame_id]
    name_set.remove(name)


def find_existing_scope(frame: FrameType, namespace: str = '') -> Optional['Scope']:
    name_set = name_sets_by_frame_id.get(id(frame.f_locals), set())
    for name in name_set:
        candidate_scope = scopes_by_name.get(name)
        if candidate_scope:
            frame_scope = frame.f_locals.get(candidate_scope.name)
            if candidate_scope is frame_scope and namespace == candidate_scope.namespace:
                return candidate_scope
    return None


def find_parent_scope(scope: 'Scope', stack: Stack):
    for i, frame_info in enumerate(stack):
        parent_scope = find_existing_scope(frame_info.frame, scope.namespace)
        if parent_scope and parent_scope is not scope:
            return parent_scope, stack[i + 1 :]
    return None, []


class Scope:
    def __init__(self, frame: FrameType, namespace: str = ''):
        # Block calling `__init__()` more than once on a given instance.
        if getattr(self, 'initialized', False):
            return
        self.initialized = True

        self.name = construct_name(frame, namespace)
        self.namespace = namespace
        self.variables: Dict[Hashable, Any] = {}

        scopes_by_name[self.name] = self
        frame.f_locals[self.name] = self
        name_set = name_sets_by_frame_id.get(id(frame.f_locals), set())
        name_set.add(self.name)
        name_sets_by_frame_id[id(frame.f_locals)] = name_set
        weakref.finalize(self, destructor, id(frame.f_locals), self.name)

    def __new__(cls, frame: FrameType, namespace: str = ''):
        # Attempt to find an existing scope for this frame.
        existing_scope = find_existing_scope(frame, namespace)
        if existing_scope:
            return existing_scope

        # Otherwise initialize a new scope.
        return super().__new__(cls)
