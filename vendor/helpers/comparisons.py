import numpy as np
from typing import NamedTuple


def isNamedTuple(t):
    """helper function to check if t is a named tuple.
    This is not a perfect check!"""
    return isinstance(t, tuple) and type(t) is not tuple


def get_dict_differences(dict_a: dict, dict_b: dict):
    assert np.array_equal(dict_a.keys(), dict_b.keys())
    different_keys = list(filter(lambda x: dict_a[x] is not dict_b[x], dict_a.keys()))
    return [(a, str(dict_a[a]) + " => " + str(dict_b[a])) for a in different_keys]


def are_equal_safe(val_a: any, val_b: any):
    """Safe comparison that deals with lists"""
    while True:
        are_equal = None
        are_same_type = type(val_a) is type(val_b)
        if not are_same_type:
            are_equal = False
            break

        type_of_val = type(val_a)
        if are_same_type and type_of_val == 'NoneType':
            are_equal = val_a == val_b
            break
        if are_same_type and isinstance(val_a, str):
            are_equal = val_a == val_b
            break
        if are_same_type and isinstance(val_a, int):
            are_equal = val_a == val_b
            break
        if are_same_type and val_a is None:
            are_equal = val_a == val_b
            break
        if are_same_type and isinstance(val_a, float):
            are_equal = val_a == val_b
            break
        if are_same_type and type_of_val == 'list':
            are_equal = np.array_equal(val_a, val_b)
            break
        if are_same_type and type_of_val in [np.ndarray, list]:
            are_equal = np.array_equal(val_a, val_b)
            break
        if are_same_type and isinstance(val_a, tuple) and type_of_val is tuple:
            are_equal = np.array_equal(val_a, val_b)
            break
        if are_same_type and isinstance(val_a, tuple) and type_of_val is not tuple:
            # Assume to be NamedTuple
            are_equal = tuples_are_equal(val_a, val_b)
            break

        if are_equal is None:
            raise TypeError('Invalid compare type ', type_of_val, val_a)

    return are_equal


def compare_named_tuples(tuple_a: NamedTuple, tuple_b: NamedTuple):
    comparisons = [
        (label, are_equal_safe(a[1], b[1]), a[1], b[1])
        for label, a, b
        in zip(tuple_a._asdict().keys(), tuple_a._asdict().items(), tuple_b._asdict().items())
    ]
    return comparisons


def tuples_are_equal(tuple_a: NamedTuple, tuple_b: NamedTuple):
    return all([
        are_equal_safe(a[1], b[1])
        for a, b
        in zip(tuple_a._asdict().items(), tuple_b._asdict().items())
    ])


def get_mismatched_tuples(tuple_a: NamedTuple, tuple_b: NamedTuple):
    comparisons = compare_named_tuples(tuple_a, tuple_b)
    filtered_comparisons = list(filter(lambda x: not x[1], comparisons))
    return filtered_comparisons


def assert_matched_tuples(tuple_a: NamedTuple, tuple_b: NamedTuple):
    mismatched_tuples = get_mismatched_tuples(tuple_a, tuple_b)
    passes = (len(mismatched_tuples) == 0)
    if not passes:
        raise AssertionError('Tuples do not match: ', mismatched_tuples)
