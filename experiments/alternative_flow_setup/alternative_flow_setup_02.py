"""We need to be able to log where inputs are coming from and the modifications we are making to the state"""
from dataclasses import dataclass
from typing import Callable, List, NamedTuple
import inspect
from functools import reduce, partial


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
    map_inputs: List[tuple] = None
    map_outputs: List[tuple] = None
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


# def get_processes():
#     processes = [
#         Process(
#             func=lambda state, config: add_me(
#                 x=state['foo']['bar'],
#                 y=config['hello']['val']
#             ),
#             comment="add_me",
#             output=lambda value, prev_state: {**prev_state, **{'foo': {'bar': value}}}
#         ),
#         [Process(
#             func=lambda state, config: mult_me(
#                 x=state['foo']['bar'],
#                 y=config['hello']['val']
#             ),
#             comment=f"mult_me - {i}",
#             output=lambda value, prev_state: {**prev_state, **{'foo': {'bar': value}}},
#             gate=lambda state, config: state['foo']['bar'] < 200
#         ) for i in range(3)]

#     ]
#     return flatten_list(processes)


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

# demo_old_process = Process(
#     func=add_me,
#     config_inputs=[
#         I('hello.val', as_='y'),
#     ],
#     state_inputs=[
#         I('foo.bar', as_='x'),
#     ],
#     state_outputs=[
#         I('_result', as_='foo.bar'),
#     ],
# )


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


# ==Methods of processing output==

# # simple approach
# state = {
#     **prev_state,
#     **{"foo": { "bar": add_me(state['foo']['bar'])}}
# }

# # or

# new_val = add_me(state['foo']['bar'])
# state = {
#     **prev_state,
#     **{"foo": { "bar": new_val}}
# }

# == Run Process ==
# state_out = run_process(state, demo_process, config)
# print(state_out)


# == Analyse inputs ==

# Analyse process object
# print(inspect.getsource(demo_process.map_inputs))
# print(inspect.unwrap(demo_process.func))
# print(inspect.unwrap(demo_process.map_inputs))

import re

def clean_key(k: str):
    stripped = k.strip()[1:-1]
    return stripped

    
def clean_val(v: str):
    """Clean the value component.

    Captured in brackets
    "(state['foo']['bar'] + 1),"
    "(state['foo']['bar'] + 1)"

    Parameters
    ----------
    v : str
        [description]
    """
    # get text inside the double inverted commas and
    r = re.compile('(?:\"|^)(.*?)(?=(?:,|\"|$|\s*[,\"]|\s*$))(?:,|$|\"|\s)*')
    stripped = r.search(v).groups()[0].strip()
    return stripped

# %%
def extract_target_path_from_val(v:str):
    print(v)

print('---extract_target_path_from_val----')
print(extract_target_path_from_val("['foo']['bar'][0][i].foo.bar"))
print('-------')

# %%
def convert_val(v: str):
    """Convert val from new style to old style.

    Expected Input:
    state['foo']['bar'][0][i] + 1

    Expected output:
    state.foo.bar.0._i_

    """
    # step 1. Find state or config
    find_state_conf_parts = '(?P<target>state|config)(?P<value>(?:\S*\[(.*?)\])\S*)'
    find_trailing_parts = '(?P<trailing>( (?![^\[]*?\])(.*?(?![^\[]*?\])) )(?![^\[]*?\]).*?)(\[|$|state|config)'
    r = re.compile(find_state_conf_parts + '|' + find_trailing_parts)
    # r = re.compile(find_trailing_parts)
    matches = r.finditer(v)
    parts = [m.groupdict() for m in matches]
    state_conf_parts = [p for p in parts if p['trailing'] is None]
    trailing_parts = [p for p in parts if p['trailing'] is not None]
    return state_conf_parts, trailing_parts

from pprint import pprint
pprint(convert_val("state['foo']['bar'] + 1"))


# print('clean_val:', clean_val(" state['foo']['bar'] + 1,"))


# print('clean_key:', clean_key('        "x"'))
# print('-------')


# def parse_inputs(process):
#     """Convert new inputs into old inputs."""
#     inputs_source = inspect.getsource(demo_process.map_inputs)
#     input_lines = inputs_source.split('\n')[1:-2]
#     input_map = [r.split(':') for r in input_lines]
#     cleaned_input_map = [(clean_key(k), clean_val(v)) for k,v in input_map]

#     input_dict = dict(cleaned_input_map)
#     return input_dict


# print(parse_inputs(demo_process))
# print(parse_inputs(demo_process).keys())






