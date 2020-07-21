from dataclasses import is_dataclass, replace
from typing import NamedTuple, List
from copy import deepcopy
from functools import reduce
import numpy as np

from .dictionary_helpers import get_nested_val
from .comparisons import isNamedTuple


def dict_to_named_tuple(data: dict, Cls, strict=False):
    """Parses a dictionary to a specific named tuple"""

    if not isinstance(data, dict):
        raise Exception('Data is invalid {}'.format(type(data)))

    cls_fields = [f for (f, t) in Cls.__annotations__.items() if f in data]

    # if strict ensure that no invalid data fields
    if strict:
        invalid_data_keys = [k for k in data.keys() if k not in cls_fields]
        if len(invalid_data_keys) > 0:
            first_invalid_key = invalid_data_keys[0]
            raise Exception('{} must be in {} fields'.format(first_invalid_key, Cls.__name__))

    cls_field_types = [t for (f, t) in Cls.__annotations__.items() if f in data]
    data_values = [data[f] for f in cls_fields]

    def get_base_val(f, t, v):
        # Check types
        if strict and not isinstance(v, t):
            raise TypeError('{} must be {}'.format(f, t))
        return v

    def get_list_val(f, t, v):
        item_type = t.__args__[0]
        if strict and not isinstance(v, list):
            raise TypeError('{} must be {}'.format(f, t))
        new_val = None
        new_val = v if item_type in [int, float, str, bool] else new_val
        new_val = [dict_to_named_tuple(vi, item_type, strict) for vi in v] \
            if item_type.__bases__[0].__name__ == 'tuple' else new_val
        return new_val

    def get_named_tuple_val(f, t, v):
        # if type is a Named Tuple then we assume nested and
        # run recursive dict_to_named_tuple
        if strict and not isinstance(v, dict):
            raise TypeError('{} must be {}'.format(f, t))
        return dict_to_named_tuple(v, t, strict)

    def get_process_type(t):
        process_type = None
        process_type = get_base_val if process_type is None \
            and t in [int, float, str, bool]\
            else process_type
        process_type = get_list_val if process_type is None\
            and type(t) == type(List) else process_type
        process_type = get_named_tuple_val if process_type is None\
            and t.__bases__[0].__name__ == 'tuple' else process_type
        if process_type is None:
            raise TypeError('{} is invalid type'.format(t))
        return process_type

    # process_types = map(get_process_type, cls_field_types)

    # TODO: Fix so this is immutable
    new_data = {}
    for (f, t, v) in zip(cls_fields, cls_field_types, data_values):
        new_data[f] = get_process_type(t)(f, t, v)

    return Cls(**new_data)


def get_next_val(last_val, k):
    next_val = None
    next_val = last_val[k] if isinstance(last_val, dict) else next_val
    next_val = last_val[int(k)] if isinstance(last_val, list) else next_val
    next_val = last_val[int(k)] if isinstance(last_val, np.ndarray) else next_val
    next_val = getattr(last_val, k) if is_dataclass(last_val) else next_val
    next_val = last_val._asdict()[k] if isNamedTuple(last_val) else next_val
    return next_val


def set_list_val(l, k, v):
    """ functional update list helper"""
    l_new = deepcopy(l)
    l_new[k] = v
    return l_new


def set_dict_val(d, k, v):
    """ functional update dict helper"""
    d_new = deepcopy(d)
    d_new[k] = v
    return d_new


def set_next_val(obj, acc):
    next_val = None
    next_val = set_dict_val(obj, acc[0], acc[1]) if isinstance(obj, dict) else next_val
    next_val = set_list_val(obj, int(acc[0]), acc[1]) if isinstance(obj, list) else next_val
    next_val = set_list_val(obj, int(acc[0]), acc[1]) if isinstance(obj, np.ndarray) else next_val
    next_val = replace(obj, **dict([acc])) if is_dataclass(obj) else next_val
    next_val = obj._replace(**dict([acc])) if isNamedTuple(obj) else next_val
    if next_val is None:
        raise ValueError()
    return next_val


def _replace_recursive(
        data_tuple: NamedTuple,
        location: str,
        value: any) -> NamedTuple:
    """replaces a value in a tuple using a dot notation str location"""
    locations = location.split('.')

    def get_val(arr, k):
        last_val = arr[-1][1]
        next_val = get_next_val(last_val, k)
        return arr + [(k, next_val)]
    tree = reduce(get_val, locations, [('root', data_tuple)])
    tree_new = tree[:-1] + [(locations[-1], value)]
    tree_new_reversed = reversed(tree_new)
    # tree is a key value list where key

    def set_vals(acc, leaf):
        # return (leaf[0], leaf[1]._replace(**dict([acc])))
        return (leaf[0], set_next_val(leaf[1], acc))
    new_data = reduce(set_vals, tree_new_reversed)
    return new_data[1]


def get_val_from_tuple(data_tuple: NamedTuple, location: str):
    """Helper class to get a nested value from a tuple
    uses get_nested_val"""
    return get_nested_val(data_tuple._asdict(), location)
