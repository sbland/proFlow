from dataclasses import dataclass, field
from typing import Callable, List

from .internal_state import Model_State_Shape


@dataclass(frozen=True)
class I:  # noqa: E742
    """interface Named Tuple"""
    from_: str
    as_: str = None


@dataclass(frozen=True)
class Process:
    """Process object that stores the function and input and output targets."""
    func: Callable[[Model_State_Shape], Model_State_Shape] = lambda: NotImplementedError()  # The function to call
    gate: bool = True  # if False process is skipped
    comment: str = ""  # used for logging
    # Inputs to function
    config_inputs: List[I] = field(default_factory=list)
    parameters_inputs: List[I] = field(default_factory=list)
    external_state_inputs: List[I] = field(default_factory=list)
    additional_inputs: List[tuple] = field(default_factory=list)
    state_inputs: List[I] = field(default_factory=list)
    state_outputs: List[I] = field(default_factory=list)
    args: List[any] = field(default_factory=list)  # additional args
