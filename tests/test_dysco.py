import pytest

from dysco import g


def test_item_tuple_access():
    g[(1, 'hi')] = True
    assert g[(1, 'hi')] == True


def test_item_attribute_interoperability():
    g.hello = 1
    assert g['hello'] == 1
    g['hello'] = 2
    assert g['hello'] == 2
    assert g.hello == 2


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
