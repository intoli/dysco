import pickle
from sys import version_info

import pytest

from dysco import Dysco, g


def test_contains():
    assert 'hi' not in g
    g['hi'] = True
    assert 'hi' in g


def test_deleting_attributes():
    g.something = 1
    assert hasattr(g, 'something')
    delattr(g, 'something')
    assert not hasattr(g, 'something')


def test_deleting_items():
    g['something'] = 1
    assert 'something' in g
    del g['something']
    assert 'something' not in g


def test_deleting_items_in_readonly_mode():
    # It should work fine in the same scope.
    dysco = Dysco(read_only=True)
    dysco['something'] = 1
    assert 'something' in dysco
    del dysco['something']
    assert 'something' not in dysco

    dysco['something'] = 1

    def delete_in_inner_scope():
        del dysco['something']

    with pytest.raises(KeyError):
        delete_in_inner_scope()
    assert 'something' in dysco


def test_deleting_private_attributes():
    dysco = Dysco(read_only=True)
    assert dysco._Dysco__read_only == True
    del dysco._Dysco__read_only
    with pytest.raises(AttributeError):
        dysco.__read_only


def test_dict_conversion():
    g.set_in_outer = 1

    def test_inner():
        g.set_in_inner = 2
        assert dict(g) == {'set_in_inner': 2, 'set_in_outer': 1}
        if version_info[0] > 3 or version_info[1] >= 7:
            assert (
                list(dict(g).keys())[0] == 'set_in_inner'
            ), 'Variables set in lower scopes should be ordered first.'

    test_inner()


def test_hasattr():
    assert not hasattr(g, 'hi')
    g['hi'] = True
    assert hasattr(g, 'hi')


def test_item_tuple_access():
    g[(1, 'hi')] = True
    assert g[(1, 'hi')] == True


def test_item_attribute_interoperability():
    g.hello = 1
    assert g['hello'] == 1
    g['hello'] = 2
    assert g['hello'] == 2
    assert g.hello == 2


def test_pickling_fails():
    with pytest.raises(pickle.PickleError):
        pickle.dumps(g)


def test_scope_in_loops():
    g.hello = -1
    for i in range(20):
        assert g.hello == i - 1
        g.hello = i


def test_scope_isolation():
    g.first = 1
    g.second = 2

    def test_first():
        g.first *= -1
        g.third = 3

    def test_second():
        g.second *= -1
        with pytest.raises(AttributeError):
            _ = g.third

    test_first()
    assert g.first == -1
    assert g.second == 2
    with pytest.raises(AttributeError):
        _ = g.third

    test_second()
    assert g.first == -1
    assert g.second == -2

    test_first()
    test_second()
    assert g.first == 1
    assert g.second == 2


def test_stacklevel_option():
    dysco = Dysco(stacklevel=2)

    def set(key, value):
        dysco[key] = value

    def nested_set(key, value):
        set(key, value)

    def get(key):
        return dysco[key]

    set('a', 1)
    assert get('a') == 1

    nested_set('b', 1)
    with pytest.raises(KeyError):
        get('b')
