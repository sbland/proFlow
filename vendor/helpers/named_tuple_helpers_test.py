from typing import NamedTuple, List, Sequence
import pytest

from .named_tuple_helpers import dict_to_named_tuple, _replace_recursive, get_val_from_tuple


def test_dict_to_named_tuple():
    class B(NamedTuple):
        foo: str = None

    class A(NamedTuple):
        b: B = B()
        c: int = None
        e: int = None

    d = {
        "b": {
            "foo": "bar"
        },
        "c": 1,
    }

    new_object = dict_to_named_tuple(d, A)
    assert new_object == A(B('bar'), 1)


def test_dict_to_named_tuple_b():
    class B(NamedTuple):
        foo: str = None

    class A(NamedTuple):
        lat: float = None
        lon: float = None

    class Wrap(NamedTuple):
        a: A = A()
        b: B = B()

    d = {
        "a": {
            "lat": 52.2,
            "lon": -1.12,
        },
    }

    new_object = dict_to_named_tuple(d, Wrap)
    assert new_object == Wrap(a=A(lat=52.2, lon=-1.12))


def test_dict_to_named_tuple_nested_named_tuple():
    class B(NamedTuple):
        parameters: List[str] = []

    class A(NamedTuple):
        lat: float = None
        lon: float = None

    class Wrap(NamedTuple):
        a: A = A()
        b: B = B()

    d = {
        "a": {
            "lat": 52.2,
            "lon": -1.12,
        },
    }

    new_object = dict_to_named_tuple(d, Wrap)
    assert new_object == Wrap(a=A(lat=52.2, lon=-1.12))


def test_dict_to_named_tuple_list():
    class B(NamedTuple):
        parameters: List[str] = []

    class A(NamedTuple):
        lat: float = None
        lon: float = None

    class Wrap(NamedTuple):
        a: A = A()
        b: B = B()
        c: List[str] = []

    d = {
        "c": ["a", "b"]
    }

    new_object = dict_to_named_tuple(d, Wrap)
    assert new_object == Wrap(c=["a", "b"])


def test_dict_to_named_tuple_nested_list():
    class B(NamedTuple):
        parameters: List[str] = []

    class A(NamedTuple):
        lat: float = None
        lon: float = None

    class Wrap(NamedTuple):
        a: A = A()
        b: B = B()
        c: List[str] = []

    d = {
        "b": {
            "parameters": [
                "a", "b"
            ]
        }
    }

    new_object = dict_to_named_tuple(d, Wrap)
    assert new_object == Wrap(b=B(parameters=["a", "b"]))


def test_dict_to_named_tuple_nested_list_of_tuple():
    class B(NamedTuple):
        parameters: List[str] = []

    class A(NamedTuple):
        lat: float = None
        lon: float = None

    class Wrap(NamedTuple):
        a: A = A()
        b: B = B()
        c: Sequence[A] = []

    d = {
        "c": [
            {
                "lat": 52.2,
                "lon": -1.12,
            },
            {
                "lat": 20.2,
                "lon": -10.12,
            },
        ]
    }

    new_object = dict_to_named_tuple(d, Wrap)
    assert new_object == Wrap(c=[A(lat=52.2, lon=-1.12), A(lat=20.2, lon=-10.12)])


def test_dict_to_named_tuple_invalid():
    class B(NamedTuple):
        foo: str = None

    class A(NamedTuple):
        lat: float = None
        lon: float = None

    class Wrap(NamedTuple):
        a: A = A()
        b: B = B()

    d = {
        "a": {
            "lat": False,
            "lon": -1.12,
        },
        "b": 4,
    }

    with pytest.raises(Exception):
        dict_to_named_tuple(d, Wrap, strict=True)

    d2 = {
        "b": 4,
    }

    with pytest.raises(Exception):
        dict_to_named_tuple(d2, Wrap, strict=True)

    d3 = {
        "z": 4,
    }

    with pytest.raises(Exception):
        dict_to_named_tuple(d3, Wrap, strict=True)


def test_replace_recursive():
    class B(NamedTuple):
        foo: str = 'hello'

    class A(NamedTuple):
        lat: float = 2
        lon: float = 3

    class Wrap(NamedTuple):
        a: A = A()
        b: B = B()
        c: int = 4

    # updated_wrap = _replace_recursive(Wrap(), 'c', 5)
    # # print(updated_wrap)
    # assert updated_wrap.c == 5

    updated_wrap_b = _replace_recursive(Wrap(), 'a.lat', 5)
    # print(updated_wrap_b)
    assert updated_wrap_b.a.lat == 5


def test_replace_recursive_with_list():
    class B(NamedTuple):
        foo: str = 'hello'

    class A(NamedTuple):
        lat: float = 2
        lon: float = 3

    class Wrap(NamedTuple):
        a: A = A()
        b: List[B] = [B(), B()]
        c: int = 4

    updated_wrap_b = _replace_recursive(Wrap(), 'b.0.foo', 'world')
    assert updated_wrap_b.b[0].foo == 'world'


def test_get_nested_args_from_tuple():
    class A(NamedTuple):
        val: int = 1

    class Tup(NamedTuple):
        foo: int = 1
        a: A = A()
        arr: List[int] = [1, 2, 3]
    tup = Tup()

    result = get_val_from_tuple(tup, 'foo')
    assert result == 1
    result = get_val_from_tuple(tup, 'arr.1')
    assert result == 2
    result = get_val_from_tuple(tup, 'a.val')
    assert result == 1
