"""This is a process runner that creates an interface process and runner function
It allows connecting plugin functions to config, state and external data and
converts them into a process
The process runner is then passed a list of processes that it runs in order
updating the state at each step
"""
from dataclasses import astuple, is_dataclass
from proflow.helpers import rgetattr
from typing import NamedTuple, List, Callable
from functools import reduce

from vendor.helpers.dictionary_helpers import get_nested_val

import numpy as np

from vendor.helpers.comparisons import isNamedTuple
from vendor.helpers.named_tuple_helpers import _replace_recursive

from .Objects.Process import Process
from .Objects.Interface import I
from .config import Config_Shape
from .parameters import Parameters_Shape
from .external_state import External_State_Shape
from .internal_state import Model_State_Shape

from .errors import Run_Process_Error


def format_with_variables(
        config: Config_Shape,
        state: Model_State_Shape,
        external_state: External_State_Shape,
        parameters: Parameters_Shape,
        additional_inputs: dict) -> Callable:
    """formats from and to string literals to replace variables
    Works the same as python string literals
    https://docs.python.org/3.6/reference/lexical_analysis.html#f-strings

    f = partial(format_with_variables, config, state, {'name': 'john' })
    e.g. f('hello {name}') == 'hello john'
    """
    raise DeprecationWarning()
    format_data = {
        # Note additional inputs are expanded to allow easy access
        **additional_inputs,
        'config': config,
        'e_state': external_state,
        'external_state': external_state,
        'parameters': parameters,
        'state': state,
    }

    def _format(string: str) -> str:
        if '{' in string:
            return string.format(**format_data)
        else:
            return string
    return _format


def get_result_from_list(lst: list, k: List[int]) -> any:
    """Recursively gets the value from the input list using the ints in k"""
    raise DeprecationWarning()
    result = lst
    for i in k:
        if k == '_list':
            break
        result = result[int(i)]
    return result


def get_result(result, k):
    """Helper func that gets the result from process output
    This allows us to work with different outputs

    if k == '_list' then we return the full list
    """
    raise DeprecationWarning()
    # TODO: Make clearer that we are getting the actual result value if result is a str, int or
    # float
    # TODO: Better error reporting when key not valid etc
    if k == '_result':
        return result
    if isinstance(result, (str, int, float, bool)):
        return result
    if isinstance(result, dict):
        return result[k]
    if isinstance(result, list) and k != '_list':
        return get_result_from_list(result, k.split('.'))
    if isinstance(result, list) and k == '_list':
        return result
    if isinstance(result, np.ndarray) and k != '_list':
        return result[int(k)]
    if isinstance(result, np.ndarray) and k == '_list':
        return result
    if is_dataclass(result):
        return getattr(result, k)
    if isNamedTuple(result):
        return result._asdict()[k]
    raise ValueError(f'Could not determine type of {result}')


def validate_input(DEBUG: bool = False) -> Callable[[any, bool, str], any]:
    raise DeprecationWarning('Depreciated')
    def validate_input_(
        input: I,
        value: any,
    ) -> any:
        if not DEBUG:
            return value
        if input.required and value is None:
            raise ValueError(f'Input is required: {input.from_}')
        return value
    return validate_input_


def get_key_values(
        f: Callable,
        data: any,
        input_keys: List[I],
        DEBUG: bool = False,
) -> List[tuple]:  # noqa: E741
    raise DeprecationWarning('Depreciated')
    """gets the key value pairs from named tuples using the input keys from and keys as

    Inputs
    ======
    f: a string formatter for parsing key from and as values. SHould be pre loaded with data
    data: The data to get the values from (Can be dict, namedtuple or dataclass)
    input_keys: a list of I tuples that contain a from_ field and as_ field

    Outputs
    =======
    Outputs a list of key value pairs
    Each key represents the target field from the input from_ and the value is the assigned value


    Example:
    =======
    ```
    data = {
        "foo": "hello",
        "bar": "world"
    }
    input_keys = [
        I(from_='foo', as_='target_A'),
        I(from_='bar', as_='target_B'),
    ]
    output = [
        ('target_A', "hello"),
        ('target_B', "world"),
    ]

    Can also use nested keys such as `nested.foo` or for lists `nested_list.0`

    ```
    """
    # -- 4.63%
    from_keys = [f(key.from_) for key in input_keys]
    # -- 7.211 %
    as_keys = [f(key.as_) if key.as_ else None for key in input_keys]
    # -- 64.6 %
    # get the values from the data matching the from_keys
    input_values = [get_nested_val(data, key) for key in from_keys]
    validated_input_values = [
        validate_input(DEBUG)(kd, v) for kd, v in zip(input_keys, input_values)] \
        if DEBUG else input_values

    # if DEBUG:
    #     if not all([validate_input(DEBUG)(kd, v) for kd, v in zip(input_keys, input_values)]):
    #         raise ValueError('Invalid Input')
    # -- 6.79 %
    key_values_pairs = [(k, v) for k, v in zip(as_keys, validated_input_values) if k is not None]

    args = [v for k, v in zip(as_keys, validated_input_values) if k is None]
    return key_values_pairs, args


