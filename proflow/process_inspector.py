from collections import namedtuple
from typing import List, Tuple, TYPE_CHECKING, Callable
import inspect
import re

from proflow.Objects.Interface import I

if TYPE_CHECKING:
    from proflow.Objects.Process import Process


# def clean_key(k: str):
#     stripped = k.strip()[1:-1]
#     return stripped


# def clean_val(v: str):
#     """Clean the value component.

#     Captured in brackets
#     "(state['foo']['bar'] + 1),"
#     "(state['foo']['bar'] + 1)"

#     Parameters
#     ----------
#     v : str
#         [description]
#     """
#     # get text inside the double inverted commas and
#     r = re.compile(r'(?:\"|^)(.*?)(?=(?:,|\"|$|\s*[,\"]|\s*$))(?:,|$|\"|\s)*')
#     stripped = r.search(v).groups()[0].strip()
#     return stripped


# def extract_target_path_from_val(v: str):
#     raise NotImplementedError()
#     # print(v)


def split_trailing_and_part(v: str):
    """Convert val from new style to old style.

    Expected Input:
    state['foo']['bar'][0][i] + 1

    Expected output:
    state.foo.bar.0._i_

    """
    # step 1. Find state or config
    find_state_conf_parts = r'(?P<target>state|config)(?P<value>(?:\S*\[(.*?)\])\S*)'
    find_trailing_parts = \
        r'(?P<trailing>( (?![^\[]*?\])(.*?(?![^\[]*?\])) )(?![^\[]*?\]).*?)(\[|$|state|config)'
    r = re.compile(find_state_conf_parts + '|' + find_trailing_parts)
    matches = r.finditer(v)
    parts = [m.groupdict() for m in matches]

    def merge_parts_fn(p):
        p_mod = {'target': p['target'], 'value': p['value']} if p['target'] is not None \
            else {'target': 'trailing', 'value': p['trailing']}
        return p_mod
    merged_parts = list(map(merge_parts_fn, parts))
    return merged_parts


# ==========================


def extract_inputs_lines(map_inputs_fn):
    inputs_source = inspect.getsource(map_inputs_fn)
    # r = re.compile(r'.(?<=\[).*\]', re.DOTALL | re.MULTILINE) # Include brackets
    r = re.compile(r'I\((.*?)\)(?:,|$)', re.DOTALL | re.MULTILINE)  # inside of I object
    matches = r.finditer(inputs_source)
    lines = (g for match in matches if match is not None for g in match.groups())
    return lines


def remove_inverted_commas_from_arg(arg: str) -> str:
    """Remove surrounding '' from string."""
    if arg[0] == "'" and arg[-1] == "'":
        return arg[1:-1]
    else:
        return arg


def split_from_and_as(raw_input_line: str) -> Tuple[List[str], dict]:
    """Convert a raw input line into args and kwargs for Interface Class.

    Parameters
    ----------
    raw_input_line : str
        Example: "config.a.foo.bar, as_='x'"

    Returns
    -------
    args
        List[str]: arguments for I
    kwargs
        dict: arguments for I
    """
    Output = namedtuple('Output', 'args kwargs')
    split_args = raw_input_line.split(',')
    split_sub_args = (s.strip().split('=') for s in split_args)
    args = (s[0] for s in split_sub_args if len(s) == 1)
    split_sub_args = (s.strip().split('=') for s in split_args)
    R = remove_inverted_commas_from_arg
    kwargs = {s[0]: R(s[1]) for s in split_sub_args if len(s) == 2}
    return Output(args, kwargs)


def parse_key(k: str) -> str:
    """Convert a input key to dot notation.

    Parameters
    ----------
    k : str
        example: config.a.foo[0][var]

    Returns
    -------
    str
        example: config.a.foo.0.[var]
    """

    def replace_var_fn(x):
        print(x.groups())
        if x.groups()[0] is not None:
            return f'.{x.groups()[0]}.'
        elif x.groups()[1] is not None:
            return f'.{x.groups()[1]}.'
        elif x.groups()[2] is not None:
            return f'.[{x.groups()[2]}].'
        else:
            return 'zzz'
    # step 1. Find state or config
    find_square_brackets = r'\[(\d*?)\]|\[\'(\D*?)\'\]|\[(\D*?)\]'
    r = re.compile(find_square_brackets, re.DOTALL)
    # print(list(r.finditer(k)))
    replaced_parts = re.sub(r, replace_var_fn, k)
    replaced_double_dots = re.sub(r'\.\.+', '.', replaced_parts)
    out = re.sub(r'^\'|\'$|\.$|^\.|\.\'$', '', replaced_double_dots)
    return out


def parse_inputs(map_inputs_fn: Callable[[any], List[I]]) -> dict:
    input_lines_row = extract_inputs_lines(map_inputs_fn)
    args_and_kwargs = (split_from_and_as(line) for line in input_lines_row)
    input_objects = (I(*out.args, **out.kwargs) for out in args_and_kwargs)
    inputs_map = {parse_key(i.from_): i.as_ for i in input_objects}
    return inputs_map


def parse_outputs(output_objects: List[I]) -> dict:
    outputs_map = {parse_key(i.from_): f'state.{i.as_}' for i in output_objects}
    return outputs_map


def inspect_process(process: 'Process'):
    args_parsed = {
        "config_inputs": parse_inputs(process.config_inputs),
        "state_inputs": parse_inputs(process.state_inputs),
        "parameter_inputs": parse_inputs(process.state_inputs),
        "additional_inputs": parse_inputs(process.additional_inputs),
        "state_outputs": parse_outputs(process.state_outputs),
    }

    return args_parsed
