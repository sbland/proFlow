""" Defines varius helpers for working with lists"""


def flatten_list(arr: list) -> list:
    """ Recursive list flatten"""
    return [item for sublist in arr
            for item in
            (flatten_list(sublist) if type(sublist) is list else [sublist])]


def flatten_tuple(arr):
    return (item for sublist in arr
            for item in
            (flatten_list(sublist) if type(sublist) is tuple else [sublist]))


def filter_none(arr):
    return [a for a in arr if a is not None]
