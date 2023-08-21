"""Functions that get input args from the process and modify state from outputs in process."""
from typing import Any, Callable, List

from .helpers import rsetattr
from .Objects.Process import Process
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
    row_index: int,
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
    row_index: int
        The current process runner row index for external state access

    Returns
    -------
    Tuple[List, dict]
        Input args and kwargs
    """
    config_args = process.config_inputs(config)
    parameters_args = process.parameters_inputs(parameters)
    external_state_args = process.external_state_inputs(
        external_state, row_index,
    )
    additional_inputs = process.additional_inputs()
    state_args = process.state_inputs(prev_state)
    args = process.args
    kwargs = {i.as_: i.from_ for i
              in config_args +
              state_args +
              additional_inputs +
              external_state_args +
              parameters_args
              if i.as_ is not None}
    args = process.args + [i.from_ for i in config_args +
                           state_args + additional_inputs + external_state_args
                           if i.as_ is None]
    return args, kwargs


def map_result_to_state(
    prev_state: Model_State_Shape,
    output_map: Callable[[Model_State_Shape, Any], Model_State_Shape],
    result: Any,
) -> Model_State_Shape:
    """Update the state based on an output mapping.
    WARNING: MUTATES STATE

    using `_result` as an output key will map the entire result to the state target

    Parameters
    ----------
    output_map : Callable
        Lambda expression that assigns the result to the state
    prev_state : Model_State_Shape
        Previous Model State
    result : [type]
        Result from process function

    Returns
    -------
    Model_State_Shape
        [description]
    """
    for from_, as_ in output_map(result):
        rsetattr(prev_state, as_, from_)
    return prev_state
