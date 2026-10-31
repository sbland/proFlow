import re
from collections import namedtuple
from dataclasses import dataclass

from proflow.objects.process import Process


@dataclass(frozen=True)
class ProcessStateNetwork:
    state_keys: list[str]
    input_links: list[list[int]]
    output_links: list[list[int]]


def get_all_unique_inputs(processes: list[Process]) -> list[str]:
    inputs_list = list({inp.from_ for p in processes for inp in p.state_inputs}) + list(
        {inp.as_ for p in processes for inp in p.state_outputs}
    )
    return list(set(inputs_list))[::-1]


def get_inputs_map(inputs_list: list[str]) -> dict[str, int]:
    return {inp: i for i, inp in enumerate(inputs_list)}


def get_links(inputs_map: dict[str, int], process: Process):
    Output = namedtuple("Output", "comment input_links output_links")
    input_links = [inputs_map[ip.from_] for ip in process.state_inputs if ip.from_ in inputs_map]
    output_links = [inputs_map[ip.as_] for ip in process.state_outputs if ip.as_ in inputs_map]
    return Output(process.comment, input_links, output_links)


def processes_to_state_network(
    processes: list[Process],
    filter_state_string: str | re.Pattern = ".*",
) -> ProcessStateNetwork:
    """Build the process-to-state links used by the canvas dataflow diagram."""
    filter_re = (
        filter_state_string
        if type(filter_state_string) is re.Pattern
        else re.compile(f".*{filter_state_string}.*")
    )
    state_keys = [key for key in get_all_unique_inputs(processes) if filter_re.match(key)]
    inputs_map = get_inputs_map(state_keys)
    links = [get_links(inputs_map, process) for process in processes]
    return ProcessStateNetwork(
        state_keys=state_keys,
        input_links=[link.input_links for link in links],
        output_links=[link.output_links for link in links],
    )