def get_process_inputs(
    process: Process,
    # sources
    prev_state: NamedTuple,
    config: Config_Shape,
    parameters: Parameters_Shape,
    external_state: External_State_Shape,
    DEBUG_MODE: bool = False,
) -> dict:
    """Get inputs from sources based on process input lists"""
    raise DeprecationWarning('Depreciated')
    # get inputs from process
    config_inputs: List[I] = process.config_inputs
    parameters_inputs: List[I] = process.parameters_inputs
    state_inputs: List[I] = process.state_inputs
    e_state_inputs: List[I] = process.external_state_inputs
    additional_inputs = process.additional_inputs

    # convert additional inputs to key value tuples
    additional_inputs_tuples = [astuple(a)[0:2] for a in additional_inputs]

    # -- 17.3%
    # create function that formats the key.as_ and key.from_
    f = format_with_variables(config, prev_state, external_state,
                              parameters, dict(additional_inputs_tuples))

    # -- 85.57 %
    # get key value inputs to pass to function
    key_values_config, args_config \
        = get_key_values(f, config, config_inputs, DEBUG=DEBUG_MODE)
    key_values_parameters, args_parameters \
        = get_key_values(f, parameters, parameters_inputs, DEBUG=DEBUG_MODE)
    key_values_state, args_state \
        = get_key_values(f, prev_state, state_inputs, DEBUG=DEBUG_MODE)
    key_values_e_state, args_e_state \
        = get_key_values(f, external_state, e_state_inputs, DEBUG=DEBUG_MODE)

    # -- 2.81 %
    # Merge inputs into a single dictionary that represents the kwargs of the process func
    kwrds = dict(
        key_values_e_state
        + key_values_config  # noqa: W503
        + key_values_parameters
        + key_values_state  # noqa: W503
        + additional_inputs_tuples)  # noqa: W503

    # -- 0.24 %
    args = process.args + args_config + args_parameters + args_state + args_e_state
    return kwrds, args


def run_process(
        prev_state: NamedTuple,  # Can be state or parameter
        process: Process,
        config: Config_Shape,
        parameters: Parameters_Shape,
        external_state: External_State_Shape,
        DEBUG_MODE: bool = False) -> NamedTuple:
    """Run a single process and output the updated state.
        The process object contains the function along with all the input
        and output targets.


        note: args from process are not garuanteed to be in the correct order

    Parameters
    ----------
    prev_state : NamedTuple
        Model state prior to this process being ran
    config : Config_Shape
        Model configuration
    parameters : Parameters_Shape
        Model derived parameters
    external_state : External_State_Shape
        External data
    DEBUG_MODE : bool, optional
        Debug processes when True, by default False

    Returns
    -------
    Model State
        Model State after process

    Raises
    ------
    Run_Process_Error
        Catches error that occur when running the process
    """
    raise DeprecationWarning('Depreciated')
    if not process.gate:
        return prev_state
    try:
        row_index = rgetattr(prev_state, 'temporal.row_index', 0)
        config_args = process.config_inputs(config)
        # parameters_args = process.parameters_inputs(parameters)
        # TODO: we need a better way of accessing current row index
        external_state_args = process.external_state_inputs(
            external_state, row_index,
        )
        additional_args = process.additional_inputs()
        state_args = process.state_inputs(prev_state)
        # additional_inputs_tuples = [astuple(a)[0:2] for a in additional_inputs]
        args = process.args
        # kwargs = {**config_args, **state_args} # fastest method
        kwargs = {i.as_: i.from_ for i in config_args +
                  state_args + additional_args + external_state_args if i.as_ is not None}
        args = process.args + [i.from_ for i in config_args +
                               state_args + additional_args + external_state_args if i.as_ is None]
        result = process.func(*args, **kwargs)
        # TODO: Implement new state out map
        # state_out = process.map_outputs(result, prev_state)
        # return state_out

        # kwrds, args = get_process_inputs(
        #     process,
        #     prev_state,
        #     config,
        #     parameters,
        #     external_state,
        #     DEBUG_MODE=DEBUG_MODE
        # )

        # # RUN PROCESS
        # result = process.func(*args, **kwrds)

        # CREATE NEW STATE
        output_map = process.state_outputs
        f = format_with_variables(config, prev_state, external_state, parameters, {})

        # iterate over output map and replace all values in state
        def update_state(prev_state, out):
            result_val = get_result(result, f(out.from_))
            # if process.debug >= 1:
            #     print(f'result_val: {result_val}')
            #     print(f'f(out.as_): {f(out.as_)}')
            return _replace_recursive(prev_state, f(out.as_), result_val)
        new_state = reduce(update_state, output_map, prev_state)
        return new_state

    except Exception as e:
        raise Run_Process_Error(process, e, prev_state) from e
