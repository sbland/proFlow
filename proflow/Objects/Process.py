from dataclasses import dataclass, field
from typing import Callable, List, Tuple
from enum import Enum
import dill as pickle

from proflow.external_state import External_State_Shape
from proflow.parameters import Parameters_Shape
from proflow.config import Config_Shape
from proflow.process_inspector import parse_inputs, parse_outputs, fieldNotEmpty
from proflow.internal_state import Model_State_Shape
from .Interface import I


class ProcessType(Enum):
    STANDARD = 0
    TIME = 1
    LOG = 2
    # TODO: Add NONMUTABLE type


def NOT_IMPLEMENTED():
    raise NotImplementedError()


def GET_STANDARD_TYPE_FACTORY():
    return ProcessType.STANDARD


def GET_INPUT_FACTORY_INNER(*args, **kwargs):
    return []


def GET_INPUT_FACTORY(**kwargs):
    return GET_INPUT_FACTORY_INNER


@dataclass
class Process:
    """Process object that stores the function and input and output targets.

    Parameters:
        func: Callable
            The function to call with the process
        ptype: ProcessType
            The type of process. Acts as a switch to decide how we run it
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
            If true then we use old system(SLOW!) to map the output string
            to the state (can then use special characters)

    """
    func: Callable[[Model_State_Shape],
                   Model_State_Shape] = NOT_IMPLEMENTED  # The function to call
    ptype: ProcessType = field(default_factory=GET_STANDARD_TYPE_FACTORY)
    gate: bool = True  # if False process is skipped
    comment: str = ""  # used for logging
    group: str = None  # group tag
    # Inputs to function
    # TODO: The below objects could be set as the actual State Shape objects instead
    state_inputs: Callable[[Model_State_Shape], List[I]] = \
        field(default_factory=GET_INPUT_FACTORY)
    config_inputs: Callable[[Config_Shape], List[I]] = \
        field(default_factory=GET_INPUT_FACTORY)
    parameters_inputs: Callable[[Parameters_Shape], List[I]] = \
        field(default_factory=GET_INPUT_FACTORY)
    external_state_inputs: Callable[[External_State_Shape, int], List[I]] = \
        field(default_factory=GET_INPUT_FACTORY)
    additional_inputs: Callable[[], List[I]] = \
        field(default_factory=GET_INPUT_FACTORY)
    state_outputs: Callable[[any], List[Tuple]] = field(default_factory=GET_INPUT_FACTORY)
    args: List[any] = field(default_factory=list)  # additional args
    format_output: bool = False  # If true we process the target output string

    def __repr__(self) -> str:
        return 'Process(' + '; '.join([
            f'func={self.func.__name__}',
            f'ptype={getattr(self, "ptype", None)}',
            f'comment="{getattr(self, "comment", None)}"',
            f'gate={getattr(self, "gate", None)}',
            f'group={getattr(self, "group", None)}',
            f'config_inputs={parse_inputs(getattr(self, "config_inputs", None))}',
            f'parameters_inputs={parse_inputs(getattr(self, "parameters_inputs", None))}',
            f'external_state_inputs={parse_inputs(getattr(self, "external_state_inputs", None))}',
            f'additional_inputs={parse_inputs(getattr(self, "additional_inputs", None))}',
            f'state_inputs={parse_inputs(getattr(self, "state_inputs", None))}',
            f'state_outputs={parse_outputs(getattr(self, "state_outputs", None))}',
            f'args={getattr(self, "args", None)}',
        ]) + ')'

    def human(self, allow_errors=False, silent=True) -> dict:
        return {
            'func': self.func.__name__,
            'ptype': getattr(self, "ptype", None),
            'comment': getattr(self, "comment", None),
            'gate': getattr(self, "gate", None),
            'group': getattr(self, "group", None),
            'config_inputs': fieldNotEmpty(getattr(self, "config_inputs", None)) and
            parse_inputs(getattr(self, "config_inputs", None), allow_errors, silent),
            'parameters_inputs': fieldNotEmpty(getattr(self, "parameters_inputs", None)) and
            parse_inputs(getattr(self, "parameters_inputs", None), allow_errors, silent),
            'external_state_inputs': fieldNotEmpty(getattr(self, "external_state_inputs", None)) and
            parse_inputs(getattr(self, "external_state_inputs", None), allow_errors, silent),
            'additional_inputs': fieldNotEmpty(getattr(self, "additional_inputs", None)) and
            parse_inputs(getattr(self, "additional_inputs", None), allow_errors, silent),
            'state_inputs': fieldNotEmpty(getattr(self, "state_inputs", None)) and
            parse_inputs(getattr(self, "state_inputs", None), allow_errors, silent),
            'state_outputs': fieldNotEmpty(getattr(self, "state_outputs", None)) and
            parse_outputs(getattr(self, "state_outputs", None)),
            'args': getattr(self, "args", None),
        }

    def __getnewargs__(self):
        return (1, 2, 3)

    def __getstate__(self):
        return {
            # 'func': marshal.dumps(self.func.__code__),
            'func': pickle.dumps(self.func),
            'ptype': getattr(self, 'ptype', None),
            'comment': getattr(self, 'comment', None),
            'gate': getattr(self, 'gate', None),
            'group': getattr(self, 'group', None),
            'config_inputs': pickle.dumps(getattr(self, "config_inputs", None)),
            'parameters_inputs': pickle.dumps(getattr(self, "parameters_inputs", None)),
            'external_state_inputs': pickle.dumps(getattr(self, "external_state_inputs", None)),
            'additional_inputs': pickle.dumps(getattr(self, "additional_inputs", None)),
            'state_inputs': pickle.dumps(getattr(self, "state_inputs", None)),
            'state_outputs': pickle.dumps(getattr(self, "state_outputs", None)),
            'args': getattr(self, 'args', None),
        }

    def __setstate__(self, state):
        # print(state)
        for key, value in state.items():
            if key in ["func", "config_inputs", "parameters_inputs", "external_state_inputs",
                       "additional_inputs", "state_inputs",
                       "state_outputs"]:
                v = pickle.loads(value)
                setattr(self, key, v)
            else:
                setattr(self, key, value)
