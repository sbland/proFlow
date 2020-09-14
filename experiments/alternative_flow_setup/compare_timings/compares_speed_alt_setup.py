# %%
from dataclasses import dataclass
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

@dataclass
class Process:
    """Process object that stores the function and input and output targets."""
    func: Callable[[dict, dict],
                   dict] = lambda: NotImplementedError()  # The function to call
    output: Callable[[dict], any] = lambda: NotImplementedError()
    gate: Callable[[dict], any] = None
    comment: str = ""  # used for logging
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
    kwargs = process.map_inputs(config, prev_state)
    result = process.func(**dict(kwargs))
    state_out = process.map_outputs(result, prev_state)
    return state_out
# %%

state = {
    'foo': {
        'bar': 123,
        "roo": 456,
    },
}
config = {
    'hello': {
        'world': 'abc',
        'val': 3
    }
}

# %%


demo_process = Process(
    func=add_me,
    map_inputs=lambda config, state: {
        "x": state['foo']['bar'] + 1,
        "y": config['hello']['val']
    },
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
from timeit import repeat


t1 = min(repeat(lambda: run_process(state, demo_process, config)))
print(t1)
# 0.6141055879998021