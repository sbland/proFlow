from dataclasses import dataclass, field
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
    group: str = ""  # group tag
    # Inputs to function
    # TODO: The below objects could be set as the actual State Shape objects instead
    state_inputs: Callable[[object], List[I]] = \
        field(default_factory=lambda: lambda *args, **kwargs: [])
    config_inputs: Callable[[object], List[I]] = \
        field(default_factory=lambda: lambda *args, **kwargs:  [])
    parameters_inputs: Callable[[object], List[I]] = \
        field(default_factory=lambda: lambda *args, **kwargs:  [])
    external_state_inputs: Callable[[object], List[I]] = \
        field(default_factory=lambda: lambda *args, **kwargs:  [])
    additional_inputs: List[tuple] = \
        field(default_factory=lambda: lambda *args, **kwargs:  [])
    # TODO: state_outputs is depreciated
    state_outputs: Callable[[any, object], object] = field(default_factory=list)
    map_outputs: Callable[[any, object], object] = field(default_factory=list)
    args: List[any] = field(default_factory=list)  # additional args

    def __repr__(self) -> str:
        return 'Process(' + '; '.join([
            f'func={self.func.__name__}',
            f'comment="{self.comment}"',
            f'gate={self.gate}',
            f'config_inputs={self.config_inputs}',
            f'parameters_inputs={self.parameters_inputs}',
            f'external_state_inputs={self.external_state_inputs}',
            f'additional_inputs={self.additional_inputs}',
            f'state_inputs={self.state_inputs}',
            f'state_outputs={self.state_outputs}',
            f'args={self.args}',

        ]) + ')'
