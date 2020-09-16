from dataclasses import is_dataclass, replace
from functools import partial, reduce
from typing import Any, List
from copy import deepcopy

from .helpers import rgetattr
from .Objects import Process, I
from .internal_state import Model_State_Shape
from .config import Config_Shape
from .external_state import External_State_Shape
from .parameters import Parameters_Shape


def get_inputs_from_process(
    process: Process,
    prev_state: Model_State_Shape,
    config: Config_Shape,
    parameters: Parameters_Shape,
    external_state: External_State_Shape,
) -> List[Any]:
    """Get the args and kwargs from the Process.

    Parameters
    ----------
    process : Process
        Process object
    prev_state : Model_State_Shape
        Previous model state
    config : Config_Shape
        Model config
    parameters : Parameters_Shape
        Model Parameters
    external_state : External_State_Shape
        External data

    Returns
    -------
    Tuple[List, dict]
        Input args and kwargs
    """
    row_index = rgetattr(prev_state, 'temporal.row_index', 0)
    config_args = process.config_inputs(config)
    parameters_args = process.parameters_inputs(parameters)
    # TODO: we need a better way of accessing current row index
    external_state_args = process.external_state_inputs(
        external_state, row_index,
    )
    additional_inputs = process.additional_inputs()
    state_args = process.state_inputs(prev_state)
    args = process.args
    kwargs = {i.as_: i.from_ for i
              in config_args
              + state_args
              + additional_inputs
              + external_state_args
              + parameters_args
              if i.as_ is not None}
    args = process.args + [i.from_ for i in config_args +
                           state_args + additional_inputs + external_state_args
                           if i.as_ is None]
    return args, kwargs


def get_new_val(attr, acc):
    if is_dataclass(attr):
        return replace(attr, **acc)
    if isinstance(attr, list) or type(attr).__module__ == 'numpy':
        list_copy = deepcopy(attr)
        for k, v in acc.items():
            list_copy[int(k)] = v
        return list_copy
    if isinstance(attr, dict):
        dict_copy = deepcopy(attr)
        for k, v in acc.items():
            dict_copy[k] = v
        return dict_copy

    # TODO: Handle named tuple
    # TODO: Handle numpy
    raise Exception(f'Invalid type: {type(attr)}')


def build_up_args(
    acc: dict,
    i: int,
    target_split: List[str],
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
    t_2_h = '.'.join(target_split[0:i+1])
    attr = rgetattr(initial_state, t_2_h)
    new_val = get_new_val(attr, acc)
    new_args = {t: new_val}
    return new_args


def replace_state_val(initial_state, target, val):
    target_split = target.split('.')
    target_indexes = reversed(list(range(len(target_split[0:-1]))))

    build_up_args_part = partial(
        build_up_args,
        target_split=target_split,
        initial_state=initial_state,
    )

    out = reduce(build_up_args_part, target_indexes, {target_split[-1]: val})
    final_state = get_new_val(initial_state, out)
    return final_state


def map_result_to_state(
    prev_state: Model_State_Shape,
    output_map: List[I],
    result,
) -> Model_State_Shape:
    """Update the state based on an output mapping.

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
    active_state = prev_state
    for o in output_map:
        result_item = rgetattr(result, o.from_) if o.from_ != '_result' else result
        active_state = replace_state_val(active_state, o.as_, result_item)
    return active_state
