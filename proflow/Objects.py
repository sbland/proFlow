from dataclasses import dataclass, field
from proflow.external_state import External_State_Shape
from proflow.parameters import Parameters_Shape
from proflow.config import Config_Shape
from proflow.process_inspector import parse_inputs
from typing import Callable, List

from .internal_state import Model_State_Shape


@dataclass(frozen=True)
class I:  # noqa: E742
    """interface Named Tuple"""
    from_: str
    as_: str = None
    required: bool = False  # If true then is asserted != null on debug mode

    def __repr__(self) -> str:
        return f'I(from_="{self.from_}" as_="{self.as_}")'


# @dataclass(frozen=True)
@dataclass
class Process:
    """Process object that stores the function and input and output targets."""
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
    state_outputs: List[I] = field(default_factory=list)
    map_outputs: Callable[[any, object], object] = field(default_factory=list)
    args: List[any] = field(default_factory=list)  # additional args

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
            f'state_outputs={self.state_outputs}',
            f'args={self.args}',
        ]) + ')'
