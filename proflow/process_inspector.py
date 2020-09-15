from __future__ import annotations

import inspect
import re

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from proflow.Objects import Process


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
    r = re.compile(r'(?:\"|^)(.*?)(?=(?:,|\"|$|\s*[,\"]|\s*$))(?:,|$|\"|\s)*')
    stripped = r.search(v).groups()[0].strip()
    return stripped


def extract_target_path_from_val(v: str):
    raise NotImplementedError()
    # print(v)


def convert_val(v: str):
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


def parse_inputs_ss(map_inputs_fn):
    """Convert new inputs into old inputs."""
    inputs_source = inspect.getsource(map_inputs_fn)
    input_lines = inputs_source.split('\n')[1:-2]
    input_map = [r.split(':') for r in input_lines]
    cleaned_input_map = [(clean_key(k), clean_val(v)) for k, v in input_map]

    input_dict = dict(cleaned_input_map)
    return input_dict


def parse_inputs(map_inputs_fn):
    inputs_source = inspect.getsource(map_inputs_fn)
    # r = re.compile(r'.(?<=\[).*\]', re.DOTALL | re.MULTILINE) # Include brackets
    r = re.compile(r'I\((.*?)\)(?:,|$)', re.DOTALL | re.MULTILINE)  # inside of I object
    match = r.search(inputs_source)
    groups = match.groups() if match is not None else None
    return groups


def inspect_process_inputs(process: 'Process'):
    inputs_parsed = {
        "config_inputs": parse_inputs(process.config_inputs),
        "state_inputs": parse_inputs(process.state_inputs),
        "parameter_inputs": parse_inputs(process.state_inputs),
        "additional_inputs": parse_inputs(process.additional_inputs),
    }

    return inputs_parsed
