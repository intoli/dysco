import pickle
from sys import version_info

import pytest

from dysco import Dysco, g


@pytest.mark.asyncio
async def test_async_functions():
    g.value = 1

    async def test_inner():
        assert g.value == 1
        g.value = 2
        g.inner_value = 3

    await test_inner()
    with pytest.raises(AttributeError):
        g.inner_value
    assert g.value == 2


def test_calling_dysco_as_a_decorator():
    g.value = 1

    @g(readonly=True)
    def check_access(g, arg, kwarg):
        assert arg == 'arg'
        assert kwarg == 'kwarg'
        g.inner_value = 2
        with pytest.raises(AttributeError):
            g.value = 3
        assert g.inner_value == 2

    check_access(arg='arg', kwarg='kwarg')
    assert g.value == 1
    assert 'inner_value' not in g


@pytest.mark.asyncio
async def test_calling_dysco_as_a_decorator_on_an_async_function():
    g.value = 1

    @g(readonly=True)
    async def check_access(g, arg, kwarg):
        assert arg == 'arg'
        assert kwarg == 'kwarg'
        g.inner_value = 2
        with pytest.raises(AttributeError):
            g.value = 3
        assert g.inner_value == 2

    await check_access(arg='arg', kwarg='kwarg')
    assert g.value == 1
    assert 'inner_value' not in g


def test_calling_dysco_to_create_a_variant():
    g.value = 1
    readonly_g = g(readonly=True)

    def check_access():
        assert g.value == 1
        assert readonly_g.value == 1

        g.value = 2
        assert readonly_g.value == 2
        with pytest.raises(AttributeError):
            readonly_g.value = 3

        g.writeable_value = 4
        readonly_g.readonly_value = 5

    check_access()

    assert g.value == 2
    assert readonly_g.value == 2
    assert 'writable_value' not in g
    assert 'writable_value' not in readonly_g
    assert 'readonly_value' not in g
    assert 'readonly_value' not in readonly_g


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
    dysco = Dysco(readonly=True)
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
    dysco = Dysco(readonly=True)
    assert dysco._Dysco__readonly == True
    del dysco._Dysco__readonly
    with pytest.raises(AttributeError):
        dysco.__readonly


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


def test_readonly_option():
    dysco = Dysco(readonly=True)
    dysco.value = 1

    def check_access():
        dysco.inner_value = 2
        with pytest.raises(AttributeError):
            dysco.value = 3

    check_access()

    assert dysco.value == 1
    assert 'inner_value' not in dysco


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


def test_shadow_option():
    with pytest.raises(ValueError):
        dysco = Dysco(readonly=True, shadow=True)

    dysco = Dysco(shadow=True)
    dysco.value = 1

    def check_access():
        dysco.value = 2

        def inner_check_access():
            assert dysco.value == 2
            dysco.value = 3

        inner_check_access()
        assert dysco.value == 2

    check_access()
    assert dysco.value == 1


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
