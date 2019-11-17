import gc
import inspect

from dysco.scope import Scope, find_parent_scope, scopes_by_name


def test_f_local_keys_are_tuples():
    frame = inspect.stack()[0].frame
    assert not any(isinstance(key, tuple) for key in frame.f_locals.keys())
    Scope(frame)
    [name_tuple] = [key for key in frame.f_locals.keys() if isinstance(key, tuple)]
    assert len(name_tuple) == 1
    assert name_tuple[0].startswith('_Dysco__')


def test_namespaces_produce_new_scopes():
    frame = inspect.stack()[0].frame
    old_scope = Scope(frame)
    new_scope = Scope(frame, 'something else')
    assert old_scope != new_scope
    assert old_scope is not new_scope


def test_parent_stacks_can_be_found():
    frame = inspect.stack()[0].frame
    expected_parent_scope = Scope(frame)

    def get_parent_scope():
        stack = inspect.stack()
        frame = stack[0].frame
        inner_scope = Scope(frame)
        return find_parent_scope(inner_scope, stack)[0]

    parent_scope = get_parent_scope()
    assert parent_scope is expected_parent_scope


def test_scopes_are_successfully_retrieved():
    frame = inspect.stack()[0].frame
    old_scope = Scope(frame)
    new_scope = Scope(frame, '')
    assert old_scope == new_scope
    assert old_scope is new_scope


def test_scopes_are_garbage_collected():
    def get_scope_name():
        frame = inspect.stack()[0].frame
        scope = Scope(frame)
        assert scope.name in scopes_by_name

    scope_name = get_scope_name()
    gc.collect()
    assert scope_name not in scopes_by_name


test_namespaces_produce_new_scopes()
