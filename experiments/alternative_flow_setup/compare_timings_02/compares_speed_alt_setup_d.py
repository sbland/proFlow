# %%
from timeit import repeat
from dataclasses import dataclass, field
from typing import Callable, List, NamedTuple
import inspect
from functools import reduce, partial


def flatten_list(arr: list) -> list:
    """ Recursive list flatten"""
    return [item for sublist in arr
            for item in
            (flatten_list(sublist) if type(sublist) is list else [sublist])]


def add_me(x, y):
    return x + y


# %%

@dataclass(frozen=True)
class I:  # noqa: E742
    """interface Named Tuple"""
    from_: any
    as_: str = None
    required: bool = False  # If true then is asserted != null on debug mode

    def __repr__(self) -> str:
        return f'I(from_="{self.from_}" as_="{self.as_}")'


@dataclass
class Process:
    """Process object that stores the function and input and output targets."""
    func: Callable[[dict, dict],
                   dict] = lambda: NotImplementedError()  # The function to call
    gate: Callable[[dict], any] = None
    comment: str = ""  # used for logging
    output: Callable[[dict], any] = lambda: NotImplementedError()
    config_inputs: List[I] = field(default_factory=list)
    parameters_inputs: List[I] = field(default_factory=list)
    external_state_inputs: List[I] = field(default_factory=list)
    additional_inputs: List[tuple] = field(default_factory=list)
    state_inputs: List[tuple] = field(default_factory=list)

    map_inputs: List[tuple] = None
    map_outputs: List[tuple] = None

# %%


def run_process(
        prev_state: NamedTuple,  # Can be state or parameter
        process: Process,
        config) -> NamedTuple:
    """ Run a single process and output the updated state.
        The process object contains the function along with all the input
        and output targets.


        note: args from process are not garuanteed to be in the correct order
    """
    config_args = process.config_inputs(config)
    # parameters_args = process.parameters_inputs(parameters)
    # external_state_args = process.external_state_inputs(external_state)
    # additional_args = process.additional_inputs(additional)
    state_args = process.state_inputs(prev_state)


    # kwargs = {**config_args, **state_args} # fastest method
    kwargs = {i.as_: i.from_ for i in config_args + state_args}

    result = process.func(**kwargs)
    state_out = process.map_outputs(result, prev_state)
    return state_out
# %%

state = {
    'foo': {
        'bar': 123,
        "roo": 456,
        "lst": [1,2,3,4]
    },
}
config = {
    'hello': {
        'world': 'abc',
        'val': 3,
        "nested": {
            "really": {
                "deep": 9,
            }
        }
    }
}

# %%


demo_process = Process(
    func=add_me,
    config_inputs=lambda config: (
        I(config['hello']['nested']['really']['deep'], as_='y'),
    ),
    state_inputs=lambda state: (
        I(state['foo']['lst'][1] + 1, as_='x'),
    ),
    map_outputs=lambda result, prev_state: {
        **prev_state,
        **{"foo": {"bar": result}},
    }
)


# %%
state_out = run_process(state, demo_process, config)
print(state_out)

# %%

# Compare timeings


t1 = min(repeat(lambda: run_process(state, demo_process, config)))
print(t1)
# 2.52
