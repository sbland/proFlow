"""Functions that modify state without mutation."""

from copy import deepcopy
from dataclasses import is_dataclass, replace
from functools import partial, reduce

from .helpers import rgetattr
from .internal_state import Model_State_Shape
from .objects.interface import I


def get_new_val_fn(attr, acc):
    """sets the value based on the type of input.

    Same as get_new_val but does not mutate the state

    Parameters
    ----------
    attr : Any(assignable)
        The state object to be modified
    acc : dict
        dictionary of changes to make e.g. { foo: 'newFoo' }

    Returns
    -------
    Any(assignable)
        The modified object

    """
    # NOTE: We can speed this up by removeing the replace and deepcopy functions
    if is_dataclass(attr):
        return replace(attr, **acc)
    if isinstance(attr, list) or type(attr).__module__ == "numpy":
        list_copy = deepcopy(attr)
        for k, v in acc.items():
            if k == "+":
                list_copy.append(v)
            else:
                list_copy[int(k)] = v
        return list_copy
    if isinstance(attr, dict):
        dict_copy = deepcopy(attr)
        for k, v in acc.items():
            dict_copy[k] = v
        return dict_copy

    # TODO: Handle named tuple
    # TODO: Handle numpy
    raise TypeError(f"Invalid type: {type(attr)}")


def build_up_args(
    acc: dict,
    i: int,
    target_split: list[str],
    initial_state: object,
) -> dict:
    """Part of iterator to replace part of object starting at bottom.

    Parameters
    ----------
    acc : dict
        Previous result from iterator
    i : int
        current iterator index (In reverse order)
    target_split : List[str]
        Dotstring split into list
    initial_state : object
        Object to update

    Returns
    -------
    dict
        [description]
    """

    # TODO: Test me
    t = target_split[i]
    t_2_h = ".".join(target_split[0 : i + 1])
    attr = rgetattr(initial_state, t_2_h)
    new_val = get_new_val_fn(attr, acc)
    new_args = {t: new_val}
    return new_args


def replace_state_val(initial_state, target, val):
    target_split = target.split(".")
    target_indexes = reversed(list(range(len(target_split[0:-1]))))

    build_up_args_part = partial(
        build_up_args,
        target_split=target_split,
        initial_state=initial_state,
    )

    out = reduce(build_up_args_part, target_indexes, {target_split[-1]: val})
    final_state = get_new_val_fn(initial_state, out)
    return final_state


_OUTPUT_VALUE = object()


def _build_update_tree(updates):
    """Build a path tree, returning None when targets overlap."""
    tree = {}
    for value, target in updates:
        node = tree
        for segment in target.split("."):
            if _OUTPUT_VALUE in node:
                return None
            node = node.setdefault(segment, {})
        if node:
            return None
        node[_OUTPUT_VALUE] = value
    return tree


def _apply_update_tree(current, tree, detached=False):
    """Apply a path trie, copying each mutable container only once.

    Descendants of a detached container can be updated in place; dataclasses
    along the updated paths are rebuilt with ``replace``.
    """
    if _OUTPUT_VALUE in tree:
        return tree[_OUTPUT_VALUE]

    is_list = isinstance(current, list)
    is_dict = isinstance(current, dict)
    is_numpy = type(current).__module__ == "numpy"
    if (is_list or is_dict or is_numpy) and not detached:
        current = deepcopy(current)
        detached = True

    changes = {}
    for key, child_tree in tree.items():
        if key is _OUTPUT_VALUE:
            continue

        child_is_value = _OUTPUT_VALUE in child_tree
        if child_is_value:
            child_value = child_tree[_OUTPUT_VALUE]
        else:
            child = (
                current[int(key)]
                if is_list or is_numpy
                else current[key]
                if is_dict
                else getattr(current, key)
            )
            child_value = _apply_update_tree(child, child_tree, detached)

        if is_list:
            if key == "+" and child_is_value:
                current.append(child_value)
            else:
                current[int(key)] = child_value
        elif is_numpy:
            current[int(key)] = child_value
        elif is_dict:
            current[key] = child_value
        else:
            changes[key] = child_value

    if is_dataclass(current):
        return replace(current, **changes)
    if changes:
        return get_new_val_fn(current, changes)
    return current


# TODO: Find optimized version of implementing non mutable version
def map_result_to_state_fn(
    prev_state: Model_State_Shape,
    output_map: list[I],
    result,
) -> Model_State_Shape:
    """Update the state based on an output mapping.

    Without state mutation.

    NOTE: This uses old output setup but is immutable and can use complex characters in target

    using `_result` as an output key will map the entire result to the state target

    Parameters
    ----------
    output_map : List[I]
        List of output mappings
    prev_state : Model_State_Shape
        Previous Model State
    result : [type]
        Result from process function

    Returns
    -------
    Model_State_Shape
        [description]
    """
    updates = list(output_map(result))
    if not updates:
        return prev_state
    update_tree = _build_update_tree(updates)
    if update_tree is not None:
        return _apply_update_tree(prev_state, update_tree)

    active_state = prev_state
    for from_, as_ in updates:
        active_state = replace_state_val(active_state, as_, from_)
    return active_state


# Version of get_new_val that mutates state but is much quicker!
# def get_new_val(attr, acc):
#     """sets the value based on the type of input.

#     WARNING: MUTATES STATE
#     TODO: We have removed the deepcopy and replace to speed this up but this removes immutability

#     Parameters
#     ----------
#     attr : Any(assignable)
#         The state object to be modified
#     acc : dict
#         dictionary of changes to make e.g. { foo: 'newFoo' }

#     Returns
#     -------
#     Any(assignable)
#         The modified object

#     """
#     if is_dataclass(attr):
#         for k, v in acc.items():
#             setattr(attr, k, v)
#         return attr
#         # return replace(attr, **acc)
#     if isinstance(attr, list) or type(attr).__module__ == 'numpy':
#         list_copy = attr  # deepcopy(attr) removed deepcopy
#         for k, v in acc.items():
#             if k == '+':
#                 list_copy.append(v)
#             else:
#                 list_copy[int(k)] = v
#         return list_copy
#     if isinstance(attr, dict):
#         dict_copy = attr  # deepcopy(attr) removed deepcopy
#         for k, v in acc.items():
#             dict_copy[k] = v
#         return dict_copy

#     # TODO: Handle named tuple
#     # TODO: Handle numpy
#     raise Exception(f'Invalid type: {type(attr)}')
