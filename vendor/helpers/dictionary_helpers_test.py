from typing import NamedTuple

from .fill_np_array import fill_np_array_with_cls
from .dictionary_helpers import get_nested_arg_from_dict


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
    result = get_nested_arg_from_dict(data, 'bar.roo')
    assert result == 4
    result = get_nested_arg_from_dict(data, 'bar.ree.sow')
    assert result == 10
    result = get_nested_arg_from_dict(data, 'arr.1')
    assert result == 2
    result = get_nested_arg_from_dict(data, 'a.val')
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
    result = get_nested_arg_from_dict(data, 'a.sub.0.name')
    assert result == 'dave'
