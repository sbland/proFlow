from dataclasses import dataclass, field
from typing import Callable, List, Tuple

from proflow.external_state import External_State_Shape
from proflow.parameters import Parameters_Shape
from proflow.config import Config_Shape
from proflow.process_inspector import parse_inputs, parse_outputs
from proflow.internal_state import Model_State_Shape
from .Interface import I


@dataclass
class Process:
    """Process object that stores the function and input and output targets.

    Parameters:
        func: Callable
            The function to call with the process
        gate: bool
            if false we skip the process
        comment: string
            a comment to display on logs and errors
        group: string
            used for grouping processes (Currently only used for logging)
        state_inputs: Callable
            returns a list of (I)nterfaces for mapping state to the function
        config_inputs: Callable
            returns a list of (I)nterfaces for mapping config to the function
        parameters_inputs: Callable
            returns a list of (I)nterfaces for mapping parameters to the function
        external_state_inputs: Callable
            returns a list of (I)nterfaces for mapping external state to the function
        additional_inputs: Callable
            returns a list of (I)nterfaces for mapping additional inputs to the function
        state_outputs: Callable
            returns a list of tuples as (new value, dot notation target) e.g. (1, 'temporal.hh')
        args: Callable
            additional args as a list (*args)
        format_output: Callable
            If true then we use old system(SLOW!) to map the output string to the state (can then use special characters)
    """
    func: Callable[[Model_State_Shape],
                   Model_State_Shape] = lambda: NotImplementedError()  # The function to call
    gate: bool = True  # if False process is skipped
    comment: str = ""  # used for logging
    group: str = None  # group tag
    # Inputs to function
    # TODO: The below objects could be set as the actual State Shape objects instead
    state_inputs: Callable[[Model_State_Shape], List[I]] = \
        field(default_factory=lambda: lambda state: [])
    config_inputs: Callable[[Config_Shape], List[I]] = \
        field(default_factory=lambda: lambda config: [])
    parameters_inputs: Callable[[Parameters_Shape], List[I]] = \
        field(default_factory=lambda: lambda params: [])
    external_state_inputs: Callable[[External_State_Shape, int], List[I]] = \
        field(default_factory=lambda: lambda e_state, row_index: [])
    additional_inputs: Callable[[], List[I]] = \
        field(default_factory=lambda: lambda: [])
    # TODO: state_outputs is depreciated
    state_outputs: Callable[[any], List[Tuple]] = field(default_factory=lambda: lambda result: [])
    # map_outputs: Callable[[any, object], object] = field(default_factory=list) # Depreciated
    args: List[any] = field(default_factory=list)  # additional args
    format_output: bool = False  # If true we process the target output string

    def __repr__(self) -> str:
        return 'Process(' + '; '.join([
            f'func={self.func.__name__}',
            f'comment="{self.comment}"',
            f'gate={self.gate}',
            f'group={self.group}',
            f'config_inputs={parse_inputs(self.config_inputs)}',
            f'parameters_inputs={parse_inputs(self.parameters_inputs)}',
            f'external_state_inputs={parse_inputs(self.external_state_inputs)}',
            f'additional_inputs={parse_inputs(self.additional_inputs)}',
            f'state_inputs={parse_inputs(self.state_inputs)}',
            f'state_outputs={parse_outputs(self.state_outputs)}',
            f'args={self.args}',
        ]) + ')'
