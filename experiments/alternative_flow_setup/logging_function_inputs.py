"""We need to be able to log where inputs are coming from and the modifications we are making to the state"""
from dataclasses import dataclass
from typing import Callable
import inspect
from functools import reduce


def flatten_list(arr: list) -> list:
    """ Recursive list flatten"""
    return [item for sublist in arr
            for item in
            (flatten_list(sublist) if type(sublist) is list else [sublist])]


@dataclass
class Process:
    """Process object that stores the function and input and output targets."""
    func: Callable[[dict, dict],
                   dict] = lambda: NotImplementedError()  # The function to call
    output: Callable[[dict], any] = lambda: NotImplementedError()
    gate: Callable[[dict], any] = None
    comment: str = ""  # used for logging
    # group: str = ""  # group tag
    # # Inputs to function
    # config_inputs: List[I] = field(default_factory=list)
    # parameters_inputs: List[I] = field(default_factory=list)
    # external_state_inputs: List[I] = field(default_factory=list)
    # additional_inputs: List[tuple] = field(default_factory=list)
    # state_inputs: List[I] = field(default_factory=list)
    # state_outputs: List[I] = field(default_factory=list)
    # args: List[any] = field(default_factory=list)  # additional args


def add_me(x, y):
    return x + y


def mult_me(x, y):
    return x * y


state = {
    'foo': {
        'bar': 123
    }
}
config = {
    'hello': {
        'world': 'abc',
        'val': 3
    }
}


def get_processes():
    processes = [
        Process(
            func=lambda state, config: add_me(
                x=state['foo']['bar'],
                y=config['hello']['val']
            ),
            comment="add_me",
            output=lambda value, prev_state: {**prev_state, **{'foo': {'bar': value}}}
        ),
        [Process(
            func=lambda state, config: mult_me(
                x=state['foo']['bar'],
                y=config['hello']['val']
            ),
            comment=f"mult_me - {i}",
            output=lambda value, prev_state: {**prev_state, **{'foo': {'bar': value}}},
            gate=lambda state, config: state['foo']['bar'] < 200
        ) for i in range(3)]

    ]
    return flatten_list(processes)

def process_wrapper(config, state):
    def run(fn):
        pass

processes = get_processes()
print(list(map(lambda p: p.comment, processes)))

# Can we print where in the variables came from
print(list(map(lambda p: p.func.__name__, processes)))

print(inspect.getsource(processes[0].func))




# def process_runner():


#     def run_process(prev_state, process):
#         if process.gate is not None and not process.gate(prev_state, config):
#             return prev_state
#         out = process.func(prev_state, config)
#         return process.output(out, prev_state)

#     processes = get_processes()

#     state_out = reduce(run_process, get_processes(), state)
#     return state_out, processes


# final_state, processes_ran = process_runner()
# print(final_state)
# assert final_state == {
#     'foo': {
#         'bar': 378
#     }
# }

# # How do we get the inputs and outputs
# print(processes_ran[0].func)
