
from typing import NamedTuple

from .fill_np_array import fill_np_array_with_cls
from .dictionary_helpers import get_nested_val


def test_get_nested_args_from_dict():
    class A(NamedTuple):
        val: int = 1

    data = {
        'foo': 1,
        'bar': {
            'roo': 4,
            'ree': {
                'sow': 10,
            }
        },
        'arr': [1, 2, 3],
        'a': A(),
    }
    result = get_nested_val(data, 'bar.roo')
    assert result == 4
    result = get_nested_val(data, 'bar.ree.sow')
    assert result == 10
    result = get_nested_val(data, 'arr.1')
    assert result == 2
    result = get_nested_val(data, 'a.val')
    assert result == 1


def test_get_nested_args_with_numpy_list():
    class Sub(NamedTuple):
        name: str = 'dave'

    class A(NamedTuple):
        val: int = 1
        sub: Sub = fill_np_array_with_cls(3, Sub)

    data = {
        'a': A(),
    }
    result = get_nested_val(data, 'a.sub.0.name')
    assert result == 'dave'


def test_get_nested_arg_from_list():
    class A(NamedTuple):
        val: int = 1

    data = {
        'foo': 1,
        'arr': [1, 2, 3],
        'matrix': [[1, 2, 3], [4, 5, 6]]
    }
    result = get_nested_val(data, 'arr.1')
    assert result == 2
    result = get_nested_val(data, 'matrix.1.1')
    assert result == 5


def test_get_nested_arg_from_list_with_wildcard():
    class A(NamedTuple):
        val: int = 1

    data = {
        'foo': 1,
        'arr': [1, 2, 3],
        'matrix': [[1, 2, 3], [4, 5, 6]],
        'deepmatrix': [[[1, 2], [3, 4]], [[5, 6], [7, 8]]],
        'dictlist': [{'foo': 'abc'}, {'foo': 'def'}]
    }
    # result = get_nested_val(data, 'matrix.1.x')
    # assert result == [4, 5, 6]
    result = get_nested_val(data, 'matrix._.1')
    assert result == [2, 5]
    result = get_nested_val(data, 'deepmatrix._.1._')
    assert result == [[3, 4], [7, 8]]
    result = get_nested_val(data, 'dictlist._.foo')
